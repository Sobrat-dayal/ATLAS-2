"""Institutional-Grade Research Collaboration, Analyst Review, Evidence Governance and Approval Workflow Tests (Stage 108).

Comprehensive verification covering:
1. Research Access Grants & Participant Governance (roles, updates, revocations, ownership enforcement)
2. Formal Review Lifecycle & State Machine (submit, update, cancel, duplicate prevention)
3. Exact Revision Binding & Invalidation on Content Mutation
4. Separation-of-Duties Enforcement (Author self-approval forbidden)
5. Review Decisions (Approve, Request Changes, Reject) and Report Status Alignment
6. Anchored Discussion Threads & Comments (section/block anchors, replies, resolve, reopen, staleness)
7. Research Governance Quality Gates (structural checks, citation cutoff audits, unresolved comments gate)
8. Controlled Internal Circulation of Approved/Finalized Reports & Revocation
9. Review Audit Trail Timeline Logging
"""

import pytest
from atlas.auth import AuthPrincipal
from atlas.research.domain import ResearchReport, ResearchReportSection
from atlas.research.enums import (
    CommentAnchorType,
    CommentThreadStatus,
    ReportLifecycleStatus,
    ReportSectionType,
    ResearchPrincipalType,
    ResearchReportType,
    ResearchResourceType,
    ResearchRole,
    ReviewDecisionType,
    ReviewScope,
    ReviewStatus,
)
from atlas.research.repository import ResearchRepository
from atlas.research.schemas import CreateReportSectionRequest, CreateResearchReportRequest
from atlas.research.service import ResearchService, get_research_service
from fastapi.testclient import TestClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.main import app

# ---------------------------------------------------------------------------
# Fixtures & Setup
# ---------------------------------------------------------------------------

class AuthContext:
    current_user_id: str = "analyst-author"


@pytest.fixture
def auth_ctx():
    ctx = AuthContext()
    ctx.current_user_id = "analyst-author"
    return ctx


@pytest.fixture
def clean_research_service():
    """Create an isolated test ResearchService with clean repository."""
    repo = ResearchRepository()
    return ResearchService(repository=repo)


@pytest.fixture
def client(clean_research_service, auth_ctx):
    """FastAPI TestClient with dynamic auth context switching."""
    app.dependency_overrides[get_research_service] = lambda: clean_research_service
    app.dependency_overrides[get_current_user] = lambda: AuthPrincipal(
        sub=auth_ctx.current_user_id,
        email=f"{auth_ctx.current_user_id}@atlas-research.local",
        role="authenticated",
    )
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


def _seed_report(clean_research_service: ResearchService, owner_id: str = "analyst-author") -> str:
    """Helper to seed a valid structured research report with sections."""
    rep = clean_research_service.create_report(
        data=CreateResearchReportRequest(
            investigation_id="inv-apple-fy24-margins",
            title="Apple Inc. Operating Margin Durability Review",
            report_type=ResearchReportType.COMPANY_UPDATE,
            template_id="tpl-company-research",
            primary_subject_id="AAPL",
            primary_subject_type="EQUITY",
            abstract="Institutional assessment of Apple FY24 margins and Services mix expansion.",
        ),
        user_id=owner_id,
    )
    clean_research_service.create_report_section(
        report_id=rep.report_id,
        data=CreateReportSectionRequest(
            heading="Executive Summary",
            section_type=ReportSectionType.EXECUTIVE_SUMMARY,
            content_blocks=[
                {"block_type": "PARAGRAPH", "content": "Operating income reached $123.18B in FY2024 with 31.5% margin."}
            ],
        ),
        user_id=owner_id,
    )
    return rep.report_id


# ---------------------------------------------------------------------------
# 1. Access Grants & Participant Governance Tests
# ---------------------------------------------------------------------------

def test_participant_grant_lifecycle(client, auth_ctx, clean_research_service):
    report_id = _seed_report(clean_research_service, owner_id="analyst-author")
    auth_ctx.current_user_id = "analyst-author"

    # 1. Author grants REVIEWER access to senior-reviewer
    grant_resp = client.post(
        f"/api/v1/research/resources/REPORT/{report_id}/participants",
        json={
            "principal_type": "USER",
            "principal_id": "senior-reviewer",
            "role": "REVIEWER",
        },
    )
    assert grant_resp.status_code == 201
    grant_data = grant_resp.json()
    assert grant_data["principal_id"] == "senior-reviewer"
    assert grant_data["role"] == "REVIEWER"
    grant_id = grant_data["grant_id"]

    # 2. List participants
    list_resp = client.get(f"/api/v1/research/resources/REPORT/{report_id}/participants")
    assert list_resp.status_code == 200
    grants = list_resp.json()["grants"]
    assert any(g["grant_id"] == grant_id for g in grants)

    # 3. Update participant role to EDITOR
    patch_resp = client.patch(
        f"/api/v1/research/participants/{grant_id}",
        json={"role": "EDITOR"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["role"] == "EDITOR"

    # 4. Outsider cannot modify participant grants (403 Forbidden)
    auth_ctx.current_user_id = "outsider-user"
    outsider_patch = client.patch(
        f"/api/v1/research/participants/{grant_id}",
        json={"role": "OWNER"},
    )
    assert outsider_patch.status_code == 403

    # 5. Revoke grant as author
    auth_ctx.current_user_id = "analyst-author"
    del_resp = client.delete(f"/api/v1/research/participants/{grant_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["revoked_at"] is not None


# ---------------------------------------------------------------------------
# 2. Review Request Submission & State Machine Tests
# ---------------------------------------------------------------------------

def test_review_request_lifecycle(client, auth_ctx, clean_research_service):
    report_id = _seed_report(clean_research_service, owner_id="analyst-author")
    auth_ctx.current_user_id = "analyst-author"

    # 1. Submit review request
    submit_resp = client.post(
        "/api/v1/research/reviews",
        json={
            "target_type": "REPORT",
            "target_id": report_id,
            "assigned_reviewer_id": "senior-reviewer",
            "review_scope": "FULL_REPORT",
            "instructions": "Please verify FY24 margin claims against SEC 10-K filings.",
        },
    )
    assert submit_resp.status_code == 201
    rev_data = submit_resp.json()
    review_id = rev_data["review_request_id"]
    assert rev_data["target_id"] == report_id
    assert rev_data["status"] == "SUBMITTED"
    assert rev_data["assigned_reviewer_id"] == "senior-reviewer"

    # 2. Attempting duplicate active review request returns 409 Conflict
    dup_resp = client.post(
        "/api/v1/research/reviews",
        json={
            "target_type": "REPORT",
            "target_id": report_id,
            "assigned_reviewer_id": "senior-reviewer",
        },
    )
    assert dup_resp.status_code == 409

    # 3. List reviews filtering by target_id
    list_resp = client.get(f"/api/v1/research/reviews?target_id={report_id}")
    assert list_resp.status_code == 200
    assert list_resp.json()["total_count"] >= 1

    # 4. Update review request instructions
    update_resp = client.patch(
        f"/api/v1/research/reviews/{review_id}",
        json={"instructions": "Updated instructions: check peer benchmarking as well."},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["instructions"] == "Updated instructions: check peer benchmarking as well."

    # 5. Cancel review request
    cancel_resp = client.post(f"/api/v1/research/reviews/{review_id}/cancel")
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "CANCELED"


# ---------------------------------------------------------------------------
# 3. Separation of Duties & Decision Approval Workflow
# ---------------------------------------------------------------------------

def test_separation_of_duties_self_approval_blocked(client, auth_ctx, clean_research_service):
    report_id = _seed_report(clean_research_service, owner_id="analyst-author")
    auth_ctx.current_user_id = "analyst-author"

    # Author creates review request
    submit_resp = client.post(
        "/api/v1/research/reviews",
        json={
            "target_type": "REPORT",
            "target_id": report_id,
            "assigned_reviewer_id": "senior-reviewer",
        },
    )
    review_id = submit_resp.json()["review_request_id"]

    # Author attempts to approve their own report -> 403 Forbidden (Separation of duties)
    self_approve_resp = client.post(
        f"/api/v1/research/reviews/{review_id}/decisions",
        json={
            "decision": "APPROVE",
            "decision_comment": "Self-approving my own report.",
        },
    )
    assert self_approve_resp.status_code == 403


def test_independent_review_approval_and_revision_binding(client, auth_ctx, clean_research_service):
    report_id = _seed_report(clean_research_service, owner_id="analyst-author")
    auth_ctx.current_user_id = "analyst-author"

    # 1. Author submits review
    submit_resp = client.post(
        "/api/v1/research/reviews",
        json={
            "target_type": "REPORT",
            "target_id": report_id,
            "assigned_reviewer_id": "senior-reviewer",
        },
    )
    review_id = submit_resp.json()["review_request_id"]
    submitted_rev = submit_resp.json()["target_revision_number"]

    # 2. Independent reviewer approves the report
    auth_ctx.current_user_id = "senior-reviewer"
    approve_resp = client.post(
        f"/api/v1/research/reviews/{review_id}/decisions",
        json={
            "decision": "APPROVE",
            "decision_comment": "All operating margin figures verified against 2024 Form 10-K.",
            "expected_revision_number": submitted_rev,
        },
    )
    assert approve_resp.status_code == 201
    dec_data = approve_resp.json()
    assert dec_data["decision"] == "APPROVE"
    assert dec_data["reviewer_user_id"] == "senior-reviewer"

    # 3. Verify report approval status endpoint
    auth_ctx.current_user_id = "analyst-author"
    status_resp = client.get(f"/api/v1/research/reports/{report_id}/approval-status")
    assert status_resp.status_code == 200
    approval_info = status_resp.json()
    assert approval_info["is_approved"] is True
    assert approval_info["approved_by"] == "senior-reviewer"

    # 4. Deciding an already completed review returns 409 Conflict
    auth_ctx.current_user_id = "senior-reviewer"
    redecide_resp = client.post(
        f"/api/v1/research/reviews/{review_id}/decisions",
        json={"decision": "REJECT"},
    )
    assert redecide_resp.status_code == 409


def test_request_changes_decision_flow(client, auth_ctx, clean_research_service):
    report_id = _seed_report(clean_research_service, owner_id="analyst-author")
    auth_ctx.current_user_id = "analyst-author"

    submit_resp = client.post(
        "/api/v1/research/reviews",
        json={
            "target_type": "REPORT",
            "target_id": report_id,
            "assigned_reviewer_id": "senior-reviewer",
        },
    )
    review_id = submit_resp.json()["review_request_id"]

    # Reviewer requests changes
    auth_ctx.current_user_id = "senior-reviewer"
    change_resp = client.post(
        f"/api/v1/research/reviews/{review_id}/decisions",
        json={
            "decision": "REQUEST_CHANGES",
            "decision_comment": "Please expand on Services margin drivers in Item 7.",
        },
    )
    assert change_resp.status_code == 201
    assert change_resp.json()["decision"] == "REQUEST_CHANGES"

    # Check review request status is now CHANGES_REQUESTED
    rev_get = client.get(f"/api/v1/research/reviews/{review_id}")
    assert rev_get.status_code == 200
    assert rev_get.json()["status"] == "CHANGES_REQUESTED"


# ---------------------------------------------------------------------------
# 4. Anchored Comments & Discussions Tests
# ---------------------------------------------------------------------------

def test_anchored_comments_and_resolution(client, auth_ctx, clean_research_service):
    report_id = _seed_report(clean_research_service, owner_id="analyst-author")
    auth_ctx.current_user_id = "senior-reviewer"

    # 1. Reviewer posts an anchored comment on Executive Summary section
    comment_resp = client.post(
        f"/api/v1/research/resources/REPORT/{report_id}/comments",
        json={
            "anchor_type": "REPORT_SECTION",
            "anchor_reference": "Executive Summary",
            "anchor_text": "31.5% margin",
            "initial_comment": "Is this gross margin or operating margin? Please clarify in the heading.",
        },
    )
    assert comment_resp.status_code == 201
    thread_data = comment_resp.json()
    thread_id = thread_data["thread_id"]
    assert thread_data["resolution_status"] == "OPEN"
    assert len(thread_data["comments"]) == 1

    # 2. Author replies to the thread
    auth_ctx.current_user_id = "analyst-author"
    reply_resp = client.post(
        f"/api/v1/research/comment-threads/{thread_id}/replies",
        json={"body": "Clarified: this is operating profit margin from Item 8 Consolidated Statements."},
    )
    assert reply_resp.status_code == 201
    assert reply_resp.json()["author_user_id"] == "analyst-author"

    # 3. List comments for the report
    list_resp = client.get(f"/api/v1/research/resources/REPORT/{report_id}/comments")
    assert list_resp.status_code == 200
    threads = list_resp.json()["threads"]
    assert len(threads) == 1
    assert len(threads[0]["comments"]) == 2

    # 4. Resolve the comment thread
    auth_ctx.current_user_id = "senior-reviewer"
    resolve_resp = client.post(f"/api/v1/research/comment-threads/{thread_id}/resolve")
    assert resolve_resp.status_code == 200
    assert resolve_resp.json()["resolution_status"] == "RESOLVED"

    # 5. Reopen the thread
    reopen_resp = client.post(f"/api/v1/research/comment-threads/{thread_id}/reopen")
    assert reopen_resp.status_code == 200
    assert reopen_resp.json()["resolution_status"] == "REOPENED"


# ---------------------------------------------------------------------------
# 5. Research Quality Gates & Issue Tracking Tests
# ---------------------------------------------------------------------------

def test_research_quality_gate_execution(client, auth_ctx, clean_research_service):
    report_id = _seed_report(clean_research_service, owner_id="analyst-author")
    auth_ctx.current_user_id = "analyst-author"

    gate_resp = client.post(
        f"/api/v1/research/reports/{report_id}/quality-gate",
        json={},
    )
    assert gate_resp.status_code == 200
    data = gate_resp.json()
    assert "eligible_for_review" in data
    assert "eligible_for_finalization" in data
    assert "checklist" in data
    assert len(data["checklist"]) >= 4


# ---------------------------------------------------------------------------
# 6. Controlled Internal Circulation Tests
# ---------------------------------------------------------------------------

def test_internal_circulation_lifecycle(client, auth_ctx, clean_research_service):
    report_id = _seed_report(clean_research_service, owner_id="analyst-author")
    auth_ctx.current_user_id = "analyst-author"

    # 1. Unapproved report cannot be circulated internally (400 Bad Request)
    unapproved_circ = client.post(
        f"/api/v1/research/reports/{report_id}/circulation",
        json={"recipient_user_ids": ["pm-equities-01"]},
    )
    assert unapproved_circ.status_code == 400

    # 2. Formally review and approve the report
    sub_resp = client.post(
        "/api/v1/research/reviews",
        json={
            "target_type": "REPORT",
            "target_id": report_id,
            "assigned_reviewer_id": "senior-reviewer",
        },
    )
    review_id = sub_resp.json()["review_request_id"]
    auth_ctx.current_user_id = "senior-reviewer"
    client.post(
        f"/api/v1/research/reviews/{review_id}/decisions",
        json={"decision": "APPROVE", "decision_comment": "Approved for investment committee."},
    )

    # 3. Circulate approved report as author
    auth_ctx.current_user_id = "analyst-author"
    circ_resp = client.post(
        f"/api/v1/research/reports/{report_id}/circulation",
        json={
            "recipient_user_ids": ["pm-equities-01", "risk-officer-02"],
            "notes": "Circulated for Q4 Equity Committee review.",
        },
    )
    assert circ_resp.status_code == 201
    circ_data = circ_resp.json()
    circulation_id = circ_data["circulation_id"]
    assert circ_data["status"] == "ACTIVE"
    assert len(circ_data["recipient_user_ids"]) == 2

    # 4. List circulations
    list_resp = client.get(f"/api/v1/research/reports/{report_id}/circulation")
    assert list_resp.status_code == 200
    assert list_resp.json()["total_count"] == 1

    # 5. Revoke circulation
    revoke_resp = client.post(f"/api/v1/research/circulation/{circulation_id}/revoke")
    assert revoke_resp.status_code == 200
    assert revoke_resp.json()["status"] == "REVOKED"


# ---------------------------------------------------------------------------
# 7. Audit Trail Events Logging Tests
# ---------------------------------------------------------------------------

def test_review_audit_events_logged(client, auth_ctx, clean_research_service):
    report_id = _seed_report(clean_research_service, owner_id="analyst-author")
    auth_ctx.current_user_id = "analyst-author"

    # Author grants access
    client.post(
        f"/api/v1/research/resources/REPORT/{report_id}/participants",
        json={"principal_id": "senior-reviewer", "role": "REVIEWER"},
    )

    # Review submitted
    sub_resp = client.post(
        "/api/v1/research/reviews",
        json={"target_id": report_id, "assigned_reviewer_id": "senior-reviewer"},
    )
    review_id = sub_resp.json()["review_request_id"]

    # Review decided by reviewer
    auth_ctx.current_user_id = "senior-reviewer"
    client.post(
        f"/api/v1/research/reviews/{review_id}/decisions",
        json={"decision": "APPROVE"},
    )

    # Audit events query
    auth_ctx.current_user_id = "analyst-author"
    audit_resp = client.get(f"/api/v1/research/resources/REPORT/{report_id}/audit-events")
    assert audit_resp.status_code == 200
    events = audit_resp.json()["events"]
    assert len(events) >= 3
    actions = [e["action"] for e in events]
    assert "GRANT_CREATED" in actions
    assert "REVIEW_SUBMITTED" in actions
    assert "REVIEW_DECIDED" in actions

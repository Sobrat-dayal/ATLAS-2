"""Path Explanation Formatter (Stage 136).

Renders hop-by-hop factual explanations for multi-hop graph paths.
Strictly adheres to verified evidence and prohibits any speculative
financial impact or causal claims.
"""

from typing import List
from ..domain import GraphPath, GraphPathHop


def format_path_explanation(path: GraphPath) -> str:
    """Formats a multi-hop graph path into an institutional, evidence-grounded summary."""
    if not path.hops:
        return f"Direct node reference: {path.source_node.canonical_name}"

    lines: List[str] = [
        f"Verified Knowledge Path ({path.total_hops} hop{'s' if path.total_hops > 1 else ''}):"
    ]
    for hop in path.hops:
        role_clause = f" (Role: {hop.predicate.value})"
        status_clause = f" [{hop.verification_status.value}]"
        evidence_clause = f" (Evidence count: {len(hop.evidence_ids)})" if hop.evidence_ids else ""
        lines.append(
            f"  {hop.hop_number}. {hop.from_node.canonical_name} "
            f"--> [{hop.predicate.value}] --> {hop.to_node.canonical_name}"
            f"{status_clause}{evidence_clause}"
        )

    lines.append(
        "Factual Notice: Path depicts verified relationship topology only; "
        "no economic exposure, operational downtime, or financial loss is claimed or implied."
    )
    return "\n".join(lines)

"use client";

import React, { useState } from "react";
import { InvestigationWorkspace } from "./InvestigationWorkspace";
import { NewInvestigationDialog } from "./NewInvestigationDialog";
import { ResearchActivityTimeline } from "./ResearchActivityTimeline";
import { ResearchDocumentComparison } from "./ResearchDocumentComparison";
import { ResearchDocumentViewer } from "./ResearchDocumentViewer";
import { ResearchHeader } from "./ResearchHeader";
import { ResearchInvestigationsTable } from "./ResearchInvestigationsTable";
import { ResearchOverview } from "./ResearchOverview";
import { ResearchSourceDiscovery } from "./ResearchSourceDiscovery";
import { ResearchSourceLibrary } from "./ResearchSourceLibrary";
import { ResearchAnalysisWorkspace } from "./analysis/ResearchAnalysisWorkspace";
import { ResearchReportsWorkspace } from "./reports/ResearchReportsWorkspace";
import { ResearchReviewsWorkspace } from "./reviews/ResearchReviewsWorkspace";
import { ResearchKnowledgeWorkspace } from "./knowledge/ResearchKnowledgeWorkspace";
import { ResearchUpdatesWorkspace } from "./updates/ResearchUpdatesWorkspace";
import { useResearchWorkspace } from "@/hooks/research/useResearchWorkspace";

export function ResearchWorkspace() {
  const {
    activeTab,
    setActiveTab,
    selectedInvestigationId,
    selectInvestigation,
    activeSection,
    setActiveSection,

    overview,
    isOverviewLoading,

    investigations,
    isInvestigationsLoading,
    statusFilter,
    setStatusFilter,
    typeFilter,
    setTypeFilter,
    searchQuery,
    setSearchQuery,

    currentInvestigation,
    notes,
    questions,
    hypotheses,
    claims,
    linkedSources,
    evidenceList,

    createInvestigation,
    updateInvestigation,
    archiveInvestigation,
    createNote,
    saveNote,
    addQuestion,
    updateQuestionStatus,
    addHypothesis,
    updateHypothesisStatus,
    createClaim,
    attachEvidence,

    selectedEvidence,
    setSelectedEvidence,
    selectedSource,
    setSelectedSource,

    // Stage 105: Source Discovery
    discoveryQuery,
    discoveryResults,
    discoveryTotal,
    isDiscoveryLoading,
    sourceTypes,
    searchDiscovery,

    // Stage 105: Document Viewer
    activeDocumentId,
    activeDocument,
    documentProcessingStatus,
    documentOutline,
    activeDocumentSectionId,
    activeDocumentSection,
    documentTables,
    documentSearchQuery,
    documentSearchHits,
    isDocSearchLoading,
    candidates,
    isDocumentLoading,
    selectDocumentSection,
    searchInDocument,
    convertCandidate,

    // Stage 105: Document Comparison
    compareLeftDocId,
    compareRightDocId,
    compareMode,
    comparisonResult,
    isComparing,
    executeDocumentComparison,

    // Shortcuts
    openDocument,
    openComparison,

    // Stage 106: Research Analysis
    analyses,
    analysesTotal,
    isAnalysesLoading,
    selectedAnalysisId,
    selectAnalysis,
    currentAnalysis,
    analysisRuns,
    selectedRunId,
    selectRun,
    currentRunResult,
    currentRunProvenance,
    isRunExecuting,
    analysisFindings,
    analysisAssumptions,
    sensitivityResult,
    isSensitivityLoading,
    hypothesisEvaluations,
    isHypothesisEvaluating,
    createAnalysis,
    duplicateAnalysis,
    deleteAnalysis,
    executeAnalysisRun,
    createFinding,
    updateFinding,
    deleteFinding,
    createAssumption,
    deleteAssumption,
    executeSensitivity,
    evaluateHypothesis,

    // Stage 107: Reports & Theses
    reports,
    reportsTotal,
    isReportsLoading,
    selectedReportId,
    selectReport,
    currentReport,
    reportSections,
    selectedSectionId,
    setSelectedSectionId,
    reportTemplates,
    reportRevisions,
    verificationResult,
    isVerifying,
    reportExports,
    theses,
    selectedThesisId,
    selectThesis,
    currentThesis,
    thesisArguments,
    isThesesLoading,
    reportStatusFilter,
    setReportStatusFilter,
    reportTypeFilter,
    setReportTypeFilter,
    reportSearchQuery,
    setReportSearchQuery,
    createReport,
    updateReport,
    finalizeReport,
    deleteReport,
    createReportSection,
    updateReportSection,
    deleteReportSection,
    reorderReportSections,
    compareReportRevisions,
    verifyReport,
    createReportExport,
    createThesis,
    updateThesis,
    deleteThesis,
    createThesisArgument,
    deleteThesisArgument,

    // Stage 108 Reviews & Governance
    reviews,
    selectedReviewId,
    currentReview,
    isReviewsLoading,
    reviewStatusFilter,
    setReviewStatusFilter,
    selectReview,
    submitReview,
    decideReview,
    cancelReview,
    participants,
    isParticipantsLoading,
    loadParticipants,
    grantParticipant,
    updateParticipant,
    revokeParticipant,
    comments,
    isCommentsLoading,
    loadComments,
    createCommentThread,
    addCommentReply,
    resolveCommentThread,
    reopenCommentThread,
    qualityGateResult,
    isQualityGateRunning,
    runQualityGate,
    circulations,
    isCirculationsLoading,
    loadCirculations,
    circulateReport,
    revokeCirculation,

    // Stage 109 Knowledge, Monitoring & Lifecycle
    knowledgeEntries,
    knowledgeTotal,
    isKnowledgeLoading,
    knowledgeSearchQuery,
    setKnowledgeSearchQuery,
    selectedKnowledgeEntryId,
    selectedKnowledgeEntry,
    dependencyLineage,
    isLineageLoading,
    sourceChangeEvents,
    isSourceChangesLoading,
    selectedSourceChangeEvent,
    impactAssessments,
    isImpactsLoading,
    updateItems,
    updateItemsTotal,
    isUpdateItemsLoading,
    institutionalOverview,
    isInstitutionalOverviewLoading,
    searchKnowledge,
    selectKnowledgeEntry,
    loadDependencyLineage,
    selectSourceChangeEvent,
    acknowledgeUpdate,
    resolveUpdate,
    dismissUpdate,
    reopenUpdate,
    executeRevalidation,

    globalError,
    clearError,
  } = useResearchWorkspace();

  const [isNewDialogOpen, setIsNewDialogOpen] = useState(false);

  // If inside an active investigation, render the multi-pane console
  if (selectedInvestigationId && currentInvestigation) {
    return (
      <InvestigationWorkspace
        investigation={currentInvestigation}
        notes={notes}
        questions={questions}
        hypotheses={hypotheses}
        claims={claims}
        linkedSources={linkedSources}
        evidenceList={evidenceList}
        activeSection={activeSection}
        onSectionChange={setActiveSection}
        onBack={() => selectInvestigation(null)}
        onUpdateInvestigationStatus={(st) =>
          updateInvestigation({ expected_revision: currentInvestigation.revision, status: st })
        }
        onCreateNote={async (title, type) => createNote({ title, note_type: type })}
        onSaveNote={async (noteId, title, body, type) => {
          const target = notes.find((n) => n.note_id === noteId);
          if (!target) return;
          return saveNote(noteId, {
            expected_revision: target.revision,
            title,
            body_document: body,
            note_type: type,
          });
        }}
        onAddQuestion={async (text) => addQuestion({ question_text: text })}
        onUpdateQuestionStatus={updateQuestionStatus}
        onAddHypothesis={async (stmt) => addHypothesis({ statement: stmt })}
        onUpdateHypothesisStatus={updateHypothesisStatus}
        onCreateClaim={async (stmt, cat) => createClaim({ statement: stmt, claim_category: cat })}
        onAttachEvidence={async (sourceId, loc, page, excerpt) =>
          attachEvidence({
            source_reference_id: sourceId,
            source_location_reference: loc,
            page_number: page,
            allowed_excerpt: excerpt,
          })
        }
        selectedEvidence={selectedEvidence}
        onSelectEvidence={setSelectedEvidence}
        selectedSource={selectedSource}
        onSelectSource={setSelectedSource}
      />
    );
  }

  return (
    <div className="flex h-full flex-col overflow-hidden bg-atlas-surface-0">
      {/* Top Header */}
      <ResearchHeader
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onNewInvestigation={() => setIsNewDialogOpen(true)}
        activeCount={overview?.active_investigations_count ?? 0}
      />

      {/* Global Error Alert Banner */}
      {globalError && (
        <div className="flex items-center justify-between border-b border-atlas-negative/30 bg-atlas-negative/10 px-4 py-2 text-xs text-atlas-negative">
          <span>{globalError}</span>
          <button onClick={clearError} className="font-mono text-xs hover:underline">
            ✕ Dismiss
          </button>
        </div>
      )}

      {/* Main Tab Views */}
      <div className="flex-1 overflow-hidden">
        {activeTab === "OVERVIEW" && (
          <div className="h-full overflow-y-auto">
            <ResearchOverview
              overview={overview}
              institutionalOverview={institutionalOverview}
              isLoading={isOverviewLoading || isInstitutionalOverviewLoading}
              onSelectInvestigation={selectInvestigation}
              onNewInvestigation={() => setIsNewDialogOpen(true)}
              onViewAllInvestigations={() => setActiveTab("INVESTIGATIONS")}
              onNavigateTab={(t) => setActiveTab(t)}
            />
          </div>
        )}

        {activeTab === "KNOWLEDGE" && (
          <ResearchKnowledgeWorkspace
            entries={knowledgeEntries}
            totalCount={knowledgeTotal}
            isLoading={isKnowledgeLoading}
            searchQuery={knowledgeSearchQuery}
            onSearchChange={setKnowledgeSearchQuery}
            onSearchSubmit={(types) => searchKnowledge({ query: knowledgeSearchQuery || undefined, entry_types: types })}
            selectedEntryId={selectedKnowledgeEntryId}
            selectedEntry={selectedKnowledgeEntry}
            onSelectEntry={selectKnowledgeEntry}
            lineage={dependencyLineage}
            isLineageLoading={isLineageLoading}
            onInspectLineage={(type, id) => loadDependencyLineage(type, id)}
            onNavigateToResource={(type, id) => {
              if (type === "REPORT") {
                setActiveTab("REPORTS");
                selectReport(id);
              } else if (type === "ANALYSIS") {
                setActiveTab("ANALYSIS");
                selectAnalysis(id);
              } else if (type === "INVESTIGATION") {
                selectInvestigation(id);
              } else if (type === "SOURCE" || type === "DOCUMENT") {
                openDocument(id);
              }
            }}
          />
        )}

        {activeTab === "UPDATES" && (
          <ResearchUpdatesWorkspace
            updateItems={updateItems}
            updateItemsTotal={updateItemsTotal}
            isUpdateItemsLoading={isUpdateItemsLoading}
            onAcknowledgeUpdate={acknowledgeUpdate}
            onResolveUpdate={resolveUpdate}
            onDismissUpdate={dismissUpdate}
            onReopenUpdate={reopenUpdate}
            sourceChangeEvents={sourceChangeEvents}
            isSourceChangesLoading={isSourceChangesLoading}
            selectedSourceChangeEvent={selectedSourceChangeEvent}
            onSelectSourceChangeEvent={selectSourceChangeEvent}
            impactAssessments={impactAssessments}
            isImpactsLoading={isImpactsLoading}
            dependencyLineage={dependencyLineage}
            isLineageLoading={isLineageLoading}
            onInspectLineage={(type, id) => loadDependencyLineage(type, id)}
            onExecuteRevalidation={executeRevalidation}
          />
        )}

        {activeTab === "REVIEWS" && (
          <ResearchReviewsWorkspace
            reviews={reviews}
            selectedReviewId={selectedReviewId}
            currentReview={currentReview}
            isReviewsLoading={isReviewsLoading}
            reviewStatusFilter={reviewStatusFilter}
            setReviewStatusFilter={setReviewStatusFilter}
            availableReports={reports}
            qualityGateResult={qualityGateResult}
            isQualityGateRunning={isQualityGateRunning}
            participants={participants}
            isParticipantsLoading={isParticipantsLoading}
            comments={comments}
            isCommentsLoading={isCommentsLoading}
            circulations={circulations}
            isCirculationsLoading={isCirculationsLoading}
            onSelectReview={selectReview}
            onSubmitReview={submitReview}
            onDecideReview={decideReview}
            onCancelReview={cancelReview}
            onRunQualityGate={runQualityGate}
            onLoadParticipants={loadParticipants}
            onGrantParticipant={grantParticipant}
            onUpdateParticipant={updateParticipant}
            onRevokeParticipant={revokeParticipant}
            onLoadComments={loadComments}
            onAddCommentThread={createCommentThread}
            onAddCommentReply={addCommentReply}
            onResolveCommentThread={resolveCommentThread}
            onReopenCommentThread={reopenCommentThread}
            onLoadCirculations={loadCirculations}
            onCirculateReport={circulateReport}
            onRevokeCirculation={revokeCirculation}
          />
        )}

        {(activeTab === "REPORTS" || activeTab === "THESES") && (
          <ResearchReportsWorkspace
            reports={reports}
            reportsTotal={reportsTotal}
            isReportsLoading={isReportsLoading}
            selectedReportId={selectedReportId}
            currentReport={currentReport}
            reportSections={reportSections}
            selectedSectionId={selectedSectionId}
            reportTemplates={reportTemplates}
            reportRevisions={reportRevisions}
            verificationResult={verificationResult}
            isVerifying={isVerifying}
            reportExports={reportExports}
            reportStatusFilter={reportStatusFilter}
            onStatusFilterChange={setReportStatusFilter}
            reportTypeFilter={reportTypeFilter}
            onTypeFilterChange={setReportTypeFilter}
            reportSearchQuery={reportSearchQuery}
            onReportSearchChange={setReportSearchQuery}
            theses={theses}
            selectedThesisId={selectedThesisId}
            currentThesis={currentThesis}
            thesisArguments={thesisArguments}
            isThesesLoading={isThesesLoading}
            onSelectReport={selectReport}
            onCreateReport={createReport}
            onUpdateReport={updateReport}
            onFinalizeReport={finalizeReport}
            onDeleteReport={deleteReport}
            onSelectSection={setSelectedSectionId}
            onCreateSection={createReportSection}
            onUpdateSection={updateReportSection}
            onDeleteSection={deleteReportSection}
            onReorderSections={reorderReportSections}
            onVerifyReport={verifyReport}
            onCompareRevisions={compareReportRevisions}
            onCreateExport={createReportExport}
            onSelectThesis={selectThesis}
            onCreateThesis={createThesis}
            onUpdateThesis={updateThesis}
            onDeleteThesis={deleteThesis}
            onCreateThesisArgument={createThesisArgument}
            onDeleteThesisArgument={deleteThesisArgument}
            onOpenSource={(srcId) => openDocument(srcId)}
          />
        )}

        {activeTab === "ANALYSIS" && (
          <ResearchAnalysisWorkspace
            analyses={analyses}
            analysesTotal={analysesTotal}
            isAnalysesLoading={isAnalysesLoading}
            selectedAnalysisId={selectedAnalysisId}
            currentAnalysis={currentAnalysis}
            analysisRuns={analysisRuns}
            selectedRunId={selectedRunId}
            currentRunResult={currentRunResult}
            currentRunProvenance={currentRunProvenance}
            isRunExecuting={isRunExecuting}
            analysisFindings={analysisFindings}
            analysisAssumptions={analysisAssumptions}
            sensitivityResult={sensitivityResult}
            isSensitivityLoading={isSensitivityLoading}
            hypothesisEvaluations={hypothesisEvaluations}
            isHypothesisEvaluating={isHypothesisEvaluating}
            investigations={investigations}
            hypotheses={hypotheses}
            onSelectAnalysis={selectAnalysis}
            onCreateAnalysis={createAnalysis}
            onDuplicateAnalysis={duplicateAnalysis}
            onDeleteAnalysis={deleteAnalysis}
            onExecuteAnalysisRun={executeAnalysisRun}
            onSelectRun={selectRun}
            onCreateFinding={(data) => selectedAnalysisId ? createFinding(selectedAnalysisId, data) : Promise.reject("No analysis selected")}
            onUpdateFinding={updateFinding}
            onDeleteFinding={deleteFinding}
            onCreateAssumption={(data) => selectedAnalysisId ? createAssumption(selectedAnalysisId, data) : Promise.reject("No analysis selected")}
            onDeleteAssumption={deleteAssumption}
            onExecuteSensitivity={(data) => selectedAnalysisId ? executeSensitivity(selectedAnalysisId, data) : Promise.reject("No analysis selected")}
            onEvaluateHypothesis={evaluateHypothesis}
            onOpenSource={(srcId) => openDocument(srcId)}
          />
        )}

        {activeTab === "DISCOVERY" && (
          <ResearchSourceDiscovery
            query={discoveryQuery}
            results={discoveryResults}
            totalMatches={discoveryTotal}
            isLoading={isDiscoveryLoading}
            sourceTypes={sourceTypes}
            onSearch={(q) => searchDiscovery(q)}
            onOpenDocument={(docId) => openDocument(docId)}
            onCompareDocument={(docId) => openComparison(undefined, docId)}
          />
        )}

        {activeTab === "DOCUMENT_VIEWER" && (
          <ResearchDocumentViewer
            documentId={activeDocumentId}
            document={activeDocument}
            processingStatus={documentProcessingStatus}
            outline={documentOutline}
            activeSectionId={activeDocumentSectionId}
            activeSection={activeDocumentSection}
            tables={documentTables}
            searchQuery={documentSearchQuery}
            searchHits={documentSearchHits}
            isSearching={isDocSearchLoading}
            candidates={candidates}
            isLoading={isDocumentLoading}
            investigations={investigations}
            onSelectSection={selectDocumentSection}
            onSearchInDocument={searchInDocument}
            onConvertCandidate={convertCandidate}
            onCompareWithAnother={(docId) => openComparison(undefined, docId)}
          />
        )}

        {activeTab === "COMPARE" && (
          <ResearchDocumentComparison
            leftDocId={compareLeftDocId}
            rightDocId={compareRightDocId}
            comparisonMode={compareMode}
            comparisonResult={comparisonResult}
            isLoading={isComparing}
            onCompare={(l, r, m) => executeDocumentComparison(l, r, m)}
            onOpenDocument={(docId) => openDocument(docId)}
          />
        )}

        {activeTab === "INVESTIGATIONS" && (
          <ResearchInvestigationsTable
            investigations={investigations}
            isLoading={isInvestigationsLoading}
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            statusFilter={statusFilter}
            onStatusFilterChange={setStatusFilter}
            typeFilter={typeFilter}
            onTypeFilterChange={setTypeFilter}
            onSelectInvestigation={selectInvestigation}
            onArchiveInvestigation={archiveInvestigation}
            onNewInvestigation={() => setIsNewDialogOpen(true)}
          />
        )}

        {activeTab === "SOURCES" && <ResearchSourceLibrary />}

        {activeTab === "ACTIVITY" && (
          <ResearchActivityTimeline
            activities={overview?.recent_activities ?? []}
            isLoading={isOverviewLoading}
          />
        )}
      </div>

      {/* Modal Dialog for New Investigation */}
      <NewInvestigationDialog
        isOpen={isNewDialogOpen}
        onClose={() => setIsNewDialogOpen(false)}
        onSubmit={async (data) => {
          await createInvestigation(data);
        }}
      />
    </div>
  );
}

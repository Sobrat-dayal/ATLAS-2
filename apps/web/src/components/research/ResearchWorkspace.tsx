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
              isLoading={isOverviewLoading}
              onSelectInvestigation={selectInvestigation}
              onNewInvestigation={() => setIsNewDialogOpen(true)}
              onViewAllInvestigations={() => setActiveTab("INVESTIGATIONS")}
            />
          </div>
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

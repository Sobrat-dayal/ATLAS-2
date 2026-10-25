"use client";

import { useCallback, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  AtlasInspector,
  AtlasPanel,
  AtlasResizeHandle,
  AtlasSplit,
  Badge,
  Button,
  Input,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/design-system";
import { useCompanyOverview } from "@/hooks/companies/useCompanyOverview";
import { useCompanySearch } from "@/hooks/companies/useCompanySearch";
import { CompanyEmptyState } from "./CompanyEmptyState";
import { CompanyErrorState } from "./CompanyErrorState";
import { CompanyFinancialsTab } from "./CompanyFinancialsTab";
import { CompanyHeader } from "./CompanyHeader";
import { CompanyNewsDocsTab } from "./CompanyNewsDocsTab";
import { CompanyOverviewTab } from "./CompanyOverviewTab";
import { CompanySecuritiesTab } from "./CompanySecuritiesTab";
import {
  ArrowLeft,
  Building2,
  DollarSign,
  FileText,
  Layers,
  Loader2,
  Search,
} from "lucide-react";

export interface CompaniesWorkspaceProps {
  initialCompanyId?: string | null;
}

export function CompaniesWorkspace({ initialCompanyId }: CompaniesWorkspaceProps) {
  const router = useRouter();
  const searchParams = useSearchParams();

  // Selected company ID priority: initialCompanyId prop -> URL query param 'id'
  const paramId = searchParams?.get("id");
  const selectedCompanyId = initialCompanyId || paramId || null;

  const [activeTab, setActiveTab] = useState<string>("overview");

  // Company Overview Query
  const { data: overview, loading, error, refresh } = useCompanyOverview(selectedCompanyId);

  // Directory Search Query
  const searchHook = useCompanySearch();

  const handleSelectCompany = useCallback(
    (companyId: string) => {
      // Update browser URL to maintain deep-linkable canonical route
      router.push(`/companies?id=${encodeURIComponent(companyId)}`);
    },
    [router]
  );

  const handleBackToDirectory = useCallback(() => {
    router.push("/companies");
  }, [router]);

  return (
    <div className="flex h-full flex-col bg-atlas-bg-0 text-atlas-text-primary">
      {/* Top Module Subheader */}
      <div className="px-6 py-2.5 shrink-0 border-b border-atlas-border-default bg-atlas-surface-1 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          {selectedCompanyId && (
            <Button
              variant="secondary"
              size="sm"
              onClick={handleBackToDirectory}
              className="text-xs gap-1.5 h-8 px-2.5"
              title="Return to Company Directory"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Directory</span>
            </Button>
          )}

          <div className="flex items-center gap-2">
            <Building2 className="w-4 h-4 text-atlas-text-muted" aria-hidden="true" />
            <h1 className="text-sm font-bold uppercase tracking-wider text-atlas-text-primary">
              Companies V1
            </h1>
            <Badge variant="outline" className="font-mono text-[10px]">
              Stage 81
            </Badge>
          </div>
        </div>

        {/* Global Directory Search Bar */}
        <div className="relative w-full max-w-xs sm:max-w-md">
          <Search className="absolute left-2.5 top-2.5 w-3.5 h-3.5 text-atlas-text-muted" aria-hidden="true" />
          <Input
            value={searchHook.query}
            onChange={(e) => {
              searchHook.setQuery(e.target.value);
              if (selectedCompanyId && e.target.value.trim()) {
                // If user starts searching while on a company page, clear to show search results
                router.push("/companies");
              }
            }}
            placeholder="Search companies by name, ticker, LEI, or CIK..."
            className="pl-8 text-xs h-8"
          />
        </div>
      </div>

      {/* Main Workspace Area */}
      <div className="flex-1 overflow-hidden">
        {selectedCompanyId ? (
          // A Company is Selected
          loading ? (
            <div className="flex flex-col items-center justify-center h-full gap-3 text-atlas-text-muted text-xs">
              <Loader2 className="w-6 h-6 animate-spin text-atlas-accent" />
              <span>Loading canonical company intelligence profile...</span>
            </div>
          ) : error ? (
            <CompanyErrorState error={error} onRetry={refresh} />
          ) : overview ? (
            <AtlasSplit id="layout.companies.workspace" direction="horizontal" defaultLayout={[75, 25]}>
              {/* Left Main Panel: Company Profile & Tabs */}
              <AtlasPanel id="companies.main.panel" minSize={45} defaultSize={75} scrollable className="p-0">
                <div className="flex flex-col h-full">
                  {/* Verified Corporate Header */}
                  <CompanyHeader overview={overview} />

                  {/* Navigation Tabs */}
                  <div className="p-6">
                    <Tabs value={activeTab} onValueChange={setActiveTab}>
                      <TabsList className="bg-transparent border-b border-atlas-border-default h-9 mb-4">
                        <TabsTrigger value="overview" className="gap-1.5 text-xs">
                          <Building2 className="w-3.5 h-3.5" />
                          <span>Overview</span>
                        </TabsTrigger>

                        <TabsTrigger value="securities" className="gap-1.5 text-xs">
                          <Layers className="w-3.5 h-3.5" />
                          <span>Securities ({overview.related_securities.length})</span>
                        </TabsTrigger>

                        <TabsTrigger value="financials" className="gap-1.5 text-xs">
                          <DollarSign className="w-3.5 h-3.5" />
                          <span>Financial Statements</span>
                        </TabsTrigger>

                        <TabsTrigger value="news" className="gap-1.5 text-xs">
                          <FileText className="w-3.5 h-3.5" />
                          <span>News & Docs ({overview.recent_news.length + overview.documents.length})</span>
                        </TabsTrigger>
                      </TabsList>

                      <TabsContent value="overview">
                        <CompanyOverviewTab overview={overview} />
                      </TabsContent>

                      <TabsContent value="securities">
                        <CompanySecuritiesTab securities={overview.related_securities} />
                      </TabsContent>

                      <TabsContent value="financials">
                        <CompanyFinancialsTab
                          financialSummary={overview.financial_summary}
                          companyId={overview.company_entity_id}
                          companyName={overview.identity.display_name}
                        />
                      </TabsContent>

                      <TabsContent value="news">
                        <CompanyNewsDocsTab news={overview.recent_news} documents={overview.documents} />
                      </TabsContent>
                    </Tabs>
                  </div>
                </div>
              </AtlasPanel>

              <AtlasResizeHandle />

              {/* Right Inspector Panel */}
              <AtlasInspector
                id="companies.inspector.panel"
                title="Entity Metadata"
                minSize={20}
                maxSize={35}
                defaultSize={25}
              >
                <div className="p-4 space-y-4 text-xs">
                  <div>
                    <div className="text-atlas-text-muted">Entity UUID</div>
                    <div className="font-mono text-[11px] text-atlas-text-primary mt-0.5 break-all">
                      {overview.company_entity_id}
                    </div>
                  </div>

                  <div>
                    <div className="text-atlas-text-muted">Primary Country</div>
                    <div className="font-medium text-atlas-text-secondary mt-0.5">
                      {overview.geography.headquarters_country || "Unspecified"}
                    </div>
                  </div>

                  <div>
                    <div className="text-atlas-text-muted">Taxonomy Sector</div>
                    <div className="font-medium text-atlas-text-secondary mt-0.5">
                      {overview.classification.sector_name || "Unclassified"}
                    </div>
                  </div>

                  <div>
                    <div className="text-atlas-text-muted">Taxonomy Industry</div>
                    <div className="font-medium text-atlas-text-secondary mt-0.5">
                      {overview.classification.industry_name || "Unclassified"}
                    </div>
                  </div>

                  <div className="pt-3 border-t border-atlas-border-subtle">
                    <div className="text-atlas-text-muted mb-2 font-semibold">Section Data Availability</div>
                    <div className="space-y-1.5 text-[11px] font-mono">
                      <div className="flex justify-between">
                        <span>Identity:</span>
                        <span className="text-atlas-positive">{overview.section_availability.identity}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Classification:</span>
                        <span className={overview.section_availability.classification === "AVAILABLE" ? "text-atlas-positive" : "text-atlas-text-muted"}>
                          {overview.section_availability.classification}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Securities:</span>
                        <span className={overview.section_availability.securities === "AVAILABLE" ? "text-atlas-positive" : "text-atlas-text-muted"}>
                          {overview.section_availability.securities}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Fundamentals:</span>
                        <span className={overview.section_availability.financial_summary === "AVAILABLE" ? "text-atlas-positive" : "text-atlas-text-muted"}>
                          {overview.section_availability.financial_summary}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>News:</span>
                        <span className={overview.section_availability.news === "AVAILABLE" ? "text-atlas-positive" : "text-atlas-text-muted"}>
                          {overview.section_availability.news}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </AtlasInspector>
            </AtlasSplit>
          ) : null
        ) : (
          // No Company Selected: Render Directory / Discovery View
          <div className="h-full overflow-y-auto">
            <CompanyEmptyState
              query={searchHook.query}
              onQueryChange={searchHook.setQuery}
              results={searchHook.results}
              loading={searchHook.loading}
              total={searchHook.total}
              onSelectCompany={handleSelectCompany}
            />
          </div>
        )}
      </div>
    </div>
  );
}

import { Suspense } from "react";
import { CompaniesWorkspace } from "@/components/companies";
import { Loader2 } from "lucide-react";

export default async function CompanyDetailPage({
  params,
}: {
  params: Promise<{ companyId: string }>;
}) {
  const { companyId } = await params;

  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center h-full text-xs text-atlas-text-muted gap-2">
          <Loader2 className="w-5 h-5 animate-spin text-atlas-accent" />
          <span>Loading Company Overview...</span>
        </div>
      }
    >
      <CompaniesWorkspace initialCompanyId={companyId} />
    </Suspense>
  );
}

import { AtlasModuleDefinition } from "@/config/atlas-modules";

interface ModuleFoundationProps {
  module: AtlasModuleDefinition;
  plannedStage?: number;
}

export function ModuleFoundation({ module, plannedStage }: ModuleFoundationProps) {
  return (
    <div className="flex h-full flex-col p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-atlas-text-primary flex items-center">
          <module.icon className="mr-3 h-6 w-6 text-atlas-accent" />
          {module.label}
        </h1>
        <p className="mt-2 text-atlas-text-secondary max-w-2xl">{module.description}</p>
      </div>

      <div className="flex-1 flex items-center justify-center rounded-md border border-dashed border-atlas-border-default bg-atlas-surface-1 p-8 text-center">
        <div className="max-w-md">
          <module.icon className="mx-auto mb-4 h-12 w-12 text-atlas-border-default" />
          <h2 className="text-lg font-medium text-atlas-text-primary">Foundation Ready</h2>
          <p className="mt-2 text-sm text-atlas-text-muted">
            This module has been structurally registered in the ATLAS navigation registry. 
            Full functionality will be implemented in a subsequent development stage.
          </p>
          {plannedStage && (
            <div className="mt-6 inline-flex items-center rounded-full bg-atlas-surface-hover px-3 py-1 text-xs font-medium text-atlas-text-secondary">
              Planned for Stage {plannedStage}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

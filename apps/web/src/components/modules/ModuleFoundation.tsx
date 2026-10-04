import { AtlasModuleDefinition } from "@/config/atlas-modules";

interface ModuleFoundationProps {
  module: AtlasModuleDefinition;
  plannedStage?: number;
}

export function ModuleFoundation({ module, plannedStage }: ModuleFoundationProps) {
  return (
    <div className="flex h-full flex-col p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-white flex items-center">
          <module.icon className="mr-3 h-6 w-6 text-[#60A5FA]" />
          {module.label}
        </h1>
        <p className="mt-2 text-gray-400 max-w-2xl">{module.description}</p>
      </div>

      <div className="flex-1 flex items-center justify-center rounded-md border border-dashed border-[#1E2330] bg-[#0F131C] p-8 text-center">
        <div className="max-w-md">
          <module.icon className="mx-auto mb-4 h-12 w-12 text-[#1E2330]" />
          <h2 className="text-lg font-medium text-gray-300">Foundation Ready</h2>
          <p className="mt-2 text-sm text-gray-500">
            This module has been structurally registered in the ATLAS navigation registry. 
            Full functionality will be implemented in a subsequent development stage.
          </p>
          {plannedStage && (
            <div className="mt-6 inline-flex items-center rounded-full bg-[#1A202E] px-3 py-1 text-xs font-medium text-gray-400">
              Planned for Stage {plannedStage}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

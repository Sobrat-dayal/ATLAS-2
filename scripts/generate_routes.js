const fs = require('fs');
const path = require('path');

const modules = [
  'home', 'markets', 'charts', 'watchlists', 'screeners', 
  'companies', 'economics', 'news', 'research', 'maps', 
  'intelligence', 'options', 'trading', 'portfolios', 'risk', 
  'ai', 'data', 'saved', 'workspaces', 'agents'
];

const basePath = path.join(__dirname, 'apps', 'web', 'src', 'app', '(atlas)');

if (!fs.existsSync(basePath)) {
  fs.mkdirSync(basePath, { recursive: true });
}

modules.forEach(mod => {
  const modPath = path.join(basePath, mod);
  if (!fs.existsSync(modPath)) {
    fs.mkdirSync(modPath, { recursive: true });
  }
  
  const pageContent = `import { ATLAS_MODULES } from "@/config/atlas-modules";
import { ModuleFoundation } from "@/components/modules/ModuleFoundation";
import { Metadata } from "next";

export function generateMetadata(): Metadata {
  return {
    title: \`\${ATLAS_MODULES.${mod}.label} | ATLAS\`
  };
}

export default function ${mod.charAt(0).toUpperCase() + mod.slice(1)}Page() {
  return <ModuleFoundation module={ATLAS_MODULES.${mod}} />;
}
`;

  fs.writeFileSync(path.join(modPath, 'page.tsx'), pageContent);
});

// Overwrite home with the custom mock content from before
const homeContent = `import { ATLAS_MODULES } from "@/config/atlas-modules";
import { Metadata } from "next";

export function generateMetadata(): Metadata {
  return {
    title: \`\${ATLAS_MODULES.home.label} | ATLAS\`
  };
}

export default function HomePage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-4 text-white">ATLAS Command Center</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="rounded-md border border-[#1E2330] bg-[#0F131C] p-4">
          <h2 className="text-sm font-medium text-gray-400 mb-2">Market Overview</h2>
          <div className="h-32 flex items-center justify-center border border-dashed border-[#1E2330] rounded">
            <span className="text-xs text-gray-500">Market Data Placeholder</span>
          </div>
        </div>
        <div className="rounded-md border border-[#1E2330] bg-[#0F131C] p-4">
          <h2 className="text-sm font-medium text-gray-400 mb-2">Active Agents</h2>
          <div className="h-32 flex items-center justify-center border border-dashed border-[#1E2330] rounded">
            <span className="text-xs text-gray-500">No active agents</span>
          </div>
        </div>
        <div className="rounded-md border border-[#1E2330] bg-[#0F131C] p-4">
          <h2 className="text-sm font-medium text-gray-400 mb-2">Recent News</h2>
          <div className="h-32 flex items-center justify-center border border-dashed border-[#1E2330] rounded">
            <span className="text-xs text-gray-500">News Feed Placeholder</span>
          </div>
        </div>
      </div>
    </div>
  );
}
`;
fs.writeFileSync(path.join(basePath, 'home', 'page.tsx'), homeContent);

// Remove the default src/app/page.tsx that was created in stage 3
const defaultPagePath = path.join(__dirname, 'apps', 'web', 'src', 'app', 'page.tsx');
if (fs.existsSync(defaultPagePath)) {
  fs.unlinkSync(defaultPagePath);
}

console.log("Modules generated.");

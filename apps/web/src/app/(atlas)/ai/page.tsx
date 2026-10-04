"use client";

import { ATLAS_MODULES } from "@/config/atlas-modules";
import { 
  AtlasSplit, 
  AtlasPanel, 
  AtlasResizeHandle, 
  AtlasInspector,
  PageHeader
} from "@/design-system";
import { MessageSquare, Bot } from "lucide-react";

export default function AIPage() {
  return (
    <div className="flex h-full flex-col">
      <div className="px-4 py-3 shrink-0 border-b border-atlas-border-default bg-atlas-surface-1">
        <PageHeader 
          title={ATLAS_MODULES.ai.label} 
          description={ATLAS_MODULES.ai.description}
          className="mb-0 pb-0 border-b-0"
        />
      </div>

      <div className="flex-1 overflow-hidden">
        <AtlasSplit id="layout.ai" direction="horizontal" defaultLayout={[20, 55, 25]}>
          {/* Conversation History */}
          <AtlasPanel id="ai.history" minSize={15} defaultSize={20}>
            <div className="h-full bg-atlas-surface-1 border-r border-atlas-border-default flex flex-col">
              <div className="p-3 border-b border-atlas-border-default text-sm font-medium">
                Conversations
              </div>
              <div className="flex-1 overflow-auto p-2 space-y-1">
                <div className="px-3 py-2 text-sm text-atlas-text-primary bg-atlas-surface-selected rounded-sm cursor-pointer transition-colors flex items-center">
                  <MessageSquare className="w-4 h-4 mr-2" />
                  Market Analysis
                </div>
              </div>
            </div>
          </AtlasPanel>

          <AtlasResizeHandle />

          {/* AI Workspace */}
          <AtlasPanel id="ai.workspace" minSize={40} defaultSize={55} className="flex flex-col bg-atlas-bg-0">
            <div className="flex-1 p-6 flex flex-col items-center justify-center text-atlas-text-muted">
              <Bot className="w-12 h-12 mb-4 text-atlas-blue" />
              <p>How can I help you analyze the markets today?</p>
            </div>
            <div className="p-4 border-t border-atlas-border-default bg-atlas-surface-1">
              <div className="bg-atlas-surface-2 border border-atlas-border-strong rounded-md h-12 flex items-center px-4 text-sm text-atlas-text-muted">
                Ask ATLAS AI...
              </div>
            </div>
          </AtlasPanel>

          <AtlasResizeHandle />

          {/* AI Context Inspector */}
          <AtlasInspector 
            id="ai.context" 
            title="Context & Memory" 
            minSize={20} 
            maxSize={40}
            defaultSize={25}
          >
            <div className="p-4 text-sm text-atlas-text-muted space-y-4">
              <p>The AI is currently analyzing your active portfolio and recent news events.</p>
              <div className="p-3 bg-atlas-surface-2 border border-atlas-border-default rounded-sm">
                <strong>Active Context:</strong>
                <ul className="mt-2 list-disc list-inside space-y-1">
                  <li>Portfolio: Tech Heavy</li>
                  <li>Screener: High Yield</li>
                </ul>
              </div>
            </div>
          </AtlasInspector>
        </AtlasSplit>
      </div>
    </div>
  );
}

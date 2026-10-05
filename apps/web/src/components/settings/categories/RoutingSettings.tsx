import React from 'react';
import { SettingsSection, SettingsControlGroup, SettingsToggle, SettingsSelect } from '../SettingsControls';
import { Network, ServerOff, Server } from 'lucide-react';

export function RoutingSettings() {
  return (
    <div className="space-y-12">
      <SettingsSection
        title="Routing Policies"
        description="Configure provider priorities and routing strategies for different domains."
      >
        <SettingsControlGroup>
          <SettingsSelect
            label="Domain"
            description="Select a domain to configure routing policies."
            value="market_data"
            options={[
              { value: 'market_data', label: 'Market Data' },
              { value: 'news', label: 'News' },
              { value: 'fundamentals', label: 'Fundamentals' },
              { value: 'economics', label: 'Economics' }
            ]}
            onChange={() => {}}
          />
          <SettingsToggle
            label="Enable Routing Policy"
            description="Use explicit provider routing instead of default system resolution."
            checked={true}
            onChange={() => {}}
          />
          <SettingsToggle
            label="Enable Fallback"
            description="Automatically fallback to the next candidate on transient failures."
            checked={true}
            onChange={() => {}}
          />
        </SettingsControlGroup>
      </SettingsSection>

      <SettingsSection
        title="Provider Priority Configuration"
        description="Drag and drop providers to set their priority order for the selected domain."
      >
        <SettingsControlGroup>
          <div className="flex flex-col space-y-2 p-2">
            <div className="flex items-center space-x-4 p-3 bg-atlas-bg-2 border border-atlas-border rounded-md">
              <Network className="w-4 h-4 text-atlas-text-secondary" />
              <div className="flex-1">
                <span className="text-sm text-atlas-text-primary">yfinance</span>
              </div>
              <span className="text-xs text-atlas-text-secondary">Position 1</span>
            </div>
            <div className="flex items-center space-x-4 p-3 bg-atlas-bg-2 border border-atlas-border rounded-md">
              <Network className="w-4 h-4 text-atlas-text-secondary" />
              <div className="flex-1">
                <span className="text-sm text-atlas-text-primary">polygon</span>
              </div>
              <span className="text-xs text-atlas-text-secondary">Position 2</span>
            </div>
          </div>
        </SettingsControlGroup>
      </SettingsSection>
    </div>
  );
}

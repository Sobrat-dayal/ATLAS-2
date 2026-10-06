import React, { useState, useEffect } from 'react';
import { SettingsSection, SettingsControlGroup, SettingsToggle, SettingsSelect } from '../SettingsControls';
import { Network, ServerOff, Server, GripVertical } from 'lucide-react';
import { useRoutingSettings } from '../../../hooks/providers/useRoutingSettings';
import { useProviders } from '../../../hooks/providers/useProviders';

export function RoutingSettings() {
  const [domain, setDomain] = useState('market_data');
  const { policy, isLoading, updatePolicy } = useRoutingSettings(domain);
  const { providers } = useProviders(domain);

  const handleToggleRouting = async (checked: boolean) => {
    if (policy) {
      await updatePolicy(checked, policy.fallback_enabled, policy.candidates.map(c => c.provider_key));
    }
  };

  const handleToggleFallback = async (checked: boolean) => {
    if (policy) {
      await updatePolicy(policy.enabled, checked, policy.candidates.map(c => c.provider_key));
    }
  };

  const handleMoveUp = async (index: number) => {
    if (!policy) return;
    if (index === 0) return;
    const newKeys = [...policy.candidates.map(c => c.provider_key)];
    const temp = newKeys[index];
    newKeys[index] = newKeys[index - 1];
    newKeys[index - 1] = temp;
    await updatePolicy(policy.enabled, policy.fallback_enabled, newKeys);
  };

  const handleMoveDown = async (index: number) => {
    if (!policy) return;
    if (index === policy.candidates.length - 1) return;
    const newKeys = [...policy.candidates.map(c => c.provider_key)];
    const temp = newKeys[index];
    newKeys[index] = newKeys[index + 1];
    newKeys[index + 1] = temp;
    await updatePolicy(policy.enabled, policy.fallback_enabled, newKeys);
  };

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
            value={domain}
            options={[
              { value: 'market_data', label: 'Market Data' },
              { value: 'news', label: 'News' },
              { value: 'fundamentals', label: 'Fundamentals' },
              { value: 'economics', label: 'Economics' },
              { value: 'research', label: 'Research' }
            ]}
            onChange={(val) => setDomain(val)}
          />
          <SettingsToggle
            label="Enable Routing Policy"
            description="Use explicit provider routing instead of default system resolution."
            checked={policy?.enabled ?? false}
            onChange={handleToggleRouting}
          />
          <SettingsToggle
            label="Enable Fallback"
            description="Automatically fallback to the next candidate on transient failures."
            checked={policy?.fallback_enabled ?? false}
            onChange={handleToggleFallback}
          />
        </SettingsControlGroup>
      </SettingsSection>

      <SettingsSection
        title="Provider Priority Configuration"
        description="Set the priority order for the selected domain."
      >
        <SettingsControlGroup>
          <div className="flex flex-col space-y-2 p-2">
            {isLoading && <div className="text-sm text-atlas-text-secondary">Loading...</div>}
            {!isLoading && policy?.candidates?.length === 0 && (
              <div className="text-sm text-atlas-text-secondary">No providers configured for this domain.</div>
            )}
            {!isLoading && policy?.candidates?.map((candidate, idx) => (
              <div key={candidate.provider_key} className="flex items-center space-x-4 p-3 bg-atlas-bg-2 border border-atlas-border rounded-md">
                <Network className="w-4 h-4 text-atlas-text-secondary" />
                <div className="flex-1">
                  <span className="text-sm text-atlas-text-primary">{candidate.provider_key}</span>
                </div>
                <div className="flex space-x-2">
                  <button 
                    disabled={idx === 0} 
                    onClick={() => handleMoveUp(idx)}
                    className="text-xs text-atlas-text-secondary hover:text-atlas-text-primary disabled:opacity-50"
                  >
                    Up
                  </button>
                  <button 
                    disabled={idx === policy.candidates.length - 1} 
                    onClick={() => handleMoveDown(idx)}
                    className="text-xs text-atlas-text-secondary hover:text-atlas-text-primary disabled:opacity-50"
                  >
                    Down
                  </button>
                </div>
                <span className="text-xs text-atlas-text-secondary w-16 text-right">Pos {idx + 1}</span>
              </div>
            ))}
          </div>
        </SettingsControlGroup>
      </SettingsSection>
    </div>
  );
}

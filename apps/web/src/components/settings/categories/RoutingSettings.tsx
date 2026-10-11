"use client";

import React, { useState } from 'react';
import { SettingsGroup, SettingsRow } from '../SettingsControls';
import { Network } from 'lucide-react';
import { useRoutingSettings } from '../../../hooks/providers/useRoutingSettings';
import { useProviders } from '../../../hooks/providers/useProviders';

export function RoutingSettings() {
  const [domain, setDomain] = useState('market_data');
  const { policy, isLoading, updatePolicy } = useRoutingSettings(domain);
  const { providers: _providers } = useProviders(domain);

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
    <div className="space-y-8">
      <SettingsGroup
        title="Routing Policies"
        description="Configure provider priorities and routing strategies for different domains."
      >
        <SettingsRow
          label="Domain"
          description="Select a domain to configure routing policies."
        >
          <select
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            className="rounded bg-atlas-surface-2 border border-atlas-border-default px-2 py-1 text-xs text-atlas-text-primary focus:outline-none"
          >
            <option value="market_data">Market Data</option>
            <option value="news">News</option>
            <option value="fundamentals">Fundamentals</option>
            <option value="economics">Economics</option>
            <option value="research">Research</option>
          </select>
        </SettingsRow>
        <SettingsRow
          label="Enable Routing Policy"
          description="Use explicit provider routing instead of default system resolution."
        >
          <input
            type="checkbox"
            checked={policy?.enabled ?? false}
            onChange={(e) => handleToggleRouting(e.target.checked)}
            className="rounded border-atlas-border-default bg-atlas-surface-2 text-atlas-accent"
          />
        </SettingsRow>
        <SettingsRow
          label="Enable Fallback"
          description="Automatically fallback to the next candidate on transient failures."
        >
          <input
            type="checkbox"
            checked={policy?.fallback_enabled ?? false}
            onChange={(e) => handleToggleFallback(e.target.checked)}
            className="rounded border-atlas-border-default bg-atlas-surface-2 text-atlas-accent"
          />
        </SettingsRow>
      </SettingsGroup>

      <SettingsGroup
        title="Provider Priority Configuration"
        description="Set the priority order for the selected domain."
      >
        <div className="flex flex-col space-y-2 p-2">
          {isLoading && <div className="text-sm text-atlas-text-muted">Loading...</div>}
          {!isLoading && policy?.candidates?.length === 0 && (
            <div className="text-sm text-atlas-text-muted">No providers configured for this domain.</div>
          )}
          {!isLoading && policy?.candidates?.map((candidate, idx) => (
            <div key={candidate.provider_key} className="flex items-center space-x-4 p-3 bg-atlas-surface-2 border border-atlas-border-default rounded-md">
              <Network className="w-4 h-4 text-atlas-text-muted" />
              <div className="flex-1">
                <span className="text-sm text-atlas-text-primary">{candidate.provider_key}</span>
              </div>
              <div className="flex space-x-2">
                <button 
                  disabled={idx === 0} 
                  onClick={() => handleMoveUp(idx)}
                  className="text-xs text-atlas-text-muted hover:text-atlas-text-primary disabled:opacity-50"
                >
                  Up
                </button>
                <button 
                  disabled={idx === policy.candidates.length - 1} 
                  onClick={() => handleMoveDown(idx)}
                  className="text-xs text-atlas-text-muted hover:text-atlas-text-primary disabled:opacity-50"
                >
                  Down
                </button>
              </div>
              <span className="text-xs text-atlas-text-muted w-16 text-right">Pos {idx + 1}</span>
            </div>
          ))}
        </div>
      </SettingsGroup>
    </div>
  );
}

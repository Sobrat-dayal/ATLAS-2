"use client";

import React, { useState } from "react";
import type { PluginInstallation, PluginManifest } from "@/lib/ecosystem/types";
import { ecosystemApi } from "@/lib/ecosystem/api";

interface PluginRegistryProps {
  initialPlugins?: PluginManifest[];
  initialInstallations?: PluginInstallation[];
}

export const PluginRegistry: React.FC<PluginRegistryProps> = ({
  initialPlugins = [],
  initialInstallations = [],
}) => {
  const [plugins] = useState<PluginManifest[]>(initialPlugins);
  const [installations, setInstallations] = useState<PluginInstallation[]>(initialInstallations);
  const [selectedManifest, setSelectedManifest] = useState<PluginManifest | null>(null);
  const [installingPlugin, setInstallingPlugin] = useState<PluginManifest | null>(null);
  const [grantedScopes, setGrantedScopes] = useState<string[]>([]);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleOpenInstall = (p: PluginManifest) => {
    setInstallingPlugin(p);
    setGrantedScopes([...p.permissions]); // pre-select required permissions
    setErrorMsg(null);
  };

  const handleConfirmInstall = async () => {
    if (!installingPlugin) return;
    setErrorMsg(null);
    try {
      const res = await ecosystemApi.installPlugin(installingPlugin.plugin_id, grantedScopes);
      setInstallations((prev) => [
        ...prev,
        {
          installation_id: res.installation_id,
          plugin_id: installingPlugin.plugin_id,
          version: installingPlugin.version,
          status: "ENABLED",
          granted_permissions: grantedScopes,
          installed_at: new Date().toISOString(),
        },
      ]);
      setInstallingPlugin(null);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to install plugin.");
    }
  };

  const handleDisable = async (instId: string) => {
    try {
      await ecosystemApi.disablePlugin(instId);
      setInstallations((prev) =>
        prev.map((i) => (i.installation_id === instId ? { ...i, status: "DISABLED" } : i))
      );
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to disable plugin.");
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-zinc-800 pb-3">
        <h2 className="text-sm font-bold uppercase tracking-wider text-zinc-100">
          Plugin Architecture &amp; Extensions Platform
        </h2>
        <p className="text-xs text-zinc-400 mt-0.5">
          Tenant-governed plugin installation, explicit permission grants, lifecycle management, and revocation firewalls.
        </p>
      </div>

      {errorMsg && (
        <div className="rounded border border-rose-900 bg-rose-950/60 p-2.5 text-xs text-rose-300">
          {errorMsg}
        </div>
      )}

      {/* Installed Plugins Section */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400">
          Installed Tenant Plugins ({installations.length})
        </h3>
        {installations.length === 0 ? (
          <div className="rounded border border-zinc-800/60 bg-[#0d0d0d] p-4 text-center text-xs text-zinc-500">
            No plugins installed in this tenant workspace. Browse available plugins below.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {installations.map((inst) => (
              <div
                key={inst.installation_id}
                className="rounded border border-zinc-800 bg-[#0d0d0d] p-3 space-y-2 text-xs"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-zinc-200">{inst.plugin_id}</span>
                  <span
                    className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${
                      inst.status === "ENABLED"
                        ? "bg-emerald-950 border border-emerald-800 text-emerald-400"
                        : inst.status === "DISABLED"
                        ? "bg-amber-950 border border-amber-800 text-amber-400"
                        : "bg-rose-950 border border-rose-800 text-rose-400"
                    }`}
                  >
                    {inst.status}
                  </span>
                </div>
                <div className="text-[11px] text-zinc-400">Version: v{inst.version}</div>
                <div className="text-[10px] text-zinc-500 font-mono">
                  Permissions: {inst.granted_permissions.join(", ") || "None"}
                </div>
                <div className="flex items-center space-x-2 pt-1 border-t border-zinc-800/60">
                  {inst.status === "ENABLED" && (
                    <button
                      onClick={() => handleDisable(inst.installation_id)}
                      className="rounded border border-amber-900/60 bg-amber-950/40 px-2 py-0.5 text-[11px] text-amber-300 hover:bg-amber-900/60"
                    >
                      Disable
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Available Plugin Catalog */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400">
          Institutional Plugin Catalog
        </h3>
        <div className="rounded border border-zinc-800 bg-[#0a0a0a] overflow-hidden">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-zinc-800 bg-zinc-900/50 text-zinc-400">
              <tr>
                <th className="p-2.5 font-medium">Plugin</th>
                <th className="p-2.5 font-medium">Publisher</th>
                <th className="p-2.5 font-medium">Capabilities</th>
                <th className="p-2.5 font-medium">License</th>
                <th className="p-2.5 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/60">
              {plugins.map((p) => {
                const isInstalled = installations.some((i) => i.plugin_id === p.plugin_id);
                return (
                  <tr key={p.plugin_id} className="hover:bg-zinc-900/30">
                    <td className="p-2.5">
                      <div className="font-semibold text-zinc-200">{p.name}</div>
                      <div className="text-[11px] text-zinc-400 line-clamp-1">{p.description}</div>
                      <div className="text-[10px] text-zinc-500 font-mono mt-0.5">v{p.version}</div>
                    </td>
                    <td className="p-2.5 text-zinc-400">{p.publisher}</td>
                    <td className="p-2.5 text-zinc-400 text-[11px]">
                      {p.capabilities.join(", ")}
                    </td>
                    <td className="p-2.5 font-mono text-[11px] text-zinc-500">{p.license}</td>
                    <td className="p-2.5 text-right space-x-2">
                      <button
                        onClick={() => setSelectedManifest(p)}
                        className="rounded border border-zinc-700 bg-zinc-800 px-2 py-0.5 text-[11px] text-zinc-300 hover:bg-zinc-700"
                      >
                        Manifest
                      </button>
                      <button
                        onClick={() => handleOpenInstall(p)}
                        disabled={isInstalled}
                        className={`rounded px-2.5 py-0.5 text-[11px] font-semibold ${
                          isInstalled
                            ? "bg-zinc-800 text-zinc-500 cursor-not-allowed"
                            : "bg-emerald-950 border border-emerald-800 text-emerald-400 hover:bg-emerald-900"
                        }`}
                      >
                        {isInstalled ? "Installed" : "Install"}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Permission Grant / Install Modal */}
      {installingPlugin && (
        <div className="rounded border border-zinc-700 bg-[#0d0d0d] p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
            <h3 className="text-xs font-bold text-zinc-200">
              Authorize Plugin Installation: {installingPlugin.name}
            </h3>
            <button
              onClick={() => setInstallingPlugin(null)}
              className="text-xs text-zinc-400 hover:text-zinc-200"
            >
              Cancel
            </button>
          </div>
          <div className="space-y-2 text-xs">
            <p className="text-zinc-400">
              Review and affirmative grant the required permission scopes. Unchecked scopes will reject the installation.
            </p>
            <div className="rounded bg-black p-3 space-y-2 border border-zinc-800">
              {installingPlugin.permissions.map((perm) => (
                <label key={perm} className="flex items-center space-x-2 font-mono text-[11px] text-zinc-300">
                  <input
                    type="checkbox"
                    checked={grantedScopes.includes(perm)}
                    onChange={(e) => {
                      if (e.target.checked) setGrantedScopes((prev) => [...prev, perm]);
                      else setGrantedScopes((prev) => prev.filter((s) => s !== perm));
                    }}
                    className="rounded border-zinc-700 bg-zinc-900 text-emerald-500"
                  />
                  <span>{perm}</span>
                </label>
              ))}
            </div>
            <div className="flex justify-end pt-2">
              <button
                onClick={handleConfirmInstall}
                className="rounded bg-emerald-900 border border-emerald-700 px-4 py-1.5 text-xs font-semibold text-emerald-200 hover:bg-emerald-800 transition"
              >
                Confirm &amp; Install Plugin
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Manifest Viewer Modal */}
      {selectedManifest && (
        <div className="rounded border border-zinc-700 bg-[#0d0d0d] p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
            <h3 className="text-xs font-bold text-zinc-200">
              Plugin Manifest: {selectedManifest.name} (v{selectedManifest.version})
            </h3>
            <button
              onClick={() => setSelectedManifest(null)}
              className="text-xs text-zinc-400 hover:text-zinc-200"
            >
              Close
            </button>
          </div>
          <pre className="rounded bg-black p-3 font-mono text-[11px] text-emerald-400 overflow-x-auto border border-zinc-800">
            {JSON.stringify(selectedManifest, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};


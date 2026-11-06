"use client";

import React, { useState } from "react";
import type { PackageInstallation, PackageValidationResult } from "@/lib/ecosystem/types";
import { ecosystemApi } from "@/lib/ecosystem/api";

interface PackageRegistryProps {
  initialInstallations?: PackageInstallation[];
}

export const PackageRegistry: React.FC<PackageRegistryProps> = ({
  initialInstallations = [],
}) => {
  const [installations, setInstallations] = useState<PackageInstallation[]>(initialInstallations);
  const [base64Input, setBase64Input] = useState("");
  const [validationResult, setValidationResult] = useState<PackageValidationResult | null>(null);
  const [isImporting, setIsImporting] = useState(false);
  const [exportAgentId, setExportAgentId] = useState("");
  const [exportPackageId, setExportPackageId] = useState("");
  const [isExporting, setIsExporting] = useState(false);
  const [exportedResult, setExportedResult] = useState<{ filename: string; base64: string } | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      const b64 = result.split(",")[1] || result;
      setBase64Input(b64);
      setValidationResult(null);
    };
    reader.readAsDataURL(file);
  };

  const handleValidate = async () => {
    if (!base64Input) return;
    setErrorMsg(null);
    try {
      const res = await ecosystemApi.validatePackage(base64Input);
      setValidationResult(res);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Validation error.");
    }
  };

  const handleImport = async () => {
    if (!base64Input) return;
    setIsImporting(true);
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      const res = await ecosystemApi.importPackage({
        archive_base64: base64Input,
        granted_permissions: ["READ_RESEARCH", "EXECUTE_APPROVED_TOOLS"],
      });
      setSuccessMsg(`Package '${res.package_id}' installed successfully as DRAFT Agent (ID: ${res.agent_id}).`);
      setInstallations((prev) => [
        ...prev,
        {
          installation_id: `pkg-inst-${Date.now()}`,
          package_id: res.package_id,
          package_version: "1.0.0",
          status: "DRAFT",
          agent_reference_id: res.agent_id,
          installed_at: new Date().toISOString(),
        },
      ]);
      setBase64Input("");
      setValidationResult(null);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Import failed.");
    } finally {
      setIsImporting(false);
    }
  };

  const handleExport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!exportAgentId) return;
    setIsExporting(true);
    setErrorMsg(null);
    try {
      const res = await ecosystemApi.exportPackage(exportAgentId, exportPackageId || undefined);
      setExportedResult({ filename: res.filename, base64: res.archive_base64 });
      setSuccessMsg(`Agent exported successfully to '${res.filename}'.`);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Export failed.");
    } finally {
      setIsExporting(false);
    }
  };

  const downloadFile = (filename: string, b64: string) => {
    const link = document.createElement("a");
    link.href = `data:application/zip;base64,${b64}`;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-zinc-800 pb-3">
        <h2 className="text-sm font-bold uppercase tracking-wider text-zinc-100">
          .atlas-agent Package Platform
        </h2>
        <p className="text-xs text-zinc-400 mt-0.5">
          Standardized portable agent packaging, checksum verification, secret redaction, and safe draft installation.
        </p>
      </div>

      {errorMsg && (
        <div className="rounded border border-rose-900 bg-rose-950/60 p-2.5 text-xs text-rose-300">
          {errorMsg}
        </div>
      )}

      {successMsg && (
        <div className="rounded border border-emerald-800 bg-emerald-950/60 p-2.5 text-xs text-emerald-300">
          {successMsg}
        </div>
      )}

      {/* Grid: Import & Export */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Import Box */}
        <div className="rounded border border-zinc-800 bg-[#0d0d0d] p-4 space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-300">
            Import .atlas-agent Package
          </h3>
          <p className="text-[11px] text-zinc-400">
            Upload an existing package archive or paste base64. The package is verified against Zip-Slip, secret leaks, and checksum integrity before installing into a non-executing DRAFT state.
          </p>

          <input
            type="file"
            accept=".atlas-agent,.zip"
            onChange={handleFileUpload}
            className="w-full text-xs text-zinc-400 file:mr-2 file:py-1 file:px-2.5 file:rounded file:border file:border-zinc-700 file:bg-zinc-800 file:text-zinc-200 file:text-xs"
          />

          <div className="flex space-x-2">
            <button
              onClick={handleValidate}
              disabled={!base64Input}
              className="rounded border border-zinc-700 bg-zinc-800 px-3 py-1 text-xs font-semibold text-zinc-200 hover:bg-zinc-700 disabled:opacity-50"
            >
              Validate Package
            </button>
            <button
              onClick={handleImport}
              disabled={!base64Input || isImporting}
              className="rounded bg-emerald-900 border border-emerald-700 px-3 py-1 text-xs font-semibold text-emerald-200 hover:bg-emerald-800 disabled:opacity-50"
            >
              {isImporting ? "Importing..." : "Install to Draft Agent"}
            </button>
          </div>

          {validationResult && (
            <div
              className={`rounded border p-2.5 text-xs space-y-1 ${
                validationResult.is_valid
                  ? "border-emerald-800 bg-emerald-950/40 text-emerald-300"
                  : "border-rose-900 bg-rose-950/40 text-rose-300"
              }`}
            >
              <div className="font-bold">
                Validation Status: {validationResult.is_valid ? "VALID" : "INVALID"}
              </div>
              <div className="text-[11px]">
                Package ID: {validationResult.package_id || "N/A"} | Files: {validationResult.file_count} | Size: {validationResult.total_bytes} bytes
              </div>
              <div className="text-[11px]">
                Checksum Integrity: {validationResult.checksum_verified ? "VERIFIED" : "UNVERIFIED"} | Secret Leaks: {validationResult.secrets_detected ? "DETECTED" : "CLEAN"}
              </div>
              {validationResult.errors.length > 0 && (
                <ul className="list-disc pl-4 text-[10px] space-y-0.5 mt-1 text-rose-300">
                  {validationResult.errors.map((e, idx) => (
                    <li key={idx}>{e}</li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>

        {/* Export Box */}
        <div className="rounded border border-zinc-800 bg-[#0d0d0d] p-4 space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-300">
            Export Agent to .atlas-agent
          </h3>
          <p className="text-[11px] text-zinc-400">
            Bundle an existing registered Agent definition into an immutable, portable .atlas-agent archive with secret redaction and checksum verification.
          </p>

          <form onSubmit={handleExport} className="space-y-3 text-xs">
            <div>
              <label className="text-zinc-400">Agent ID to Export</label>
              <input
                type="text"
                required
                value={exportAgentId}
                onChange={(e) => setExportAgentId(e.target.value)}
                placeholder="Enter agent UUID..."
                className="w-full mt-1 rounded border border-zinc-800 bg-black px-2.5 py-1 text-zinc-200 font-mono"
              />
            </div>
            <div>
              <label className="text-zinc-400">Target Package ID (Optional)</label>
              <input
                type="text"
                value={exportPackageId}
                onChange={(e) => setExportPackageId(e.target.value)}
                placeholder="pkg.custom-analyst"
                className="w-full mt-1 rounded border border-zinc-800 bg-black px-2.5 py-1 text-zinc-200 font-mono"
              />
            </div>
            <button
              type="submit"
              disabled={isExporting}
              className="rounded border border-blue-800 bg-blue-950 px-3 py-1 text-xs font-semibold text-blue-200 hover:bg-blue-900 disabled:opacity-50"
            >
              {isExporting ? "Generating..." : "Generate .atlas-agent Archive"}
            </button>
          </form>

          {exportedResult && (
            <div className="rounded border border-zinc-700 bg-black p-2.5 text-xs flex items-center justify-between">
              <span className="font-mono text-zinc-300 truncate max-w-[200px]">
                {exportedResult.filename}
              </span>
              <button
                onClick={() => downloadFile(exportedResult.filename, exportedResult.base64)}
                className="rounded bg-emerald-950 border border-emerald-800 px-2 py-0.5 text-[11px] text-emerald-300 font-semibold"
              >
                Download .atlas-agent
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Installed Packages Table */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400">
          Installed Packages ({installations.length})
        </h3>
        {installations.length === 0 ? (
          <div className="rounded border border-zinc-800/60 bg-[#0d0d0d] p-4 text-center text-xs text-zinc-500">
            No agent packages installed in this tenant environment.
          </div>
        ) : (
          <div className="rounded border border-zinc-800 bg-[#0a0a0a] overflow-hidden">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-zinc-800 bg-zinc-900/50 text-zinc-400">
                <tr>
                  <th className="p-2.5 font-medium">Package ID</th>
                  <th className="p-2.5 font-medium">Version</th>
                  <th className="p-2.5 font-medium">Status</th>
                  <th className="p-2.5 font-medium">Agent Ref</th>
                  <th className="p-2.5 font-medium text-right">Installed At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60">
                {installations.map((inst) => (
                  <tr key={inst.installation_id} className="hover:bg-zinc-900/30">
                    <td className="p-2.5 font-semibold text-zinc-200">{inst.package_id}</td>
                    <td className="p-2.5 font-mono text-zinc-400">v{inst.package_version}</td>
                    <td className="p-2.5">
                      <span className="rounded bg-amber-950 border border-amber-800 px-1.5 py-0.5 text-[10px] text-amber-300 font-semibold">
                        {inst.status}
                      </span>
                    </td>
                    <td className="p-2.5 font-mono text-[11px] text-zinc-400">
                      {inst.agent_reference_id || "None"}
                    </td>
                    <td className="p-2.5 text-right text-[11px] text-zinc-500">
                      {new Date(inst.installed_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

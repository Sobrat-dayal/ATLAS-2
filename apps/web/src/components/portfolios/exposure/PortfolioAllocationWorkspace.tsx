/**
 * Master Portfolio Allocation, Exposure Intelligence & Concentration Workspace (Stage 112).
 * Professional Bloomberg-style layout for `/portfolios` ("allocation" tab).
 */

'use client';

import React, { useState } from 'react';
import { usePortfolioExposures } from '@/hooks/portfolios/usePortfolioExposures';
import { ExposureBasis } from '@/lib/portfolios/exposure/types';
import { AllocationSummaryCards } from './AllocationSummaryCards';
import { AssetClassAllocationPanel } from './AssetClassAllocationPanel';
import { CurrencyExposurePanel } from './CurrencyExposurePanel';
import { ExposureDataQualityPanel } from './ExposureDataQualityPanel';
import { FundLookThroughPanel } from './FundLookThroughPanel';
import { GeographicExposurePanel } from './GeographicExposurePanel';
import { HistoricalAllocationPanel } from './HistoricalAllocationPanel';
import { PortfolioConcentrationPanel } from './PortfolioConcentrationPanel';
import { SectorExposurePanel } from './SectorExposurePanel';

interface PortfolioAllocationWorkspaceProps {
  portfolioId: string;
}

type AllocationTab =
  | 'sectors'
  | 'asset_classes'
  | 'geography'
  | 'currency'
  | 'concentration'
  | 'look_through'
  | 'historical'
  | 'data_quality';

export const PortfolioAllocationWorkspace: React.FC<PortfolioAllocationWorkspaceProps> = ({
  portfolioId,
}) => {
  const [activeTab, setActiveTab] = useState<AllocationTab>('sectors');

  const {
    run,
    loading,
    error,
    exposureBasis,
    setExposureBasis,
    geographyPolicy,
    setGeographyPolicy,
    enableLookThrough,
    setEnableLookThrough,
    historicalChanges,
    historicalLoading,
    fetchHistoricalChanges,
    refetch,
    recalculate,
  } = usePortfolioExposures(portfolioId);

  return (
    <div className="space-y-6">
      {/* Top Controls Bar */}
      <div className="bg-[#0f1523] border border-slate-800 rounded-lg p-3 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-1.5">
            <span className="text-xs text-slate-400 font-medium">Basis:</span>
            <select
              value={exposureBasis}
              onChange={(e) => setExposureBasis(e.target.value as ExposureBasis)}
              className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded px-2.5 py-1 focus:outline-none"
            >
              <option value="NET_ASSET_VALUE">Net Asset Value (NAV)</option>
              <option value="DIRECT">Direct Holdings Only</option>
              <option value="LOOK_THROUGH">Full Look-Through</option>
              <option value="GROSS">Gross Market Value</option>
            </select>
          </div>

          <label className="flex items-center space-x-1.5 cursor-pointer text-xs text-slate-300">
            <input
              type="checkbox"
              checked={enableLookThrough}
              onChange={(e) => setEnableLookThrough(e.target.checked)}
              className="rounded bg-slate-900 border-slate-700 text-blue-600 focus:ring-0"
            />
            <span>Decompose Funds & ETFs</span>
          </label>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => recalculate()}
            disabled={loading}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded transition-colors flex items-center space-x-1.5"
          >
            {loading ? (
              <span>Calculating...</span>
            ) : (
              <>
                <span>⚡</span>
                <span>Recalculate Exposures</span>
              </>
            )}
          </button>
          <button
            onClick={() => refetch()}
            disabled={loading}
            className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs rounded transition-colors"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-rose-950/40 border border-rose-800 text-rose-300 p-3 rounded-lg text-xs">
          <strong>Exposure Error:</strong> {error}
        </div>
      )}

      {/* Summary KPI Cards */}
      <AllocationSummaryCards run={run} loading={loading} />

      {/* Sub-tab Navigation */}
      <div className="border-b border-slate-800 flex items-center space-x-1 overflow-x-auto pb-px">
        <button
          onClick={() => setActiveTab('sectors')}
          className={`px-3 py-2 text-xs font-medium border-b-2 transition-colors whitespace-nowrap ${
            activeTab === 'sectors'
              ? 'border-blue-500 text-blue-400 font-semibold'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Sectors & Industries
        </button>
        <button
          onClick={() => setActiveTab('asset_classes')}
          className={`px-3 py-2 text-xs font-medium border-b-2 transition-colors whitespace-nowrap ${
            activeTab === 'asset_classes'
              ? 'border-blue-500 text-blue-400 font-semibold'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Asset Classes
        </button>
        <button
          onClick={() => setActiveTab('geography')}
          className={`px-3 py-2 text-xs font-medium border-b-2 transition-colors whitespace-nowrap ${
            activeTab === 'geography'
              ? 'border-blue-500 text-blue-400 font-semibold'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Geographic Exposure
        </button>
        <button
          onClick={() => setActiveTab('currency')}
          className={`px-3 py-2 text-xs font-medium border-b-2 transition-colors whitespace-nowrap ${
            activeTab === 'currency'
              ? 'border-blue-500 text-blue-400 font-semibold'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Currencies
        </button>
        <button
          onClick={() => setActiveTab('concentration')}
          className={`px-3 py-2 text-xs font-medium border-b-2 transition-colors whitespace-nowrap ${
            activeTab === 'concentration'
              ? 'border-blue-500 text-blue-400 font-semibold'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Concentration & Weights
        </button>
        <button
          onClick={() => setActiveTab('look_through')}
          className={`px-3 py-2 text-xs font-medium border-b-2 transition-colors whitespace-nowrap ${
            activeTab === 'look_through'
              ? 'border-blue-500 text-blue-400 font-semibold'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Fund Look-Through & Overlap
        </button>
        <button
          onClick={() => setActiveTab('historical')}
          className={`px-3 py-2 text-xs font-medium border-b-2 transition-colors whitespace-nowrap ${
            activeTab === 'historical'
              ? 'border-blue-500 text-blue-400 font-semibold'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Historical Drift
        </button>
        <button
          onClick={() => setActiveTab('data_quality')}
          className={`px-3 py-2 text-xs font-medium border-b-2 transition-colors whitespace-nowrap ${
            activeTab === 'data_quality'
              ? 'border-blue-500 text-blue-400 font-semibold'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Data Quality & Audit
        </button>
      </div>

      {/* Tab Panels */}
      <div>
        {activeTab === 'sectors' && (
          <SectorExposurePanel
            sectorData={run ? run.sectors : null}
            industryData={run ? run.industries : null}
            baseCurrency={run?.base_currency}
            loading={loading}
          />
        )}

        {activeTab === 'asset_classes' && (
          <AssetClassAllocationPanel
            data={run ? run.asset_classes : null}
            baseCurrency={run?.base_currency}
            loading={loading}
          />
        )}

        {activeTab === 'geography' && (
          <GeographicExposurePanel
            data={run ? run.countries : null}
            geographyPolicy={geographyPolicy}
            onPolicyChange={setGeographyPolicy}
            baseCurrency={run?.base_currency}
            loading={loading}
          />
        )}

        {activeTab === 'currency' && (
          <CurrencyExposurePanel
            data={run ? run.currencies : null}
            baseCurrency={run?.base_currency}
            loading={loading}
          />
        )}

        {activeTab === 'concentration' && (
          <PortfolioConcentrationPanel
            concentration={run ? run.concentration : null}
            securities={run ? run.security_weights : []}
            issuers={run ? run.issuer_weights : []}
            baseCurrency={run?.base_currency}
            loading={loading}
          />
        )}

        {activeTab === 'look_through' && (
          <FundLookThroughPanel
            funds={run ? run.funds : []}
            overlaps={run ? run.cross_fund_overlap : []}
            baseCurrency={run?.base_currency}
            loading={loading}
          />
        )}

        {activeTab === 'historical' && (
          <HistoricalAllocationPanel
            changes={historicalChanges}
            loading={historicalLoading}
            onFetchChanges={fetchHistoricalChanges}
            baseCurrency={run?.base_currency}
          />
        )}

        {activeTab === 'data_quality' && (
          <ExposureDataQualityPanel
            dataQuality={run ? run.data_quality : null}
            inputHash={run?.input_hash}
            calculationVersion={run?.calculation_version}
            loading={loading}
          />
        )}
      </div>
    </div>
  );
};

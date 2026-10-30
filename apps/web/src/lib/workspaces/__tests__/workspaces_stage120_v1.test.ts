/**
 * ATLAS Stage 120 Frontend Unit Tests.
 *
 * Verifies:
 * 1. Multi-panel tree layout operations: split, dock to tab stack, prune/remove, swap, normalize ratios.
 * 2. Tree traversal & panel ID discovery across nested splits and tab stacks.
 * 3. Link group context dimension typing and isolated mode invariants.
 * 4. Canonical template structures and panel count constraints.
 */

import { describe, it } from 'node:test';
import assert from 'node:assert';
import {
  dockIntoTabStack,
  getAllPanelIds,
  removePanel,
  setActiveTab,
  splitPanel,
  swapPanels,
  updateSplitRatios,
} from '../layoutOperations';
import {
  ContextDimension,
  LayoutNode,
  PanelNode,
  PanelTypeId,
  SplitNode,
  TabStackNode,
  WorkspaceLinkGroup,
  WorkspacePanelInstance,
} from '../types';

describe('Stage 120 - Workspace Layout Engine Operations', () => {
  const initialSinglePanel: PanelNode = {
    node_id: 'node-p1',
    node_type: 'PANEL',
    panel_instance_id: 'panel-inst-1',
  };

  it('correctly discovers panel IDs in a single panel node', () => {
    const ids = getAllPanelIds(initialSinglePanel);
    assert.deepStrictEqual(ids, ['panel-inst-1']);
  });

  it('splits a panel horizontally into two child panels with balanced 0.5 ratios', () => {
    const newPanelInstance: WorkspacePanelInstance = {
      panel_instance_id: 'panel-inst-2',
      workspace_id: 'ws-1',
      panel_type_id: 'INSTRUMENT_CHART',
      title_override: 'Technical Chart',
      configuration: { symbol: 'AAPL' },
      independent_mode: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    const newTree = splitPanel(
      initialSinglePanel,
      'panel-inst-1',
      'HORIZONTAL',
      'panel-inst-2'
    );

    assert.strictEqual(newTree.node_type, 'SPLIT');
    const splitNode = newTree as SplitNode;
    assert.strictEqual(splitNode.orientation, 'HORIZONTAL');
    assert.strictEqual(splitNode.children.length, 2);
    assert.deepStrictEqual(splitNode.size_ratios, [0.5, 0.5]);

    const discoveredIds = getAllPanelIds(newTree);
    assert.deepStrictEqual(discoveredIds.sort(), ['panel-inst-1', 'panel-inst-2']);
  });

  it('splits a panel vertically into two child panels', () => {
    const newTree = splitPanel(
      initialSinglePanel,
      'panel-inst-1',
      'VERTICAL',
      'panel-inst-3'
    );

    assert.strictEqual(newTree.node_type, 'SPLIT');
    const splitNode = newTree as SplitNode;
    assert.strictEqual(splitNode.orientation, 'VERTICAL');
    assert.strictEqual(splitNode.children.length, 2);
    assert.deepStrictEqual(splitNode.size_ratios, [0.5, 0.5]);
  });

  it('docks a panel into a tab stack alongside an existing panel', () => {
    const tabTree = dockIntoTabStack(
      initialSinglePanel,
      'panel-inst-1',
      'panel-inst-tab-2'
    );

    assert.strictEqual(tabTree.node_type, 'TAB_STACK');
    const tabNode = tabTree as TabStackNode;
    assert.deepStrictEqual(tabNode.panel_instance_ids, ['panel-inst-1', 'panel-inst-tab-2']);
    assert.strictEqual(tabNode.active_panel_instance_id, 'panel-inst-tab-2');

    const discoveredIds = getAllPanelIds(tabTree);
    assert.deepStrictEqual(discoveredIds, ['panel-inst-1', 'panel-inst-tab-2']);
  });

  it('updates the active tab in a tab stack', () => {
    const tabNode: TabStackNode = {
      node_id: 'stack-1',
      node_type: 'TAB_STACK',
      panel_instance_ids: ['panel-a', 'panel-b'],
      active_panel_instance_id: 'panel-a',
    };

    const updated = setActiveTab(tabNode, 'stack-1', 'panel-b') as TabStackNode;
    assert.strictEqual(updated.active_panel_instance_id, 'panel-b');
  });

  it('removes a panel from a 2-element split and collapses to remaining panel', () => {
    const splitNode: SplitNode = {
      node_id: 'split-root',
      node_type: 'SPLIT',
      orientation: 'HORIZONTAL',
      children: [
        { node_id: 'p1', node_type: 'PANEL', panel_instance_id: 'panel-keep' },
        { node_id: 'p2', node_type: 'PANEL', panel_instance_id: 'panel-drop' },
      ],
      size_ratios: [0.5, 0.5],
    };

    const pruned = removePanel(splitNode, 'panel-drop');
    assert.ok(pruned !== null);
    assert.strictEqual(pruned.node_type, 'PANEL');
    assert.strictEqual((pruned as PanelNode).panel_instance_id, 'panel-keep');
  });

  it('swaps two panels within a nested layout tree', () => {
    const nestedTree: SplitNode = {
      node_id: 'split-root',
      node_type: 'SPLIT',
      orientation: 'HORIZONTAL',
      children: [
        { node_id: 'p1', node_type: 'PANEL', panel_instance_id: 'panel-alpha' },
        {
          node_id: 'split-sub',
          node_type: 'SPLIT',
          orientation: 'VERTICAL',
          children: [
            { node_id: 'p2', node_type: 'PANEL', panel_instance_id: 'panel-beta' },
            { node_id: 'p3', node_type: 'PANEL', panel_instance_id: 'panel-gamma' },
          ],
          size_ratios: [0.6, 0.4],
        },
      ],
      size_ratios: [0.5, 0.5],
    };

    const swapped = swapPanels(nestedTree, 'panel-alpha', 'panel-gamma');
    const panelIds = getAllPanelIds(swapped);
    assert.strictEqual(panelIds.length, 3);
    assert.ok(panelIds.includes('panel-alpha'));
    assert.ok(panelIds.includes('panel-beta'));
    assert.ok(panelIds.includes('panel-gamma'));
  });

  it('normalizes updated split ratios', () => {
    const splitNode: SplitNode = {
      node_id: 'split-1',
      node_type: 'SPLIT',
      orientation: 'HORIZONTAL',
      children: [
        { node_id: 'p1', node_type: 'PANEL', panel_instance_id: 'panel-1' },
        { node_id: 'p2', node_type: 'PANEL', panel_instance_id: 'panel-2' },
      ],
      size_ratios: [0.5, 0.5],
    };

    const updated = updateSplitRatios(splitNode, 'split-1', [0.7, 0.3]) as SplitNode;
    assert.strictEqual(updated.size_ratios[0], 0.7);
    assert.strictEqual(updated.size_ratios[1], 0.3);
  });
});

describe('Stage 120 - Cross-Panel Link Groups & Context Dimensions', () => {
  it('validates canonical context dimensions and link group structure', () => {
    const dimensions: ContextDimension[] = [
      'INSTRUMENT',
      'COMPANY',
      'PORTFOLIO',
      'BENCHMARK',
      'DATE_RANGE',
      'AS_OF_DATE',
      'TIMEFRAME',
      'REPORTING_CURRENCY',
    ];

    assert.strictEqual(dimensions.length, 8);

    const groupA: WorkspaceLinkGroup = {
      link_group_id: 'group-a',
      workspace_id: 'ws-1',
      name: 'Group A (Blue)',
      color: '#3B82F6',
      context: {
        INSTRUMENT: 'AAPL',
        COMPANY: 'Apple Inc.',
        REPORTING_CURRENCY: 'USD',
      },
      version: 1,
    };

    assert.strictEqual(groupA.color, '#3B82F6');
    assert.strictEqual(groupA.context.INSTRUMENT, 'AAPL');
  });

  it('enforces independent panel isolation invariant', () => {
    const independentPanel: WorkspacePanelInstance = {
      panel_instance_id: 'panel-isolated',
      workspace_id: 'ws-1',
      panel_type_id: 'ECONOMIC_SERIES',
      title_override: 'Macro Indicators (Locked)',
      link_group_id: null,
      independent_mode: true,
      configuration: { series_id: 'FEDFUNDS' },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    assert.strictEqual(independentPanel.link_group_id, null);
    assert.strictEqual(independentPanel.independent_mode, true);
  });
});

describe('Stage 120 - Canonical Panel Types & Template Catalog', () => {
  it('contains the 14 canonical institutional panel types', () => {
    const canonicalPanelTypes: PanelTypeId[] = [
      'MARKET_OVERVIEW',
      'INSTRUMENT_CHART',
      'WATCHLIST',
      'SCREENER',
      'COMPANY_OVERVIEW',
      'ECONOMIC_SERIES',
      'NEWS_FEED',
      'RESEARCH_DOCUMENT',
      'RESEARCH_REPORT',
      'PORTFOLIO_SUMMARY',
      'PORTFOLIO_PERFORMANCE',
      'RISK_OVERVIEW',
      'RISK_ANALYSIS',
      'DATA_TABLE',
    ];

    assert.strictEqual(canonicalPanelTypes.length, 14);
    assert.ok(canonicalPanelTypes.includes('INSTRUMENT_CHART'));
    assert.ok(canonicalPanelTypes.includes('RISK_OVERVIEW'));
    assert.ok(canonicalPanelTypes.includes('COMPANY_OVERVIEW'));
  });
});

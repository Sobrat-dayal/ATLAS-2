/**
 * Immutable Layout Tree Operations (Stage 120).
 */

import { LayoutNode, PanelNode, SplitNode, SplitOrientation, TabStackNode } from "./types";

function generateNodeId(prefix: string = "node"): string {
  return `${prefix}_${Math.random().toString(36).substring(2, 9)}`;
}

export function getAllPanelIds(node: LayoutNode): string[] {
  if (node.node_type === "PANEL") {
    return node.panel_instance_id ? [node.panel_instance_id] : [];
  }
  if (node.node_type === "TAB_STACK") {
    return [...node.panel_instance_ids];
  }
  if (node.node_type === "SPLIT") {
    const ids: string[] = [];
    for (const child of node.children) {
      ids.push(...getAllPanelIds(child));
    }
    return ids;
  }
  return [];
}

export function splitPanel(
  root: LayoutNode,
  targetPanelId: string,
  orientation: SplitOrientation,
  newPanelId: string
): LayoutNode {
  function _walk(node: LayoutNode): LayoutNode {
    if (node.node_type === "PANEL") {
      if (node.panel_instance_id === targetPanelId) {
        const newPanelNode: PanelNode = {
          node_id: generateNodeId("panel"),
          node_type: "PANEL",
          panel_instance_id: newPanelId,
        };
        const split: SplitNode = {
          node_id: generateNodeId("split"),
          node_type: "SPLIT",
          orientation,
          children: [{ ...node }, newPanelNode],
          size_ratios: [0.5, 0.5],
        };
        return split;
      }
      return node;
    }

    if (node.node_type === "TAB_STACK") {
      if (node.panel_instance_ids.includes(targetPanelId)) {
        const newPanelNode: PanelNode = {
          node_id: generateNodeId("panel"),
          node_type: "PANEL",
          panel_instance_id: newPanelId,
        };
        const split: SplitNode = {
          node_id: generateNodeId("split"),
          node_type: "SPLIT",
          orientation,
          children: [{ ...node }, newPanelNode],
          size_ratios: [0.5, 0.5],
        };
        return split;
      }
      return node;
    }

    if (node.node_type === "SPLIT") {
      return {
        ...node,
        children: node.children.map(_walk),
      };
    }

    return node;
  }

  return _walk(root);
}

export function dockIntoTabStack(
  root: LayoutNode,
  targetPanelId: string,
  newPanelId: string
): LayoutNode {
  function _walk(node: LayoutNode): LayoutNode {
    if (node.node_type === "PANEL") {
      if (node.panel_instance_id === targetPanelId) {
        const tabStack: TabStackNode = {
          node_id: generateNodeId("tabstack"),
          node_type: "TAB_STACK",
          panel_instance_ids: [targetPanelId, newPanelId],
          active_panel_instance_id: newPanelId,
        };
        return tabStack;
      }
      return node;
    }

    if (node.node_type === "TAB_STACK") {
      if (node.panel_instance_ids.includes(targetPanelId)) {
        return {
          ...node,
          panel_instance_ids: [...node.panel_instance_ids, newPanelId],
          active_panel_instance_id: newPanelId,
        };
      }
      return node;
    }

    if (node.node_type === "SPLIT") {
      return {
        ...node,
        children: node.children.map(_walk),
      };
    }

    return node;
  }

  return _walk(root);
}

export function removePanel(root: LayoutNode, panelIdToRemove: string): LayoutNode | null {
  function _walk(node: LayoutNode): LayoutNode | null {
    if (node.node_type === "PANEL") {
      return node.panel_instance_id === panelIdToRemove ? null : node;
    }

    if (node.node_type === "TAB_STACK") {
      const remaining = node.panel_instance_ids.filter((id) => id !== panelIdToRemove);
      if (remaining.length === 0) {
        return null;
      }
      if (remaining.length === 1) {
        return {
          node_id: generateNodeId("panel"),
          node_type: "PANEL",
          panel_instance_id: remaining[0],
        };
      }
      const newActive =
        node.active_panel_instance_id === panelIdToRemove ? remaining[0] : node.active_panel_instance_id;
      return {
        ...node,
        panel_instance_ids: remaining,
        active_panel_instance_id: newActive,
      };
    }

    if (node.node_type === "SPLIT") {
      const newChildren: LayoutNode[] = [];
      for (const child of node.children) {
        const walked = _walk(child);
        if (walked) {
          newChildren.push(walked);
        }
      }

      if (newChildren.length === 0) {
        return null;
      }
      if (newChildren.length === 1) {
        return newChildren[0];
      }

      const count = newChildren.length;
      return {
        ...node,
        children: newChildren,
        size_ratios: Array(count).fill(1 / count),
      };
    }

    return node;
  }

  return _walk(root);
}

export function swapPanels(root: LayoutNode, panelIdA: string, panelIdB: string): LayoutNode {
  function _walk(node: LayoutNode): LayoutNode {
    if (node.node_type === "PANEL") {
      if (node.panel_instance_id === panelIdA) {
        return { ...node, panel_instance_id: panelIdB };
      }
      if (node.panel_instance_id === panelIdB) {
        return { ...node, panel_instance_id: panelIdA };
      }
      return node;
    }

    if (node.node_type === "TAB_STACK") {
      const remapped = node.panel_instance_ids.map((id) => {
        if (id === panelIdA) return panelIdB;
        if (id === panelIdB) return panelIdA;
        return id;
      });
      let active = node.active_panel_instance_id;
      if (active === panelIdA) active = panelIdB;
      else if (active === panelIdB) active = panelIdA;

      return {
        ...node,
        panel_instance_ids: remapped,
        active_panel_instance_id: active,
      };
    }

    if (node.node_type === "SPLIT") {
      return {
        ...node,
        children: node.children.map(_walk),
      };
    }

    return node;
  }

  return _walk(root);
}

export function updateSplitRatios(
  root: LayoutNode,
  splitNodeId: string,
  newRatios: number[]
): LayoutNode {
  function _walk(node: LayoutNode): LayoutNode {
    if (node.node_type === "SPLIT") {
      if (node.node_id === splitNodeId) {
        return {
          ...node,
          size_ratios: newRatios,
        };
      }
      return {
        ...node,
        children: node.children.map(_walk),
      };
    }
    return node;
  }

  return _walk(root);
}

export function setActiveTab(
  root: LayoutNode,
  tabStackNodeId: string,
  activePanelId: string
): LayoutNode {
  function _walk(node: LayoutNode): LayoutNode {
    if (node.node_type === "TAB_STACK" && node.node_id === tabStackNodeId) {
      return {
        ...node,
        active_panel_instance_id: activePanelId,
      };
    }
    if (node.node_type === "SPLIT") {
      return {
        ...node,
        children: node.children.map(_walk),
      };
    }
    return node;
  }

  return _walk(root);
}


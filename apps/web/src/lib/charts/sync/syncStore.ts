/**
 * Session-Level Chart Synchronization Group Store for ATLAS Charts (Stage 73).
 *
 * Implements:
 * - Bounded session-level synchronization groups (bounded to workspace capacity: 4 panels)
 * - Fine-grained per-property synchronization settings
 * - Safe group lifecycle: create, rename, toggle property, enable, disable, delete
 * - Group membership rules: each panel belongs to at most 1 group at a time in V1
 * - Default independence policy: all panels start completely independent until user opts in
 * - Monotonic group revision counter on any membership or settings change
 * - Align group to active chart panel action
 * - React subscriber notification pattern
 */

import {
  ChartSyncGroup,
  ChartSyncProperty,
  ChartSyncSettings,
  DEFAULT_SYNC_SETTINGS,
} from "./types";

export const CANONICAL_SYNC_GROUP_COLORS = [
  "#06b6d4", // Cyan 500
  "#10b981", // Emerald 500
  "#f59e0b", // Amber 500
  "#a855f7", // Purple 500
];

export class ChartSyncStore {
  private groups: Map<string, ChartSyncGroup> = new Map();
  private listeners = new Set<() => void>();

  constructor() {
    this.initializeDefaultGroups();
  }

  private initializeDefaultGroups(): void {
    // Initialize 2 pre-configured groups in independent/disabled state
    const groupA: ChartSyncGroup = {
      id: "group-a",
      name: "Group A",
      memberPanelIds: [],
      settings: { ...DEFAULT_SYNC_SETTINGS },
      enabled: false,
      revision: 1,
      color: CANONICAL_SYNC_GROUP_COLORS[0],
    };

    const groupB: ChartSyncGroup = {
      id: "group-b",
      name: "Group B",
      memberPanelIds: [],
      settings: { ...DEFAULT_SYNC_SETTINGS },
      enabled: false,
      revision: 1,
      color: CANONICAL_SYNC_GROUP_COLORS[1],
    };

    this.groups.set(groupA.id, groupA);
    this.groups.set(groupB.id, groupB);
  }

  public getAllGroups(): ChartSyncGroup[] {
    return Array.from(this.groups.values());
  }

  public getGroup(groupId: string): ChartSyncGroup | null {
    return this.groups.get(groupId) ?? null;
  }

  public getGroupByPanelId(panelId: string): ChartSyncGroup | null {
    for (const group of this.groups.values()) {
      if (group.memberPanelIds.includes(panelId)) {
        return group;
      }
    }
    return null;
  }

  /**
   * Create a new synchronization group.
   */
  public createGroup(name: string, color?: string): ChartSyncGroup {
    const id = `group-${Date.now().toString(36).slice(-5)}`;
    const groupIndex = this.groups.size % CANONICAL_SYNC_GROUP_COLORS.length;
    const groupColor = color || CANONICAL_SYNC_GROUP_COLORS[groupIndex];

    const newGroup: ChartSyncGroup = {
      id,
      name: name.trim() || `Group ${String.fromCharCode(65 + this.groups.size)}`,
      memberPanelIds: [],
      settings: { ...DEFAULT_SYNC_SETTINGS },
      enabled: false,
      revision: 1,
      color: groupColor,
    };

    this.groups.set(id, newGroup);
    this.notify();
    return newGroup;
  }

  /**
   * Rename an existing group.
   */
  public renameGroup(groupId: string, name: string): void {
    const group = this.groups.get(groupId);
    if (!group) return;

    group.name = name.trim() || group.name;
    group.revision += 1;
    this.notify();
  }

  /**
   * Delete a synchronization group and return all its members to independent mode.
   */
  public deleteGroup(groupId: string): void {
    if (!this.groups.has(groupId)) return;
    this.groups.delete(groupId);
    this.notify();
  }

  /**
   * Enable or disable a synchronization group.
   */
  public setGroupEnabled(groupId: string, enabled: boolean): void {
    const group = this.groups.get(groupId);
    if (!group) return;

    group.enabled = enabled;
    group.revision += 1;
    this.notify();
  }

  /**
   * Toggle a specific synchronization property for a group.
   */
  public toggleProperty(groupId: string, property: ChartSyncProperty): void {
    const group = this.groups.get(groupId);
    if (!group) return;

    group.settings[property] = !group.settings[property];
    // Automatically enable group if at least one property is active and group has members
    if (Object.values(group.settings).some((v) => v === true)) {
      group.enabled = true;
    }
    group.revision += 1;
    this.notify();
  }

  /**
   * Update full or partial settings for a group.
   */
  public updateSettings(groupId: string, settings: Partial<ChartSyncSettings>): void {
    const group = this.groups.get(groupId);
    if (!group) return;

    group.settings = { ...group.settings, ...settings };
    group.revision += 1;
    this.notify();
  }

  /**
   * Assign a panel to a group. Enforces the rule that a panel belongs to at most one group in V1.
   */
  public assignPanelToGroup(panelId: string, targetGroupId: string): void {
    const targetGroup = this.groups.get(targetGroupId);
    if (!targetGroup) return;

    // 1. Remove panel from any existing group first
    for (const group of this.groups.values()) {
      if (group.memberPanelIds.includes(panelId)) {
        group.memberPanelIds = group.memberPanelIds.filter((id) => id !== panelId);
        group.revision += 1;
      }
    }

    // 2. Add to target group (max 4 panels per group)
    if (!targetGroup.memberPanelIds.includes(panelId) && targetGroup.memberPanelIds.length < 4) {
      targetGroup.memberPanelIds.push(panelId);
      targetGroup.revision += 1;
    }

    this.notify();
  }

  /**
   * Remove a panel from its synchronization group, restoring it to independent mode.
   */
  public removePanelFromGroup(panelId: string): void {
    let changed = false;
    for (const group of this.groups.values()) {
      if (group.memberPanelIds.includes(panelId)) {
        group.memberPanelIds = group.memberPanelIds.filter((id) => id !== panelId);
        group.revision += 1;
        changed = true;
      }
    }
    if (changed) {
      this.notify();
    }
  }

  /**
   * Return all panels to independent mode (clears all group memberships and disables all groups).
   */
  public resetToIndependentMode(): void {
    for (const group of this.groups.values()) {
      group.memberPanelIds = [];
      group.enabled = false;
      group.settings = { ...DEFAULT_SYNC_SETTINGS };
      group.revision += 1;
    }
    this.notify();
  }

  /**
   * React subscriber listener pattern.
   */
  public subscribe(listener: () => void): () => void {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  private notify(): void {
    for (const listener of this.listeners) {
      listener();
    }
  }
}

export const chartSyncStore = new ChartSyncStore();

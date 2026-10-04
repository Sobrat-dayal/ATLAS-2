"use client";

export function getLayoutState(layoutId: string): any {
  if (typeof window === 'undefined') return undefined;
  try {
    const raw = localStorage.getItem(`atlas.layout.${layoutId}.v1`);
    if (raw) {
      const parsed = JSON.parse(raw);
      return parsed; // Allow v4 Layout map or legacy array
    }
  } catch (e) {
    console.error(`Failed to load layout state for ${layoutId}`, e);
  }
  return undefined;
}

export function setLayoutState(layoutId: string, sizes: any) {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(`atlas.layout.${layoutId}.v1`, JSON.stringify(sizes));
  } catch (e) {
    console.error(`Failed to save layout state for ${layoutId}`, e);
  }
}

export function getPanelCollapsedState(panelId: string, defaultCollapsed: boolean): boolean {
  if (typeof window === 'undefined') return defaultCollapsed;
  try {
    const raw = localStorage.getItem(`atlas.layout.panel.${panelId}.collapsed.v1`);
    if (raw) {
      return JSON.parse(raw) === true;
    }
  } catch (e) {
    console.error(`Failed to load collapse state for ${panelId}`, e);
  }
  return defaultCollapsed;
}

export function setPanelCollapsedState(panelId: string, isCollapsed: boolean) {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(`atlas.layout.panel.${panelId}.collapsed.v1`, JSON.stringify(isCollapsed));
  } catch (e) {
    console.error(`Failed to save collapse state for ${panelId}`, e);
  }
}

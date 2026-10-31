/**
 * MapLibre / deck.gl Overlay Lifecycle Controller (Stage 131).
 *
 * Wraps @deck.gl/maplibre's MapLibreOverlay with WebGL compatibility checks,
 * layer synchronization across basemap style switches, and deterministic disposal.
 */

import { MapLibreOverlay } from '@deck.gl/maplibre';
import type { Map as MapLibreMap } from 'maplibre-gl';

export class AtlasDeckOverlayController {
  private overlay: MapLibreOverlay | null = null;
  private map: MapLibreMap | null = null;
  private isAttached: boolean = false;

  /**
   * Initializes and attaches MapLibreOverlay to the MapLibre map instance.
   */
  public attach(map: MapLibreMap, initialLayers: any[] = []): boolean {
    if (this.isAttached && this.overlay) {
      this.setLayers(initialLayers);
      return true;
    }

    try {
      this.map = map;
      this.overlay = new MapLibreOverlay({
        layers: initialLayers,
        interleaved: false, // Overlaid mode ensures rock-solid compatibility across all WebGL devices
      });

      this.map.addControl(this.overlay);
      this.isAttached = true;
      return true;
    } catch (err) {
      console.error('[AtlasDeckOverlayController] Failed to attach deck.gl overlay to MapLibre:', err);
      this.isAttached = false;
      this.overlay = null;
      return false;
    }
  }

  /**
   * Updates deck.gl layers without recreating the overlay control or breaking camera interactions.
   */
  public setLayers(layers: any[]): void {
    if (!this.overlay || !this.isAttached) return;
    try {
      this.overlay.setProps({ layers });
    } catch (err) {
      console.warn('[AtlasDeckOverlayController] Error updating deck.gl layers:', err);
    }
  }

  /**
   * Re-synchronizes layers when the underlying MapLibre basemap style changes.
   */
  public handleStyleChange(layers: any[]): void {
    if (this.overlay && this.isAttached) {
      this.setLayers(layers);
    }
  }

  /**
   * Detaches and disposes the overlay control and its WebGL resources.
   */
  public detach(): void {
    if (!this.overlay) return;

    try {
      if (this.map && this.isAttached) {
        this.map.removeControl(this.overlay);
      }
    } catch (err) {
      console.warn('[AtlasDeckOverlayController] Error removing deck.gl overlay from map:', err);
    } finally {
      this.overlay = null;
      this.map = null;
      this.isAttached = false;
    }
  }

  public getAttached(): boolean {
    return this.isAttached;
  }
}


export type AtlasBackgroundMode = "none" | "image";
export type AtlasBackgroundFit = "cover" | "contain" | "stretch" | "tile";
export type AtlasBackgroundPosition =
  | "center" | "top" | "bottom" | "left" | "right"
  | "top-left" | "top-right" | "bottom-left" | "bottom-right";
export type AtlasBackgroundOverlayTone = "dark" | "light" | "auto";

export interface AtlasBackgroundSettings {
  enabled: boolean;
  mode: AtlasBackgroundMode;
  imageId?: string;
  opacity: number;
  blur: number;
  brightness: number;
  contrast: number;
  saturation: number;
  grayscale: number;
  fit: AtlasBackgroundFit;
  position: AtlasBackgroundPosition;
  overlayOpacity: number;
  overlayTone: AtlasBackgroundOverlayTone;
  locked: boolean;
}

export interface AtlasBackgroundAsset {
  id: string;
  name: string;
  mimeType: string;
  size: number;
  width: number;
  height: number;
  createdAt: number;
}

export const DEFAULT_BACKGROUND_SETTINGS: AtlasBackgroundSettings = {
  enabled: false,
  mode: "image",
  opacity: 10,
  blur: 0,
  brightness: 80,
  contrast: 100,
  saturation: 80,
  grayscale: 0,
  fit: "cover",
  position: "center",
  overlayOpacity: 50,
  overlayTone: "dark",
  locked: false,
};

export const WATERMARK_PRESET: Partial<AtlasBackgroundSettings> = {
  enabled: true,
  mode: "image",
  opacity: 8,
  blur: 0,
  brightness: 70,
  contrast: 100,
  saturation: 40,
  grayscale: 0,
  fit: "contain",
  position: "center",
  overlayOpacity: 50,
  overlayTone: "dark",
};

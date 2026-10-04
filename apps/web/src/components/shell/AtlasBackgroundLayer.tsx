"use client";

import { useBackground } from "@/hooks/background";
import { useAppearance } from "@/hooks/appearance";

export function AtlasBackgroundLayer() {
  const { settings, draftSettings, activeImageUrl } = useBackground();
  const { theme } = useAppearance();

  const active = draftSettings || settings;

  if (!active.enabled || active.mode === "none" || !activeImageUrl) {
    return null;
  }

  const {
    opacity,
    blur,
    brightness,
    contrast,
    saturation,
    grayscale,
    fit,
    position,
    overlayOpacity,
    overlayTone
  } = active;

  // Resolve overlay color
  let overlayColor = "transparent";
  if (overlayOpacity > 0) {
    const tone = overlayTone === "auto" 
      ? (theme === "light" ? "light" : "dark") 
      : overlayTone;
      
    if (tone === "dark") {
      overlayColor = `rgba(0, 0, 0, ${overlayOpacity / 100})`;
    } else {
      overlayColor = `rgba(255, 255, 255, ${overlayOpacity / 100})`;
    }
  }

  const getObjectFit = () => {
    switch (fit) {
      case "contain": return "contain";
      case "stretch": return "fill";
      case "tile": return "none"; // Handled by background-repeat if we used background-image, but we are using img tag for better filter support
      case "cover":
      default: return "cover";
    }
  };

  const getObjectPosition = () => {
    return position.replace("-", " ");
  };

  // Build filter string
  const filters = [
    blur > 0 ? `blur(${blur}px)` : "",
    brightness !== 100 ? `brightness(${brightness}%)` : "",
    contrast !== 100 ? `contrast(${contrast}%)` : "",
    saturation !== 100 ? `saturate(${saturation}%)` : "",
    grayscale > 0 ? `grayscale(${grayscale}%)` : ""
  ].filter(Boolean).join(" ");

  return (
    <div 
      className="fixed inset-0 pointer-events-none z-[-20] overflow-hidden"
      style={{ opacity: opacity / 100 }}
      aria-hidden="true"
    >
      {/* 
        We scale slightly if there's a blur to avoid the edges of the image showing 
        the underlying background color bleeding in.
      */}
      {fit === "tile" ? (
        <div 
          className="absolute inset-0"
          style={{
            backgroundImage: `url(${activeImageUrl})`,
            backgroundRepeat: "repeat",
            backgroundPosition: getObjectPosition(),
            filter: filters,
            transform: blur > 0 ? `scale(${1 + (blur * 0.01)})` : "none"
          }}
        />
      ) : (
        <img 
          src={activeImageUrl} 
          alt=""
          className="absolute inset-0 w-full h-full"
          style={{
            objectFit: getObjectFit(),
            objectPosition: getObjectPosition(),
            filter: filters,
            transform: blur > 0 && fit === "cover" ? `scale(${1 + (blur * 0.01)})` : "none"
          }}
        />
      )}

      {/* Readability Overlay Layer */}
      <div 
        className="absolute inset-0 z-[-15] pointer-events-none"
        style={{ backgroundColor: overlayColor }}
      />
    </div>
  );
}

import React from "react";
import { COLORS } from "../utils/colors";
import { ICON_CONFIG } from "../utils/iconPaths";
import type { IconId } from "../utils/layout";

interface SoftwareIconProps {
  id: IconId;
  x: number;
  y: number;
  opacity?: number;
  scale?: number;
  glowing?: boolean;
}

export const SoftwareIcon: React.FC<SoftwareIconProps> = ({
  id,
  x,
  y,
  opacity = 1,
  scale = 1,
  glowing = false,
}) => {
  const { color, emoji, label } = ICON_CONFIG[id];
  const size = 88;

  return (
    <div
      style={{
        position: "absolute",
        left: x - (size / 2) * scale,
        top: y - (size / 2) * scale,
        width: size * scale,
        height: size * scale,
        opacity,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 6 * scale,
      }}
    >
      {/* Icon box */}
      <div
        style={{
          width: size * scale,
          height: size * scale,
          borderRadius: 18 * scale,
          border: `1.5px solid ${color}55`,
          background: `radial-gradient(circle at 40% 35%, ${color}22, ${COLORS.iconFill})`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 38 * scale,
          boxShadow: glowing
            ? `0 0 ${24 * scale}px ${color}88, 0 0 ${48 * scale}px ${color}44`
            : `0 0 ${12 * scale}px ${color}33`,
          position: "relative",
        }}
      >
        {emoji}
        {/* Color accent dot */}
        <div
          style={{
            position: "absolute",
            bottom: 8 * scale,
            right: 8 * scale,
            width: 10 * scale,
            height: 10 * scale,
            borderRadius: "50%",
            background: color,
            boxShadow: `0 0 6px ${color}`,
          }}
        />
      </div>
      {/* Label */}
      <div
        style={{
          color: COLORS.textSecondary,
          fontSize: 13 * scale,
          fontFamily: "'Inter', 'SF Pro Display', system-ui, sans-serif",
          fontWeight: 500,
          letterSpacing: "0.05em",
          textAlign: "center",
          marginTop: 4 * scale,
          whiteSpace: "nowrap",
        }}
      >
        {label}
      </div>
    </div>
  );
};

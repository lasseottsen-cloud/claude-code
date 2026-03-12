import React from "react";
import { COLORS } from "../utils/colors";

interface ModuleCardProps {
  x: number;
  y: number;
  title: string;
  items: string[];
  opacity?: number;
  scale?: number;
  accentColor?: string;
  width?: number;
}

export const ModuleCard: React.FC<ModuleCardProps> = ({
  x,
  y,
  title,
  items,
  opacity = 1,
  scale = 1,
  accentColor = COLORS.streamBlue,
  width = 220,
}) => {
  const h = (items.length * 28 + 64) * scale;
  const w = width * scale;

  return (
    <div
      style={{
        position: "absolute",
        left: x - w / 2,
        top: y - h / 2,
        width: w,
        height: h,
        opacity,
        background: "rgba(10, 12, 28, 0.85)",
        border: `1px solid ${accentColor}44`,
        borderRadius: 12 * scale,
        overflow: "hidden",
        boxShadow: `0 0 20px ${accentColor}22, inset 0 1px 0 rgba(255,255,255,0.05)`,
        backdropFilter: "blur(8px)",
      }}
    >
      {/* Header */}
      <div
        style={{
          background: `linear-gradient(90deg, ${accentColor}33, transparent)`,
          borderBottom: `1px solid ${accentColor}33`,
          padding: `${8 * scale}px ${12 * scale}px`,
          display: "flex",
          alignItems: "center",
          gap: 6 * scale,
        }}
      >
        <div
          style={{
            width: 8 * scale,
            height: 8 * scale,
            borderRadius: "50%",
            background: accentColor,
            boxShadow: `0 0 6px ${accentColor}`,
          }}
        />
        <span
          style={{
            color: COLORS.textPrimary,
            fontSize: 13 * scale,
            fontFamily: "'Inter', system-ui, sans-serif",
            fontWeight: 600,
            letterSpacing: "0.04em",
          }}
        >
          {title}
        </span>
      </div>

      {/* Items */}
      <div style={{ padding: `${6 * scale}px ${12 * scale}px` }}>
        {items.map((item, i) => (
          <div
            key={i}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8 * scale,
              padding: `${4 * scale}px 0`,
              borderBottom:
                i < items.length - 1
                  ? `1px solid rgba(255,255,255,0.05)`
                  : "none",
            }}
          >
            <div
              style={{
                width: 4 * scale,
                height: 4 * scale,
                borderRadius: "50%",
                background: `${accentColor}99`,
              }}
            />
            <span
              style={{
                color: COLORS.textSecondary,
                fontSize: 11 * scale,
                fontFamily: "'Inter', system-ui, sans-serif",
                fontWeight: 400,
              }}
            >
              {item}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

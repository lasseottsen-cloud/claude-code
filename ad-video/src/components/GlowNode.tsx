import React from "react";
import { COLORS } from "../utils/colors";

interface GlowNodeProps {
  cx: number;
  cy: number;
  scale: number; // 0–1+
  opacity?: number;
  pulseProgress?: number; // 0–1 for pulsing ring
}

export const GlowNode: React.FC<GlowNodeProps> = ({
  cx,
  cy,
  scale,
  opacity = 1,
  pulseProgress = 0,
}) => {
  const coreRadius = 24 * scale;
  const innerGlow = 60 * scale;
  const outerGlow = 120 * scale;

  return (
    <svg
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        overflow: "visible",
        opacity,
        pointerEvents: "none",
      }}
    >
      {/* Outer glow */}
      <circle
        cx={cx}
        cy={cy}
        r={outerGlow}
        fill={`radial-gradient(circle, ${COLORS.glowBlue}22 0%, transparent 70%)`}
        opacity={0.4}
      />
      <circle
        cx={cx}
        cy={cy}
        r={outerGlow}
        fill="none"
        stroke={COLORS.glowBlue}
        strokeWidth={1}
        strokeOpacity={0.15}
      />

      {/* Inner glow */}
      <circle
        cx={cx}
        cy={cy}
        r={innerGlow}
        fill="none"
        stroke={COLORS.streamCyan}
        strokeWidth={1.5}
        strokeOpacity={0.3}
      />

      {/* Pulse ring */}
      {pulseProgress > 0 && (
        <circle
          cx={cx}
          cy={cy}
          r={coreRadius + (outerGlow - coreRadius) * pulseProgress}
          fill="none"
          stroke={COLORS.streamCyan}
          strokeWidth={2}
          strokeOpacity={1 - pulseProgress}
        />
      )}

      {/* Core */}
      <circle
        cx={cx}
        cy={cy}
        r={coreRadius}
        fill="white"
        opacity={0.95}
        style={{
          filter: `drop-shadow(0 0 ${12 * scale}px ${COLORS.streamCyan}) drop-shadow(0 0 ${24 * scale}px ${COLORS.glowBlue})`,
        }}
      />

      {/* Center dot */}
      <circle
        cx={cx}
        cy={cy}
        r={coreRadius * 0.3}
        fill={COLORS.glowBlue}
      />
    </svg>
  );
};

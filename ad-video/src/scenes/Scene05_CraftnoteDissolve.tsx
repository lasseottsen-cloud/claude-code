import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { SoftwareIcon } from "../components/SoftwareIcon";
import { ParticleSystem } from "../components/ParticleSystem";
import { GlowNode } from "../components/GlowNode";
import { DataStreamLine } from "../components/DataStreamLine";
import { COLORS } from "../utils/colors";
import { ICON_POSITIONS, CENTER, type IconId } from "../utils/layout";
import { lerp, smoothIn } from "../utils/animations";

const OTHER_ICONS: IconId[] = ["BLS", "BMD", "Sevdesk", "Excel", "OneDrive", "Dropbox", "Email"];

export const Scene05_CraftnoteDissolve: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Craftnote drifts toward center
  const craftnotePos = ICON_POSITIONS["Craftnote"];
  const driftProgress = lerp(frame, [0, 45], [0, 1]);
  const cx = craftnotePos.x + (CENTER.x - craftnotePos.x) * driftProgress;
  const cy = craftnotePos.y + (CENTER.y - craftnotePos.y) * driftProgress;

  // Bubble opacity (appears as icon approaches center)
  const bubbleOpacity = lerp(frame, [20, 40], [0, 0.5]);
  const bubbleRadius = lerp(frame, [40, 55], [50, 80]);

  // Dissolve: icon fades, particles appear
  const iconOpacity = lerp(frame, [45, 60], [1, 0]);
  const particleProgress = lerp(frame, [50, 85], [0, 1]);

  // Ordered lines from center
  const linesOpacity = lerp(frame, [0, 20], [0, 0.6]);

  return (
    <AbsoluteFill
      style={{
        background: "radial-gradient(ellipse at 50% 50%, #05050F 0%, #000000 70%)",
      }}
    >
      {/* Lines from center to remaining icons */}
      {OTHER_ICONS.map((id) => (
        <DataStreamLine
          key={id}
          x1={CENTER.x}
          y1={CENTER.y}
          x2={ICON_POSITIONS[id].x}
          y2={ICON_POSITIONS[id].y}
          progress={1}
          color={COLORS.streamCyan}
          opacity={linesOpacity}
          curved={false}
        />
      ))}

      {/* Central glow node */}
      <GlowNode cx={CENTER.x} cy={CENTER.y} scale={1} opacity={1} />

      {/* Bubble around Craftnote */}
      <svg
        style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", overflow: "visible", pointerEvents: "none" }}
      >
        <circle
          cx={cx}
          cy={cy}
          r={bubbleRadius}
          fill="none"
          stroke={COLORS.streamCyan}
          strokeWidth={1.5}
          opacity={bubbleOpacity}
          style={{ filter: `drop-shadow(0 0 8px ${COLORS.streamCyan})` }}
        />
      </svg>

      {/* Particles */}
      {particleProgress > 0 && (
        <ParticleSystem
          cx={CENTER.x}
          cy={CENTER.y}
          progress={particleProgress}
          count={36}
        />
      )}

      {/* Craftnote icon (drifting to center, then dissolving) */}
      <div
        style={{ position: "absolute", left: 0, top: 0 }}
      >
        <SoftwareIcon
          id="Craftnote"
          x={cx}
          y={cy}
          opacity={iconOpacity}
          scale={1 - driftProgress * 0.2}
        />
      </div>

      {/* Other icons remain */}
      {OTHER_ICONS.map((id, i) => {
        const pos = ICON_POSITIONS[id];
        const floatY = Math.sin(frame * 0.04 + i * 0.8) * 4;
        return (
          <div key={id} style={{ position: "absolute", left: 0, top: 0, transform: `translateY(${floatY}px)` }}>
            <SoftwareIcon id={id} x={pos.x} y={pos.y} opacity={0.7} />
          </div>
        );
      })}

      <div
        style={{
          position: "absolute",
          bottom: 80,
          left: 0,
          right: 0,
          textAlign: "center",
          opacity: lerp(frame, [50, 65], [0, 1]),
        }}
      >
        <p style={{ color: COLORS.textSecondary, fontSize: 16, fontFamily: "'Inter', system-ui, sans-serif", letterSpacing: "0.15em", textTransform: "uppercase", margin: 0 }}>
          Ein System, das bestehende Tools integriert — oder sogar ersetzt.
        </p>
      </div>
    </AbsoluteFill>
  );
};

export default Scene05_CraftnoteDissolve;

import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { SoftwareIcon } from "../components/SoftwareIcon";
import { DataStreamLine } from "../components/DataStreamLine";
import { GlowNode } from "../components/GlowNode";
import { COLORS } from "../utils/colors";
import { ICON_POSITIONS, CENTER, type IconId } from "../utils/layout";
import { lerp, smoothIn, fadeIn } from "../utils/animations";

const ICONS = Object.keys(ICON_POSITIONS) as IconId[];

const CONNECTIONS: [IconId, IconId][] = [
  ["Excel", "BMD"], ["Email", "Craftnote"],
  ["Dropbox", "BLS"], ["OneDrive", "Sevdesk"],
  ["BLS", "Craftnote"], ["BMD", "Email"],
];

export const Scene04_SystemEmerges: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Chaos lines fade out
  const chaosOpacity = lerp(frame, [0, 40], [0.5, 0]);
  // Central node grows in
  const nodeScale = smoothIn(frame, fps, 20);
  // Ordered lines from center to icons (appear after chaos gone)
  const orderedProgress = lerp(frame, [45, 80], [0, 1]);

  // Pulse ring
  const pulseProgress = lerp(frame, [30, 70], [0, 1]);

  return (
    <AbsoluteFill
      style={{
        background: "radial-gradient(ellipse at 50% 50%, #05050F 0%, #000000 70%)",
      }}
    >
      {/* Old chaotic lines fading */}
      {CONNECTIONS.map(([from, to], i) => (
        <DataStreamLine
          key={`chaos-${i}`}
          x1={ICON_POSITIONS[from].x}
          y1={ICON_POSITIONS[from].y}
          x2={ICON_POSITIONS[to].x}
          y2={ICON_POSITIONS[to].y}
          progress={1}
          color={COLORS.streamBlue}
          opacity={chaosOpacity}
        />
      ))}

      {/* New ordered lines from center to each icon */}
      {ICONS.map((id, i) => {
        const pos = ICON_POSITIONS[id];
        return (
          <DataStreamLine
            key={`ordered-${id}`}
            x1={CENTER.x}
            y1={CENTER.y}
            x2={pos.x}
            y2={pos.y}
            progress={orderedProgress}
            color={COLORS.streamCyan}
            opacity={orderedProgress * 0.7}
            curved={false}
          />
        );
      })}

      {/* Glow node */}
      <GlowNode
        cx={CENTER.x}
        cy={CENTER.y}
        scale={nodeScale}
        opacity={nodeScale}
        pulseProgress={pulseProgress}
      />

      {/* Icons (slightly dimmed) */}
      {ICONS.map((id, i) => {
        const pos = ICON_POSITIONS[id];
        const floatY = Math.sin(frame * 0.04 + i * 0.8) * 4;
        return (
          <div
            key={id}
            style={{ position: "absolute", left: 0, top: 0, transform: `translateY(${floatY}px)` }}
          >
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
          opacity: fadeIn(frame, 50, 20),
        }}
      >
        <p
          style={{
            color: COLORS.textSecondary,
            fontSize: 16,
            fontFamily: "'Inter', system-ui, sans-serif",
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            margin: 0,
          }}
        >
          Was wäre, wenn alles zusammenkommt?
        </p>
      </div>
    </AbsoluteFill>
  );
};

export default Scene04_SystemEmerges;

import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { SoftwareIcon } from "../components/SoftwareIcon";
import { DataStreamLine } from "../components/DataStreamLine";
import { COLORS } from "../utils/colors";
import { ICON_POSITIONS, CENTER, type IconId } from "../utils/layout";
import { lerp, fadeIn } from "../utils/animations";

const ICONS = Object.keys(ICON_POSITIONS) as IconId[];

const CONNECTIONS: [IconId, IconId][] = [
  ["Excel", "BMD"],
  ["Email", "Craftnote"],
  ["Dropbox", "BLS"],
  ["OneDrive", "Sevdesk"],
  ["BLS", "Craftnote"],
  ["BMD", "Email"],
  ["Sevdesk", "Excel"],
  ["OneDrive", "BMD"],
  ["Dropbox", "Email"],
  ["Excel", "Craftnote"],
  ["BLS", "Sevdesk"],
  ["Dropbox", "BMD"],
];

export const Scene03_ChaosFreeze: React.FC = () => {
  const frame = useCurrentFrame();

  // Zoom out effect
  const scale = lerp(frame, [0, 60], [1, 0.85]);
  const freezeOpacity = lerp(frame, [55, 70], [0, 0.6]);

  // Freeze overlay — white flash then dark vignette
  const flashOpacity = lerp(frame, [60, 70], [0, 1]);

  return (
    <AbsoluteFill
      style={{
        background: "radial-gradient(ellipse at 50% 50%, #050510 0%, #000000 70%)",
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          transformOrigin: `${CENTER.x}px ${CENTER.y}px`,
          transform: `scale(${scale})`,
        }}
      >
        {/* Lines */}
        {CONNECTIONS.map(([from, to], i) => {
          const a = ICON_POSITIONS[from];
          const b = ICON_POSITIONS[to];
          return (
            <DataStreamLine
              key={i}
              x1={a.x}
              y1={a.y}
              x2={b.x}
              y2={b.y}
              progress={1}
              color={i % 2 === 0 ? COLORS.streamCyan : COLORS.streamBlue}
              opacity={0.6}
            />
          );
        })}

        {/* Icons */}
        {ICONS.map((id, i) => {
          const pos = ICON_POSITIONS[id];
          const floatY = Math.sin(frame * 0.04 + i * 0.8) * 4;
          return (
            <div
              key={id}
              style={{
                position: "absolute",
                left: 0,
                top: 0,
                transform: `translateY(${floatY}px)`,
              }}
            >
              <SoftwareIcon id={id} x={pos.x} y={pos.y} />
            </div>
          );
        })}
      </div>

      {/* Freeze flash overlay */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "rgba(255,255,255,0.04)",
          opacity: freezeOpacity,
          pointerEvents: "none",
        }}
      />

      {/* Caption */}
      <div
        style={{
          position: "absolute",
          bottom: 80,
          left: 0,
          right: 0,
          textAlign: "center",
          opacity: fadeIn(frame, 5, 20),
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
          Daten wandern. Informationen gehen verloren.
        </p>
      </div>
    </AbsoluteFill>
  );
};

export default Scene03_ChaosFreeze;

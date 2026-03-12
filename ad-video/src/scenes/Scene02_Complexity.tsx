import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { SoftwareIcon } from "../components/SoftwareIcon";
import { DataStreamLine } from "../components/DataStreamLine";
import { COLORS } from "../utils/colors";
import { ICON_POSITIONS, type IconId } from "../utils/layout";
import { lerp } from "../utils/animations";

const ICONS = Object.keys(ICON_POSITIONS) as IconId[];

// Connections between icons — intentionally crossing/chaotic
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

const LINE_COLORS = [
  COLORS.streamCyan,
  COLORS.streamBlue,
  COLORS.glowPurple,
  "#FF6B35",
  "#FF9800",
];

export const Scene02_Complexity: React.FC = () => {
  const frame = useCurrentFrame();

  const floatY = (i: number) => Math.sin(frame * 0.04 + i * 0.8) * 5;

  return (
    <AbsoluteFill
      style={{
        background: "radial-gradient(ellipse at 50% 50%, #050510 0%, #000000 70%)",
      }}
    >
      {/* Data stream lines */}
      {CONNECTIONS.map(([from, to], i) => {
        const a = ICON_POSITIONS[from];
        const b = ICON_POSITIONS[to];
        // Stagger line appearance
        const lineProgress = lerp(frame, [i * 4, i * 4 + 30], [0, 1]);
        const color = LINE_COLORS[i % LINE_COLORS.length];
        return (
          <DataStreamLine
            key={`${from}-${to}`}
            x1={a.x}
            y1={a.y}
            x2={b.x}
            y2={b.y}
            progress={lineProgress}
            color={color}
            opacity={0.7}
            curved={true}
          />
        );
      })}

      {/* Icons */}
      {ICONS.map((id, i) => {
        const pos = ICON_POSITIONS[id];
        return (
          <div
            key={id}
            style={{
              position: "absolute",
              left: 0,
              top: 0,
              transform: `translateY(${floatY(i)}px)`,
            }}
          >
            <SoftwareIcon id={id} x={pos.x} y={pos.y} opacity={1} scale={1} />
          </div>
        );
      })}

      {/* Caption */}
      <div
        style={{
          position: "absolute",
          bottom: 80,
          left: 0,
          right: 0,
          textAlign: "center",
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
            opacity: lerp(frame, [60, 75], [0, 1]),
          }}
        >
          Jedes Tool erfüllt seine Aufgabe. Doch zusammenarbeiten tun sie selten.
        </p>
      </div>
    </AbsoluteFill>
  );
};

export default Scene02_Complexity;

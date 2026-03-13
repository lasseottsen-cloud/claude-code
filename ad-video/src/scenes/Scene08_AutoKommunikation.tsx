import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { SoftwareIcon } from "../components/SoftwareIcon";
import { DataStreamLine } from "../components/DataStreamLine";
import { ModuleCard } from "../components/ModuleCard";
import { GlowNode } from "../components/GlowNode";
import { COLORS } from "../utils/colors";
import { ICON_POSITIONS, CENTER } from "../utils/layout";
import { lerp, fadeIn } from "../utils/animations";

const PROJ_POS = { x: 960, y: 480 };

// Mini email symbols at various positions
const EMAIL_SOURCES = [
  { x: 250, y: 200 },
  { x: 400, y: 350 },
  { x: 200, y: 500 },
];

export const Scene08_AutoKommunikation: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill
      style={{
        background: "radial-gradient(ellipse at 50% 50%, #05050F 0%, #000000 70%)",
      }}
    >
      {/* Center node */}
      <GlowNode cx={CENTER.x} cy={CENTER.y} scale={0.6} opacity={0.5} />

      {/* Email streams into project card */}
      {EMAIL_SOURCES.map((src, i) => (
        <DataStreamLine
          key={i}
          x1={src.x}
          y1={src.y}
          x2={PROJ_POS.x - 120}
          y2={PROJ_POS.y}
          progress={lerp(frame, [i * 12, i * 12 + 40], [0, 1])}
          color={COLORS.glowPurple}
          width={1.5}
        />
      ))}

      {/* OneDrive stream into project */}
      <DataStreamLine
        x1={ICON_POSITIONS["OneDrive"].x}
        y1={ICON_POSITIONS["OneDrive"].y}
        x2={PROJ_POS.x}
        y2={PROJ_POS.y + 70}
        progress={lerp(frame, [20, 60], [0, 1])}
        color={COLORS.streamBlue}
        width={1.5}
      />

      {/* Email icon */}
      <SoftwareIcon
        id="Email"
        x={ICON_POSITIONS["Email"].x}
        y={ICON_POSITIONS["Email"].y}
        glowing
      />

      {/* OneDrive icon */}
      <SoftwareIcon
        id="OneDrive"
        x={ICON_POSITIONS["OneDrive"].x}
        y={ICON_POSITIONS["OneDrive"].y}
        opacity={0.8}
      />

      {/* Projektverwaltung with auto-sorted items */}
      <ModuleCard
        x={PROJ_POS.x}
        y={PROJ_POS.y}
        title="Projektverwaltung"
        items={["✉ Neue E-Mail → Aufgabe", "📁 Datei angehängt", "🔔 Update gesendet", "📋 Dokument verknüpft"]}
        opacity={lerp(frame, [0, 25], [0, 1])}
        accentColor="#00FFEE"
        width={280}
      />

      <div
        style={{
          position: "absolute",
          bottom: 80,
          left: 0,
          right: 0,
          textAlign: "center",
          opacity: fadeIn(frame, 55, 20),
        }}
      >
        <p style={{ color: COLORS.textSecondary, fontSize: 16, fontFamily: "'Inter', system-ui, sans-serif", letterSpacing: "0.15em", textTransform: "uppercase", margin: 0 }}>
          Dokumente und Kommunikation finden automatisch ihren Platz.
        </p>
      </div>
    </AbsoluteFill>
  );
};

export default Scene08_AutoKommunikation;

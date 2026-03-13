import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { DataStreamLine } from "../components/DataStreamLine";
import { ModuleCard } from "../components/ModuleCard";
import { GlowNode } from "../components/GlowNode";
import { COLORS } from "../utils/colors";
import { CENTER } from "../utils/layout";
import { lerp, fadeIn } from "../utils/animations";

const WARE_POS = { x: 580, y: 400 };
const PROJ_POS = { x: 1100, y: 400 };
const TIME_POS = { x: 1100, y: 680 };

export const Scene07_Projektverwaltung: React.FC = () => {
  const frame = useCurrentFrame();

  const wareOpacity = lerp(frame, [0, 20], [0, 1]);
  const streamProgress = lerp(frame, [15, 55], [0, 1]);
  const projOpacity = lerp(frame, [50, 70], [0, 1]);
  const timeOpacity = lerp(frame, [60, 78], [0, 1]);

  // Connection line between Warenwirtschaft → Projektverwaltung
  const connProgress = lerp(frame, [20, 60], [0, 1]);

  return (
    <AbsoluteFill
      style={{
        background: "radial-gradient(ellipse at 50% 50%, #05050F 0%, #000000 70%)",
      }}
    >
      {/* Center node */}
      <GlowNode cx={CENTER.x} cy={CENTER.y} scale={0.7} opacity={0.6} />

      {/* Warenwirtschaft → Projektverwaltung stream */}
      <DataStreamLine
        x1={WARE_POS.x + 120}
        y1={WARE_POS.y}
        x2={PROJ_POS.x - 120}
        y2={PROJ_POS.y}
        progress={connProgress}
        color={COLORS.streamCyan}
        width={2}
      />

      {/* Projektverwaltung → Zeiterfassung */}
      <DataStreamLine
        x1={PROJ_POS.x}
        y1={PROJ_POS.y + 80}
        x2={TIME_POS.x}
        y2={TIME_POS.y - 70}
        progress={lerp(frame, [55, 80], [0, 1])}
        color={COLORS.glowPurple}
        width={1.5}
      />

      {/* Warenwirtschaft card */}
      <ModuleCard
        x={WARE_POS.x}
        y={WARE_POS.y}
        title="Warenwirtschaft"
        items={["Artikel & Material", "Lagerbestände", "Bestellungen"]}
        opacity={wareOpacity}
        accentColor="#00AAFF"
        width={220}
      />

      {/* Projektverwaltung card */}
      <ModuleCard
        x={PROJ_POS.x}
        y={PROJ_POS.y}
        title="Projektverwaltung"
        items={["Projekte & Aufgaben", "Fortschritt", "Ressourcen", "Meilensteine"]}
        opacity={projOpacity}
        accentColor="#00FFEE"
        width={240}
      />

      {/* Zeiterfassung card */}
      <ModuleCard
        x={TIME_POS.x}
        y={TIME_POS.y}
        title="Zeiterfassung"
        items={["Arbeitszeiten", "Auswertungen"]}
        opacity={timeOpacity}
        accentColor={COLORS.glowPurple}
        width={220}
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
          Projekte werden strukturiert verwaltet.
        </p>
      </div>
    </AbsoluteFill>
  );
};

export default Scene07_Projektverwaltung;

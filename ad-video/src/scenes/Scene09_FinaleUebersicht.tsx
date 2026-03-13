import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { ModuleCard } from "../components/ModuleCard";
import { GlowNode } from "../components/GlowNode";
import { DataStreamLine } from "../components/DataStreamLine";
import { COLORS } from "../utils/colors";
import { CENTER } from "../utils/layout";
import { lerp, fadeIn } from "../utils/animations";

// Dashboard module layout
const MODULES = [
  { x: 380,  y: 300,  title: "Projekte",       items: ["Aktive Projekte", "Aufgaben", "Fortschritt"],      color: "#00AAFF", w: 200 },
  { x: 620,  y: 300,  title: "Material",        items: ["Bestände", "Bestellungen"],                       color: "#00FFEE", w: 200 },
  { x: 860,  y: 300,  title: "Kommunikation",   items: ["E-Mails", "Benachrichtigungen"],                  color: COLORS.glowPurple, w: 200 },
  { x: 1100, y: 300,  title: "Dokumente",        items: ["Dateien", "Verträge", "Pläne"],                  color: "#FF9800", w: 200 },
  { x: 1340, y: 300,  title: "Zeiterfassung",   items: ["Arbeitszeiten", "Auswertungen"],                  color: "#4CAF50", w: 200 },
  { x: 380,  y: 600,  title: "Buchhaltung",      items: ["Rechnungen", "Angebote", "BMD-Sync"],            color: "#E53935", w: 200 },
  { x: 620,  y: 600,  title: "Kalkulation",      items: ["BLS-Import", "Positionen", "Preise"],            color: "#FF6B35", w: 200 },
  { x: 860,  y: 600,  title: "Kundenportal",     items: ["Auftraggeber", "Freigaben"],                     color: "#9C27B0", w: 200 },
  { x: 1100, y: 600,  title: "Berichte",         items: ["Auswertungen", "KPIs"],                          color: "#00BCD4", w: 200 },
  { x: 1340, y: 600,  title: "Einstellungen",    items: ["Nutzer", "Integrationen"],                       color: "#607D8B", w: 200 },
];

export const Scene09_FinaleUebersicht: React.FC = () => {
  const frame = useCurrentFrame();

  // Camera pulls back (scale from 1.2 → 1)
  const scale = lerp(frame, [0, 50], [1.15, 1]);

  return (
    <AbsoluteFill
      style={{
        background: "radial-gradient(ellipse at 50% 50%, #060612 0%, #000000 70%)",
        transformOrigin: `${CENTER.x}px ${CENTER.y}px`,
        transform: `scale(${scale})`,
      }}
    >
      {/* Central glow */}
      <GlowNode cx={CENTER.x} cy={CENTER.y} scale={0.5} opacity={0.4} />

      {/* Connection lines from center to modules */}
      {MODULES.map((m, i) => (
        <DataStreamLine
          key={i}
          x1={CENTER.x}
          y1={CENTER.y}
          x2={m.x}
          y2={m.y}
          progress={1}
          color={m.color}
          opacity={lerp(frame, [i * 3, i * 3 + 20], [0, 0.3])}
          curved={false}
        />
      ))}

      {/* Module cards stagger in */}
      {MODULES.map((m, i) => (
        <ModuleCard
          key={i}
          x={m.x}
          y={m.y}
          title={m.title}
          items={m.items}
          opacity={lerp(frame, [i * 4, i * 4 + 20], [0, 1])}
          scale={lerp(frame, [i * 4, i * 4 + 20], [0.85, 1])}
          accentColor={m.color}
          width={m.w}
        />
      ))}

      <div
        style={{
          position: "absolute",
          bottom: 80,
          left: 0,
          right: 0,
          textAlign: "center",
          opacity: fadeIn(frame, 60, 20),
        }}
      >
        <p style={{ color: COLORS.textSecondary, fontSize: 16, fontFamily: "'Inter', system-ui, sans-serif", letterSpacing: "0.15em", textTransform: "uppercase", margin: 0 }}>
          Aus vielen Programmen wird eine Plattform.
        </p>
      </div>
    </AbsoluteFill>
  );
};

export default Scene09_FinaleUebersicht;

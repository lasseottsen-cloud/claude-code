import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { SoftwareIcon } from "../components/SoftwareIcon";
import { DataStreamLine } from "../components/DataStreamLine";
import { ModuleCard } from "../components/ModuleCard";
import { GlowNode } from "../components/GlowNode";
import { COLORS } from "../utils/colors";
import { ICON_POSITIONS, CENTER } from "../utils/layout";
import { lerp, fadeIn, smoothIn } from "../utils/animations";

// Module position (right side, centered vertically)
const MODULE_POS = { x: 1300, y: 540 };

export const Scene06_OneDriveStream: React.FC = () => {
  const frame = useCurrentFrame();

  const streamProgress = lerp(frame, [5, 50], [0, 1]);
  const moduleOpacity = lerp(frame, [45, 65], [0, 1]);
  const moduleScale = lerp(frame, [45, 65], [0.8, 1]);

  return (
    <AbsoluteFill
      style={{
        background: "radial-gradient(ellipse at 40% 50%, #05050F 0%, #000000 70%)",
      }}
    >
      {/* Central node */}
      <GlowNode cx={CENTER.x} cy={CENTER.y} scale={0.8} opacity={0.8} />

      {/* OneDrive data stream to module */}
      <DataStreamLine
        x1={ICON_POSITIONS["OneDrive"].x}
        y1={ICON_POSITIONS["OneDrive"].y}
        x2={MODULE_POS.x}
        y2={MODULE_POS.y}
        progress={streamProgress}
        color={COLORS.streamCyan}
        width={2}
      />

      {/* OneDrive to center */}
      <DataStreamLine
        x1={ICON_POSITIONS["OneDrive"].x}
        y1={ICON_POSITIONS["OneDrive"].y}
        x2={CENTER.x}
        y2={CENTER.y}
        progress={1}
        color={COLORS.streamBlue}
        opacity={0.4}
        curved={false}
      />

      {/* OneDrive icon highlighted */}
      <SoftwareIcon
        id="OneDrive"
        x={ICON_POSITIONS["OneDrive"].x}
        y={ICON_POSITIONS["OneDrive"].y}
        glowing
      />

      {/* Warenwirtschaft module */}
      <ModuleCard
        x={MODULE_POS.x}
        y={MODULE_POS.y}
        title="Warenwirtschaft"
        items={["Artikel & Material", "Lagerbestände", "Bestellungen", "Lieferanten"]}
        opacity={moduleOpacity}
        scale={moduleScale}
        accentColor="#00AAFF"
        width={240}
      />

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
        <p style={{ color: COLORS.textSecondary, fontSize: 16, fontFamily: "'Inter', system-ui, sans-serif", letterSpacing: "0.15em", textTransform: "uppercase", margin: 0 }}>
          Material wird automatisch organisiert.
        </p>
      </div>
    </AbsoluteFill>
  );
};

export default Scene06_OneDriveStream;

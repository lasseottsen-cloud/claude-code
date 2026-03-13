import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { SoftwareIcon } from "../components/SoftwareIcon";
import { COLORS } from "../utils/colors";
import { ICON_POSITIONS, type IconId } from "../utils/layout";
import { fadeIn, lerp } from "../utils/animations";

const ICONS = Object.keys(ICON_POSITIONS) as IconId[];

export const Scene01_FragmentedWorld: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Slow camera drift — subtle translateX on the whole scene
  const drift = lerp(frame, [0, 90], [0, -18]);

  return (
    <AbsoluteFill
      style={{
        background: "radial-gradient(ellipse at 50% 50%, #050510 0%, #000000 70%)",
        transform: `translateX(${drift}px)`,
      }}
    >
      {/* Title card */}
      <div
        style={{
          position: "absolute",
          bottom: 80,
          left: 0,
          right: 0,
          textAlign: "center",
          opacity: fadeIn(frame, 10, 20),
        }}
      >
        <p
          style={{
            color: COLORS.textSecondary,
            fontSize: 16,
            fontFamily: "'Inter', system-ui, sans-serif",
            letterSpacing: "0.2em",
            textTransform: "uppercase",
            margin: 0,
          }}
        >
          Viele Handwerksbetriebe arbeiten mit einer Vielzahl einzelner Systeme.
        </p>
      </div>

      {/* Icons */}
      {ICONS.map((id, i) => {
        const pos = ICON_POSITIONS[id];
        // Stagger icon appearance
        const iconOpacity = fadeIn(frame, i * 6, 15);
        // Gentle float animation
        const floatY = Math.sin(frame * 0.04 + i * 0.8) * 6;
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
            <SoftwareIcon
              id={id}
              x={pos.x}
              y={pos.y}
              opacity={iconOpacity}
              scale={1}
            />
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

export default Scene01_FragmentedWorld;

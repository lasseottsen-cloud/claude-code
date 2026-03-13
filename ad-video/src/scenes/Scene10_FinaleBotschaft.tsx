import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { COLORS } from "../utils/colors";
import { lerp, fadeIn, fadeOut } from "../utils/animations";

export const Scene10_FinaleBotschaft: React.FC = () => {
  const frame = useCurrentFrame();

  // Subtle glow pulse
  const glowOpacity = 0.3 + Math.sin(frame * 0.08) * 0.1;

  // Text appear
  const line1Opacity = fadeIn(frame, 10, 20);
  const line2Opacity = fadeIn(frame, 30, 20);

  // Final fade to black
  const fadeToBlack = lerp(frame, [72, 89], [0, 1]);

  return (
    <AbsoluteFill
      style={{
        background: "#000000",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {/* Ambient glow */}
      <div
        style={{
          position: "absolute",
          width: 600,
          height: 600,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${COLORS.glowBlue}18 0%, transparent 70%)`,
          opacity: glowOpacity,
          pointerEvents: "none",
        }}
      />

      {/* Horizontal line */}
      <div
        style={{
          width: lerp(frame, [5, 25], [0, 320]),
          height: 1,
          background: `linear-gradient(90deg, transparent, ${COLORS.streamCyan}66, transparent)`,
          marginBottom: 40,
          opacity: fadeIn(frame, 5, 15),
        }}
      />

      {/* Main tagline */}
      <div style={{ opacity: line1Opacity, textAlign: "center" }}>
        <h1
          style={{
            color: COLORS.textPrimary,
            fontSize: 64,
            fontFamily: "'Inter', 'SF Pro Display', system-ui, sans-serif",
            fontWeight: 300,
            letterSpacing: "-0.02em",
            margin: 0,
            lineHeight: 1.1,
          }}
        >
          Ein Betriebssystem
        </h1>
      </div>

      <div style={{ opacity: line2Opacity, textAlign: "center" }}>
        <h1
          style={{
            color: COLORS.textPrimary,
            fontSize: 64,
            fontFamily: "'Inter', 'SF Pro Display', system-ui, sans-serif",
            fontWeight: 700,
            letterSpacing: "-0.02em",
            margin: 0,
            lineHeight: 1.1,
            background: `linear-gradient(90deg, ${COLORS.streamCyan}, ${COLORS.glowBlue})`,
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          für deinen Betrieb.
        </h1>
      </div>

      {/* Subtitle */}
      <div
        style={{
          marginTop: 32,
          opacity: fadeIn(frame, 50, 20) * (1 - lerp(frame, [72, 85], [0, 1])),
        }}
      >
        <p
          style={{
            color: COLORS.textSecondary,
            fontSize: 18,
            fontFamily: "'Inter', system-ui, sans-serif",
            fontWeight: 400,
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            margin: 0,
            textAlign: "center",
          }}
        >
          Übersichtlich · Strukturiert · Für deinen Betrieb gebaut
        </p>
      </div>

      {/* Fade to black overlay */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "#000000",
          opacity: fadeToBlack,
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
};

export default Scene10_FinaleBotschaft;

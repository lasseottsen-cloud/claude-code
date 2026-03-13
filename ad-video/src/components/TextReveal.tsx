import React from "react";
import { interpolate } from "remotion";
import { COLORS } from "../utils/colors";

interface TextRevealProps {
  text: string;
  frame: number;
  startFrame: number;
  style?: React.CSSProperties;
  wordDelay?: number; // frames between each word appearing
  fadeInDuration?: number;
}

export const TextReveal: React.FC<TextRevealProps> = ({
  text,
  frame,
  startFrame,
  style = {},
  wordDelay = 4,
  fadeInDuration = 8,
}) => {
  const words = text.split(" ");
  const localFrame = frame - startFrame;

  return (
    <div
      style={{
        display: "flex",
        flexWrap: "wrap",
        gap: "0.3em",
        justifyContent: "center",
        ...style,
      }}
    >
      {words.map((word, i) => {
        const wordStart = i * wordDelay;
        const opacity = interpolate(
          localFrame,
          [wordStart, wordStart + fadeInDuration],
          [0, 1],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
        );
        const translateY = interpolate(
          localFrame,
          [wordStart, wordStart + fadeInDuration],
          [12, 0],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
        );
        return (
          <span
            key={i}
            style={{
              opacity,
              transform: `translateY(${translateY}px)`,
              display: "inline-block",
              color: COLORS.textPrimary,
              fontFamily: "'Inter', 'SF Pro Display', system-ui, sans-serif",
            }}
          >
            {word}
          </span>
        );
      })}
    </div>
  );
};

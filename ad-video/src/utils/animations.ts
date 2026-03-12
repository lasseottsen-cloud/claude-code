import { interpolate, spring } from "remotion";

export const lerp = (
  frame: number,
  input: [number, number],
  output: [number, number]
) =>
  interpolate(frame, input, output, {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

export const fadeIn = (frame: number, startFrame: number, duration = 15) =>
  lerp(frame, [startFrame, startFrame + duration], [0, 1]);

export const fadeOut = (frame: number, endFrame: number, duration = 15) =>
  lerp(frame, [endFrame - duration, endFrame], [1, 0]);

export const popIn = (
  frame: number,
  fps: number,
  startFrame = 0,
  config: { damping?: number; stiffness?: number; mass?: number } = {}
) =>
  spring({
    fps,
    frame: frame - startFrame,
    config: { damping: 14, stiffness: 180, mass: 1, ...config },
  });

export const smoothIn = (frame: number, fps: number, startFrame = 0) =>
  spring({
    fps,
    frame: frame - startFrame,
    config: { damping: 30, stiffness: 120, mass: 1 },
  });

export const easeInOut = (t: number): number => {
  return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
};

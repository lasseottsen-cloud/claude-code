import React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import Scene01 from "./scenes/Scene01_FragmentedWorld";
import Scene02 from "./scenes/Scene02_Complexity";
import Scene03 from "./scenes/Scene03_ChaosFreeze";
import Scene04 from "./scenes/Scene04_SystemEmerges";
import Scene05 from "./scenes/Scene05_CraftnoteDissolve";
import Scene06 from "./scenes/Scene06_OneDriveStream";
import Scene07 from "./scenes/Scene07_Projektverwaltung";
import Scene08 from "./scenes/Scene08_AutoKommunikation";
import Scene09 from "./scenes/Scene09_FinaleUebersicht";
import Scene10 from "./scenes/Scene10_FinaleBotschaft";

// 10 scenes × 90 frames each = 900 frames @ 30fps = 30 seconds
const SCENE_DURATION = 90;

export const AdVideo: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#000000" }}>
    <Sequence from={0}   durationInFrames={SCENE_DURATION}><Scene01 /></Sequence>
    <Sequence from={90}  durationInFrames={SCENE_DURATION}><Scene02 /></Sequence>
    <Sequence from={180} durationInFrames={SCENE_DURATION}><Scene03 /></Sequence>
    <Sequence from={270} durationInFrames={SCENE_DURATION}><Scene04 /></Sequence>
    <Sequence from={360} durationInFrames={SCENE_DURATION}><Scene05 /></Sequence>
    <Sequence from={450} durationInFrames={SCENE_DURATION}><Scene06 /></Sequence>
    <Sequence from={540} durationInFrames={SCENE_DURATION}><Scene07 /></Sequence>
    <Sequence from={630} durationInFrames={SCENE_DURATION}><Scene08 /></Sequence>
    <Sequence from={720} durationInFrames={SCENE_DURATION}><Scene09 /></Sequence>
    <Sequence from={810} durationInFrames={SCENE_DURATION}><Scene10 /></Sequence>
  </AbsoluteFill>
);

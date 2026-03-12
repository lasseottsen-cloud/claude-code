import React from "react";
import { Composition } from "remotion";
import { AdVideo } from "./AdVideo";

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="AdVideo"
      component={AdVideo}
      durationInFrames={900}
      fps={30}
      width={1920}
      height={1080}
    />
  </>
);

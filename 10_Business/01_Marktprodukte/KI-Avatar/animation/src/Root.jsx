import React from 'react';
import {Composition} from 'remotion';
import {CheckerVideo, TIMING} from './CheckerVideo.jsx';
import beispiel from './data/beispiel-dossier.json';

// Gesamtdauer hängt von der Anzahl Warnsignale im Dossier ab —
// calculateMetadata liest die tatsächlichen Props (auch bei --props=datei.json).
const dauerLong = ({props}) => ({
  durationInFrames:
    TIMING.long.intro +
    props.warnsignale.length * TIMING.long.signal +
    TIMING.long.score +
    TIMING.long.outro,
});

const dauerShort = () => ({
  durationInFrames:
    TIMING.short.intro + TIMING.short.signal + TIMING.short.score + TIMING.short.outro,
});

export const Root = () => (
  <>
    <Composition
      id="CheckerLong"
      component={CheckerVideo}
      width={1920}
      height={1080}
      fps={30}
      defaultProps={{...beispiel, variante: 'long'}}
      calculateMetadata={dauerLong}
    />
    <Composition
      id="CheckerShort"
      component={CheckerVideo}
      width={1080}
      height={1920}
      fps={30}
      defaultProps={{...beispiel, variante: 'short'}}
      calculateMetadata={dauerShort}
    />
  </>
);

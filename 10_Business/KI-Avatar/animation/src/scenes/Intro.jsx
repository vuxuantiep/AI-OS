import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {THEME} from '../theme.js';
import {FadeUp, Hintergrund} from './Bausteine.jsx';

export const Intro = ({titel, anbieter, claim, kompakt = false}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const logoPop = spring({frame, fps, config: {damping: 12}});
  const s = kompakt ? 0.82 : 1; // Short-Variante etwas kompakter

  return (
    <Hintergrund>
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', padding: 80, textAlign: 'center'}}>
        <div style={{transform: `scale(${logoPop})`, fontSize: 110 * s}}>🛡️</div>
        <FadeUp delay={8}>
          <div style={{fontSize: 54 * s, fontWeight: 800, letterSpacing: 3, color: THEME.teal}}>
            AI BUSINESS CHECKER
          </div>
          <div style={{fontSize: 30 * s, color: THEME.muted, marginTop: 8}}>
            Wir prüfen, bevor du zahlst.
          </div>
        </FadeUp>
        <FadeUp delay={30} style={{marginTop: 60 * s, maxWidth: 1400}}>
          <div style={{fontSize: 58 * s, fontWeight: 700, lineHeight: 1.25}}>{titel}</div>
        </FadeUp>
        <FadeUp delay={50} style={{marginTop: 40 * s}}>
          <div
            style={{
              background: THEME.bgCard,
              border: `1px solid ${THEME.line}`,
              borderRadius: 16,
              padding: `${22 * s}px ${40 * s}px`,
              fontSize: 34 * s,
              color: THEME.amber,
              fontStyle: 'italic',
              maxWidth: 1300,
            }}
          >
            Das Versprechen: „{claim}“
          </div>
          <div style={{fontSize: 26 * s, color: THEME.muted, marginTop: 16}}>
            Geprüfter Anbieter: {anbieter}
          </div>
        </FadeUp>
      </AbsoluteFill>
    </Hintergrund>
  );
};

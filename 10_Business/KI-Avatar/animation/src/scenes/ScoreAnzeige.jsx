import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {THEME, scoreColor, scoreLabel} from '../theme.js';
import {FadeUp, Hintergrund} from './Bausteine.jsx';

export const ScoreAnzeige = ({score, einschaetzung, kompakt = false}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  // Score zählt in den ersten 2 Sekunden animiert hoch
  const angezeigt = interpolate(frame, [10, 10 + fps * 2], [0, score], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const farbe = scoreColor(score);
  const s = kompakt ? 0.85 : 1;
  const balkenBreite = interpolate(angezeigt, [0, 10], [0, 100]);

  return (
    <Hintergrund>
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', padding: 90}}>
        <FadeUp>
          <div style={{fontSize: 34 * s, color: THEME.muted, letterSpacing: 3, textAlign: 'center'}}>
            UNSER RISIKO-SCORE
          </div>
        </FadeUp>
        <div style={{fontSize: 190 * s, fontWeight: 800, color: farbe, lineHeight: 1.1}}>
          {angezeigt.toFixed(1)}
          <span style={{fontSize: 70 * s, color: THEME.muted}}> / 10</span>
        </div>
        <div style={{width: 1100 * s, height: 26 * s, background: THEME.bgCard, borderRadius: 13, overflow: 'hidden', border: `1px solid ${THEME.line}`}}>
          <div style={{width: `${balkenBreite}%`, height: '100%', background: farbe}} />
        </div>
        <div style={{fontSize: 46 * s, fontWeight: 800, color: farbe, marginTop: 30 * s, letterSpacing: 2}}>
          {scoreLabel(score)}
        </div>
        <FadeUp delay={fps * 2} style={{marginTop: 44 * s, maxWidth: 1350}}>
          <div style={{fontSize: 38 * s, textAlign: 'center', lineHeight: 1.45, color: THEME.ink}}>
            {einschaetzung}
          </div>
          <div style={{fontSize: 24 * s, textAlign: 'center', color: THEME.muted, marginTop: 18}}>
            Einschätzung des AI Business Checker — Meinungsäußerung auf Basis der gezeigten Belege.
          </div>
        </FadeUp>
      </AbsoluteFill>
    </Hintergrund>
  );
};

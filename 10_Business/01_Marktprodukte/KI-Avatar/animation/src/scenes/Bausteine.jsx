import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {THEME} from '../theme.js';

// Pflicht-Label nach Art. 50 EU-KI-VO: ab Frame 0 dauerhaft sichtbar.
export const KiLabel = () => (
  <div
    style={{
      position: 'absolute',
      top: 24,
      right: 28,
      background: 'rgba(14, 23, 38, 0.85)',
      border: `1px solid ${THEME.line}`,
      color: THEME.muted,
      fontFamily: THEME.font,
      fontSize: 22,
      padding: '8px 16px',
      borderRadius: 10,
      zIndex: 50,
    }}
  >
    🤖 KI-generierte Stimme &amp; Animation
  </div>
);

// Durchlaufende Quellenleiste unten — Glaubwürdigkeits-Baustein Nr. 1.
export const QuellenLeiste = ({text}) => (
  <div
    style={{
      position: 'absolute',
      bottom: 0,
      left: 0,
      right: 0,
      background: 'rgba(14, 23, 38, 0.92)',
      borderTop: `1px solid ${THEME.line}`,
      color: THEME.muted,
      fontFamily: THEME.font,
      fontSize: 24,
      padding: '14px 32px',
      zIndex: 40,
    }}
  >
    📎 Quelle: {text}
  </div>
);

// Weiche Einblendung von unten — Standard-Enter-Animation aller Szenen.
export const FadeUp = ({children, delay = 0, style}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const progress = spring({frame: frame - delay, fps, config: {damping: 200}});
  return (
    <div
      style={{
        opacity: progress,
        transform: `translateY(${interpolate(progress, [0, 1], [40, 0])}px)`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

export const Hintergrund = ({children}) => (
  <AbsoluteFill
    style={{
      background: `radial-gradient(ellipse at 30% 20%, #16233a 0%, ${THEME.bg} 65%)`,
      fontFamily: THEME.font,
      color: THEME.ink,
    }}
  >
    {children}
  </AbsoluteFill>
);

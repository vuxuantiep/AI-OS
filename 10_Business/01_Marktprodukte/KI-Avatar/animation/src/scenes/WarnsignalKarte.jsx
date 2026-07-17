import React from 'react';
import {AbsoluteFill, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {THEME} from '../theme.js';
import {FadeUp, Hintergrund, QuellenLeiste} from './Bausteine.jsx';

export const WarnsignalKarte = ({signal, index, total, kompakt = false}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const badgePop = spring({frame: frame - 5, fps, config: {damping: 10}});
  const s = kompakt ? 0.85 : 1;

  return (
    <Hintergrund>
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', padding: 90}}>
        <FadeUp>
          <div style={{fontSize: 30 * s, color: THEME.muted, textAlign: 'center', letterSpacing: 2}}>
            WARNSIGNAL {index + 1} VON {total}
          </div>
        </FadeUp>
        <div
          style={{
            transform: `scale(${badgePop})`,
            background: THEME.coral,
            color: '#fff',
            borderRadius: 24,
            padding: `${16 * s}px ${44 * s}px`,
            fontSize: 56 * s,
            fontWeight: 800,
            marginTop: 28 * s,
          }}
        >
          ⚠️ {signal.code} · {signal.name}
        </div>
        <FadeUp delay={22} style={{marginTop: 52 * s, maxWidth: 1450}}>
          <div
            style={{
              background: THEME.bgCard,
              border: `2px solid ${THEME.coral}`,
              borderRadius: 20,
              padding: `${36 * s}px ${48 * s}px`,
              fontSize: 42 * s,
              lineHeight: 1.4,
              textAlign: 'center',
            }}
          >
            {signal.zitat}
          </div>
        </FadeUp>
      </AbsoluteFill>
      <QuellenLeiste text={signal.quelle} />
    </Hintergrund>
  );
};

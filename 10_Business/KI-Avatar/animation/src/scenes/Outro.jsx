import React from 'react';
import {AbsoluteFill} from 'remotion';
import {THEME} from '../theme.js';
import {FadeUp, Hintergrund} from './Bausteine.jsx';

const CHECKLISTE = [
  'Impressum & Firma im Register prüfen',
  'Nach „[Anbieter] + Erfahrungen“ suchen',
  'Nie für „Gewinn-Freischaltung“ zahlen',
];

export const Outro = ({stellungnahme, datum, kompakt = false}) => {
  const s = kompakt ? 0.82 : 1;
  return (
    <Hintergrund>
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', padding: 90}}>
        <FadeUp>
          <div style={{fontSize: 48 * s, fontWeight: 800, color: THEME.teal, textAlign: 'center'}}>
            ✅ Deine 3-Punkte-Schnellprüfung
          </div>
        </FadeUp>
        <div style={{marginTop: 40 * s}}>
          {CHECKLISTE.map((punkt, i) => (
            <FadeUp key={punkt} delay={15 + i * 12}>
              <div
                style={{
                  background: THEME.bgCard,
                  border: `1px solid ${THEME.line}`,
                  borderRadius: 14,
                  padding: `${18 * s}px ${34 * s}px`,
                  fontSize: 36 * s,
                  marginBottom: 18 * s,
                  minWidth: 900 * s,
                }}
              >
                {i + 1}. {punkt}
              </div>
            </FadeUp>
          ))}
        </div>
        <FadeUp delay={60} style={{marginTop: 30 * s, maxWidth: 1350, textAlign: 'center'}}>
          <div style={{fontSize: 26 * s, color: THEME.muted, lineHeight: 1.5}}>
            {stellungnahme} · Alle Quellen in der Videobeschreibung · Stand: {datum}
          </div>
          <div style={{fontSize: 34 * s, color: THEME.ink, marginTop: 22, fontWeight: 700}}>
            🔔 Abonnieren für die nächste Prüfung — bevor du zahlst.
          </div>
        </FadeUp>
      </AbsoluteFill>
    </Hintergrund>
  );
};

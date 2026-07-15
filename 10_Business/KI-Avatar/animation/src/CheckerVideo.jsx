import React from 'react';
import {Series} from 'remotion';
import {Intro} from './scenes/Intro.jsx';
import {WarnsignalKarte} from './scenes/WarnsignalKarte.jsx';
import {ScoreAnzeige} from './scenes/ScoreAnzeige.jsx';
import {Outro} from './scenes/Outro.jsx';
import {KiLabel} from './scenes/Bausteine.jsx';

// Szenen-Längen in Frames (30 fps) — auch von Root.jsx für die
// Gesamtdauer-Berechnung importiert. Eine Quelle der Wahrheit.
export const TIMING = {
  long: {intro: 120, signal: 180, score: 150, outro: 150},
  short: {intro: 75, signal: 150, score: 105, outro: 90},
};

// Ein Template für beide Formate: `variante` steuert Timing + Kompaktheit,
// alles Inhaltliche kommt aus dem Dossier-JSON (props).
export const CheckerVideo = ({
  titel,
  anbieter,
  claim,
  warnsignale,
  score,
  einschaetzung,
  stellungnahme,
  datum,
  variante = 'long',
}) => {
  const t = TIMING[variante];
  const kompakt = variante === 'short';
  const signale = kompakt ? warnsignale.slice(0, 1) : warnsignale;

  return (
    <>
      <Series>
        <Series.Sequence durationInFrames={t.intro}>
          <Intro titel={titel} anbieter={anbieter} claim={claim} kompakt={kompakt} />
        </Series.Sequence>
        {signale.map((signal, i) => (
          <Series.Sequence key={signal.code} durationInFrames={t.signal}>
            <WarnsignalKarte signal={signal} index={i} total={signale.length} kompakt={kompakt} />
          </Series.Sequence>
        ))}
        <Series.Sequence durationInFrames={t.score}>
          <ScoreAnzeige score={score} einschaetzung={einschaetzung} kompakt={kompakt} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={t.outro}>
          <Outro stellungnahme={stellungnahme} datum={datum} kompakt={kompakt} />
        </Series.Sequence>
      </Series>
      <KiLabel />
    </>
  );
};

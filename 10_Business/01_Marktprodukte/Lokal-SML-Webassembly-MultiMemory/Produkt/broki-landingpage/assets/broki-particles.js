// =============================================================================
// Broki AI — Partikel-Netzwerk-Hintergrund (Constellation-Effekt)
//
// Self-contained Canvas-Animation, KEINE Fremd-Library (kein particles.js/jQuery)
// — damit CSP-konform für die MV3-Extension UND passend zur „keine Cloud"-Botschaft.
// Verbundene, langsam driftende Punkte + Linien zwischen nahen Punkten,
// im Broki-Corporate-Grün. Reagiert dezent auf die Maus.
//
// Performance-Regeln (die CPU gehört dem LLM, nicht der Deko):
//   • requestAnimationFrame, pausiert wenn Tab unsichtbar (document.hidden)
//   • respektiert prefers-reduced-motion (dann statisch/aus)
//   • Partikelzahl skaliert mit Bildschirmfläche, gedeckelt
//   • devicePixelRatio-bewusst (scharf auf Retina, ohne Overdraw)
//
// Nutzung:  <canvas id="broki-bg"></canvas>
//           <script src="assets/broki-particles.js"></script>
//           BrokiParticles.init("broki-bg");   // optionale Config als 2. Arg
// =============================================================================

(function (global) {
  "use strict";

  const DEFAULTS = {
    partikelFarbe: "rgba(180, 200, 190, 0.55)", // dezente helle Punkte
    linienFarbe:   "0, 199, 88",                // Broki-Grün #00c758 (als RGB für rgba())
    dichte:        11000,   // 1 Partikel je X Pixel Fläche (kleiner = mehr Punkte)
    maxPartikel:   140,
    maxDistanz:    140,     // px: bis hierhin werden Linien gezogen
    tempo:         0.18,    // Driftgeschwindigkeit
    mausRadius:    170,     // px: Einflussbereich des Cursors
    punktGroesse:  1.6
  };

  function BrokiParticles(canvasId, userCfg) {
    const cfg = Object.assign({}, DEFAULTS, userCfg || {});
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext("2d", { alpha: true });

    const reduce = global.matchMedia &&
      global.matchMedia("(prefers-reduced-motion: reduce)").matches;

    let dpr = Math.min(global.devicePixelRatio || 1, 2);
    let w = 0, h = 0;
    let partikel = [];
    const maus = { x: -9999, y: -9999 };
    let laufid = null;

    function groesseSetzen() {
      dpr = Math.min(global.devicePixelRatio || 1, 2);
      w = canvas.clientWidth;
      h = canvas.clientHeight;
      canvas.width = Math.floor(w * dpr);
      canvas.height = Math.floor(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const anzahl = Math.min(cfg.maxPartikel, Math.floor((w * h) / cfg.dichte));
      partikel = [];
      for (let i = 0; i < anzahl; i++) {
        partikel.push({
          x: Math.random() * w,
          y: Math.random() * h,
          vx: (Math.random() - 0.5) * cfg.tempo,
          vy: (Math.random() - 0.5) * cfg.tempo
        });
      }
    }

    function schritt() {
      ctx.clearRect(0, 0, w, h);

      for (const p of partikel) {
        p.x += p.vx;
        p.y += p.vy;
        // an den Rändern sanft abprallen
        if (p.x < 0 || p.x > w) p.vx *= -1;
        if (p.y < 0 || p.y > h) p.vy *= -1;

        // dezente Cursor-Anziehung
        const dxm = p.x - maus.x, dym = p.y - maus.y;
        const dm = Math.hypot(dxm, dym);
        if (dm < cfg.mausRadius) {
          const kraft = (cfg.mausRadius - dm) / cfg.mausRadius * 0.03;
          p.x += (dxm / dm) * kraft * cfg.mausRadius * 0.05;
          p.y += (dym / dm) * kraft * cfg.mausRadius * 0.05;
        }

        ctx.beginPath();
        ctx.arc(p.x, p.y, cfg.punktGroesse, 0, Math.PI * 2);
        ctx.fillStyle = cfg.partikelFarbe;
        ctx.fill();
      }

      // Linien zwischen nahen Punkten (inkl. Linie zum Cursor)
      for (let i = 0; i < partikel.length; i++) {
        for (let j = i + 1; j < partikel.length; j++) {
          const a = partikel[i], b = partikel[j];
          const d = Math.hypot(a.x - b.x, a.y - b.y);
          if (d < cfg.maxDistanz) {
            const alpha = (1 - d / cfg.maxDistanz) * 0.5;
            ctx.strokeStyle = `rgba(${cfg.linienFarbe}, ${alpha})`;
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
          }
        }
        // Linie Partikel ↔ Cursor (macht die Interaktion sichtbar)
        const dc = Math.hypot(partikel[i].x - maus.x, partikel[i].y - maus.y);
        if (dc < cfg.maxDistanz) {
          const alpha = (1 - dc / cfg.maxDistanz) * 0.7;
          ctx.strokeStyle = `rgba(${cfg.linienFarbe}, ${alpha})`;
          ctx.beginPath();
          ctx.moveTo(partikel[i].x, partikel[i].y);
          ctx.lineTo(maus.x, maus.y);
          ctx.stroke();
        }
      }

      laufid = global.requestAnimationFrame(schritt);
    }

    function starten() {
      if (laufid) return;
      if (reduce) { schritt(); return; }        // 1 statisches Bild, keine Animation
      laufid = global.requestAnimationFrame(schritt);
    }
    function stoppen() {
      if (laufid) { global.cancelAnimationFrame(laufid); laufid = null; }
    }

    // Tab unsichtbar → Animation aus (spart CPU/Akku)
    document.addEventListener("visibilitychange", () =>
      document.hidden ? stoppen() : starten());
    global.addEventListener("resize", groesseSetzen);
    global.addEventListener("mousemove", (e) => {
      const r = canvas.getBoundingClientRect();
      maus.x = e.clientX - r.left;
      maus.y = e.clientY - r.top;
    });
    global.addEventListener("mouseout", () => { maus.x = -9999; maus.y = -9999; });

    groesseSetzen();
    starten();
    return { starten, stoppen, groesseSetzen };
  }

  global.BrokiParticles = { init: BrokiParticles, DEFAULTS };
})(window);

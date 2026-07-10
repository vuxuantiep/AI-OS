# Hermes Desktop ↔ Self-Hosted Server — Setup-Prompt

**So benutzt du das:** Öffne **Claude Code oder Codex** (oder ein anderes agentisches CLI) **auf dem Server, auf dem dein Hermes-Docker-Container läuft** — nicht auf deinem Laptop. Kopiere dann alles unter der Linie in den Prompt. Claude führt dich durch den Rest, führt die Server-Befehle selbst aus und sagt dir genau, was du an deinem eigenen Gerät (Tailscale-App, Hermes-Desktop-App) tun musst.

> Voraussetzungen, die du bereithalten solltest:
> - SSH-/Terminal-Zugang zum Server, auf dem Hermes im Docker-Container läuft (dort läuft auch Claude Code).
> - Ein kostenloses **Tailscale**-Konto: <https://login.tailscale.com> — und ein **Auth-Key** aus <https://login.tailscale.com/admin/settings/keys> (Typ *Reusable*, gern *Ephemeral: off*).
> - Die **Hermes Desktop App** auf deinem PC/Mac: (aus deiner Hermes-Bezugsquelle) + **Tailscale** auf demselben Gerät.

---

Du hilfst mir, meinen selbst-gehosteten **Hermes-Agenten** (läuft in einem Docker-Container auf diesem Server) mit der **Hermes Desktop App** auf meinen persönlichen Geräten zu verbinden — **privat über Tailscale** und mit **Passwort-Login**. Arbeite in klar getrennten Phasen, führe die Server-Befehle selbst aus, fasse nach jeder Phase kurz das Ergebnis zusammen und frag mich, bevor du etwas Unumkehrbares tust. Maskiere Secrets in deiner Ausgabe.

## Ziel-Architektur (bitte verstehen, bevor du loslegst)
- `hermes dashboard` (Standard-Port **9119**) ist der einzige Netzwerk-Gateway, mit dem sich die Desktop-App verbindet — nicht der Agent-Port selbst.
- Das Dashboard zeigt **API-Keys, Config und Sessions** an → es darf **niemals offen ins Internet** (kein Traefik-Label, kein öffentliches Port-Mapping, keine öffentliche Domain).
- Deshalb: ein **Tailscale-Sidecar-Container**. Das Dashboard teilt sich dessen Netzwerk-Namespace (`network_mode: service:tailscale`) und ist damit **nur im Tailnet** erreichbar — als privater Hostname wie `hermes-dashboard`, von allen meinen Geräten, ohne Terminal, dauerhaft.
- Ab **Hermes v0.18** verlangt jeder Nicht-Loopback-Bind einen **echten Auth-Provider** (Passwort oder OAuth). Wir nutzen **Passwort** (`basic`-Provider). `--insecure` ist ab v0.18 wirkungslos (No-Op) und wird nicht mehr benutzt.

## Wichtige, empirisch verifizierte Stolperfallen (beachte sie proaktiv)
1. **Version prüfen.** Passwort-Auth (`basic`) gibt es erst ab **v0.18**. Ältere Versionen (z. B. v0.15) haben nur einen rotierenden Session-Token und einen kaputten Remote-Chat. Wenn die Desktop-App **neuer** als der Server ist, scheitert der Auth-Handshake (App schickt u. U. die URL statt Token, viele 401er). ⇒ Server muss **≥ v0.18 und ≥ App-Version** sein. Notfalls Image aktualisieren.
2. **Passwort-Hash NICHT in `.env`.** Der scrypt-Hash enthält `$`-Zeichen, die docker-compose als Variablen interpoliert und den Hash zerstört (Warnung „variable is not set"). ⇒ In `.env` die **Klartext**-Variable `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` benutzen (oder den Hash ausschließlich in `config.yaml`, die wird nicht interpoliert).
3. **Session-Secret fest setzen** (`HERMES_DASHBOARD_BASIC_AUTH_SECRET`, z. B. `openssl rand -hex 32`), sonst wird jeder bei jedem Container-Neustart ausgeloggt.
4. **`--tui` im Dashboard-Command behalten**, sonst kommt kein Chat-WebSocket zustande.
5. **Server-spezifische Änderungen gehören in `docker-compose.override.yml`**, niemals in die vom Repo/Provider gelieferte `docker-compose.yml`. Vor jeder Änderung Backup der betroffenen Datei; vor einem Image-Update das alte Image als Rollback-Tag sichern.
6. **MagicDNS** muss im Tailnet aktiv sein, damit der Kurzname (`hermes-dashboard`) auf den Geräten auflöst (Admin-Konsole → DNS → MagicDNS aktivieren). Sonst die `100.x.y.z`-Tailscale-IP verwenden.

---

## Phase 0 — Recon (nur lesen, nichts ändern)
Finde und berichte:
- Das Verzeichnis mit der `docker-compose.yml` des Hermes-Agenten und ob bereits eine `docker-compose.override.yml` existiert.
- Den laufenden Agent-Container, sein Image und die **Hermes-Version** (`docker exec <agent> hermes --version`, ggf. mit `gosu hermes`).
- Wie der Agent-Container startet (User/Entrypoint/Datenpfad wie `/opt/data`), damit du den Dashboard-Service exakt dazu passend baust.
- Ob schon ein Tailscale-Sidecar / Dashboard-Service existiert (dann anpassen statt neu anlegen).
Danach: kurze Ist-Zustand-Zusammenfassung + Plan, dann auf mein OK warten.

## Phase 1 — Version sicherstellen (≥ v0.18)
Wenn die Version < v0.18 ist ODER älter als meine Desktop-App:
- Sag mir, welche App-Version ich habe (steht in der App bzw. im App-Log als `Hermes/<version>`).
- Tagge zuerst das laufende Image als Rollback (`docker tag <alte-image-id> <name>:rollback-<version>`).
- `docker pull` das aktuelle Image, prüfe die Version in einem **Wegwerf-Container** (`docker run --rm --entrypoint sh <image> -c "hermes --version"`), bevor du irgendetwas neu startest.
- Erst nach meinem OK die Container mit dem neuen Image neu erstellen. Weise mich darauf hin, dass v0.18 `--insecure` abschafft (⇒ wir richten gleich Passwort-Auth ein) und dass ein alter rotierender Token damit entfällt.

## Phase 2 — Tailscale-Sidecar + Dashboard-Service (in `docker-compose.override.yml`)
Frag mich nach meinem **Tailscale Auth-Key** und lege ihn als `TS_AUTHKEY` in `.env` ab (nicht in eine committede Datei, nicht in die Ausgabe echoen). Ergänze in der **override**-Datei (Werte an das reale Setup aus Phase 0 anpassen — Image, Datenpfad, User):

```yaml
services:
  tailscale:
    image: tailscale/tailscale:latest
    container_name: hermes-dashboard-tailscale
    hostname: hermes-dashboard          # <- Name, unter dem das Dashboard im Tailnet erscheint
    environment:
      TS_AUTHKEY: ${TS_AUTHKEY}
      TS_STATE_DIR: /var/lib/tailscale
      TS_HOSTNAME: hermes-dashboard
      TS_USERSPACE: "false"
    volumes:
      - ./tailscale-state:/var/lib/tailscale
    devices:
      - /dev/net/tun:/dev/net/tun
    cap_add: [net_admin, sys_module]
    restart: unless-stopped

  hermes-dashboard:
    image: <DASSELBE_IMAGE_WIE_DER_AGENT>
    container_name: hermes-dashboard
    restart: unless-stopped
    network_mode: "service:tailscale"    # <- teilt den Tailnet-Namespace, KEIN eigenes port-mapping, KEIN traefik-label
    depends_on: [tailscale]
    env_file: [.env]
    volumes:
      - ./data:/opt/data                 # <- SELBER Datenpfad wie der Agent (gemeinsame Config/Keys/Sessions)
    entrypoint: ["/bin/sh", "-c"]
    command:
      - |
        chown -R hermes:hermes /opt/data 2>/dev/null || true
        exec gosu hermes hermes dashboard \
          --host=0.0.0.0 --port=9119 \
          --no-open --skip-build --tui
```
Erkläre mir dabei kurz, warum es KEIN Port-Mapping und KEIN Traefik-Label gibt (= nur übers Tailnet erreichbar). Passe `gosu hermes` / Pfade an, falls mein Image anders gebaut ist.

## Phase 3 — Passwort-Auth setzen (v0.18 `basic`-Provider, via `.env`)
- Frag mich nach einem Wunsch-Passwort **oder** generiere ein starkes und zeig es mir (ich kann es später ändern).
- Backup der `.env`. Dann diese Variablen in `.env` ergänzen (Klartext-Passwort wegen der `$`-Stolperfalle, siehe oben):
  ```
  HERMES_DASHBOARD_BASIC_AUTH_USERNAME=<username>
  HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=<klartext-passwort>
  HERMES_DASHBOARD_BASIC_AUTH_SECRET=<openssl rand -hex 32>
  ```
- `docker compose config` laufen lassen und sicherstellen, dass **keine** „variable is not set"-Warnung erscheint (sonst steckt doch ein `$` im Wert).

## Phase 4 — Starten & serverseitig verifizieren
- `docker compose up -d` und prüfen:
  - Sidecar ist im Tailnet: `docker exec hermes-dashboard-tailscale tailscale status` zeigt den Hostnamen; IP mit `tailscale ip -4`.
  - Dashboard bindet: im Log `HERMES_DASHBOARD_READY port=9119` und **keine** „Refusing to bind"-Meldung.
  - Login funktioniert (vom Server aus, gegen die Bridge-IP des Sidecars):
    - Provider-Check: `GET /api/auth/providers` → enthält `"name":"basic"`.
    - `POST /auth/password-login` mit JSON `{"provider":"basic","username":"<user>","password":"<pw>","next":"/"}` → **200** + `set-cookie: hermes_session_at=…`. Falsches Passwort → **401**.
- MagicDNS im Tailnet aktiv? Falls nicht, weise mich hin, es in der Tailscale-Admin-Konsole (DNS → MagicDNS) zu aktivieren, oder gib mir die `100.x`-IP als Alternative.
- Berichte mir am Ende **kompakt**: Remote-URL, Username, Passwort.

## Phase 5 — Mein Gerät verbinden (führe mich Schritt für Schritt)
1. **Tailscale auf meinem Gerät** installieren (<https://tailscale.com/download>) und mit **demselben** Tailscale-Konto anmelden. Einmalig — läuft danach im Hintergrund bei jedem Start. Prüfen: der Server-Host (`hermes-dashboard`) taucht in meiner Geräteliste auf.
2. **Hermes Desktop App** öffnen → **Settings → Gateway → Remote connection** (Bezeichnung kann je nach App-Version leicht variieren) und eintragen:
   - **Remote URL:** `http://hermes-dashboard:9119`  (falls der Name nicht auflöst: `http://<tailscale-ip>:9119`)
   - **Username:** `<user>`
   - **Passwort:** `<pw>`
3. Verbinden. **Erfolg =** Dashboard lädt **und** ich kann tatsächlich **chatten** (nicht nur „connected"). Lass mich beides bestätigen.

## Phase 6 — Troubleshooting (nutze das, wenn etwas klemmt)
- **Reset-Schleife / „connected" aber kein Chat, viele 401:** Server-Version < App-Version → zurück zu Phase 1 (Server updaten).
- **Name löst nicht auf:** MagicDNS aus → aktivieren oder `100.x`-IP nutzen. Tailscale auf dem Gerät wirklich verbunden?
- **„Refusing to bind … no auth providers":** `basic`-Env-Vars fehlen/falsch → Phase 3; `docker compose config` auf `$`-Warnung prüfen.
- **Login 401 trotz richtigem Passwort:** Der `$`-Hash-Fehler (Phase 3, Stolperfalle 2) — auf Klartext-`PASSWORD`-Var umstellen und Container neu erstellen.
- **Chat-WS bricht ab:** `--tui` fehlt im Dashboard-Command → Phase 2.
- **Dashboard aus Versehen öffentlich erreichbar:** sofort jedes Port-Mapping/Traefik-Label am Dashboard-Service entfernen — es darf ausschließlich über `network_mode: service:tailscale` laufen.

Wenn alles steht, gib mir eine kurze Zusammenfassung: URL, Username, Passwort, und den Hinweis, dass ich mich künftig **einfach durch Öffnen der App** (bei laufendem Tailscale) verbinde — kein Terminal, kein rotierender Token.

#!/usr/bin/env bash
# Installation auf dem Raspberry Pi 4 (Raspberry Pi OS / Debian). Aufruf im Projektordner:
#   sudo ./install_pi.sh <linux-benutzer>
set -euo pipefail
BENUTZER="${1:-${SUDO_USER:-pi}}"
ZIEL=/opt/tagesimpuls

apt-get install -y python3-venv alsa-utils >/dev/null
mkdir -p "$ZIEL"
cp -r tagesimpuls daten requirements.txt "$ZIEL"/
[ -f .env ] && cp .env "$ZIEL"/.env && chmod 600 "$ZIEL"/.env
chown -R "$BENUTZER": "$ZIEL"
sudo -u "$BENUTZER" python3 -m venv "$ZIEL/.venv"
sudo -u "$BENUTZER" "$ZIEL/.venv/bin/pip" install -q -r "$ZIEL/requirements.txt"
# Benutzer darf Ton ausgeben
usermod -aG audio "$BENUTZER"

for teil in impuls wecker finanz; do
  sed "s/%i/$BENUTZER/" "systemd/tagesimpuls-$teil.service" > "/etc/systemd/system/tagesimpuls-$teil.service"
  cp "systemd/tagesimpuls-$teil.timer" /etc/systemd/system/
done
systemctl daemon-reload
systemctl enable --now tagesimpuls-impuls.timer tagesimpuls-finanz.timer
if grep -q '^GOOGLE_SA_DATEI=.\+' "$ZIEL/.env" 2>/dev/null; then
  systemctl enable --now tagesimpuls-wecker.timer
else
  echo "Hinweis: Wecker-Timer erst nach Google-Einrichtung aktivieren: sudo systemctl enable --now tagesimpuls-wecker.timer"
fi
systemctl list-timers 'tagesimpuls-*' --no-pager
echo "Test: cd $ZIEL && sudo -u $BENUTZER .venv/bin/python -m tagesimpuls test-push"

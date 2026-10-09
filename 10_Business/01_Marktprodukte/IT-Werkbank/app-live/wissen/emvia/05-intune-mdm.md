# FAQ EMVIA: Intune und MDM

## Wie kommt ein neuer Windows-PC in Intune?
Am saubersten über Windows Autopilot: Hardware-Hash erfassen (Vorlage "Autopilot: Hardware-Hash"), in Intune importieren (Geräte > Windows > Registrierung > Geräte), Gruppen-Tag/Profil zuweisen. Danach meldet sich der Benutzer beim Auspacken mit dem Firmenkonto an. Voraussetzung: automatische MDM-Registrierung ist für die Benutzer aktiviert (Intune > Geräte > Registrierung > Automatische Registrierung).

## Wie kommen iPhones und iPads rein?
Firmengeräte über Apple Business Manager mit automatischer Geräteregistrierung (ADE): Die Geräte werden beim Kauf dem Tenant zugeordnet und sind nach dem Zurücksetzen sofort verwaltet. Wichtig: Das Apple-MDM-Push-Zertifikat und das ABM-Token laufen jährlich ab. Rechtzeitig verlängern, und zwar mit derselben Apple-ID. Sonst verliert man die Verwaltung aller Apple-Geräte.

## Wie kommen Android-Geräte rein?
Über Android Enterprise (verknüpftes, verwaltetes Google-Play-Konto). Für Pflege-Tablets mit festem Zweck passt "Dediziertes Gerät" mit Kiosk-/Mehrfach-App-Modus. Für Diensthandys mit persönlicher Nutzung passt "Vollständig verwaltet" bzw. "Unternehmenseigen mit Arbeitsprofil".

## Was ist der Unterschied zwischen Retire und Wipe?
- Retire (Unternehmensdaten entfernen): Firmen-Apps, -Profile und -Daten weg, private Daten bleiben. Für BYOD und beim Austritt.
- Wipe (Zurücksetzen): Werkseinstellungen, alles weg. Für Verlust, Diebstahl oder die Neuvergabe eines Firmengeräts.
Beides ist nicht umkehrbar, deshalb Freigabe und Nachweis dokumentieren.

## Gerät ist "nicht konform", was nun?
Intune > Geräte > <Gerät> > Gerätekonformität zeigt die verletzte Einstellung (z. B. Betriebssystem zu alt, keine PIN, Verschlüsselung aus). Ursache beheben und dann synchronisieren (Vorlage "Intune: Gerät synchronisieren" oder Unternehmensportal > Synchronisieren). Ohne manuellen Sync meldet sich ein Gerät regulär etwa alle 8 Stunden.

## Gerät taucht seit Wochen nicht mehr auf?
Vorlage "Intune: Gerätebestand" zeigt Geräte ohne Synchronisation seit X Tagen. Klären: verloren, defekt, ausgemustert? Danach Retire/Wipe bzw. aus Intune und Entra löschen. Optional eine Bereinigungsregel in Intune (Geräte > Gerätebereinigungsregeln).

## Pflege-Tablet: worauf achten?
Checkliste "MDM: Pflege-Tablet" im Vorlagen-Tab:
- Kiosk-Modus, Bildschirmsperre und Verschlüsselung
- WLAN-Profil per MDM verteilen
- Updates außerhalb der Übergabezeiten der Pflege
- Kamera/Screenshots je nach Datenschutzvorgabe einschränken
- Inventar mit Station und Seriennummer

"""
Vorlagen-Paket "EMVIA · Benutzerverwaltung (AD/Exchange/M365) -- Abnahme M1".

Einspielen wie die anderen EMVIA-Pakete: eigene PAKET_ID, genau einmal je
Instanz, danach gehoeren die Vorlagen dem Nutzer.

Die Modul-Vorlage liest den Quelltext aus skripte/emvia/EmviaAdmin/ (eine
Quelle fuer Repo-Datei und Werkbank-Vorlage; im Docker-Image per
"COPY skripte ./skripte" enthalten). Hier stehen zusaetzlich die
Ablauf-Checklisten fuer die Einarbeitung.
"""
from pathlib import Path

MODUL = "emvia"
PAKET_ID = "emvia-benutzerverwaltung-v1"

_MODUL_ORDNER = Path(__file__).resolve().parent.parent / "skripte" / "emvia" / "EmviaAdmin"


def _lies(name: str) -> str:
    return (_MODUL_ORDNER / name).read_text(encoding="utf-8")


VORLAGEN: tuple[dict, ...] = (
    {
        "id": "emvia-modul-emviaadmin",
        "typ": "skript",
        "titel": "EmviaAdmin.psm1: PowerShell-Modul Neuanlage/Aenderung/Austritt/Kennwort/Funktionspostfach/MFA (kommentiert)",
        "sprache": "powershell",
        "inhalt": _lies("EmviaAdmin.psm1"),
    },
    {
        "id": "emvia-modul-emviaadmin-config",
        "typ": "skript",
        "titel": "EmviaAdmin.config.json: Vorlage (nur OUs/Domains, KEINE Kennwoerter)",
        "sprache": "json",
        "inhalt": _lies("EmviaAdmin.config.example.json"),
    },
    {
        "id": "emvia-doku-m1-ablaeufe",
        "typ": "doku",
        "titel": "Abnahme M1 (29.10.2026): Ablaeufe Benutzerverwaltung mit Befehlen + Nachweis",
        "sprache": "",
        "inhalt": """ABNAHME M1 -- Benutzerverwaltung (Stufe 2 ab 19.10.: Kennwort-Reset, Benutzer- und Gruppenpflege in Einrichtungs-OUs)
Regel: jede Aenderung erst mit -WhatIf, Ticketnummer immer angeben, Richtlinie IT.10.0x geht vor.

NEUANLAGE (3x)
[ ] Antrag vollstaendig + berechtigt (wer darf beantragen?)
[ ] Get-ADUser -Filter "SamAccountName -eq 'DE...'" -> gibt es das Konto schon?
[ ] New-EmviaBenutzer -Kennung -Vorname -Nachname -OENR -Rollengruppe -Stelle -Ticket -WhatIf
[ ] Fremdpersonal: -Fremdpersonal -Firma -Ablaufdatum (Konto laeuft automatisch ab)
[ ] Lizenzgruppe / Postfach pruefen (nach Sync ~30 Min)
[ ] Einmalkennwort nur ueber geregelten Weg

AENDERUNG (3x)
[ ] Namensaenderung: Set-EmviaBenutzer -Kennung -Nachname -Ticket (Kennung/UPN bleiben)
[ ] Einrichtungswechsel: Set-EmviaBenutzer -NeueOENR [-NeueRollengruppe -AlteRollengruppe]
[ ] Recht dazu/weg: Add-/Remove-EmviaGruppenmitglied (wirkt nach Neuanmeldung)

AUSTRITT (3x)
[ ] Austrittsdatum + Freigabe Vertretungszugriff klaeren
[ ] Disable-EmviaBenutzer -Kennung -Austrittsdatum -Ticket [-PostfachZuFreigegeben] [-SitzungenWiderrufen]
    (sichert Gruppen ins Protokoll, sperrt, entfernt Gruppen, blendet aus, verschiebt)
[ ] Fachanwendungen (SAP-Team!) / Geraete laut Checkliste
[ ] Loeschen erst nach Aufbewahrungsfrist: Remove-EmviaBenutzer

KENNWORT / ENTSPERREN
[ ] Get-EmviaKontoStatus -> nur gesperrt? abgelaufen? deaktiviert?
[ ] Pruefweg: Anforderung aus Funktionspostfach EL ODER Rueckruf an bekannte Durchwahl (Telefonliste!)
[ ] Reset-EmviaKennwort -Pruefweg RueckrufDurchwahl -Nachweis '<Nummer, Uhrzeit, wer>' -Ticket
[ ] Wiederholte Sperre: Get-EmviaSperrquelle -> Geraet mit altem Kennwort finden

FUNKTIONSPOSTFACH
[ ] Ist-Stand: Get-EmviaPostfachRechte <postfach> (ins Ticket)
[ ] Grant-EmviaPostfachRecht -Recht Vollzugriff,SendenAls -Ticket
[ ] Revoke-EmviaPostfachRecht -Ticket (mind. 1x entziehen fuer M1!)

M365
[ ] Lizenz: Lizenzgruppe ODER Set-EmviaLizenz (UsageLocation DE)
[ ] MFA neues Handy: Reset-EmviaMfa -Pruefweg -Nachweis -TapAusstellen

NACHWEIS VOR DEM 29.10.
[ ] Get-EmviaProtokoll -Seit 2026-10-19 | Group-Object Aktion | Select Name,Count
[ ] Weitergabe an synaforce / Ditcon / SAP-Team mind. 1x (Ticketsystem)
[ ] Prioritaeten richtig gesetzt (Ticketsystem)""",
    },
)

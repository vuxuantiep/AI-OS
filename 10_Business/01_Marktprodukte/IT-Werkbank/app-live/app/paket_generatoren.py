"""
Vorlagen-Paket "Generatoren": Grundgerueste fuer die Module PowerShell-Generator,
Prompt-Generator und Datenbank-Generator. Einspielen wie paket_emvia_m365
(einmalig je Instanz, danach frei editierbar).
"""

MODUL = "gen-powershell"  # Standard; einzelne Vorlagen setzen ihr Modul selbst
PAKET_ID = "generatoren-v1"

VORLAGEN: tuple[dict, ...] = (
    {
        "id": "gen-ps-geruest",
        "modul": "gen-powershell",
        "typ": "skript",
        "titel": "PowerShell-Grundgeruest: Parameter, -WhatIf, Fehlerbehandlung, Protokoll",
        "sprache": "powershell",
        "inhalt": r"""<#
.SYNOPSIS
    Kurzbeschreibung: was macht das Skript?
.EXAMPLE
    .\Skript.ps1 -Ziel 'xyz' -WhatIf      # Testlauf: zeigt nur an
    .\Skript.ps1 -Ziel 'xyz'              # echte Ausfuehrung
.NOTES
    Module: ...   Rechte/Scopes: ...   PowerShell 5.1 und 7
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)][ValidateNotNullOrEmpty()][string]$Ziel,
    [string]$Protokoll = ".\protokoll-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
)

function Schreibe-Protokoll([string]$Text) {
    $Zeile = '{0}  {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Text
    Add-Content -Path $Protokoll -Value $Zeile
    Write-Verbose $Zeile
}

try {
    Schreibe-Protokoll "Start fuer $Ziel"
    # 1) Lesen / pruefen
    $Objekte = @()   # z. B. Get-...

    foreach ($O in $Objekte) {
        # 2) Aendern nur nach ShouldProcess -> -WhatIf funktioniert automatisch
        if ($PSCmdlet.ShouldProcess($O, 'Aenderung XY')) {
            # Set-... $O
            Schreibe-Protokoll "Geaendert: $O"
        }
        [pscustomobject]@{ Objekt = $O; Status = 'ok' }   # Ergebnis als Objekt
    }
}
catch {
    Schreibe-Protokoll "FEHLER: $($_.Exception.Message)"
    Write-Error "Abbruch: $($_.Exception.Message)"
    exit 1
}
finally {
    Schreibe-Protokoll 'Ende'
}""",
    },
    {
        "id": "gen-prompt-rkzfe",
        "modul": "gen-prompt",
        "typ": "doku",
        "titel": "Prompt-Geruest RKZFE (Rolle, Kontext, Ziel, Format, Einschraenkungen)",
        "sprache": "",
        "inhalt": """ROLLE
Du bist {Experte fuer ...} mit Erfahrung in {Bereich}.

KONTEXT
{Ausgangslage in 2-4 Saetzen: wer, was, warum. Keine Personen-, Patienten- oder Zugangsdaten!}

ZIEL
Erstelle {konkretes Ergebnis}, damit {Nutzen / wer es verwendet}.

FORMAT
- {z. B. Tabelle mit Spalten A, B, C | Schritt-fuer-Schritt-Liste | E-Mail max. 120 Woerter}
- Sprache: {Deutsch}, Ton: {sachlich / freundlich}

EINSCHRAENKUNGEN
- Nutze nur die Informationen oben; fehlt etwas Wichtiges, frage zuerst nach.
- Erfinde keine Fakten, Namen oder Zahlen; kennzeichne Annahmen als Annahme.
- {weitere Grenzen: Laenge, Zielgruppe, was NICHT enthalten sein soll}

BEISPIEL (optional, verbessert die Treffsicherheit)
Eingabe: {...}
Gewuenschte Ausgabe: {...}""",
    },
    {
        "id": "gen-sql-sichere-aenderung-tsql",
        "modul": "gen-sql",
        "typ": "skript",
        "titel": "SQL Server (T-SQL): Daten sicher aendern -- Vorschau, Transaktion, Kontrolle",
        "sprache": "sql",
        "inhalt": """-- 0) Vorher: Backup bzw. Kopie der betroffenen Zeilen (Produktivsystem!)
-- SELECT * INTO dbo.Kunden_Sicherung_20261015 FROM dbo.Kunden WHERE Ort = 'Hamburg';

-- 1) VORSCHAU: genau dieselbe WHERE-Bedingung wie unten -- wie viele Zeilen?
SELECT COUNT(*) AS betroffen FROM dbo.Kunden WHERE Ort = 'Hamburg' AND Status = 'alt';

-- 2) Aenderung in einer Transaktion (Transaktion = alles oder nichts)
BEGIN TRANSACTION;

UPDATE dbo.Kunden
SET    Status = 'inaktiv'
WHERE  Ort = 'Hamburg' AND Status = 'alt';

SELECT @@ROWCOUNT AS geaendert;      -- muss zur Vorschau passen

-- 3) Kontrolle
SELECT TOP (20) * FROM dbo.Kunden WHERE Ort = 'Hamburg' ORDER BY Id;

-- 4) Bewusst entscheiden -- EINE der beiden Zeilen ausfuehren:
ROLLBACK TRANSACTION;   -- rueckgaengig (Standard, sicher)
-- COMMIT TRANSACTION;  -- endgueltig speichern""",
    },
    {
        "id": "gen-sql-sichere-aenderung-postgres",
        "modul": "gen-sql",
        "typ": "skript",
        "titel": "PostgreSQL: Daten sicher aendern -- Vorschau, Transaktion, Kontrolle",
        "sprache": "sql",
        "inhalt": """-- 0) Vorher: Sicherung der betroffenen Zeilen
-- CREATE TABLE kunden_sicherung_20261015 AS SELECT * FROM kunden WHERE ort = 'Hamburg';

-- 1) VORSCHAU
SELECT count(*) AS betroffen FROM kunden WHERE ort = 'Hamburg' AND status = 'alt';

-- 2) Transaktion
BEGIN;

UPDATE kunden
SET    status = 'inaktiv'
WHERE  ort = 'Hamburg' AND status = 'alt'
RETURNING id, status;                -- zeigt die geaenderten Zeilen direkt an

-- 3) Bewusst entscheiden:
ROLLBACK;     -- rueckgaengig (Standard, sicher)
-- COMMIT;    -- endgueltig speichern""",
    },
)

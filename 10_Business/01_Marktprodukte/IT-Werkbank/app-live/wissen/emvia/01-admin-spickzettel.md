# FAQ EMVIA: Admin-Center und PowerShell-Spickzettel

## Welche Admin-Center brauche ich wofür?
- Microsoft 365 Admin Center: https://admin.microsoft.com (Benutzer, Lizenzen, Dienststatus, Nachrichtencenter)
- Entra Admin Center: https://entra.microsoft.com (Identitäten, Gruppen, MFA, Conditional Access, Anmeldeprotokolle, PIM)
- Exchange Admin Center: https://admin.exchange.microsoft.com (Postfächer, freigegebene Postfächer, Nachrichtenablaufverfolgung)
- Intune Admin Center: https://intune.microsoft.com (Geräte, Richtlinien, Apps, Autopilot, Compliance)
- Microsoft Defender: https://security.microsoft.com (Vorfälle, Quarantäne, Phishing-Meldungen)
- Microsoft Purview: https://purview.microsoft.com (Aufbewahrung, eDiscovery, Audit-Protokoll)
- Teams Admin Center: https://admin.teams.microsoft.com
- SharePoint Admin Center: https://<tenant>-admin.sharepoint.com

## Welche PowerShell-Module nutze ich?
- Microsoft.Graph (Benutzer, Gruppen, Lizenzen, Intune): `Install-Module Microsoft.Graph -Scope CurrentUser`
- ExchangeOnlineManagement (Postfächer, Berechtigungen): `Install-Module ExchangeOnlineManagement -Scope CurrentUser`
- MSOnline und AzureAD sind abgekündigt bzw. abgeschaltet. Nicht mehr verwenden, alte Skripte auf Microsoft.Graph umstellen.

## Wie verbinde ich mich?
- Graph: `Connect-MgGraph -Scopes 'User.Read.All' -NoWelcome`. Nur die Scopes anfordern, die das Skript braucht. Mit `Get-MgContext` prüfen, wer angemeldet ist.
- Exchange: `Connect-ExchangeOnline -ShowBanner:$false`, am Ende `Disconnect-ExchangeOnline -Confirm:$false`.

## Welche Admin-Rolle reicht?
Least Privilege. Für den Alltag reichen meist:
- Benutzeradministrator: Konten, Kennwörter, Gruppen
- Exchange-Administrator: Postfächer, Berechtigungen
- Intune-Administrator: Geräte und Richtlinien
- Lizenzadministrator: nur Lizenzen
Globaler Administrator nur für Ausnahmen und am besten über PIM zeitlich begrenzt. Alltagskonto und Admin-Konto trennen.

## Wo sehe ich, warum etwas nicht geht?
- Anmeldeprobleme: Entra > Benutzer > Anmeldeprotokolle (Fehlercode und Conditional-Access-Ergebnis)
- Mail kommt nicht an: Exchange Admin Center > Nachrichtenfluss > Nachrichtenablaufverfolgung bzw. `Get-MessageTraceV2` (das alte `Get-MessageTrace` ist abgekündigt)
- Wer hat was geändert: Purview > Audit (Überwachungsprotokoll)
- Störungen bei Microsoft: M365 Admin Center > Integrität > Dienstintegrität

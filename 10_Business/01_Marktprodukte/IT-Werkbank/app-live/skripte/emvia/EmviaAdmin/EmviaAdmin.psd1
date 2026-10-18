# Modul-Manifest: beschreibt das Modul und legt fest, WELCHE Funktionen
# nach aussen sichtbar sind (FunctionsToExport). Interne Helfer wie
# Write-EmviaProtokoll oder Resolve-EmviaEinrichtungsOU bleiben verborgen.
@{
    RootModule        = 'EmviaAdmin.psm1'
    ModuleVersion     = '1.0.0'
    GUID              = '5b0c6a3e-2f4d-4c8e-9a51-7e3d2b1f0a64'
    Author            = 'vuxuantiep'
    Description       = 'EMVIA Benutzerverwaltung (AD, Exchange, M365) - Neuanlage, Aenderung, Austritt, Kennwort, Funktionspostfaecher, MFA, Lizenzen. Lern-Modul mit Protokoll.'
    PowerShellVersion = '5.1'
    FunctionsToExport = @(
        'Get-EmviaKonfig'
        'New-EmviaBenutzer', 'Set-EmviaBenutzer', 'Disable-EmviaBenutzer', 'Remove-EmviaBenutzer'
        'Get-EmviaKontoStatus', 'Unlock-EmviaKonto', 'Get-EmviaSperrquelle', 'Reset-EmviaKennwort'
        'Get-EmviaBenutzerGruppen', 'Add-EmviaGruppenmitglied', 'Remove-EmviaGruppenmitglied'
        'New-EmviaFunktionspostfach', 'Grant-EmviaPostfachRecht', 'Revoke-EmviaPostfachRecht', 'Get-EmviaPostfachRechte'
        'Get-EmviaMfaStatus', 'Reset-EmviaMfa', 'Set-EmviaLizenz'
        'Get-EmviaProtokoll'
    )
    CmdletsToExport   = @()
    VariablesToExport = @()
    AliasesToExport   = @()
}

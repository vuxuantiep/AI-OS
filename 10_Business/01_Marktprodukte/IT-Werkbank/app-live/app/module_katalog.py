"""
Modulkatalog der IT-Werkbank.

Ein Modul = ein Fachgebiet mit eigenem Fachprompt, eigenen Wiki-Namensraum
und eigenen Bausteinen in der Skriptbibliothek. Neue Module hier ergaenzen,
Frontend und RAG ziehen sich den Katalog automatisch.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class Modul:
    id: str
    name: str
    kurz: str
    fachprompt: str
    stichworte: tuple[str, ...] = field(default=())


BASIS_PROMPT = """Du bist die IT-Werkbank, der Fachassistent eines Systemadministrators.
Einsatzumgebung: mittelstaendischer Betreiber mit Windows-Server-Landschaft, Hyper-V,
Microsoft 365 und mobilen Endgeraeten in der Pflegedokumentation. DSGVO ist relevant.

Arbeitsweise:
- Antworte knapp und praezise, in deutscher Sprache, ohne Fuellsaetze.
- Nenne konkrete Klickpfade, Cmdlets oder Konfigurationswerte, keine Allgemeinplaetze.
- Erfinde keine Menuepunkte, Parameter oder Cmdlets. Bist du unsicher, sage es in einem Satz.
- Warne von selbst, wenn ein Schritt Ausfall, Datenverlust oder Datenschutzfolgen hat.
- Skripte immer als vollstaendiger Codeblock mit Sprachangabe, lauffaehig und kommentiert.
- Nutze den mitgelieferten Wissenskontext, wenn er passt, und sage wenn er nicht passt.

Umgang mit Wissensluecken (verbindlich, keine Ausnahme):
- Beantworte Fragen zu konkreten Eigennamen (Programme, Projekte, Behoerden,
  Produkte, Gesetze, Organisationen) NUR, wenn dazu entweder (a) etwas im
  mitgelieferten Wissenskontext steht, oder (b) du dir aus verlaesslichem,
  antrainiertem Wissen wirklich sicher bist. Im Zweifel gilt: nicht sicher.
- Ist beides nicht der Fall, erfinde NICHTS -- keine plausibel klingende
  Beschreibung, kein vermuteter Zweck, kein geratener Name. Sage stattdessen
  wortwoertlich, dass dir dazu keine verlaessliche Information vorliegt.
- Ein Abschnitt "Live-Websuche" im Wissenskontext bedeutet: das System hat
  bereits automatisch im Internet gesucht, weil Wiki und Gedaechtnis nichts
  Passendes hatten. Nutze ausschliesslich diese Suchergebnisse als Grundlage,
  nenne die Quelle (URL), und gib nichts hinzu, was dort nicht steht. Steht
  auch dort nichts Brauchbares, sage explizit, dass auch die Websuche keinen
  verlaesslichen Treffer geliefert hat -- rate nicht ersatzweise selbst.
- **Erzeuge SELBST NIEMALS eine Ueberschrift oder einen Abschnitt namens
  "Live-Websuche" (oder aehnlich) in deiner Antwort.** Dieser Abschnitt kommt
  ausschliesslich vom System, wenn er im Wissenskontext oben tatsaechlich
  vorhanden ist. Steht im Kontext KEIN "Live-Websuche"-Abschnitt, wurde keine
  Websuche durchgefuehrt -- schreibe dann auch keine erfundene Quellenangabe
  oder einen erfundenen Link (z.B. nicht "docs.microsoft.com" o.ae. aus dem
  Nichts erzeugen), sondern sage schlicht, dass dir aktuelle Informationen
  dazu fehlen.
- Behaupte niemals, recherchiert oder nachgeschaut zu haben, wenn dir kein
  Rechercheergebnis im Kontext vorliegt. Fuer dich selbst gibt es keine
  eigene Internetverbindung ausserhalb des dir mitgelieferten Kontexts --
  jeder Link, den du nennst, muss woertlich aus dem mitgelieferten Kontext
  stammen, nie aus eigener Vermutung, welche URL wohl plausibel waere.
- Nach einer Korrektur durch den Nutzer: uebernimm die Korrektur, aber
  erfinde nicht sofort eine neue, andere Erklaerung, wenn du dazu weiterhin
  nichts Verlaessliches weisst -- gib in diesem Fall lieber zu, dass du es
  nicht weisst, statt zu raten.

Umgang mit veraltetem Wissen bei Fragen nach Aktualitaet (verbindlich):
- Dein antrainiertes Wissen hat einen festen Stichtag (Trainingsgrenze), der
  WEIT vor dem heutigen Datum liegen kann (siehe "Heutiges Datum" oben im
  Kontext). Ein Fakt kann zum Trainingsstichtag richtig gewesen sein und
  trotzdem laengst durch neuere Entwicklungen ueberholt sein.
- Bei Fragen, die explizit nach Neuigkeiten/Aktualitaet fragen ("was gibt es
  Neues", "aktueller Stand", "letzte Updates", "ist X noch aktuell") reicht
  dein trainiertes Wissen ALLEIN NIE als Antwort, selbst wenn du dir der
  einzelnen Fakten sicher bist. Erklaere in diesem Fall, was dir aus deinem
  Training bekannt ist, kennzeichne es AUSDRUECKLICH als moeglicherweise
  veraltet (mit Bezug auf deinen Wissensstand), und stuetze dich fuer den
  aktuellen Stand auf einen mitgelieferten "Live-Websuche"-Abschnitt. Fehlt
  dieser Abschnitt im Kontext, sage explizit, dass fuer eine verlaessliche
  Aktualitaetsaussage eine echte Recherche noetig waere, statt dein
  Trainingswissen unmarkiert als aktuellen Stand zu praesentieren.
- Nenne bei versionsbezogenen Aussagen (z.B. "neueste Version") das
  Veroeffentlichungsdatum mit, wenn du es kennst -- das macht dem Nutzer
  sofort sichtbar, wie alt die Information ist, statt dass er es selbst
  einschaetzen muss.
"""

MODULE: tuple[Modul, ...] = (
    Modul(
        id="assistent",
        name="Assistent",
        kurz="Allgemeine Fragen, Architekturentscheidungen, Fehlersuche",
        fachprompt="Schwerpunkt: Architekturberatung und Fehlersuche quer ueber alle Module. "
        "Bei Architekturfragen nenne immer Alternative, Abwaegung und Empfehlung.",
        stichworte=("architektur", "entscheidung", "troubleshooting"),
    ),
    Modul(
        id="m365",
        name="Microsoft 365",
        kurz="Exchange Online, Teams, SharePoint, Lizenzen, Compliance",
        fachprompt="Schwerpunkt: Microsoft 365. Nenne Admin-Center-Pfade und die passenden "
        "Module (ExchangeOnlineManagement, Microsoft.Graph, PnP.PowerShell). "
        "Bei Postfach- und Aufbewahrungsthemen weise auf Compliance-Folgen hin.",
        stichworte=("exchange", "teams", "sharepoint", "lizenz", "purview"),
    ),
    Modul(
        id="entra",
        name="Entra ID",
        kurz="Identitaeten, Conditional Access, Rollen, Gastzugriff",
        fachprompt="Schwerpunkt: Entra ID. Unterscheide klar zwischen Rollen, Gruppen und "
        "Richtlinien. Bei Conditional Access immer Report-only-Modus als ersten "
        "Schritt vorschlagen und Notfallzugang (Break-Glass-Konto) erwaehnen.",
        stichworte=("conditional access", "mfa", "rollen", "sso", "scim"),
    ),
    Modul(
        id="sicherheit",
        name="Sicherheit & IAM",
        kurz="IAM-Strategie, Zero Trust, Härtung, Berechtigungskonzepte, Audit",
        fachprompt="Schwerpunkt: Sicherheit und Identity & Access Management uebergreifend "
        "(nicht Entra-spezifisch, sondern Konzept- und Herstellerebene: AD, LDAP, "
        "PAM-Loesungen, Cloud-IdPs). Immer Prinzip der geringsten Rechte (Least "
        "Privilege) als Ausgangspunkt nennen, RBAC vor individuellen Berechtigungen "
        "empfehlen, privilegierte Konten (Admin-Tiering, PAW) getrennt von "
        "Alltagskonten behandeln. Bei Haertungsthemen konkrete Baseline nennen "
        "(z.B. CIS Benchmark, Microsoft Security Baseline) statt allgemeiner "
        "Ratschlaege. Audit-/Log-Aufbewahrung und Nachvollziehbarkeit mitdenken.",
        stichworte=("iam", "zero trust", "pam", "rbac", "haertung", "audit", "least privilege"),
    ),
    Modul(
        id="winserver",
        name="Windows Server",
        kurz="AD DS, DNS, DHCP, GPO, Dateidienste, Patchstand",
        fachprompt="Schwerpunkt: Windows Server und Active Directory. Nenne bei GPO-Themen "
        "immer Pfad in der Richtlinienverwaltung plus Registry-Aequivalent. "
        "Weise auf Replikations- und Anmeldefolgen hin.",
        stichworte=("ad", "dns", "dhcp", "gpo", "wsus", "dfs"),
    ),
    Modul(
        id="hyperv",
        name="Hyper-V Cluster",
        kurz="Failover-Cluster, Livemigration, Storage, Replikation",
        fachprompt="Schwerpunkt: Hyper-V und Failover-Clustering. Beim Clusteraufbau immer "
        "Reihenfolge einhalten: Netztrennung, Speicher, Validierungsbericht, Cluster, "
        "Zeugenkonfiguration, Livemigration. Cluster-Validierung nie ueberspringen.",
        stichworte=("failover", "livemigration", "csv", "witness", "replica"),
    ),
    Modul(
        id="powershell",
        name="PowerShell",
        kurz="Skriptbibliothek, Automatisierung, geplante Aufgaben",
        fachprompt="Schwerpunkt: PowerShell 7. Skripte mit [CmdletBinding()], param-Block, "
        "-WhatIf wo moeglich, try/catch und Protokollausgabe. Keine Aliase, "
        "keine Write-Host fuer Daten, sondern Objekte zurueckgeben.",
        stichworte=("skript", "automatisierung", "modul", "task"),
    ),
    Modul(
        id="iac",
        name="IaC Automation",
        kurz="Terraform, Ansible, DSC, Bicep, Pipelines",
        fachprompt="Schwerpunkt: Infrastructure as Code. Zustand immer versioniert und "
        "idempotent. Nenne Ablageort fuer den State und trenne Geheimnisse "
        "vom Code. Zeige plan vor apply. Bei Ansible: Inventory sauber trennen "
        "(prod/test), Playbooks idempotent (Handler statt wiederholter Tasks), "
        "Secrets ueber Ansible Vault, --check vor echtem Lauf zeigen.",
        stichworte=("terraform", "ansible", "playbook", "bicep", "dsc", "pipeline"),
    ),
    Modul(
        id="container",
        name="Container-Technik",
        kurz="Containerisierung, Docker, Kubernetes, Helm",
        fachprompt="Schwerpunkt: Software/Webapps containerisieren und betreiben. Bei "
        "Dockerfiles: Multi-Stage-Build, kleines Basis-Image, kein root im "
        "Container, .dockerignore nicht vergessen. Bei Kubernetes: Unterschied "
        "Deployment/StatefulSet erklaeren, Ressourcen-Limits und Readiness-/"
        "Liveness-Probes immer nennen, Secrets nie im Klartext-Manifest. "
        "Zeige den Weg vom lauffaehigen Code zum produktionsreifen Container "
        "(Build -> Registry -> Deployment) konkret mit Befehlen.",
        stichworte=("docker", "dockerfile", "kubernetes", "k8s", "helm", "compose", "registry"),
    ),
    Modul(
        id="netz",
        name="Netz & VPN",
        kurz="Adressplanung, Routen, Site-to-Site, Client-VPN",
        fachprompt="Schwerpunkt: Netzwerk und VPN. Bei VPN immer beide Seiten dokumentieren: "
        "Phase-1- und Phase-2-Parameter, Netze, NAT-Ausnahmen. Adressplaene "
        "ueberschneidungsfrei halten und das pruefen.",
        stichworte=("subnetz", "routing", "ipsec", "wireguard", "firewall"),
    ),
    Modul(
        id="datenbank",
        name="Datenbank",
        kurz="SQL & Oracle, DBA-Grundlagen, Rollback- und Update-Konzepte",
        fachprompt="Schwerpunkt: Datenbank-Administration fuer einen Einsteiger in diesem "
        "Bereich (SQL und Oracle). Setze kein Vorwissen voraus: erklaere Fachbegriffe "
        "(Transaktion, Commit, Rollback, Isolation Level, Tablespace, Redo/Undo) beim "
        "ersten Gebrauch kurz mit, statt sie nur zu benutzen. Bei jedem "
        "datenveraendernden Befehl (UPDATE, DELETE, DROP, ALTER) IMMER zuerst auf "
        "Sicherung/Backup und Rollback-Moeglichkeit hinweisen und empfehlen, ihn erst in "
        "einer Testumgebung bzw. innerhalb einer Transaktion (BEGIN TRANSACTION / "
        "COMMIT / ROLLBACK) auszuprobieren, bevor er auf einem Produktivsystem laeuft. "
        "Bei Oracle-spezifischen Themen (PL/SQL, Tablespaces, RMAN-Backups) explizit als "
        "Oracle kennzeichnen, da sich Syntax und Konzepte von SQL Server/MySQL "
        "unterscheiden. Update-/Migrationsskripte immer versioniert und mit "
        "Gegenstueck (Rollback-/Down-Skript) zeigen, nie nur die Vorwaertsrichtung.",
        stichworte=("sql", "oracle", "plsql", "rollback", "commit", "transaktion",
                     "backup", "migration", "dba", "tablespace"),
    ),
    Modul(
        id="support",
        name="Support",
        kurz="Ticketbearbeitung, Kommunikationsvorlagen, Anwenderschulung",
        fachprompt="Schwerpunkt: IT-Support und Anwenderkommunikation, drei Teilbereiche. "
        "(1) Ticketbearbeitung: bearbeitete Tickets mit Problem, Ursache und Loesung "
        "dokumentieren, damit wiederkehrende Probleme aus der Loesungssammlung schneller "
        "gefunden werden. (2) Kommunikationsvorlagen: E-Mails, Terminankuendigungen "
        "(z.B. Anwendungs-Update), Release- und Change-Management-Mitteilungen kurz, "
        "professionell und mit klarem Betreff formulieren -- immer mit Zeitfenster, "
        "erwarteten Auswirkungen und Ansprechpartner. (3) Anwenderschulung: komplexe "
        "Anwendungsfunktionen in einfacher, laienverstaendlicher Sprache erklaeren, "
        "ohne unnoetigen Fachjargon. Bei Bedarf Fachbegriffe kurz einordnen, "
        "insbesondere aus der Medizin- und Praxisverwaltungssoftware (z.B. CGM Turbomed, "
        "ePA/elektronische Patientenakte) -- dabei nie medizinische Ratschlaege geben, "
        "nur die Software-/Verwaltungsseite erklaeren.",
        stichworte=("support", "ticket", "kommunikation", "schulung", "change management",
                     "release management", "turbomed", "epa", "anwenderschulung"),
    ),
    Modul(
        id="mdm",
        name="MDM",
        kurz="Endgeraeteverwaltung, Kiosk-Modus, Enrollment, Compliance",
        fachprompt="Schwerpunkt: Endgeraeteverwaltung. Das eingesetzte System kann wechseln, "
        "frage im Zweifel nach oder beschreibe herstellerneutral. Bei Pflege-Tablets "
        "gilt: Kiosk-Modus, kein Nutzerwechsel, Fernloeschung muss belegbar sein.",
        stichworte=("intune", "relution", "sophos", "kiosk", "enrollment"),
    ),
)

MODUL_INDEX = {m.id: m for m in MODULE}


# ---------------------------------------------------------------------------
# Vorlagen-Typen — ersetzt die frueher starre, nur ueber Wiki nutzbare
# Modulbindung. Jedes Modul kann in jedem dieser vier Typen eigene Eintraege
# haben (E-Mail-Vorlagen, Skript-Vorlagen, Tickets-Sammlung, Doku-Loesungen),
# gespeichert in der vorlage-Tabelle (store.py). "sprache_feld" steuert, ob
# das Frontend bei diesem Typ das Sprache-Auswahlfeld (fuer Code-Highlighting)
# anzeigt -- nur bei Skript-Vorlagen sinnvoll.
# ---------------------------------------------------------------------------

VORLAGE_TYPEN: tuple[dict, ...] = (
    {
        "id": "skript",
        "name": "Skript-Vorlagen",
        "hinweis": "Automatisierung, wiederverwendbare Codebausteine",
        "sprache_feld": True,
    },
    {
        "id": "email",
        "name": "E-Mail-Vorlagen",
        "hinweis": "Kommunikationsbausteine fuer Anwender und Kunden",
        "sprache_feld": False,
    },
    {
        "id": "ticket",
        "name": "Tickets-Sammlung",
        "hinweis": "Geloeste Faelle: Problem, Ursache, Loesung",
        "sprache_feld": False,
    },
    {
        "id": "doku",
        "name": "Doku-Lösungen",
        "hinweis": "Selbst verfasste Schritt-fuer-Schritt-Anleitungen fuer eigene Prozesse "
        "(Abgrenzung zum Wiki: dort steht extern recherchiertes/gescraptes Wissen)",
        "sprache_feld": False,
    },
)

VORLAGE_TYP_INDEX = {t["id"]: t for t in VORLAGE_TYPEN}


def systemprompt(modul_id: str, wissen: str = "") -> str:
    """Basisprompt plus Fachprompt plus abgerufener Wissenskontext.

    Das heutige Datum wird explizit mitgegeben, weil ein Sprachmodell ohne
    diesen Anker seinen eigenen Trainingsstichtag leicht mit "jetzt"
    verwechselt -- das war die Ursache fuer den Vorfall, bei dem Windows
    Server 2022 (Stand 2021) als aktuelle Neuigkeit im Jahr 2026 dargestellt
    wurde. Siehe dazu auch die BASIS_PROMPT-Regeln "Umgang mit veraltetem
    Wissen bei Fragen nach Aktualitaet".
    """
    modul = MODUL_INDEX.get(modul_id, MODUL_INDEX["assistent"])
    heute = datetime.now(UTC).strftime("%Y-%m-%d")
    teile = [
        BASIS_PROMPT,
        f"Heutiges Datum: {heute} (Format JJJJ-MM-TT). Dein antrainiertes Wissen "
        "kann deutlich aelter sein als dieses Datum.",
        f"Aktives Modul: {modul.name}. {modul.fachprompt}",
    ]
    if wissen.strip():
        teile.append(
            "Wissenskontext aus Wiki und frueheren Chats (kann unvollstaendig sein):\n"
            f"{wissen.strip()}"
        )
    return "\n\n".join(teile)


# ---------------------------------------------------------------------------
# Skriptbibliothek — waechst mit. Jeder Eintrag ist geprueft lauffaehig
# gedacht und wird im Frontend mit Kopieren-Schaltflaeche angezeigt.
# ---------------------------------------------------------------------------

SKRIPTE: tuple[dict, ...] = (
    {
        "id": "hyperv-cluster-pruefen",
        "modul": "hyperv",
        "titel": "Clusterzustand und Knoten pruefen",
        "sprache": "powershell",
        "code": """Get-Cluster | Select-Object Name, DynamicQuorum, WitnessDynamicWeight
Get-ClusterNode | Select-Object Name, State, DynamicWeight
Get-ClusterSharedVolume | Select-Object Name, State, OwnerNode
Get-VM -ComputerName (Get-ClusterNode).Name |
    Select-Object ComputerName, Name, State, Status |
    Sort-Object ComputerName, Name""",
    },
    {
        "id": "hyperv-livemigration",
        "modul": "hyperv",
        "titel": "Livemigration einrichten (pro Knoten ausfuehren)",
        "sprache": "powershell",
        "code": """$MigrationsNetz = '10.20.30.0/24'

Enable-VMMigration
Set-VMHost -VirtualMachineMigrationAuthenticationType Kerberos `
           -VirtualMachineMigrationPerformanceOption SMB `
           -MaximumVirtualMachineMigrations 2

# Nur das dedizierte Migrationsnetz zulassen
Get-VMMigrationNetwork | Remove-VMMigrationNetwork -Confirm:$false
Add-VMMigrationNetwork -Subnet $MigrationsNetz

Get-VMHost | Select-Object Name, VirtualMachineMigrationEnabled,
    VirtualMachineMigrationAuthenticationType""",
    },
    {
        "id": "ad-inaktive-konten",
        "modul": "winserver",
        "titel": "Inaktive AD-Konten finden (nur Bericht, keine Aenderung)",
        "sprache": "powershell",
        "code": """[CmdletBinding()]
param([int]$TageInaktiv = 90)

$Grenze = (Get-Date).AddDays(-$TageInaktiv)

Search-ADAccount -AccountInactive -DateTime $Grenze -UsersOnly |
    Where-Object Enabled -eq $true |
    Get-ADUser -Properties LastLogonDate, Department, Description |
    Select-Object SamAccountName, Name, Department, LastLogonDate |
    Sort-Object LastLogonDate |
    Export-Csv -Path ".\\inaktive-konten.csv" -NoTypeInformation -Encoding UTF8""",
    },
    {
        "id": "m365-postfachgroessen",
        "modul": "m365",
        "titel": "Postfachgroessen und Archivstatus auslesen",
        "sprache": "powershell",
        "code": """Connect-ExchangeOnline -ShowBanner:$false

Get-Mailbox -ResultSize Unlimited |
    ForEach-Object {
        $Stat = Get-MailboxStatistics -Identity $_.UserPrincipalName
        [pscustomobject]@{
            Benutzer      = $_.UserPrincipalName
            GroesseGB     = [math]::Round(($Stat.TotalItemSize.Value.ToBytes() / 1GB), 2)
            Elemente      = $Stat.ItemCount
            ArchivAktiv   = $_.ArchiveStatus
            Aufbewahrung  = $_.RetentionPolicy
        }
    } |
    Sort-Object GroesseGB -Descending |
    Export-Csv ".\\postfaecher.csv" -NoTypeInformation -Encoding UTF8

Disconnect-ExchangeOnline -Confirm:$false""",
    },
    {
        "id": "entra-ca-bericht",
        "modul": "entra",
        "titel": "Conditional-Access-Richtlinien dokumentieren",
        "sprache": "powershell",
        "code": """Connect-MgGraph -Scopes 'Policy.Read.All','Directory.Read.All' -NoWelcome

Get-MgIdentityConditionalAccessPolicy -All |
    Select-Object DisplayName, State,
        @{n='Benutzer';   e={ $_.Conditions.Users.IncludeUsers -join ', ' }},
        @{n='Anwendungen';e={ $_.Conditions.Applications.IncludeApplications -join ', ' }},
        @{n='Kontrollen'; e={ $_.GrantControls.BuiltInControls -join ', ' }} |
    Sort-Object State, DisplayName |
    Export-Csv ".\\conditional-access.csv" -NoTypeInformation -Encoding UTF8""",
    },
    {
        "id": "mdm-geraetebestand",
        "modul": "mdm",
        "titel": "Geraetebestand und Compliance auslesen (Intune)",
        "sprache": "powershell",
        "code": """Connect-MgGraph -Scopes 'DeviceManagementManagedDevices.Read.All' -NoWelcome

Get-MgDeviceManagementManagedDevice -All |
    Select-Object DeviceName, OperatingSystem, OsVersion, ComplianceState,
                  LastSyncDateTime, UserPrincipalName |
    Sort-Object LastSyncDateTime |
    Export-Csv ".\\geraete.csv" -NoTypeInformation -Encoding UTF8

# Geraete ohne Kontakt seit 14 Tagen
Get-MgDeviceManagementManagedDevice -All |
    Where-Object { $_.LastSyncDateTime -lt (Get-Date).AddDays(-14) } |
    Select-Object DeviceName, UserPrincipalName, LastSyncDateTime""",
    },
    {
        "id": "iac-terraform-grundgeruest",
        "modul": "iac",
        "titel": "Terraform-Grundgeruest mit getrenntem State",
        "sprache": "hcl",
        "code": """terraform {
  required_version = ">= 1.7"

  # State liegt zentral, nie im Repository
  backend "http" {
    address = "https://state.intern.local/werkbank/prod"
    lock_address   = "https://state.intern.local/werkbank/prod/lock"
    unlock_address = "https://state.intern.local/werkbank/prod/lock"
  }

  required_providers {
    hyperv = { source = "taliesins/hyperv", version = "~> 1.2" }
  }
}

variable "umgebung" {
  description = "prod oder test"
  type        = string
  validation {
    condition     = contains(["prod", "test"], var.umgebung)
    error_message = "Nur prod oder test zulaessig."
  }
}""",
    },
    {
        "id": "iac-ansible-baseline-playbook",
        "modul": "iac",
        "titel": "Ansible-Playbook: Server-Baseline idempotent ausrollen",
        "sprache": "yaml",
        "code": """---
- name: Server-Baseline
  hosts: baseline
  become: true
  vars_files:
    - vault/secrets.yml   # ansible-vault verschluesselt

  tasks:
    - name: Pakete aktuell halten
      ansible.builtin.package:
        name: "*"
        state: latest
      register: paketupdate

    - name: Zeitzone setzen
      community.general.timezone:
        name: Europe/Berlin

    - name: SSH-Passwortanmeldung deaktivieren
      ansible.builtin.lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^#?PasswordAuthentication'
        line: 'PasswordAuthentication no'
      notify: sshd neu laden

  handlers:
    - name: sshd neu laden
      ansible.builtin.service:
        name: sshd
        state: reloaded

# Testlauf ohne Aenderung: ansible-playbook baseline.yml --check --diff""",
    },
    {
        "id": "container-dockerfile-multistage",
        "modul": "container",
        "titel": "Dockerfile: Webapp als Multi-Stage-Build containerisieren",
        "sprache": "dockerfile",
        "code": """# Stufe 1: bauen
FROM node:20-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY . .
RUN npm run build

# Stufe 2: schlankes Laufzeit-Image, kein Build-Werkzeug im Endprodukt
FROM node:20-slim
WORKDIR /app
RUN useradd --system --uid 10001 app
COPY --from=build --chown=app:app /app/dist ./dist
COPY --from=build --chown=app:app /app/node_modules ./node_modules
USER app
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD node dist/health-check.js || exit 1
CMD ["node", "dist/server.js"]

# Bauen + Registry:
#   docker build -t registry.intern.local/webapp:1.0 .
#   docker push registry.intern.local/webapp:1.0""",
    },
    {
        "id": "container-k8s-deployment",
        "modul": "container",
        "titel": "Kubernetes: Deployment mit Ressourcen-Limits und Probes",
        "sprache": "yaml",
        "code": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
spec:
  replicas: 2
  selector:
    matchLabels: { app: webapp }
  template:
    metadata:
      labels: { app: webapp }
    spec:
      containers:
        - name: webapp
          image: registry.intern.local/webapp:1.0
          ports: [{ containerPort: 8080 }]
          resources:
            requests: { cpu: "100m", memory: "128Mi" }
            limits:   { cpu: "500m", memory: "256Mi" }
          readinessProbe:
            httpGet: { path: /healthz, port: 8080 }
            initialDelaySeconds: 5
          livenessProbe:
            httpGet: { path: /healthz, port: 8080 }
            initialDelaySeconds: 15
          envFrom:
            - secretRef: { name: webapp-secrets }   # nie Klartext im Manifest
---
apiVersion: v1
kind: Service
metadata:
  name: webapp
spec:
  selector: { app: webapp }
  ports: [{ port: 80, targetPort: 8080 }]""",
    },
    {
        "id": "sicherheit-privilegierte-konten-bericht",
        "modul": "sicherheit",
        "titel": "Privilegierte AD-Konten und deren letzte Anmeldung dokumentieren",
        "sprache": "powershell",
        "code": """[CmdletBinding()]
param([string[]]$PrivilegierteGruppen = @('Domain Admins','Enterprise Admins','Schema Admins'))

foreach ($Gruppe in $PrivilegierteGruppen) {
    Get-ADGroupMember -Identity $Gruppe -Recursive |
        Get-ADUser -Properties LastLogonDate, PasswordLastSet, Enabled |
        Select-Object @{n='Gruppe';e={$Gruppe}}, SamAccountName, Name,
                      Enabled, LastLogonDate, PasswordLastSet
} | Sort-Object Gruppe, LastLogonDate |
    Export-Csv ".\\privilegierte-konten.csv" -NoTypeInformation -Encoding UTF8

# Least Privilege pruefen: Konten ohne Anmeldung seit 60 Tagen sind Kandidaten
# fuer Entzug der privilegierten Mitgliedschaft (Admin-Tiering).""",
    },
    {
        "id": "db-transaktion-grundmuster",
        "modul": "datenbank",
        "titel": "Grundmuster: Transaktion mit sicherem Rollback (SQL Server/ANSI)",
        "sprache": "sql",
        "code": """-- Eine Transaktion buendelt mehrere Befehle zu einer Einheit: entweder
-- passiert alles (COMMIT) oder nichts (ROLLBACK) -- nie nur die Haelfte.
BEGIN TRANSACTION;

BEGIN TRY
    UPDATE Konten SET Saldo = Saldo - 100 WHERE KontoId = 1;
    UPDATE Konten SET Saldo = Saldo + 100 WHERE KontoId = 2;

    -- Erst wenn beide UPDATEs fehlerfrei liefen, dauerhaft speichern.
    COMMIT TRANSACTION;
    PRINT 'Erfolgreich gebucht.';
END TRY
BEGIN CATCH
    -- Bei JEDEM Fehler alles rueckgaengig machen, kein halbfertiger Zustand.
    ROLLBACK TRANSACTION;
    PRINT 'Fehler, alles zurueckgerollt: ' + ERROR_MESSAGE();
END CATCH;

-- Merksatz: ROLLBACK funktioniert nur, solange noch kein COMMIT lief.
-- Nach einem COMMIT ist die Aenderung dauerhaft -- dafuer ist ein separates
-- Backup (nicht Teil der Transaktion) die einzige Absicherung.""",
    },
    {
        "id": "db-oracle-plsql-rollback",
        "modul": "datenbank",
        "titel": "Oracle PL/SQL: UPDATE mit automatischem Rollback bei Fehler",
        "sprache": "plsql",
        "code": """-- Oracle-Besonderheit: PL/SQL-Bloecke starten mit DECLARE/BEGIN, jeder Block
-- kann eigene Fehlerbehandlung (EXCEPTION) haben.
BEGIN
    UPDATE mitarbeiter
       SET gehalt = gehalt * 1.05
     WHERE abteilung_id = 10;

    -- Ohne COMMIT bleibt die Aenderung nur in der eigenen Sitzung sichtbar
    -- und ist bei Sitzungsende automatisch weg (impliziter Rollback).
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Gehaltsanpassung gebucht.');
EXCEPTION
    WHEN OTHERS THEN
        -- Bei jedem Fehler: alles rueckgaengig, Fehlertext protokollieren.
        ROLLBACK;
        DBMS_OUTPUT.PUT_LINE('Fehler, zurueckgerollt: ' || SQLERRM);
END;
/

-- Vor echten Aenderungen an Produktivdaten: SAVEPOINT setzen, damit man
-- auch nur einen Teil eines laengeren Skripts zuruecknehmen kann:
--   SAVEPOINT vor_update;
--   ... Aenderungen ...
--   ROLLBACK TO vor_update;  -- nur bis zu diesem Punkt zuruecknehmen""",
    },
    {
        "id": "db-versionierte-migration",
        "modul": "datenbank",
        "titel": "Update-Konzept: versionierte Migration mit Rollback-Gegenstueck",
        "sprache": "sql",
        "code": """-- Grundmuster fuer Schema-Aenderungen (Update-Konzept): jede Aenderung
-- bekommt eine Versionsnummer UND ein Gegenstueck, das sie rueckgaengig
-- macht. So laesst sich jederzeit nachvollziehen, welcher Stand aktiv ist,
-- und im Notfall gezielt zurueckrollen -- nicht nur "irgendein Backup".

-- Einmalig anlegen: Tabelle, die den aktuellen Schema-Stand dokumentiert.
CREATE TABLE schema_version (
    version     INT PRIMARY KEY,
    beschreibung VARCHAR(200) NOT NULL,
    angewendet  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- === Migration 001__spalte_hinzufuegen.up.sql =============================
ALTER TABLE kunden ADD telefonnummer VARCHAR(30) NULL;
INSERT INTO schema_version (version, beschreibung) VALUES (1, 'Telefonnummer ergaenzt');

-- === Migration 001__spalte_hinzufuegen.down.sql (Rollback-Gegenstueck) ====
-- Wird ausgefuehrt, wenn Version 1 zurueckgenommen werden muss.
ALTER TABLE kunden DROP COLUMN telefonnummer;
DELETE FROM schema_version WHERE version = 1;

-- Merksatz: ALTER TABLE ist bei vielen Datenbanken NICHT Teil einer normalen
-- Transaktion (kein Rollback mehr moeglich, sobald es durchgelaufen ist) --
-- deshalb hier das Down-Skript als echtes Gegenstueck statt auf ROLLBACK zu
-- vertrauen, und vorher immer ein Backup des betroffenen Tabellenbereichs.""",
    },
    {
        "id": "support-ticket-dokumentation",
        "modul": "support",
        "titel": "Vorlage: Ticket-Dokumentation fuer die Loesungssammlung",
        "sprache": "markdown",
        "code": """## Ticket #[Nummer] -- [Kurztitel des Problems]

**Gemeldet von:** [Name/Abteilung]
**Datum:** [TT.MM.JJJJ]
**Anwendung/System:** [z. B. CGM Turbomed, Microsoft 365 ...]
**Schweregrad:** Niedrig / Mittel / Hoch / Kritisch

### Problem
[Was hat der Nutzer beobachtet? Moeglichst in seinen eigenen Worten, plus
eigene technische Einordnung.]

### Ursache
[Root Cause, sobald bekannt -- nicht nur das Symptom.]

### Loesung
[Konkrete Schritte, die das Problem behoben haben. So detailliert, dass ein
aehnlicher Fall kuenftig ohne erneute Fehlersuche geloest werden kann.]

### Vermeidung kuenftig
[Falls zutreffend: Konfigurationsaenderung, Schulungsbedarf, oder "kein
strukturelles Problem, Einzelfall".]

---
*Tipp: jedes geloeste Ticket hier nach demselben Muster ablegen -- daraus
entsteht mit der Zeit eine durchsuchbare Loesungssammlung statt Wissen nur
im Kopf einer Person.*""",
    },
    {
        "id": "support-email-anwendungsupdate",
        "modul": "support",
        "titel": "Vorlage: E-Mail-Ankuendigung Anwendungs-Update",
        "sprache": "markdown",
        "code": """Betreff: Wartungsfenster [Anwendung] am [Datum] von [Uhrzeit] bis [Uhrzeit]

Guten Tag,

am [Datum] fuehren wir zwischen [Uhrzeit] und [Uhrzeit] ein Update fuer
[Anwendung] durch.

**Was aendert sich fuer Sie:**
- [z. B. Neue Funktion X]
- [z. B. Bekannter Fehler Y wurde behoben]

**Was Sie beachten sollten:**
- [Anwendung] ist waehrend des Wartungsfensters nicht erreichbar.
- Bitte speichern Sie laufende Arbeiten vorher ab.
- [Falls zutreffend: Neuanmeldung nach dem Update erforderlich.]

Bei Rueckfragen erreichen Sie uns unter [Kontakt].

Freundliche Gruesse
[Name/Team]

---
*Change-Management-Hinweis: Diese Ankuendigung mindestens [X Tage] vorher
verschicken, bei kritischen Systemen zusaetzlich muendlich/telefonisch
bestaetigen lassen.*""",
    },
    {
        "id": "netz-vpn-tunnel-pruefen",
        "modul": "netz",
        "titel": "Site-to-Site-Tunnel und Routen pruefen",
        "sprache": "powershell",
        "code": """Get-NetIPsecMainModeSA | Select-Object LocalEndpoint, RemoteEndpoint, CipherAlgorithm
Get-NetIPsecQuickModeSA | Select-Object LocalSubnet, RemoteSubnet, EncryptionAlgorithm

# Erreichbarkeit der Gegenstelle pro Netz belegen
'10.50.0.10','10.50.1.10' | ForEach-Object {
    Test-NetConnection -ComputerName $_ -InformationLevel Detailed |
        Select-Object ComputerName, PingSucceeded, PingReplyDetails
}""",
    },
)

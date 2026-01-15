; =============================================================================
; COLAB GUI GENERATOR - Inno Setup Installer Script
; =============================================================================
; Erstellt einen professionellen Windows-Installer
;
; VORAUSSETZUNGEN:
;   1. Inno Setup 6+ installieren: https://jrsoftware.org/isinfo.php
;   2. PyInstaller-Build ausführen: python build_exe.py
;   3. Dieses Skript mit Inno Setup kompilieren
;
; ERGEBNIS:
;   ColabGUIGenerator_Setup.exe im Output-Ordner
; =============================================================================

#define MyAppName "Colab GUI Generator"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "Colab GUI Generator"
#define MyAppURL "https://github.com/colab-gui-generator"
#define MyAppExeName "ColabGUIGenerator.exe"

[Setup]
; Eindeutige ID für diese Anwendung (GUID generieren für Ihre Version)
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Installationsverzeichnis
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}

; Ausgabe
OutputDir=..\dist
OutputBaseFilename=ColabGUIGenerator_Setup_{#MyAppVersion}

; Kompression
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes

; Erscheinungsbild
WizardStyle=modern
SetupIconFile=..\assets\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

; Berechtigungen
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Weitere Optionen
DisableProgramGroupPage=yes
DisableWelcomePage=no
DisableDirPage=no
AllowNoIcons=yes
ShowLanguageDialog=auto

; Lizenz und Info (optional)
; LicenseFile=..\LICENSE.txt
; InfoBeforeFile=..\README.txt

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Hauptanwendung
Source: "..\dist\ColabGUIGenerator.exe"; DestDir: "{app}"; Flags: ignoreversion

; Dokumentation
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
; Startmenü
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{group}\Dokumentation"; Filename: "{app}\README.md"

; Desktop
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; Schnellstart
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Nach Installation starten (optional)
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
; Dateizuordnung für .ipynb (optional)
Root: HKCU; Subkey: "Software\Classes\.ipynb\OpenWithProgids"; ValueType: string; ValueName: "ColabGUIGenerator.ipynb"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\ColabGUIGenerator.ipynb"; ValueType: string; ValueName: ""; ValueData: "Jupyter Notebook"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\ColabGUIGenerator.ipynb\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKCU; Subkey: "Software\Classes\ColabGUIGenerator.ipynb\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

[UninstallDelete]
; Bereinige bei Deinstallation
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\cache"
Type: filesandordirs; Name: "{app}\__pycache__"

[Code]
// Prüfe ob bereits installiert
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  
  // Zeige Willkommensnachricht
  if MsgBox('Willkommen beim Colab GUI Generator Setup!' + #13#10 + #13#10 +
            'Diese Anwendung erstellt automatisch grafische Benutzeroberflächen ' +
            'für Ihre Google Colab Notebooks.' + #13#10 + #13#10 +
            'Möchten Sie fortfahren?', 
            mbConfirmation, MB_YESNO) = IDNO then
  begin
    Result := False;
  end;
end;

// Nach Installation
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Hier können zusätzliche Aktionen nach der Installation erfolgen
  end;
end;

// Vor Deinstallation
function InitializeUninstall(): Boolean;
begin
  Result := True;
  
  if MsgBox('Möchten Sie Colab GUI Generator wirklich deinstallieren?', 
            mbConfirmation, MB_YESNO) = IDNO then
  begin
    Result := False;
  end;
end;

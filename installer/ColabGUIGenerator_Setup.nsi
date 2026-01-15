; =============================================================================
; COLAB GUI GENERATOR - NSIS Installer Script
; =============================================================================
; Alternative zu Inno Setup - verwendet NSIS (Nullsoft Scriptable Install System)
;
; VORAUSSETZUNGEN:
;   1. NSIS installieren: https://nsis.sourceforge.io/Download
;   2. PyInstaller-Build ausführen: python build_exe.py
;   3. Dieses Skript mit NSIS kompilieren (Rechtsklick -> Compile NSIS Script)
;
; ERGEBNIS:
;   ColabGUIGenerator_Setup.exe
; =============================================================================

!include "MUI2.nsh"
!include "FileFunc.nsh"

; ============================================================================
; ALLGEMEINE EINSTELLUNGEN
; ============================================================================

!define PRODUCT_NAME "Colab GUI Generator"
!define PRODUCT_VERSION "2.0.0"
!define PRODUCT_PUBLISHER "Colab GUI Generator"
!define PRODUCT_WEB_SITE "https://github.com/colab-gui-generator"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\ColabGUIGenerator.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKCU"

; Kompression
SetCompressor /SOLID lzma
SetCompressorDictSize 64

; Installer-Attribute
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "..\dist\ColabGUIGenerator_Setup_${PRODUCT_VERSION}.exe"
InstallDir "$LOCALAPPDATA\${PRODUCT_NAME}"
InstallDirRegKey HKCU "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show
RequestExecutionLevel user

; ============================================================================
; MODERNE UI EINSTELLUNGEN
; ============================================================================

!define MUI_ABORTWARNING
!define MUI_ICON "..\assets\icon.ico"
!define MUI_UNICON "..\assets\icon.ico"

; Willkommensseite
!define MUI_WELCOMEPAGE_TITLE "Willkommen beim ${PRODUCT_NAME} Setup"
!define MUI_WELCOMEPAGE_TEXT "Dieser Assistent wird ${PRODUCT_NAME} ${PRODUCT_VERSION} auf Ihrem Computer installieren.$\r$\n$\r$\nDiese Anwendung erstellt automatisch grafische Benutzeroberflächen für Ihre Google Colab Notebooks.$\r$\n$\r$\nKlicken Sie auf Weiter, um fortzufahren."

; Fertigseite
!define MUI_FINISHPAGE_RUN "$INSTDIR\ColabGUIGenerator.exe"
!define MUI_FINISHPAGE_RUN_TEXT "${PRODUCT_NAME} jetzt starten"

; ============================================================================
; INSTALLER SEITEN
; ============================================================================

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Deinstallations-Seiten
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Sprachen
!insertmacro MUI_LANGUAGE "German"
!insertmacro MUI_LANGUAGE "English"

; ============================================================================
; INSTALLATION
; ============================================================================

Section "Hauptprogramm" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite on
  
  ; Hauptanwendung
  File "..\dist\ColabGUIGenerator.exe"
  
  ; Dokumentation
  File "..\README.md"
  
  ; Startmenü-Verknüpfungen
  CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk" "$INSTDIR\ColabGUIGenerator.exe"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\Dokumentation.lnk" "$INSTDIR\README.md"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\Deinstallieren.lnk" "$INSTDIR\uninst.exe"
  
  ; Desktop-Verknüpfung
  CreateShortCut "$DESKTOP\${PRODUCT_NAME}.lnk" "$INSTDIR\ColabGUIGenerator.exe"
SectionEnd

Section -Post
  ; Deinstaller erstellen
  WriteUninstaller "$INSTDIR\uninst.exe"
  
  ; Registry-Einträge für Deinstallation
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\ColabGUIGenerator.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
  
  ; Dateigröße berechnen
  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "EstimatedSize" "$0"
SectionEnd

; ============================================================================
; DEINSTALLATION
; ============================================================================

Section Uninstall
  ; Dateien entfernen
  Delete "$INSTDIR\ColabGUIGenerator.exe"
  Delete "$INSTDIR\README.md"
  Delete "$INSTDIR\uninst.exe"
  
  ; Verknüpfungen entfernen
  Delete "$DESKTOP\${PRODUCT_NAME}.lnk"
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk"
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\Dokumentation.lnk"
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\Deinstallieren.lnk"
  RMDir "$SMPROGRAMS\${PRODUCT_NAME}"
  
  ; Installationsverzeichnis entfernen
  RMDir /r "$INSTDIR\logs"
  RMDir /r "$INSTDIR\cache"
  RMDir "$INSTDIR"
  
  ; Registry-Einträge entfernen
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKCU "${PRODUCT_DIR_REGKEY}"
  
  SetAutoClose true
SectionEnd

; ============================================================================
; FUNKTIONEN
; ============================================================================

Function .onInit
  ; Sprache auswählen
  !insertmacro MUI_LANGDLL_DISPLAY
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Möchten Sie $(^Name) wirklich vollständig entfernen?" IDYES +2
  Abort
FunctionEnd

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) wurde erfolgreich von Ihrem Computer entfernt."
FunctionEnd

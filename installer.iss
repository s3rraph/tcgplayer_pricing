; Inno Setup script for TCG Price Adjuster.
; Ships the bundled Python (dependencies already installed) + app sources, so
; the install is fully offline. Stage dist_pkg\ with package.ps1 first, then
; compile this with iscc.exe.

#define AppName "TCG Price Adjuster"
#ifndef AppVer
  #define AppVer "0.0.0"
#endif

[Setup]
AppName={#AppName}
AppVersion={#AppVer}
DefaultDirName={localappdata}\Programs\TCG Price Adjuster
DefaultGroupName={#AppName}
OutputBaseFilename=TCGPriceAdjuster-Setup
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
; User-writable install (no admin) so the saved settings file works.
PrivilegesRequired=lowest
DisableProgramGroupPage=yes
WizardStyle=modern

[Files]
Source: "dist_pkg\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\python\pythonw.exe"; Parameters: "-s tcgplayer_pricing.py"; WorkingDir: "{app}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\python\pythonw.exe"; Parameters: "-s tcgplayer_pricing.py"; WorkingDir: "{app}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\python\pythonw.exe"; Parameters: "-s tcgplayer_pricing.py"; WorkingDir: "{app}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Runtime .pyc files and the saved settings aren't in the install manifest, so
; remove them explicitly to leave nothing behind.
Type: filesandordirs; Name: "{app}\python"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: files; Name: "{app}\settings.json"

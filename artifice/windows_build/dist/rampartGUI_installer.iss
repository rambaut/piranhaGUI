; -- ARTIFICE_installer.iss --
; script for installing artifice


[Setup]
AppName=rampartGUI
AppVersion=1.5.2
WizardStyle=modern
DefaultDirName={autopf}\rampartGUI
DefaultGroupName=rampartGUI
UninstallDisplayIcon={app}\.exe
Compression=lzma2
SolidCompression=yes
OutputDir=.\installer
OutputBaseFilename=rampartGUIv1.5.1_installer_windows

[Tasks]
Name: desktopicon; Description: "Create a &desktop icon";

[Files]
Source: "rampartGUI.exe"; DestDir: "{app}"
;Source: "runs\archived_runs.json"; DestDir: "{app}\runs"
Source: "resources\*"; DestDir: "{app}\resources"
Source: "builtin_protocols\*"; DestDir: "{app}\builtin_protocols"; Flags: ignoreversion recursesubdirs
Source: "config.yml"; DestDir: "{app}"

[Icons]
Name: "{group}\rampartGUI"; Filename: "{app}\rampartGUI.exe"
Name: "{commondesktop}\rampartGUI"; Filename: "{app}\rampartGUI.exe"; Tasks: desktopicon

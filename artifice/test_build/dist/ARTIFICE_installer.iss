; -- ARTIFICE_installer.iss --
; script for installing artifice


[Setup]
AppName=ARTIFICE
AppVersion=0.1.0
WizardStyle=modern
DefaultDirName={autopf}\artifice
DefaultGroupName=artifice
UninstallDisplayIcon={app}\ARTIFICE.exe
Compression=lzma2
SolidCompression=yes
OutputDir=.\installer

[Tasks]
Name: desktopicon; Description: "Create a &desktop icon";

[Files]
Source: "artifice.exe"; DestDir: "{app}"
;Source: "runs\archived_runs.json"; DestDir: "{app}\runs"
Source: "resources\poseqco_logo.png"; DestDir: "{app}\resources"
Source: "config.yml"; DestDir: "{app}"

[Icons]
Name: "{group}\ARTIFICE"; Filename: "{app}\artifice.exe"
Name: "{commondesktop}\ARTIFICE"; Filename: "{app}\artifice.exe"; Tasks: desktopicon

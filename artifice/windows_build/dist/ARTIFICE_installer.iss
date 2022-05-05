; -- ARTIFICE_installer.iss --
; script for installing artifice


[Setup]
AppName=piranhaGUI
AppVersion=1.1.1
WizardStyle=modern
DefaultDirName={autopf}\piranhaGUI
DefaultGroupName=pirahnaGUI
UninstallDisplayIcon={app}\.exe
Compression=lzma2
SolidCompression=yes
OutputDir=.\installer
OutputBaseFilename=PiranhaGUIv1.1.1_installer_windows

[Tasks]
Name: desktopicon; Description: "Create a &desktop icon";

[Files]
Source: "piranhaGUI.exe"; DestDir: "{app}"
;Source: "runs\archived_runs.json"; DestDir: "{app}\runs"
Source: "resources\poseqco_logo.png"; DestDir: "{app}\resources"
Source: "resources\LiberationSans-Regular.ttf"; DestDir: "{app}\resources"
Source: "resources\translation_scheme.csv"; DestDir: "{app}\resources"
Source: "resources\piranha.png"; DestDir: "{app}\resources"
Source: "config.yml"; DestDir: "{app}"

[Icons]
Name: "{group}\piranhaGUI"; Filename: "{app}\piranhaGUI.exe"
Name: "{commondesktop}\piranhaGUI"; Filename: "{app}\piranhaGUI.exe"; Tasks: desktopicon

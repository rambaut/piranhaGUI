pyinstaller piranhaGUI.spec
xcopy /s /e /D ..\resources .\dist\resources
copy ..\config.yml .\dist
xcopy /s /e /D ..\builtin_protocols .\dist\builtin_protocols


Set WshShell = CreateObject("WScript.Shell")
scriptPath = WScript.ScriptFullName
scriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(scriptPath)
WshShell.CurrentDirectory = scriptDir
WshShell.Run chr(34) & scriptDir & "\02_start_backend.bat" & chr(34), 0
Set WshShell = Nothing

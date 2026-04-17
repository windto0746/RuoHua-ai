$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\AIWriter.lnk")
$Shortcut.TargetPath = "C:\Users\zjw\Desktop\app.bat"
$Shortcut.WorkingDirectory = "C:\Users\zjw\.minimax-agent-cn\projects\5"
$Shortcut.Save()
Write-Host "Shortcut created: AIWriter.lnk"

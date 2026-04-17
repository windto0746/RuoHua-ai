$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\AIWriter.lnk")
$Shortcut.TargetPath = "C:\Users\zjw\Desktop\AIWriter.bat"
$Shortcut.WorkingDirectory = "C:\Users\zjw\Desktop"
$Shortcut.Save()
Write-Host "Done"

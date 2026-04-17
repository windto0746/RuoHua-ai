$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\VSCode_Chinese.lnk")
$Shortcut.TargetPath = "C:\Users\zjw\AppData\Local\Programs\Microsoft VS Code\Code.exe"
$Shortcut.Arguments = "--locale=zh-CN"
$Shortcut.Description = "VS Code Chinese"
$Shortcut.Save()
Write-Host "Shortcut created successfully"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\VS Code 中文版.lnk")
$Shortcut.TargetPath = "C:\Users\zjw\AppData\Local\Programs\Microsoft VS Code\Code.exe"
$Shortcut.Arguments = "--locale=zh-CN"
$Shortcut.Description = "Visual Studio Code 中文版"
$Shortcut.Save()
Write-Host "已创建中文版快捷方式到桌面"

# Create Desktop Shortcut
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:PUBLIC\Desktop\AIWriter.lnk")
$Shortcut.TargetPath = "C:\Users\zjw\.minimax-agent-cn\projects\5\启动文案生成器.bat"
$Shortcut.WorkingDirectory = "C:\Users\zjw\.minimax-agent-cn\projects\5"
$Shortcut.WindowStyle = 7
$Shortcut.Description = "AI Copywriting Generator v9.0"
$Shortcut.Save()

# Create Startup Shortcut
$StartupShortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\AIWriter.lnk")
$StartupShortcut.TargetPath = "C:\Users\zjw\.minimax-agent-cn\projects\5\启动文案生成器.bat"
$StartupShortcut.WorkingDirectory = "C:\Users\zjw\.minimax-agent-cn\projects\5"
$StartupShortcut.WindowStyle = 7
$StartupShortcut.Description = "AI Copywriting Generator v9.0"
$StartupShortcut.Save()

Write-Host "Done!"
Write-Host "Desktop: $env:PUBLIC\Desktop\AIWriter.lnk"
Write-Host "Startup: Added to startup folder"

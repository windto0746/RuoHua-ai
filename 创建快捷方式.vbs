Set WshShell = CreateObject("WScript.Shell")
Set oShellLink = WshShell.CreateShortcut("C:\Users\Public\Desktop\短视频AI文案生成器.lnk")
oShellLink.TargetPath = "C:\Users\zjw\.minimax-agent-cn\projects\5\启动文案生成器.bat"
oShellLink.WorkingDirectory = "C:\Users\zjw\.minimax-agent-cn\projects\5"
oShellLink.WindowStyle = 7
oShellLink.Description = "短视频AI文案生成器 v9.0"
oShellLink.Save

Set oShellLink2 = WshShell.CreateShortcut("C:\Users\zjw\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\短视频AI文案生成器.lnk")
oShellLink2.TargetPath = "C:\Users\zjw\.minimax-agent-cn\projects\5\启动文案生成器.bat"
oShellLink2.WorkingDirectory = "C:\Users\zjw\.minimax-agent-cn\projects\5"
oShellLink2.WindowStyle = 7
oShellLink2.Description = "短视频AI文案生成器 v9.0 - 开机自启动"
oShellLink2.Save

WScript.Echo "快捷方式创建成功！"
WScript.Echo "- 桌面快捷方式已创建"
WScript.Echo "- 开机自启动已设置"

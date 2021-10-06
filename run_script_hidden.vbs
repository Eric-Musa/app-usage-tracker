'Motivated by Daniel Morritt and Shaido's answer on StackOverflow:
'https://stackoverflow.com/questions/4277963/how-to-call-cmd-without-opening-a-window/28501808
Set objShell = WScript.CreateObject("WScript.Shell")
isHidden = 0 'change 0 to 1 to show the CMD prompt
objShell.Run "%comspec% /c run_script.bat", isHidden

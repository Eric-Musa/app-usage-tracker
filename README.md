# App-Usage-Tracker (for Windows)

### Inspired by analytics like Screen Time on iOS, this codebase allows Windows desktop users to track and be notified daily of their screen time.

---

### This program uses:
1. `psutil` to get data on running processes
2. `SQLite3` to store process data and track sent notifications
3. `smtplib` and `email` to send emails with Python (through GMail)
4. `Windows Task Scheduler` to run the usage-tracking program on a schedule
5. `VBScript` to run the usage-tracking program without a console window

---
![Screenshot of app usage summary email notification](https://github.com/Eric-Musa/app-usage-tracker/blob/main/gmail_notif_screenshot.PNG)

\*My desktop's name is "Bricktop" haha

---

### Future work:
 - assemble variable options into a single config file for user customization
 - implement a weekly summary of app usage
 - support for usage-tracking on *nix machines

---

### Please PR any improvements or contributions you've made, I'd be happy to collaborate on this project moving forward!

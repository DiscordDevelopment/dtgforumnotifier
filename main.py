import tkinter, customtkinter, psutil, time, subprocess, requests, urllib3
import browser_cookie3
from win10toast import ToastNotifier
from screeninfo import get_monitors
urllib3.disable_warnings()

toast = ToastNotifier()

def update_html(cookies):
    return requests.get('https://forums.dovetailgames.com/forums/pc-editor-discussion/', verify=False, cookies=cookies, timeout=3).text

def get_conversations(cookies):
    return requests.get('https://forums.dovetailgames.com/conversations/', verify=False, cookies=cookies, timeout=3).text

def get_message(html: str, cookies):
    try:
        amount=int(html.split("\"Total\">")[2].split("</span>")[0])
        conversations = get_conversations(cookies)
        conversation=str(conversations.split("class=\"discussionListItem unread\"")[1].split("class=\"listBlock main\"")[1].split("class=\"title\"")[1].split("/unread\">")[1].split("</a>")[0])
        author=str(conversations.split("class=\"discussionListItem unread\"")[1].split("class=\"listBlock lastPost\"")[1].split("dir=\"auto\">")[1].split("</a>")[0])
    except:
        author=None
        conversation=None
    return amount, author, conversation

def get_notification(html: str):
    try:
        amount=int(html.split("<span class=\"Total\">")[3].split("</span>")[0])
    except:
        amount=None
    return amount

current_messages=0
current_notifications=0

running=False

for monitor in get_monitors():
    if monitor.is_primary == True:
        width=int(monitor.width/2)
        height=int(monitor.height/2)

if width == None or height == None:
    print("No primary monitor is set, or the resolution could not be figured.")
    exit()

def toggle_notifier():
    global running, cookies
    if switch_variable.get() == True:
        success=True
        try:
            title.configure(text="Checking chrome cookies.")
            cookies = browser_cookie3.chrome(domain_name='.dovetailgames.com')
        except:
            success=False
            dialog = customtkinter.CTkInputDialog(text="Chrome needs to be restarted, type \"ok\" and confirm to restart now.", title="Chrome Restart necessary")
            dialog_input = dialog.get_input()
            if dialog_input == None:
                title.configure(text="Abgebrochen.")
                return
            if dialog_input.lower() == "ok":
                for proc in psutil.process_iter():
                    if proc.name() == "chrome.exe":
                        proc.kill()
                time.sleep(0.5)
                subprocess.Popen("C:\Program Files\Google\Chrome\Application\chrome.exe --disable-features=LockProfileCookieDatabase")
                time.sleep(2)
                cookies = browser_cookie3.chrome(domain_name='.dovetailgames.com')
                success=True
        html = update_html(cookies)
        if int(html.count("<a href=\"logout")) == 0:
            title.configure(text="You are not logged in.")
            return
        if success:
            running = True
            title.configure(text="Running...")
        else:
            switch_variable.set(False)
    else:
        running = False
        title.configure(text="Stopped...")

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

app=customtkinter.CTk()
app.geometry(f"{str(width)}x{str(height)}")
app.eval('tk::PlaceWindow . center')
app.title("Unofficial Dovetail Forum Viewer")

title = customtkinter.CTkLabel(app, text="Make sure, that you have logged in via Chrome...")
title.pack(padx=width/100, pady=height/100)

switch_variable = customtkinter.BooleanVar(value=False)
toggle_button_off = customtkinter.CTkRadioButton(app, text="Off", value=False, width=8, variable=switch_variable, command=toggle_notifier)
toggle_button_off.pack(padx=width/100, pady=height/80)

toggle_button_off = customtkinter.CTkRadioButton(app, text="On", value=True, width=8, variable=switch_variable, command=toggle_notifier)
toggle_button_off.pack(padx=width/100, pady=height/60)

def mainTask():
    global current_messages
    global current_notifications
    if running:
        try:
            html=update_html(cookies)
            m_amount, m_author, m_conversation = get_message(html, cookies)
            n_amount = get_notification(html)

            if m_author != None and current_messages < m_amount:
                toast.show_toast(
                    "Neue Nachricht",
                    m_author+"\nKonversation: "+m_conversation,
                    duration = 10,
                    icon_path = "dtg.ico",
                    threaded = True,
                )
            current_messages = m_amount

            if n_amount != None and current_notifications < n_amount:
                toast.show_toast(
                    "Neue Benachrichtigungen",
                    "Du hast "+str(n_amount)+" ungelese Benachrichtigungen.",
                    duration = 10,
                    icon_path = "dtg.ico",
                    threaded = True,
                )
            current_notifications = n_amount            
        except Exception as e:
            print(e)
        except KeyboardInterrupt:
            exit()
    app.after(2000, mainTask)

app.after(2000, mainTask)
app.mainloop()

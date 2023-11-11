import json
import requests
import time
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinter import messagebox

RATE_DELAY = 1

UserId = ''
FormattedUrl = 'http://inventory.roblox.com/v1/users/{0}/items/0/{1}/is-owned'
UserCheckUrl = 'https://users.roblox.com/v1/users/{0}'
ExitCalled = False


with open('Gears.json', 'r') as file:
    gears = json.load(file)

def RateLimited(url):
    global RATE_DELAY
    time.sleep(RATE_DELAY)
    Request = requests.get(url)
    if Request.status_code == 429 or Request.text == None or (Request.text != 'true' and Request.text != 'false'):
        return RateLimited(url)
    else:
        return Request.text
    
def IsTrue(str):
    return str.lower() in ['yes', '1', 'true', 't', 'y']

def Round(f, length):
    Rounded = round(f, length)
    Rounded = str(Rounded)
    if len(Rounded.split('.')) <= 1:
        Zeroes = ''
        for i in range(length):
            Zeroes = Zeroes+'0'
        Rounded = Rounded+'.'+Zeroes
    else:
        Decimal = Rounded.split('.')[1]
        if len(Decimal) < length:
            length -= len(Decimal)
            Zeroes = ''
            for i in range(length):
                Zeroes = Zeroes+'0'
            Rounded = Rounded+Zeroes
    return Rounded

def UserIdCheck(Input):
    NewUrl = UserCheckUrl.format(Input)
    r = requests.get(NewUrl)
    if r.status_code == 405:
        return 'False', 'nil'
    else:
        Json = r.json()
        if "errors" in Json.keys():
            return 'False', 'nil'
        else:
            name = Json['name']
            if Path(f"Users/{name}.json").is_file():
                return 'AlreadySaved', name
            return 'True', name
        

def RunScript(UserId, ProgressBar, StartButton, UserName):
    global ExitCalled
    StartButton.config(state="disabled")
    StartTime = time.time()
    Tools = {}
    NumItems = len(gears)
    ProgressBar['maximum'] = NumItems
    def Loop():
        global ExitCalled
        LoopedItems = 0
        for name, data in gears.items():
            if ExitCalled:
                break
            NewUrl = FormattedUrl.format(UserId, data['ID'])
            Request = requests.get(NewUrl)
            if Request.status_code == 429 or Request.text == None:
                Value = RateLimited(NewUrl)
            else:
                Value = Request.text
            LoopedItems += 1
            ProgressBar['value'] = LoopedItems
            root.update_idletasks()
            if IsTrue(Value):
                Tools[data['ID']] = name
        if not ExitCalled:
            with open(f'Users/{UserName}.json', 'w') as file:
                file.write(json.dumps(Tools))

            ProgressBar["value"] = 0
            StartButton.config(state="normal")
            messagebox.showinfo("Inventory Saved", f"Inventory Saved in {Round((time.time() - StartTime) / 60, 2)} Minutes")
        else:
            ExitCalled = False
            ProgressBar["value"] = 0
            StartButton.config(state="normal")
            messagebox.showinfo("Exit Called", "Script Has Been Cancelled")
    LoopThread = threading.Thread(target=Loop)
    LoopThread.start()

def Start():
    Input = UserIdInput.get()
    Success, name = UserIdCheck(Input)
    if Success == 'False':
        messagebox.showerror("Error Occured:", "Please Input A Valid UserId")
    elif Success == 'AlreadySaved':
        Answer = messagebox.askyesno("User Found:", f"{name} Already Found\nDo You Wish To Proceed")
        if Answer:
            messagebox.showinfo("Script Ran", f"Scanning {name}'s Inventory\nEstimated Time: 38 Minutes")
            RunScript(Input, ProgressBar, StartButton, name)
        else:
            pass
    elif Success == 'True':
        messagebox.showinfo("Script Ran", f"Scanning {name}'s Inventory\nEstimated Time: 38 Minutes")
        RunScript(Input, ProgressBar, StartButton, name)
    else:
        messagebox.showerror("Error Occured:", "Please Try Again")

def ExitScript():
    global ExitCalled
    ExitCalled = True

root = tk.Tk()
root.title("Inventory Viewer")
root.eval('tk::PlaceWindow . center')

root.configure(bg="#FFF5E1")

frame = ttk.Frame(root)
frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

style = ttk.Style()
style.configure("Brown.TLabel", foreground="#89775A")

Label = ttk.Label(frame, text="Enter a UserId:", style="Brown.TLabel")
Label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

UserIdInput = ttk.Entry(frame)
UserIdInput.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

style.configure("Brown.TButton", foreground="#89775A")

StartButton = ttk.Button(frame, text="Start", command=Start, style="Brown.TButton")
StartButton.grid(row=1, column=0, padx=5, pady=5, sticky="w")

ExitButton = ttk.Button(frame, text="Exit", command=ExitScript, style="Brown.TButton")
ExitButton.grid(row=1, column=1, padx=5, pady=5, sticky="e")

ProgressBar = ttk.Progressbar(frame, orient="horizontal", mode="determinate", maximum=100, length=0)
ProgressBar.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

root.resizable(False, False)

root.mainloop()
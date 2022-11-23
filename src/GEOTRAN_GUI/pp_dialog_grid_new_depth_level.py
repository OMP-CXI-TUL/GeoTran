import tkinter as tk
from tkinter import ttk

class NewDepthLevelGridDialog():

    def __init__(self, parent, title, value_label):
        self.topWin = tk.Toplevel(parent)
        self.topWin.transient(parent)
        self.topWin.grab_set()
        x = parent.winfo_x()
        y = parent.winfo_y()
        self.topWin.geometry("+%d+%d" % (x + 100, y + 100))
        if len(title) > 0: self.topWin.title(title)

        self.topWin.columnconfigure(1, weight=1)

        lbl = ttk.Label(self.topWin, text= 'Grid name :')
        lbl.grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        self.gridNameVar = tk.StringVar()
        self.gridNameVar.set('')
        entry = ttk.Entry(self.topWin, width=20, textvariable=self.gridNameVar)
        entry.grid(row=0, column=1, sticky=tk.EW, padx=2, pady=2)

        lbl = ttk.Label(self.topWin, text= value_label+':')
        lbl.grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        self.valueVar = tk.StringVar()
        self.valueVar.set(50)
        entry = ttk.Entry(self.topWin, width=20, textvariable=self.valueVar)
        entry.grid(row=1, column=1, sticky=tk.EW, padx=2, pady=2)

        btnOk = ttk.Button(self.topWin, text="OK", command=self.onOk, width=10)
        btnOk.grid(row=2, column=0, padx=2, pady=2, sticky=tk.E)
        self.btn_OK = False

        btnCancel = ttk.Button(self.topWin, text="Cancel", command=self.onCancel, width=10)
        btnCancel.grid(row=2, column=1, padx=2, pady=2, sticky=tk.W)
        


    def onOk(self, event=None):
        self.res_name = s if  (s:=self.gridNameVar.get().strip()) != "" else None
        self.res_value = self.valueVar.get()
        self.topWin.destroy()
        self.btn_OK = True
        

    def onCancel(self, event=None):
        self.topWin.destroy()

        



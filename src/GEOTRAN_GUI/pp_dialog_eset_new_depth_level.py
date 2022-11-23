import tkinter as tk
from tkinter import ttk

class NewDepthLevelEsetDialog():

    def __init__(self, parent, title, value_min_label, value_max_label):
        self.topWin = tk.Toplevel(parent)
        self.topWin.transient(parent)
        self.topWin.grab_set()
        x = parent.winfo_x()
        y = parent.winfo_y()
        self.topWin.geometry("+%d+%d" % (x + 100, y + 100))
        self.topWin.title(title)

        # # ovladaci prvky dialogoveho boxu
        # columns 3
        # rows 6

        # self.topWin.columnconfigure(0, minsize=10, pad=2)
        self.topWin.columnconfigure(1, weight=1, pad=2)


        lbl = ttk.Label(self.topWin, text= 'Elements set name: ')
        lbl.grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        self.esetNameVar = tk.StringVar(value='')
        entry = ttk.Entry(self.topWin, width=20, textvariable=self.esetNameVar)
        entry.grid(row=0, column=1, sticky=tk.EW, padx=2, pady=2)

        lbl = ttk.Label(self.topWin, text= value_min_label+': ')
        lbl.grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        self.valueMinVar = tk.StringVar(value="50")
        entry = ttk.Entry(self.topWin, width=20, textvariable=self.valueMinVar)
        entry.grid(row=1, column=1, sticky=tk.EW, padx=2, pady=2)

        lbl = ttk.Label(self.topWin, text= value_max_label+': ')
        lbl.grid(row=2, column=0, sticky=tk.W, padx=2, pady=2)
        self.valueMaxVar = tk.StringVar(value="100")
        entry = ttk.Entry(self.topWin, width=20, textvariable=self.valueMaxVar)
        entry.grid(row=2, column=1, sticky=tk.EW, padx=2, pady=2)

        btnOk = ttk.Button(self.topWin, text="OK", command=self.onOk, width=10)
        btnOk.grid(row=3, column=0, padx=2, pady=2, sticky=tk.E)
        self.btn_OK = False

        btnCancel = ttk.Button(self.topWin, text="Cancel", command=self.onCancel, width=10)
        btnCancel.grid(row=3, column=1, padx=2, pady=2, sticky=tk.W)
        


    def onOk(self, event=None):
        self.res_name = s if  (s:=self.esetNameVar.get().strip()) != "" else None
        self.res_min_value = self.valueMinVar.get()
        self.res_max_value = self.valueMaxVar.get()
        self.topWin.destroy()
        self.btn_OK = True
        

    def onCancel(self, event=None):
        self.topWin.destroy()

        



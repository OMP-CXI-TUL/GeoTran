import os
import tkinter as tk
from tkinter import ttk

class NewRegionsEsetDialog():

    def __init__(self, parent, title, regions_list):
      
        w = self.topWin = tk.Toplevel(parent)
        w.transient(parent)
        w.grab_set()
        x = parent.winfo_x()
        y = parent.winfo_y()
        w.geometry("+%d+%d" % (x + 100, y + 100))
        w.title(title)

        # # ovladaci prvky dialogoveho boxu
        w.columnconfigure(0, weight=1, pad=2)
        w.rowconfigure(6, weight=1, pad=2)

        lbl = ttk.Label(w, text= 'Elements set name: ')
        self.esetNameVar = tk.StringVar(value='')
        entry = ttk.Entry(w, width=50, textvariable=self.esetNameVar)
        lbl.grid(row=0, column=0, sticky=tk.W, padx=4, pady=2)
        entry.grid(row=1, column=0, sticky=tk.W+tk.E, padx=4, pady=2)

        lbl = tk.Label(w, text="Regions")        
        self.lb_regions = tk.Listbox(w, width=40, selectmode=tk.MULTIPLE)
        self.lb_regions.bind('<<ListboxSelect>>', self.on_lb_regions_selection)
        self.lb_regions.insert(tk.END, *regions_list)
        self.regselinfoVar = tk.StringVar()
        self.on_lb_regions_selection(None)
        lbl.grid(row=2, column=0, sticky=tk.W, pady=2, padx=4)
        self.lb_regions.grid(row=3, column=0, rowspan=6, padx=4, pady=2, sticky=tk.W+tk.E+tk.N+tk.S)
        
        lbr = tk.Label(w, textvariable=self.regselinfoVar)
        lbr.grid(row=3, column=1, padx=4, pady=2,sticky=tk.W)
        btn = ttk.Button(w, text="Select All", command=self.onregselectall, width=15)
        btn.grid(row=4, column=1, padx=4, pady=2, sticky=tk.E)
        btn = ttk.Button(w, text="Clear selection", command=self.onregclearsel, width=15)
        btn.grid(row=5, column=1, padx=4, pady=2, sticky=tk.E)
        
        btnOK = ttk.Button(w, text="OK", command=self.onOK, width=10)
        btnOK.grid(row=7, column=1, padx=10, pady=4, sticky=tk.S)
        self.btn_OK = False

        btnCancel = ttk.Button(self.topWin, text="Cancel", command=self.onCancel, width=10)
        btnCancel.grid(row=8, column=1, padx=10, pady=4, sticky=tk.S)
        
        
    def on_lb_regions_selection(self, event):
        self.regselinfoVar.set("{:d} / {:d} selected".format(len(self.lb_regions.curselection()), self.lb_regions.size()))

    def onregselectall(self):
        self.lb_regions.selection_set(0, tk.END)

    def onregclearsel(self):
        self.lb_regions.selection_clear(0, tk.END)


    def onOK(self, event=None):
        self.res_name = s if  (s:=self.esetNameVar.get().strip()) != "" else None
        if len(self.lb_regions.curselection()) == 0:
           tk.messagebox.showerror("No regions were selected.")
           return
        self.res_regions_name = [self.lb_regions.get(i) for i in self.lb_regions.curselection()]
        self.topWin.destroy()
        self.btn_OK = True


    def onCancel(self, event=None):
        self.topWin.destroy()

 


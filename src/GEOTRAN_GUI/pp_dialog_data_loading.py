
import tkinter as tk
from tkinter import ttk


class DataLoadingDialog():

    def __init__(self, parent, mesh_phases):
        
        w = self.topWin = tk.Toplevel(parent)
        w.transient(parent)
        w.grab_set()
        x = parent.winfo_x()
        y = parent.winfo_y()
        w.geometry("+%d+%d" % (x + 100, y + 100))
        w.title("Selecte data for loading")

        # ovladaci prvky dialogoveho boxu
        w.columnconfigure(0, weight=1)
        w.rowconfigure(7, weight=1)

        lbl = tk.Label(w, text="Species")        
        self.lb_species = tk.Listbox(w, width=30, exportselection=False, selectmode=tk.EXTENDED)
        lbl.grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        self.lb_species.grid(row=1, column=0, rowspan=9, padx=4, pady=4, sticky=tk.E+tk.W+tk.S+tk.N)
        
        lbl = tk.Label(w, text="Times")
        self.lb_times = tk.Listbox(w, width=15, exportselection=False, selectmode=tk.EXTENDED)
        lbl.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)
        self.lb_times.grid(row=1, column=1, rowspan=9, padx=4, pady=4, sticky=tk.E+tk.W+tk.S+tk.N)

        species, times = mesh_phases.load_names_times_of_element_data(None)
        self.lb_species.insert(tk.END, *species)
        self.lb_times.insert(tk.END, *times)

        btnOK = ttk.Button(self.topWin, text="OK", command=self.onOK, width=10)
        btnOK.grid(row=8, column=2, padx=4, pady=4)
        self.btn_OK = False

        btnCancel = ttk.Button(self.topWin, text="Cancel", command=self.onCancel, width=10)
        btnCancel.grid(row=9, column=2, padx=4, pady=4)
        

    def onOK(self, event=None):
        c = self.lb_times.curselection()
        if c is None: return
        self.res_times = [self.lb_times.get(i) for i in c]
        c = self.lb_species.curselection()
        if c is None: return
        self.res_species = [self.lb_species.get(i) for i in c]
        self.topWin.destroy()
        self.btn_OK = True


    def onCancel(self, event=None):
        self.topWin.destroy()

 


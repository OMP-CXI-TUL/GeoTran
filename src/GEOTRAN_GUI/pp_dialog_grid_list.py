import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk


class GridListDialog():

    def __init__(self, parent, mesh_phases):
        self.res_del = []
        self.phases = mesh_phases
      
        w = self.topWin = tk.Toplevel(parent)
        w.transient(parent)
        w.grab_set()
        x = parent.winfo_x()
        y = parent.winfo_y()
        w.geometry("+%d+%d" % (x + 100, y + 100))
        w.title("Grids")

        # ovladaci prvky
        w.rowconfigure(2, weight=1, pad=2, minsize=30)
        w.columnconfigure(0, weight=1, pad=2, minsize=50)

        lbl = tk.Label(w, text="List of grids")
        self.lb_grids = tk.Listbox(w, width=50, selectmode=tk.BROWSE)
        self._update_list()
        lbl.grid(row=0, column=0, sticky=tk.W, padx=4, pady=2)
        self.lb_grids.grid(row=1, column=0, rowspan=3, padx=4, pady=2, sticky=tk.E+tk.W+tk.S+tk.N)

        btnDelete = ttk.Button(w, text="Delete", command=self.onDelete, width=10)
        btnDelete.grid(row=1, column=1, pady=2, padx=4, sticky=tk.N)

        btnClose = ttk.Button(self.topWin, text="Close", command=self.onClose, width=10)
        btnClose.grid(row=3, column=1, pady=4, padx=4, sticky=tk.S)
        

    def _update_list(self):
        if (b:=self.lb_grids).size() > 0:
           i = b.curselection()[0]
           b.delete(0, tk.END)
           b.insert(tk.END, *self.phases.get_grids_name())
           b.selection_set(i)
        else:
           b.insert(tk.END, *self.phases.get_grids_name())


    def onDelete(self, event=None):
        a = self.lb_grids.curselection()
        if len(a) == 0: return
        self.phases.del_grid(s:=self.lb_grids.get(a[0]))
        self.res_del.append(s)
        self._update_list()

        

    def onClose(self, event=None):
        self.topWin.destroy()

 


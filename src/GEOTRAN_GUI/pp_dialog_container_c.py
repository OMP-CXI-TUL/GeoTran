import os, sys
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo


import CONTAINER_C


class ContainerCDialog():

    def __init__(self, parent, initialdir):
        self.initialdir = initialdir
        self.parent = parent
        w = self.topWin = tk.Toplevel(parent)
        w.transient(parent)
        w.grab_set()
        x = parent.winfo_x()
        y = parent.winfo_y()
        w.geometry("+%d+%d" % (x + 100, y + 100))
        w.title("Selected data loading")

        # ovladaci prvky dialogoveho boxu
        w.rowconfigure(5, weight=1, pad=2, minsize=20)
        w.columnconfigure(2, weight=1, pad=2, minsize=10)

        lbl = tk.Label(w, text="Input file:")
        lbl.grid(row=0, column=0, padx=4, pady=4, sticky=tk.W)
        self.fileVar = tk.StringVar(value="")
        lbl = tk.Label(w, textvariable=self.fileVar)
        lbl.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)
        self.edit = tk.scrolledtext.ScrolledText(w)
        self.edit.grid(row=1, column=0, rowspan=9, columnspan=3, padx=4, pady=4, sticky=tk.E+tk.W+tk.N+tk.S)

        btn = ttk.Button(w, text="Open", command=self.onOpen)
        btn.grid(row=1, column=3, sticky=tk.W+tk.E, padx=8, pady=4)

        btn = ttk.Button(w, text="Save", command=self.onSave)
        btn.grid(row=2, column=3, sticky=tk.W + tk.E, padx=8, pady=4)

        btn = ttk.Button(w, text="Save as", command=self.onSaveas)
        btn.grid(row=3, column=3, sticky=tk.W + tk.E, padx=8, pady=4)

        btn = ttk.Button(w, text="Save and Run", command=self.onSaveRun)
        btn.grid(row=4, column=3, sticky=tk.W + tk.E, padx=8, pady=4)

        btn = ttk.Button(w, text="Close", command=self.onClose)
        btn.grid(row=6, column=3, sticky=tk.W+tk.E, padx=8, pady=4)

        self.onOpen()


    def onSaveRun(self, event=None):
       input_file = self.fileVar.get()
       with open(input_file, "w") as f:
          f.write(self.edit.get("1.0", "end"))
       print("Executing Container C ...")
       self.parent.config(cursor="wait")
       if not CONTAINER_C.execute_model_as_function(input_file):
          showerror(title="Container C", message="Error occurred during execution.")
       else:
          showinfo(title="Container C", message="Calculation is complete.")
       print("Executing Container C was finished.")
       self.parent.config(cursor="")


    def onSave(self, event=None):
       input_file = self.fileVar.get()
       with open(input_file, "w") as f:
          f.write(self.edit.get("1.0", "end"))


    def onSaveas(self, event=None):
        filepath = tk.filedialog.asksaveasfilename(
            parent=self.topWin,
            title='Save Container C input file',
            initialdir=self.initialdir,
            defaultextension="*.yaml",
            filetypes=[("Container C input file (*.yaml)", "*.yaml")])
        if filepath == "": return
        self.initialdir = os.path.dirname(filepath)
        self.fileVar.set(filepath)
        self.onSave()


    def onOpen(self, event=None):
        filepath = tk.filedialog.askopenfilename(
            parent=self.topWin,
            title='Open container C input file',
            initialdir=self.initialdir,
            defaultextension="*.yaml",
            filetypes=[("Container C input file (*.yaml)","*.yaml")])
        if filepath == "": return
        self.initialdir = os.path.dirname(filepath)
        with open(filepath) as f:
           for s in f: self.edit.insert(tk.END, s)
        self.fileVar.set(filepath) 



    def onClose(self, event=None):
       self.topWin.destroy()

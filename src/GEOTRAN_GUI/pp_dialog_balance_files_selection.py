import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk


class BalanceFileSelectionDialog():

    def __init__(self, parent, title, fileTypes, currentDir):
        '''
        Frame for the modal dialog box that enables create list of selected files
        :param parent: parent frame/window
        :param title: title of the window
        :param currentDir: String with initial directory
        :param fileExtensions: Data structure with file extensions
        :param resultVariable: variable, that will store the result of the modal window
        '''
        self.currentDir = currentDir
        self.fileTypes = fileTypes
        self.topWin = tk.Toplevel(parent)
        self.topWin.transient(parent)
        self.topWin.grab_set()
        x = parent.winfo_x()
        y = parent.winfo_y()
        self.topWin.geometry("+%d+%d" % (x + 100, y + 100))
        if len(title) > 0: self.topWin.title(title)

        # # ovladaci prvky dialogoveho boxu
        self.topWin.columnconfigure(1, weight=1)
        self.topWin.columnconfigure(3, pad=7)
        self.topWin.rowconfigure(4, weight=1)
        self.topWin.rowconfigure(8, pad=7)
        lbl = tk.Label(self.topWin, text="Selected files")
        lbl.grid(sticky=tk.W, pady=2, padx=5)
        self.lbFiles = tk.Listbox(self.topWin, width=100) #, selectmode=tk.EXTENDED) # , selectmode=tk.MULTIPLE)
        self.lbFiles.grid(row=1, column=0, columnspan=2, rowspan=6,
            padx=5, pady=2, sticky=tk.E+tk.W+tk.S+tk.N)
        btnAdd = ttk.Button(self.topWin, text="Add", command=self.onAdd, width=10)
        btnAdd.grid(row=1, column=3, pady=4, padx=4)
        btnInsert = ttk.Button(self.topWin, text="Insert", command=self.onInsert, width=10)
        btnInsert.grid(row=2, column=3, pady=4, padx=4)
        btnDelete = ttk.Button(self.topWin, text="Delete", command=self.onDelete, width=10)
        btnDelete.grid(row=3, column=3, pady=4, padx=4)
        lbl = ttk.Label(self.topWin, text=" ")
        lbl.grid(row=4, column=3, pady=4)

        btnOk = ttk.Button(self.topWin, text="OK", command=self.onOk, width=10)
        btnOk.grid(row=5, column=3, pady=4, padx=4)
        self.btn_OK = False

        btnCancel = ttk.Button(self.topWin, text="Cancel", command=self.onCancel, width=10)
        btnCancel.grid(row=6, column=3, pady=4, padx=4)
        

    def onAdd(self, event=None):
        self.onInsert(event, append=True)
        

    def onInsert(self, event=None, append=False):
        filepaths = tk.filedialog.askopenfilenames(
            parent=self.topWin,
            title='Select balance file/files',
            initialdir=self.currentDir,
            defaultextension=self.fileTypes[0][1],
            filetypes=self.fileTypes)
        if filepaths is None: return
        pos = tk.END if append else tk.ANCHOR
        if len(filepaths) > 0:
            for fp in filepaths: self.lbFiles.insert(pos, fp)
            self.currentDir = os.path.dirname(filepaths[0])
        

    def onDelete(self, event=None):
        if not self.lbFiles.curselection():
            return
        self.lbFiles.delete(tk.ANCHOR)
        

    def onOk(self, event=None):
        self.res_file_names = list(self.lbFiles.get(0, tk.END))
        if len(self.res_file_names) == 0: return
        self.topWin.destroy()
        self.btn_OK = True
     

    def onCancel(self, event=None):
        self.topWin.destroy()

 


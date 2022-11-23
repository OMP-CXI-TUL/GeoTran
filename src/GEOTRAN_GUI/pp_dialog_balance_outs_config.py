from email import message
import tkinter as tk
from tkinter import ttk
from functools import partial
from tkinter.messagebox import showinfo

#from setuptools.command.register import register


class BalanceOutputConfigurationDialog():

    def __init__(self, parent, title, regionsList, quantitiesList, speciesList, regionMultisel=False):

        self.recordValue = [None, None, None]
        w = self.topWin = tk.Toplevel(parent)
        w.transient(parent)
        w.grab_set()
        x = parent.winfo_x()
        y = parent.winfo_y()
        w.geometry("+%d+%d" % (x + 100, y + 100))
        w.title(title)

        # ovladaci prvky dialogoveho boxu
        w.columnconfigure(0, weight=1, minsize=10, pad=2)
        w.columnconfigure(1, weight=1, minsize=10, pad=2)
        w.columnconfigure(2, weight=1, minsize=10, pad=2)
        w.columnconfigure(3, weight=0, minsize=10, pad=2)
        w.columnconfigure(4, weight=5, minsize=40, pad=2)
        w.rowconfigure(3, minsize=10, pad=2)
        w.rowconfigure(7, weight=1, minsize=20, pad=2)

        # column 0 - regions
        lbl = ttk.Label(w, text='Regions')
        lbl.grid(row=0, column=0, sticky=tk.W)
        #selmode = tk.MULTIPLE if regionMultisel else tk.SINGLE
        selmode = tk.EXTENDED if regionMultisel else tk.SINGLE
        self.lbRegions = tk.Listbox(w, width=25, selectforeground='Black', activestyle='underline', selectmode=selmode)
        self.lbRegions.grid(row=1, column=0, rowspan=9, columnspan=1, padx=2, pady=2, sticky=tk.W+tk.E+tk.S+tk.N)
        self.lbRegions.insert(tk.END, *regionsList)
        self.lbRegions.bind('<<ListboxSelect>>', partial(self.onLbSelection, respos=0))

        # column 1 - quantities
        lbl = ttk.Label(w, text='Quantities')
        lbl.grid(row=0, column=1, sticky=tk.W, pady=2)
        self.lbQuantities = tk.Listbox(w, width=15, selectforeground='Black', selectmode=tk.SINGLE)
        self.lbQuantities.grid(row=1, column=1, rowspan=9, columnspan=1, padx=2, pady=2, sticky=tk.W+tk.E+tk.S+tk.N)
        self.lbQuantities.insert(tk.END, *quantitiesList)
        self.lbQuantities.bind('<<ListboxSelect>>', partial(self.onLbSelection, respos=1))

        # column 2 - species
        lbl = ttk.Label(w, text='Species')
        lbl.grid(row=0, column=2, sticky=tk.W, pady=2)
        self.lbSpecies = tk.Listbox(w, width=15, selectforeground='Black', selectmode=tk.SINGLE)
        self.lbSpecies.grid(row=1, column=2, rowspan=9, columnspan=1, padx=2, pady=2, sticky=tk.W+tk.E+tk.S+tk.N)
        self.lbSpecies.insert(tk.END, *speciesList)
        self.lbSpecies.bind('<<ListboxSelect>>', partial(self.onLbSelection, respos=2))

        # column 4 - outputs
        lbl = ttk.Label(w, text='Ouput fields')
        lbl.grid(row=0, column=4, sticky=tk.W, pady=2)
        self.cols_dict = {}
        self.lbOutputs = tk.Listbox(self.topWin, width=40, selectforeground='Black',
                                    selectmode=tk.SINGLE)  # , selectmode=tk.EXTENDED)
        self.lbOutputs.grid(row=1, column=4, rowspan=9, columnspan=1, padx=2, pady=2, sticky=tk.W+tk.E+tk.S+tk.N)
        #self.lbOutputs.bind('<<ListboxSelect>>', partial(self.onLbSelection))

        # column 3 - buttons etc
        lbl = ttk.Label(self.topWin, text='Times')
        lbl.grid(row=1, column=3, padx=2, sticky=tk.W)
        self.cbTimes = ttk.Combobox(self.topWin, width=25, state = "readonly",
                                    values=('Remove phase initial times',
                                            'Remove phase terminal times',
                                            'Keep all time values'))
        self.cbTimes.current(0)
        self.cbTimes.grid(row=2, column=3, padx=2, pady=2)
        

        btnAdd = ttk.Button(self.topWin, text="Add", command=self.onAdd, width=10)
        btnAdd.grid(row=4, column=3, padx=2, pady=2)

        # btnInsert = ttk.Button(self.topWin, text="Insert", command=self.onInsert, width=10)
        # btnInsert.grid(row=5, column=3, padx=2, pady=2)

        btnDelete = ttk.Button(self.topWin, text="Delete", command=self.onDelete, width=10)
        btnDelete.grid(row=6, column=3, padx=2, pady=2)

        btnOk = ttk.Button(self.topWin, text="OK", command=self.onOk, width=10)
        btnOk.grid(row=8, column=3, padx=2, pady=2)
        self.btn_OK = False

        btnCancel = ttk.Button(self.topWin, text="Cancel", command=self.onCancel, width=10)
        btnCancel.grid(row=9, column=3, padx=2, pady=2)



    def onLbSelection(self, event=None, respos=None):
        sourceLb = event.widget
        if not sourceLb.curselection(): return
        for index in range(sourceLb.size()):
            if index in sourceLb.curselection(): sourceLb.itemconfig(index,{'bg': 'skyblue'})
            else: sourceLb.itemconfig(index,{'bg': ''})
        if respos is None: return
        value = [sourceLb.get(x) for x in sourceLb.curselection()]   
        if respos is not None: self.recordValue[respos] = value
     
       
    def GetExcludeTimeValue(self):
        return ('first', 'last', None)[self.cbTimes.current()]
        

    def onAdd(self, event=None, insert=False):
        self.onInsert(event, append=True)
        

    # insert se aktualne nepouziva, v tomto dialogu asi nema smysl
    def onInsert(self, event=None, append=False):
        if None in self.recordValue:
            tk.messagebox.showerror('Error',
                                    'One of the recor part is not selected.\n'
                                    'Select region, quantity a specie and try again'.format())
            return
        pos = tk.END if append else tk.ANCHOR
        v = self.recordValue
        lb_text = "(" + ",".join(v[0]) + ") / " + v[1][0] + " / " + v[2][0]
        self.lbOutputs.insert(pos, lb_text)
        self.cols_dict[lb_text] = [v[0], v[1][0], v[2][0]]
        

    def onDelete(self, event=None):
        if not self.lbOutputs.curselection():
            tk.messagebox.showwarning('Warning',
                                      'Nothing to delete. \nNo item is selected in Output Fields.'.format())
            return
        self.lbOutputs.delete(tk.ANCHOR)
        

    def _get_output_file(self):
        file_name = tk.filedialog.asksaveasfilename(
            parent=self.topWin,
            title='Set balance output file',
            initialdir=".",
            defaultextension="*.csv",
            filetypes=[("csv", "*.csv"),("txt", "*.txt")])
        return file_name



    def onOk(self, event=None):
        if self.lbOutputs.size() == 0:
           showinfo(message="No column in output file was defined.")
           return
        self.res_columns = [self.cols_dict[s] for s in self.lbOutputs.get(0, tk.END)]
        self.res_exclude_phase_time = self.GetExcludeTimeValue()
        self.res_output_file_name = self._get_output_file()
        if self.res_output_file_name is None: return
        self.topWin.destroy()
        self.btn_OK = True
        

    def onCancel(self, event=None):
        self.topWin.destroy()
 
        

  
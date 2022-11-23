import os
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror

class ReportBase1Dialog():

    def __init__(self, parent, title, phases, model_type, output_dir, output_type):

        self.phases = phases
        self.model_type = model_type
        self.output_dir = output_dir
        self.output_type = output_type
        
        w = self.topWin = tk.Toplevel(parent)
        w.transient(parent)
        w.grab_set()
        x = parent.winfo_x()
        y = parent.winfo_y()
        w.geometry("+%d+%d" % (x + 100, y + 100))
        w.title(title)

        # ovladaci prvky dialogoveho boxu
        w.rowconfigure(6, weight=1, pad=2, minsize=30)
        w.columnconfigure(0, weight=1, pad=2, minsize=20)

        # models
        self.lb_models = tk.Listbox(w, width=40, selectforeground='Black', activestyle='underline',
                                    exportselection=False, selectmode=tk.EXTENDED)
        self.lb_models.grid(row=1, rowspan=7, column=0, padx=4, pady=2, sticky=tk.W+tk.E+tk.S+tk.N)
        if model_type == "eset":
           lbl = ttk.Label(w, text="Elements set:")           
           self.lb_models.insert(tk.END, *phases.get_esets_name())
        elif model_type == "grid":
           lbl = ttk.Label(w, text="Grids:")           
           self.lb_models.insert(tk.END, *phases.get_grids_name())
        lbl.grid(row=0, column=0, sticky=tk.W)

        # column 1 - species
        lbl = ttk.Label(w, text='Species:')
        self.lb_species = tk.Listbox(w, width=20, selectforeground='Black', exportselection=False, selectmode=tk.EXTENDED)
        self.lb_species.insert(tk.END, *phases.get_e_data_names_loaded())
        lbl.grid(row=0, column=1, sticky=tk.W)
        self.lb_species.grid(row=1, column=1, rowspan=7, padx=2, pady=2, sticky=tk.W+tk.E+tk.S+tk.N)
       
        # column 2 - times
        lbl = ttk.Label(w, text='Times:')
        self.lb_times = tk.Listbox(w, width=10, selectforeground='Black', exportselection=False, selectmode=tk.EXTENDED)
        self.lb_times.bind('<<ListboxSelect>>', self.on_lb_times_selection)
        self.lb_times.insert(tk.END, *phases.get_e_data_times_loaded())
        lbl.grid(row=0, column=2, sticky=tk.W)
        self.lb_times.grid(row=1, column=2, rowspan=7, padx=4, pady=2, sticky=tk.W+tk.E+tk.S+tk.N)

        lbl = ttk.Label(w, text='Exclude times:')
        self.cb_extimes = ttk.Combobox(self.topWin, width=35, state = "readonly",
                                    values=('Remove phase initial times',
                                            'Remove phase terminal times',
                                            'Keep all time values'))
        self.cb_extimes.current(0)
        lbl.grid(row=1, column=4, padx=4, pady=2, sticky=tk.W)
        self.cb_extimes.grid(row=1, column=5, padx=4, pady=2, sticky=tk.W+tk.E)

        self.timesselinfoVar = tk.StringVar()
        self.on_lb_times_selection(None)
        lbr = tk.Label(w, textvariable=self.timesselinfoVar)
        lbr.grid(row=1, column=3, padx=4, pady=2, sticky=tk.W)
        btn = ttk.Button(w, text="Select all", command=self.ontimesselectall)
        btn.grid(row=2, column=3, padx=4, pady=2, sticky=tk.EW)
        btn = ttk.Button(w, text="Clear selection", command=self.ontimesclearselection)
        btn.grid(row=3, column=3, padx=4, pady=2, sticky=tk.EW)

        btnOk = ttk.Button(w, text="OK", command=self.onOk, width=10)
        btnOk.grid(row=7, column=5, padx=10, pady=4, sticky=tk.W)
        self.btn_OK = False

        btnCancel = ttk.Button(w, text="Cancel", command=self.onCancel, width=10)
        btnCancel.grid(row=7, column=5, padx=10, pady=4, sticky=tk.E)

        
    def get_exclude_phase_time(self):
       return ('first', 'last', None)[self.cb_extimes.current()]

        
    def _get_output_file(self):
        file_name = tk.filedialog.asksaveasfilename(
            parent=self.topWin,
            title='Set report output file',
            initialdir=self.output_dir,
            defaultextension="*.csv",
            filetypes=[("*.csv", "*.csv"),("*.txt", "*.txt")])
        self.output_dir = os.path.dirname(file_name)
        return file_name


    def _get_output_dir(self):
        dir = tk.filedialog.askdirectory(
            parent=self.topWin,
            title='Set report output file',
            initialdir=self.output_dir)
        self.output_dir = dir
        return dir


    def __set_next_result__(self):
       # predefinovat v potomkovi
       # pridani dalsich parametru v zavislosti na konkretni uloze
       return True


    def on_lb_times_selection(self, event):
       self.timesselinfoVar.set("{:d} / {:d} selected".format(len(self.lb_times.curselection()), self.lb_times.size()))

    def ontimesselectall(self):
       self.lb_times.selection_set(0, tk.END)

    def ontimesclearselection(self):
       self.lb_times.selection_clear(0, tk.END)

    def onOk(self, event=None):
        self.res_models = [self.lb_models.get(i) for i in self.lb_models.curselection()]
        self.res_species = [self.lb_species.get(i) for i in self.lb_species.curselection()]
        self.res_times = [self.lb_times.get(i) for i in self.lb_times.curselection()]
        if len(self.res_models) == 0 or len(self.res_species) == 0 or len(self.res_times) == 0:
           m = "elements set" if self.model_type=="eset" else "grid"
           showerror(title="Error", message="No " + m + ", specie or time was not selected.")
           return
        self.res_exclude_phase_time = self.get_exclude_phase_time()
        if not self.__set_next_result__(): return
        if self.output_type == "file":
           self.res_output_file_name = self._get_output_file()
           if self.res_output_file_name == "": return
        elif self.output_type == "dir":
           self.res_output_dir = self._get_output_dir()
           if self.res_output_dir == "": return          
        self.topWin.destroy()
        self.btn_OK = True
      
        
    def onCancel(self, event=None):
        self.topWin.destroy()
 
        

  
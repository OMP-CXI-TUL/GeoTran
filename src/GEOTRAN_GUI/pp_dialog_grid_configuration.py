import tkinter as tk
from tkinter import ttk

class GridConfigurationDialog():

    def __init__(self, parent, phases):

        self.phases = phases

        w = self.topWin = tk.Toplevel(parent)
        w.transient(parent)
        w.grab_set()
        x = parent.winfo_x()
        y = parent.winfo_y()
        w.geometry("+%d+%d" % (x + 100, y + 100))
        w.title("Grid configuration")

        # # ovladaci prvky dialogoveho boxu
        # columns 3
        # rows 5

        # self.topWin.columnconfigure(0, minsize=10, pad=2)
        # self.topWin.columnconfigure(1, minsize=10, pad=2)
        # self.topWin.columnconfigure(2, minsize=10, pad=2)

        lbl = ttk.Label(w, text='Min. value')
        lbl.grid(row=0, column=1, padx=2, pady=2)
        lbl = ttk.Label(w, text='Max. value')
        lbl.grid(row=0, column=2, padx=2, pady=2)
        lbl = ttk.Label(w, text="Difference")
        lbl.grid(row=0, column=3, padx=2, pady=2)
        
        lbl = ttk.Label(w, text='X range:')
        lbl.grid(row=1, column=0, sticky=tk.E, padx=2, pady=2)
        self.minxVar = tk.StringVar()
        self.minxVar.trace("w", self.onrangechanged)
        entry = ttk.Entry(w, width= 15, textvariable=self.minxVar, validatecommand=self.onrangechanged)
        entry.grid(row=1, column=1, sticky=tk.EW, padx=2, pady=2)
        self.maxxVar = tk.StringVar()
        self.maxxVar.trace("w", self.onrangechanged)
        entry = ttk.Entry(w, width= 15, textvariable=self.maxxVar)
        entry.grid(row=1, column=2, sticky=tk.EW, padx=2, pady=2)
        self.xrangeVar = tk.StringVar(value='0')
        lbl = ttk.Label(w, textvariable=self.xrangeVar)
        lbl.grid(row=1, column=3, padx=2, pady=2)

        lbl = ttk.Label(w, text='Y range:')
        lbl.grid(row=2, column=0, sticky=tk.E, padx=2, pady=2)
        self.minyVar = tk.StringVar()
        self.minyVar.trace("w", self.onrangechanged)
        entry = ttk.Entry(w, width=15, textvariable=self.minyVar)
        entry.grid(row=2, column=1, sticky=tk.EW, padx=2, pady=2)
        self.maxyVar = tk.StringVar()
        self.maxyVar.trace("w", self.onrangechanged)
        entry = ttk.Entry(w, width=15, textvariable=self.maxyVar)
        entry.grid(row=2, column=2, sticky=tk.EW, padx=2, pady=2)
        self.yrangeVar = tk.StringVar()
        lbl = ttk.Label(w, textvariable=self.yrangeVar)
        lbl.grid(row=2, column=3, padx=2, pady=2)

        b = ttk.Button(w, text="Reset to mesh X, Y extent", command=self.onmaxrange, width=32)
        b.grid(row=3, column=1, columnspan=2, padx=2, pady=2, sticky=tk.E)

        lbl = ttk.Label(w, text='Raster step:')
        lbl.grid(row=5, column=0, sticky=tk.E, padx=2, pady=2)
        self.rasterSizeVar = tk.StringVar()
        entry = ttk.Entry(w, width=15, textvariable=self.rasterSizeVar)
        entry.grid(row=5, column=1, sticky=tk.EW, padx=2, pady=2)

        lbl = ttk.Label(w, text='Use at most (1-20):')
        lbl.grid(row=6, column=0, sticky=tk.W, padx=2, pady=2)
        self.maxInterpPointsVar = tk.StringVar()
        entry = ttk.Entry(w, width=15, textvariable=self.maxInterpPointsVar)
        entry.grid(row=6, column=1, sticky=tk.EW, padx=2, pady=2)
        lbl = ttk.Label(w, text=' interpolation points ')
        lbl.grid(row=6, column=2, columnspan=2, sticky=tk.W, padx=2, pady=2)

        btnOk = ttk.Button(self.topWin, text="OK", command=self.onOk, width=10)
        btnOk.grid(row=7, column=2, padx=2, pady=2, sticky=tk.E)
        self.btn_OK = False

        btnCancel = ttk.Button(self.topWin, text="Cancel", command=self.onCancel, width=10)
        btnCancel.grid(row=7, column=3, padx=2, pady=2, sticky=tk.W)

        self.onmaxrange()
       
      
    def set_inputs(self, inputs):
       self.minxVar.set(inputs[0])
       self.maxxVar.set(inputs[1])
       self.minyVar.set(inputs[2])
       self.maxyVar.set(inputs[3])
       self.rasterSizeVar.set(inputs[4])
       self.maxInterpPointsVar.set(inputs[5])


    def onrangechanged(self, name, index, mode):
       try:
          s = "{:g}".format(float(self.maxxVar.get()) - float(self.minxVar.get()))
       except:
          s = "XXX"
       self.xrangeVar.set(s)
       try:
          s = "{:g}".format(float(self.maxyVar.get()) - float(self.minyVar.get()))
       except:
          s = "XXX"
       self.yrangeVar.set(s)


    def onmaxrange(self, event=None):
       r = self.phases.get_xyz_maximum_range()
       self.minxVar.set(r[0])
       self.maxxVar.set(r[3])
       self.minyVar.set(r[1])
       self.maxyVar.set(r[4])


    def onOk(self, event=None):
        self.res_min_x = self.minxVar.get()
        self.res_max_x = self.maxxVar.get()
        self.res_min_y = self.minyVar.get()
        self.res_max_y = self.maxyVar.get()
        self.res_raster_step = self.rasterSizeVar.get()
        self.res_max_interp_points = self.maxInterpPointsVar.get()
        self.res_inputs = [self.res_min_x, self.res_max_x, self.res_min_y, self.res_max_y, self.res_raster_step, self.res_max_interp_points]
        self.topWin.destroy()
        self.btn_OK = True
        

    def onCancel(self, event=None):
        self.topWin.destroy()
   
        



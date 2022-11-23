import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

class TimeConfigurationDialog():
    timeUnitLabels = ('Seconds', 'Years', '1000 years')
    timeUnitsValues = ('s', 'y', '1000.y')

    def __init__(self, parent, title, input_unit, output_unit):
        self.topWin = tk.Toplevel(parent)
        self.topWin.transient(parent)
        self.topWin.grab_set()
        x = parent.winfo_x()
        y = parent.winfo_y()
        self.topWin.geometry("+%d+%d" % (x + 100, y + 100))
        if len(title) > 0: self.topWin.title(title)

        # # ovladaci prvky dialogoveho boxu
        self.topWin.columnconfigure(0, weight=0, pad=2)
        self.topWin.columnconfigure(1, weight=1, minsize=22, pad=2)

        lbl = ttk.Label(self.topWin, text='Time unit in input files (ie model output files)')
        lbl.grid(row=0, column=0, sticky=tk.E, padx=2, pady=2)
        lbl = ttk.Label(self.topWin, text='Time unit in output reports')
        lbl.grid(row=1, column=0, sticky=tk.E, padx=2, pady=2)

        self.cbTimeUnitInput = ttk.Combobox(self.topWin, width=22, state="readonly", values=self.timeUnitLabels)
        self.cbTimeUnitInput.current(self.timeUnitsValues.index(input_unit))
        self.cbTimeUnitInput.grid(row=0, column=1, padx=2, pady=2, sticky=tk.W+tk.E)

        self.cbTimeUnitOutput = ttk.Combobox(self.topWin, width=22, state="readonly", values=self.timeUnitLabels)
        self.cbTimeUnitOutput.current(self.timeUnitsValues.index(output_unit))
        self.cbTimeUnitOutput.grid(row=1, column=1, padx=2, pady=2, sticky=tk.W+tk.E)

        btnOk = ttk.Button(self.topWin, text="OK", command=self.onOk, width=10)
        btnOk.grid(row=2, column=1, padx=2, pady=2, sticky=tk.W)
        self.btn_OK = False

        btnCancel = ttk.Button(self.topWin, text="Cancel", command=self.onCancel, width=10)
        btnCancel.grid(row=2, column=1, padx=2, pady=2, sticky=tk.E)
        

    def onOk(self, event=None):
        self.res_input_unit = self.timeUnitsValues[self.cbTimeUnitInput.current()]
        self.res_output_unit = self.timeUnitsValues[self.cbTimeUnitOutput.current()]
        self.topWin.destroy()
        self.btn_OK = True
        

    def onCancel(self, event=None):
        self.topWin.destroy()
 
        

   


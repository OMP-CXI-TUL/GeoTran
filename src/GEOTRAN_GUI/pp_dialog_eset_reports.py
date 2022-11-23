
import tkinter as tk
from tkinter.messagebox import showinfo
from tkinter import ttk

from pp_dialog_report_base_1 import ReportBase1Dialog



class ReportEsetMaxValueDialog(ReportBase1Dialog):

   def __init__(self, parent, phases, output_dir):
      super().__init__(parent, "Maximum value of elements set", phases, "eset", output_dir, "file")


# ****************************************************

class ReportEsetMaxValuesDifferenceDialog(ReportBase1Dialog):

   def __init__(self, parent, phases, output_dir):
       super().__init__(parent, "Maximum values difference of elements set", phases, "eset", output_dir, "file")

       lbl = ttk.Label(self.topWin, text='Base elements set:')
       self.cb_base_eset = ttk.Combobox(self.topWin, width=35, state="readonly", values=self.lb_models.get(0, tk.END))
       lbl.grid(row=2, column=4, padx=4, pady=2, sticky=tk.W)
       self.cb_base_eset.grid(row=2, column=5, padx=4, pady=2, sticky=tk.EW)


   def __set_next_result__(self):
      if self.cb_base_eset.current() == -1:
         showinfo(title="Error", message="Base elements set was not selected.")
         return False
      self.res_base_eset = self.cb_base_eset.get()
      if self.res_base_eset in self.res_models:
         showinfo(title="Error", message="Base elements set cannot be simultaneously selected in elements set list.")
         return False
      return True


# ******************************************************

class ReportEsetQuantilesDialog(ReportBase1Dialog):

   def __init__(self, parent, phases, output_dir):
      super().__init__(parent, "Quantiles of elements set", phases, "eset", output_dir, "file")
      
      lbl = ttk.Label(self.topWin, text='Quantiles [%]:')
      self.quantilesVar = tk.StringVar()
      entry = ttk.Entry(self.topWin, width=20, textvariable=self.quantilesVar)
      lbl.grid(row=2, column=4, sticky=tk.W, padx=4, pady=2)
      entry.grid(row=2, column=5, sticky=tk.W+tk.E, padx=4, pady=2)


   def __set_next_result__(self):
      q = self.quantilesVar.get().strip().replace(","," ").replace(";"," ").split()
      if len(q) == 0:
         showinfo(title="Error", message="Quantiles were not set.")
         return False
      for s in q:
         try: 
            if not 0 < float(s) < 100: raise Exception()
         except:
            showinfo(title="Error", message="Value '{:s}' is not valid quantile from interval (0;100)".format(s))
            return False
      self.res_quantiles = q
      return True


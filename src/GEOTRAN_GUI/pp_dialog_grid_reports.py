
from sre_parse import State
import tkinter as tk
from tkinter.messagebox import showerror
from tkinter import ttk

from pp_dialog_report_base_1 import ReportBase1Dialog


# ******************************************************

class ReportGridMaxValueDialog(ReportBase1Dialog):

   def __init__(self, parent, phases, output_dir):
      super().__init__(parent, "Maximum value of grid", phases, "grid", output_dir, "file")


# ***********************************************************

class ReportGridMaxValuesDifferenceDialog(ReportBase1Dialog):

   def __init__(self, parent, phases, output_dir):
       super().__init__(parent, "Maximum value difference between grids", phases, "grid", output_dir, "file")

       lbl = ttk.Label(self.topWin, text='Base grid:')
       self.cb_base_grid = ttk.Combobox(self.topWin, width=35, state="readonly", values=self.lb_models.get(0, tk.END))
       lbl.grid(row=2, column=4, padx=4, pady=2, sticky=tk.W)
       self.cb_base_grid.grid(row=2, column=5, padx=4, pady=2, sticky=tk.W+tk.E)

   def __set_next_result__(self):
      if self.cb_base_grid.current() == -1:
         showerror(title="Error", message="Base grid was not selected.")
         return False
      self.res_base_grid = self.cb_base_grid.get()
      if self.res_base_grid in self.res_models:
         showerror(title="Error", message="Base grid cannot be simultaneously selected in grids list.")
         return False
      return True



# ************************************************************

class ReportGridQuantilesDialog(ReportBase1Dialog):

   def __init__(self, parent, phases, output_dir):
      super().__init__(parent, "Quantiles of grid", phases, "grid", output_dir, "file")
      
      lbl = ttk.Label(self.topWin, text='Quantiles [%]:')
      self.quantilesVar = tk.StringVar()
      entry = ttk.Entry(self.topWin, width=20, textvariable=self.quantilesVar)
      lbl.grid(row=2, column=4, sticky=tk.W, padx=4, pady=2)
      entry.grid(row=2, column=5, sticky=tk.W+tk.E, padx=4, pady=2)


   def __set_next_result__(self):
      q = self.quantilesVar.get().strip().replace(","," ").replace(";"," ").split()
      if len(q) == 0:
         showerror(title="Error", message="Quantiles were not set.")
         return False
      for s in q:
         try: 
            if not 0 < float(s) < 100: raise Exception("")
         except:
            showerror(title="Error", message="Value {:s} is not valid real number from interval (0;100)".format(s))
            return False
      self.res_quantiles = q
      return True


# *********************************************************

class ReportGridAreaOverLimitsDialog(ReportBase1Dialog):

   def __init__(self, parent, phases, output_dir):
      super().__init__(parent, "Grid area over limit", phases, "grid", output_dir, "file")
      
      lbl = ttk.Label(self.topWin, text='Limit values:')
      self.limitsVar = tk.StringVar()
      entry = ttk.Entry(self.topWin, width=20, textvariable=self.limitsVar)
      lbl.grid(row=2, column=4, sticky=tk.W, padx=4, pady=2)
      entry.grid(row=2, column=5, sticky=tk.W+tk.E, padx=4, pady=2)


   def __set_next_result__(self):
      limits = self.limitsVar.get().strip().replace(","," ").replace(";"," ").split()
      if len(limits) == 0:
         showerror(title="Error", message="Limit values were not set.")
         return False
      for s in limits:
         try: 
            float(s)
         except:
            showerror(title="Error", message="Value {:s} is not valid real number".format(s))
            return False
      self.res_limits = limits
      return True


# *********************************************************

class ReportGridImagesDialog(ReportBase1Dialog):

   def __init__(self, parent, phases, output_dir):
      super().__init__(parent, "Genetate grid images", phases, "grid", output_dir, "dir")
      
      w = self.topWin

      lbl = ttk.Label(w, text='Isoline values:')
      self.limitsVar = tk.StringVar(value="")
      entry = ttk.Entry(w, textvariable=self.limitsVar)
      btngenlimits = ttk.Button(w, text="Set automaticaly", command=self.ongenlimits, width=20)
      lbl.grid(row=2, column=4, sticky=tk.W, padx=4, pady=2)
      entry.grid(row=2, column=5, sticky=tk.W+tk.E, padx=4, pady=2)
      btngenlimits.grid(row=2, column=6, sticky=tk.W, padx=4, pady=2)

      lbl = ttk.Label(w, text='Color scheme:')
      self.cb_colors = ttk.Combobox(w, width=25, state = "readonly",
                                  values=('blue red (blurry, 2 isolines)',
                                          'blue green red (blurry, 3 isolines)',
                                          'blue red (1 isoline)',
                                          'blue green red (2 isolines)',
                                          'blue green red black (3 isolines)'))
      self.colors = (None,
                     None,
                     ((0,0,255), (0,255,0)),
                     ((0,0,255), (0,255,0), (255,0,0)),
                     ((0,0,255), (0,255,0), (255,0,0), (0,0,0))
                    )
      self.cb_colors.current(0)
      lbl.grid(row=3, column=4, padx=4, pady=2, sticky=tk.W)
      self.cb_colors.grid(row=3, column=5, padx=4, pady=2, sticky=tk.W+ tk.E)

      lbl = ttk.Label(w, text='Output file name prefix:')
      self.fileprefixVar = tk.StringVar(value="")
      entry = ttk.Entry(w, width=20, textvariable=self.fileprefixVar)
      lbl.grid(row=4, column=4, padx=4, pady=2, sticky=tk.W)
      entry.grid(row=4, column=5, padx=4, pady=2, sticky=tk.W+tk.E)

      lbl = ttk.Label(w, text='output file type:')
      self.cb_ext = ttk.Combobox(w, width=10, state = "readonly", values=("bmp","png","jpg"))
      self.cb_ext.current(1)
      lbl.grid(row=5, column=4, sticky=tk.W, padx=4, pady=2)
      self.cb_ext.grid(row=5, column=5, sticky=tk.W+tk.E, padx=4, pady=2)


   def ongenlimits(self, event=None):
      g = [self.lb_models.get(i) for i in self.lb_models.curselection()]
      s = [self.lb_species.get(i) for i in self.lb_species.curselection()]
      t = [self.lb_times.get(i) for i in self.lb_times.curselection()]
      if len(g) == 0 or len(s) == 0 or len(t) == 0: return
      def wlim(*limits):
         self.limitsVar.set(" ".join(["{:.4G}".format(x) for x in limits]))
      x_min, x_max = self.phases.get_grids_min_max_value(g, s, t, self.get_exclude_phase_time())
      i = self.cb_colors.current()
      if i == 0: wlim(x_min, x_max)
      elif i == 1: wlim(x_min, x_min+(x_max-x_min)/2, x_max)
      elif i == 2: wlim(x_min+(x_max-x_min)/2)
      elif i == 3: wlim(x_min + (k:=(x_max-x_min)/3), x_min + 2*k)
      elif i == 4: wlim(x_min + (k:=(x_max-x_min)/4), x_min + 2*k, x_min + 3*k)

      
   def __set_next_result__(self):
      limits = self.limitsVar.get().strip().replace(","," ").replace(";"," ").split()
      i_colors = self.cb_colors.current()
      lim_count = [2, 3, 1, 2, 3][i_colors]
      if len(limits) != lim_count:
         showerror(title="Error", message="Number of limits must be {:d} for selected color scheme.".format(lim_count))
         return False
      for s in limits:
         try: float(s)
         except:
            showerror(title="Error", message="Value {:s} is not valid real number".format(s))
            return False
      self.res_limits = limits
      self.res_colors = self.colors[i_colors]
      self.res_file_prefix = self.fileprefixVar.get().strip()
      self.res_file_ext = self.cb_ext.get()
      return True


# ************************************************************

class ReportGridASCDialog(ReportBase1Dialog):

   def __init__(self, parent, phases, output_dir):
      super().__init__(parent, "Save grid to ASC file", phases, "grid", output_dir, "dir")

      w = self.topWin

      lbl = ttk.Label(w, text='No data value:')
      self.novalueVar = tk.StringVar(value="-9999")
      entry = ttk.Entry(w, width=20, textvariable=self.novalueVar)
      lbl.grid(row=2, column=4, sticky=tk.W, padx=4, pady=2)
      entry.grid(row=2, column=5, sticky=tk.W+tk.E, padx=4, pady=2)

      lbl = ttk.Label(w, text='Output file name prefix:')
      self.fileprefixVar = tk.StringVar()
      entry = ttk.Entry(w, width=25, textvariable=self.fileprefixVar)
      lbl.grid(row=3, column=4, sticky=tk.W, padx=4, pady=2)
      entry.grid(row=3, column=5, sticky=tk.W+tk.E, padx=4, pady=2)


   def __set_next_result__(self):
      self.res_value_instead_of_nan = v = self.novalueVar.get().strip()
      try: float(v)
      except:
         showerror(title="Error", message="No data value must be valid real number.")
         return False
      self.res_file_prefix = self.fileprefixVar.get().strip()
      return True


# ************************************************************

class ReportGridDifferenceASCDialog(ReportBase1Dialog):

   def __init__(self, parent, phases, output_dir):
      super().__init__(parent, "Save grids difference to ASC file", phases, "grid", output_dir, "dir")

      w = self.topWin

      lbl = ttk.Label(w, text='Base grid:')
      self.cb_base_grid = ttk.Combobox(w, width=35, state="readonly", values=self.lb_models.get(0, tk.END))
      lbl.grid(row=2, column=4, padx=4, pady=2, sticky=tk.W)
      self.cb_base_grid.grid(row=2, column=5, padx=4, pady=2, sticky=tk.EW)

      lbl = ttk.Label(w, text='No data value:')
      self.novalueVar = tk.StringVar(value="-9999")
      entry = ttk.Entry(w, width=20, textvariable=self.novalueVar)
      lbl.grid(row=3, column=4, sticky=tk.W, padx=4, pady=2)
      entry.grid(row=3, column=5, sticky=tk.EW, padx=4, pady=2)

      lbl = ttk.Label(w, text='Output file name prefix:')
      self.fileprefixVar = tk.StringVar()
      entry = ttk.Entry(w, width=25, textvariable=self.fileprefixVar)
      lbl.grid(row=4, column=4, sticky=tk.W, padx=4, pady=2)
      entry.grid(row=4, column=5, sticky=tk.EW, padx=4, pady=2)


   def __set_next_result__(self):
      if self.cb_base_grid.current() == -1:
         showerror(title="Error", message="Base grid was not selected.")
         return False
      self.res_base_grid = self.cb_base_grid.get()
      if self.res_base_grid in self.res_models:
         showerror(title="Error", message="Base grid cannot be simultaneously selected in grids list.")
         return False
      self.res_value_instead_of_nan = v = self.novalueVar.get().strip()
      try: float(v)
      except:
         showerror(title="Error", message="No data value must be valid real number.")
         return False
      self.res_file_prefix = self.fileprefixVar.get().strip()
      return True


# ************************************************************

class ReportGridASCasPctDialog(ReportBase1Dialog):

   def __init__(self, parent, phases, output_dir):
      super().__init__(parent, "Save grid to ASC file by percentiles", phases, "grid", output_dir, "dir")

      w = self.topWin

      lbl = ttk.Label(w, text='Value of 100%:')
      self.value100pctVar = tk.StringVar()
      entry = ttk.Entry(w, width=20, textvariable=self.value100pctVar)
      lbl.grid(row=2, column=4, sticky=tk.W, padx=4, pady=2)
      entry.grid(row=2, column=5, sticky=tk.EW, padx=4, pady=2)

      lbl = ttk.Label(w, text='No data value:')
      self.novalueVar = tk.StringVar(value="-1")
      entry = ttk.Entry(w, width=20, textvariable=self.novalueVar)
      lbl.grid(row=3, column=4, sticky=tk.W, padx=4, pady=2)
      entry.grid(row=3, column=5, sticky=tk.EW, padx=4, pady=2)

      lbl = ttk.Label(w, text='Decimals number:')
      self.cb_decnum = ttk.Combobox(w, width=20, state="readonly", values=("0","1","2","3","4"))
      self.cb_decnum.current(0)
      lbl.grid(row=4, column=4, sticky=tk.W, padx=4, pady=2)
      self.cb_decnum.grid(row=4, column=5, sticky=tk.EW, padx=4, pady=2)

      lbl = ttk.Label(w, text='Output file name prefix:')
      self.fileprefixVar = tk.StringVar(value="")
      entry = ttk.Entry(w, width=25, textvariable=self.fileprefixVar)
      lbl.grid(row=5, column=4, sticky=tk.W, padx=4, pady=2)
      entry.grid(row=5, column=5, sticky=tk.EW, padx=4, pady=2)


   def __set_next_result__(self):
      self.res_value_100pct = v = self.value100pctVar.get().strip()
      try: float(v)
      except:
         showerror(title="Error", message="Value repesented 100% must be valid real number.")
         return False
      self.res_value_instead_of_nan = v = self.novalueVar.get().strip()
      try: float(v)
      except:
         showerror(title="Error", message="No data value must be valid real number.")
         return False
      self.res_decnum = self.cb_decnum.get()
      self.res_file_prefix = self.fileprefixVar.get().strip()
      return True



# ************************************************************

class ReportGridDifferenceASCasPctDialog(ReportBase1Dialog):

   def __init__(self, parent, phases, output_dir):
      super().__init__(parent, "Save grid difference to ASC file as percentiles", phases, "grid", output_dir, "dir")

      w = self.topWin

      lbl = ttk.Label(w, text='Base grid:')
      self.cb_base_grid = ttk.Combobox(w, width=35, state="readonly", values=self.lb_models.get(0, tk.END))
      lbl.grid(row=2, column=4, padx=4, pady=2, sticky=tk.W)
      self.cb_base_grid.grid(row=2, column=5, padx=4, pady=2, sticky=tk.EW)

      lbl = ttk.Label(w, text='No data value:')
      self.novalueVar = tk.StringVar(value="-9999")
      entry = ttk.Entry(w, width=20, textvariable=self.novalueVar)
      lbl.grid(row=3, column=4, sticky=tk.W, padx=4, pady=2)
      entry.grid(row=3, column=5, sticky=tk.EW, padx=4, pady=2)

      lbl = ttk.Label(w, text='Decimals number:')
      self.cb_decnum = ttk.Combobox(w, width=20, state="readonly", values=("0","1","2","3","4"))
      self.cb_decnum.current(0)
      lbl.grid(row=4, column=4, sticky=tk.W, padx=4, pady=2)
      self.cb_decnum.grid(row=4, column=5, sticky=tk.EW, padx=4, pady=2)

      lbl = ttk.Label(w, text='Output file name prefix:')
      self.fileprefixVar = tk.StringVar(value="")
      entry = ttk.Entry(w, width=25, textvariable=self.fileprefixVar)
      lbl.grid(row=5, column=4, sticky=tk.W, padx=4, pady=2)
      entry.grid(row=5, column=5, sticky=tk.EW, padx=4, pady=2)


   def __set_next_result__(self):
      if self.cb_base_grid.current() == -1:
         showerror(title="Error", message="Base grid was not selected.")
         return False
      self.res_base_grid = self.cb_base_grid.get()
      if self.res_base_grid in self.res_models:
         showerror(title="Error", message="Base grid cannot be simultaneously selected in grids list.")
         return False
      self.res_value_instead_of_nan = v = self.novalueVar.get().strip()
      try: float(v)
      except:
         showerror(title="Error", message="No data value must be valid real number.")
         return False
      self.res_decnum = self.cb_decnum.get()
      self.res_file_prefix = self.fileprefixVar.get().strip()
      return True



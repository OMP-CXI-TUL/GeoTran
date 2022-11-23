import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror


class BalanceOptionsDialog:

    def __init__(self, parent, balance):
        b = self.balance = balance

        w = self.topWin = tk.Toplevel(parent)
        w.transient(parent)
        w.grab_set()
        x = parent.winfo_x()
        y = parent.winfo_y()
        w.geometry("+%d+%d" % (x + 100, y + 100))
        w.title("Balance Options")

        lbl = ttk.Label(w, text='Column separator in output files:')
        self.cb_colsep = ttk.Combobox(w, width=15, state = "readonly",
          values=('comma (,)', 'semicolon (;)', 'tabulator', 'space'))
        self.colsep = [",", ";", "\t", " "]
        self.cb_colsep.current(self.colsep.index(b.params.out_column_separator))
        lbl.grid(row=0, column=0, padx=4, pady=4, sticky=tk.W)
        self.cb_colsep.grid(row=0, column=1, padx=4, pady=4, sticky=tk.W)

        lbl = ttk.Label(w, text='Decimal separator in output files:')
        self.cb_decsep = ttk.Combobox(w, width=15, state = "readonly", values=("Point","Comma"))
        self.cb_decsep.current(1 if b.params.out_decimal_comma else 0)
        lbl.grid(row=1, column=0, padx=4, pady=4, sticky=tk.W)
        self.cb_decsep.grid(row=1, column=1, padx=4, pady=4, sticky=tk.W)

        btnOk = ttk.Button(w, text="OK", command=self.onOk, width=10)
        btnOk.grid(row=2, column=2, padx=4, pady=4, sticky=tk.E)
        self.btn_OK = False

        btnCancel = ttk.Button(w, text="Cancel", command=self.onCancel, width=10)
        btnCancel.grid(row=2, column=3, padx=4, pady=4)


    def onOk(self, event=None):
        self.balance.params.set_out_column_separator(self.colsep[self.cb_colsep.current()])
        self.balance.params.set_out_decimal_comma(self.cb_decsep.current() == 1)
        self.topWin.destroy()
        self.btn_OK = True
        

    def onCancel(self, event=None):
        self.topWin.destroy()



# *********************************************************

class TransportOptionsDialog:

    def __init__(self, parent, phases):
        p = self.phases = phases

        w = self.topWin = tk.Toplevel(parent)
        w.transient(parent)
        w.grab_set()
        x = parent.winfo_x()
        y = parent.winfo_y()
        w.geometry("+%d+%d" % (x + 100, y + 100))
        w.title("Postrocessing options")


        # ********* base options *******************
        w.rowconfigure(4, weight=1, minsize=20)
        w.columnconfigure(2, weight=1)

        lbl = ttk.Label(w, text='Base options:')
        lbl.grid(row=0, column=0, padx=4, pady=4, sticky=tk.W)

        lbl = ttk.Label(w, text='Column separator in output files:')
        self.cb_colsep = ttk.Combobox(w, width=15, state = "readonly",
          values=('comma (,)', 'semicolon (;)', 'tabulator', 'space'))
        self.colsep = [",", ";", "\t", " "]
        self.cb_colsep.current(self.colsep.index(p.params.out_column_separator))
        lbl.grid(row=1, column=0, padx=4, pady=4, sticky=tk.W)
        self.cb_colsep.grid(row=1, column=1, padx=4, pady=4, sticky=tk.W)

        lbl = ttk.Label(w, text='Decimal separator in output files:')
        self.cb_decsep = ttk.Combobox(w, width=15, state = "readonly", values=("Point","Comma"))
        self.cb_decsep.current(1 if p.params.out_decimal_comma else 0)
        lbl.grid(row=2, column=0, padx=4, pady=4, sticky=tk.W)
        self.cb_decsep.grid(row=2, column=1, padx=4, pady=4, sticky=tk.W)

        lbl = ttk.Label(w, text= 'Grid IDW interpolation factor:')        
        self.IDWfacVar = tk.StringVar(value=p.get_OPTION_asstr("IDW_factor"))
        entry = ttk.Entry(w, width=10, textvariable=self.IDWfacVar)
        lbl.grid(row=3, column=0, sticky=tk.W, padx=4, pady=4)
        entry.grid(row=3, column=1, sticky=tk.W, padx=4, pady=4)


        # ********* extended options options *******************

        lbl = ttk.Label(w, text='Extended options:')
        lbl.grid(row=5, column=0, padx=4, pady=4, sticky=tk.W)

        lbl = ttk.Label(w, text="Bands xy width:")
        self.bandxywidthVar = tk.StringVar(value= v if (v:=p.get_OPTION_asstr("band_xy_width")) != "None" else "")
        entry = ttk.Entry(w, width=10, textvariable=self.bandxywidthVar)
        lbl.grid(row=6, column=0, sticky=tk.W, padx=4, pady=4)
        entry.grid(row=6, column=1, sticky=tk.W, padx=4, pady=4)

        lbl = ttk.Label(w, text="Bands z width:")
        self.bandzwidthVar = tk.StringVar(value=v if (v:=p.get_OPTION_asstr("band_z_width")) != "None" else "")
        entry = ttk.Entry(w, width=10, textvariable=self.bandzwidthVar)
        lbl.grid(row=7, column=0, sticky=tk.W, padx=4, pady=4)
        entry.grid(row=7, column=1, sticky=tk.W, padx=4, pady=4)

        self.keepbandstriaVar = tk.BooleanVar(value=(p.get_OPTION_asstr("keep_bands_tria")=="True"))
        c = tk.Checkbutton(w, text="Keep triangles bands", variable=self.keepbandstriaVar)
        c.grid(row=8, column=0, columnspan=2, padx=4, pady=4, sticky=tk.W)

        self.keepbufbandsVar = tk.BooleanVar(value=(p.get_OPTION_asstr("keep_buf_bands")=="True"))
        c = tk.Checkbutton(w, text="Keep intersections of x, y, z bands", variable=self.keepbufbandsVar)
        c.grid(row=9, column=0, columnspan=2, padx=4, pady=4, sticky=tk.W)

        self.keepeplanesVar = tk.BooleanVar(value=(p.get_OPTION_asstr("keep_e_planes")=="True"))
        c = tk.Checkbutton(w, text="Buffering mesh elements planes equations", variable=self.keepeplanesVar)
        c.grid(row=10, column=0, columnspan=2, padx=4, pady=4, sticky=tk.W)

        self.keepIDWVar = tk.BooleanVar(value=(p.get_OPTION_asstr("keep_IDW_weights")=="True"))
        c = tk.Checkbutton(w, text="Buffering IDW weights of grid", variable=self.keepIDWVar)
        c.grid(row=11, column=0, columnspan=2, padx=4, pady=4, sticky=tk.W)

        lbl = tk.Label(w, text="Regions for surface creation:")
        self.lb_regions = tk.Listbox(w, width=40, selectmode=tk.EXTENDED)
        regions = p.get_physicals_name_of_phase_0()
        self.lb_regions.bind('<<ListboxSelect>>', self.on_lb_regions_selection)
        self.lb_regions.insert(tk.END, *regions)
        regions_i = [regions.index(r) for r in p.get_physicals_OPTION_e2_e4_to_tria()]
        for i in regions_i: self.lb_regions.selection_set(i)
        self.regselinfoVar = tk.StringVar()
        self.on_lb_regions_selection(None)
        lbl.grid(row=0, column=2, sticky=tk.W, pady=4, padx=4)
        self.lb_regions.grid(row=1, column=2, rowspan=11, padx=4, pady=4, sticky=tk.E+tk.W+tk.S+tk.N)

        lbr = tk.Label(w, textvariable=self.regselinfoVar)
        lbr.grid(row=1, column=3, padx=4, pady=4,sticky=tk.W)
        btn = ttk.Button(w, text="Select All", command=self.onregselectall, width=15)
        btn.grid(row=2, column=3, padx=4, pady=4, sticky=tk.E)
        btn = ttk.Button(w, text="Clear selection", command=self.onregclearsel, width=15)
        btn.grid(row=3, column=3, padx=4, pady=4, sticky=tk.E)



        # ***************************************************

        btnOk = ttk.Button(w, text="OK", command=self.onOk, width=10)
        btnOk.grid(row=10, column=3, padx=4, pady=4, sticky=tk.EW)
        self.btn_OK = False

        btnCancel = ttk.Button(w, text="Cancel", command=self.onCancel, width=10)
        btnCancel.grid(row=11, column=3, padx=4, pady=4, sticky=tk.EW)


    def on_lb_regions_selection(self, event):
        self.regselinfoVar.set("{:d} / {:d} selected".format(len(self.lb_regions.curselection()), self.lb_regions.size()))

    def onregselectall(self):
        self.lb_regions.selection_set(0, tk.END)

    def onregclearsel(self):
        self.lb_regions.selection_clear(0, tk.END)


    def onOk(self, event=None):
        p = self.phases
        p.params.set_out_column_separator(self.colsep[self.cb_colsep.current()])
        p.params.set_out_decimal_comma(self.cb_decsep.current() == 1)
        try:
           r = float(self.IDWfacVar.get())
           if not 0 <= r <= 32: raise Exception()
        except:
           showerror(title="Error", message="IDW factor must be valid real value between 0 and 32")
           return
        p.set_OPTION("IDW_factor", r)
        if (s:=self.bandxywidthVar.get().strip()) == "": r = None
        else:
           try:
              if (r := float(s)) <= 0: raise Exception()
           except:
              showerror(title="Error", message="Band width of xy axis must be valid number more than zero.")
              return
        p.set_OPTION("band_xy_width", r)
        if (s:=self.bandzwidthVar.get().strip()) == "": r = None
        else:
           try:
              if (r := float(s)) <= 0: raise Exception()
           except:
              showerror(title="Error", message="Band width of z axis must be valid number more than zero.")
              return
        p.set_OPTION("band_z_width", r)
        p.set_OPTION("keep_bands_tria", self.keepbandstriaVar.get())
        p.set_OPTION("keep_buf_bands", self.keepbufbandsVar.get())
        p.set_OPTION("keep_e_planes", self.keepeplanesVar.get())
        p.set_OPTION("keep_IDW_weights", self.keepIDWVar.get())
        p.update_OPTIONs()
        if len(self.lb_regions.curselection()) == 0:
           tk.messagebox.showerror(message="No regions were selected.")
           return
        p.set_OPTION_e2_e4_to_tria_by_physicals([self.lb_regions.get(i) for i in self.lb_regions.curselection()])
        self.topWin.destroy()
        self.btn_OK = True
        

    def onCancel(self, event=None):
        self.topWin.destroy()



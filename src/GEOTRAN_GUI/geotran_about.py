import tkinter as tk
from tkinter import ttk

class AboutWin():

    def __init__(self, parent):
        self.topWin = tk.Toplevel(parent)
        self.topWin.transient(parent)
        self.topWin.grab_set()
        x = parent.winfo_x()
        y = parent.winfo_y()
        self.topWin.geometry("+%d+%d" % (x + 100, y + 100))
        self.topWin.title("About")

        lbl = ttk.Label(self.topWin, text='GEOTRAN', font=('Arial', 24, 'bold'), foreground='#905090')
        lbl.grid(row=0, column=0, sticky=tk.E, pady=20)
        lbl = ttk.Label(self.topWin, text='tools', font=('Arial', 18, 'bold'), foreground='#505050')
        lbl.grid(row=0, column=1, sticky=tk.W + tk.S, pady=18)
        lbl = ttk.Label(self.topWin, text='Software for processsing of transport outputs of Flow123d')
        lbl.grid(row=1, column=0, columnspan=2, sticky=tk.W + tk.E, padx=4, pady=2)
        lbl = ttk.Label(self.topWin, text='Lincenced under GNU General Public License v3.0')
        lbl.grid(row=2, column=0, columnspan=2, sticky=tk.W + tk.E, padx=4, pady=2)
        lbl = ttk.Label(self.topWin, text='Version 1.0')
        lbl.grid(row=3, column=0, columnspan=2, sticky=tk.W + tk.E, padx=4, pady=2)







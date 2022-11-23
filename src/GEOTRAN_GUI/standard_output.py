import io
import sys
import threading
from time import sleep
import tkinter as tk
from tkinter import scrolledtext


class OutputThread(threading.Thread):
   
   def __init__(self, gtapp):
      super().__init__()
      self.gtapp = gtapp
      sys.stdout = io.StringIO()
      self.log = open("geotran.log", "w")


   def run(self):
      while True:
         sys.stdout.seek(0)
         s = sys.stdout.getvalue()
         if len(s) > 0:
            sys.stdout.truncate(0)
            self.log.write(s)
            self.log.flush()
            self.gtapp.bottomInfoPanel.insert(tk.END, s)   
            self.gtapp.bottomInfoPanel.see(tk.END)
            self.gtapp.bottomInfoPanel.update_idletasks()
         sleep(0.1)


def init_standard_output(gtapp):
  # th = OutputThread(gtapp)
  # th.start()
   pass
   




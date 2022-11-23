import io
import sys
import threading
import tkinter as tk
from tkinter import scrolledtext


class OutputThread(threading.Thread):
   
   def __init__(self, appwin):
      super().__init__()
      self.appwin = appwin
      self.terminate = False
      sys.stdout = io.StringIO()
      self.log = open("geotran.log", "w")


   def ontimer(self):
     sys.stdout.seek(0)
     s = sys.stdout.getvalue()
     sys.stdout.truncate(0)
     if len(s) > 0:
        self.log.write(s)
        self.log.flush()
        self.text.insert(tk.END, s)
        self.text.see(tk.END)
     if self.terminate: self.win.destroy()
     self.win.after(100, self.ontimer)

   def no_close(self):
      pass

   def run(self):
      w = self.win = tk.Tk()
      w.grab_set()
      x = self.appwin.winfo_x()
      y = self.appwin.winfo_y()
      width = self.appwin.winfo_width()
      height = self.appwin.winfo_height() + 65
      w.geometry("+%d+%d" % (x, y + height))
      w.title("GEOTRANtools processing log")
      w.protocol("WM_DELETE_WINDOW", self.no_close)
      w.columnconfigure(0, weight=1)
      w.rowconfigure(0,weight=1)

      self.text = tk.scrolledtext.ScrolledText(w, width=120, height=14)
      self.text.grid(sticky=tk.W+tk.E+tk.N+tk.S)

      self.ontimer()
      w.mainloop()


class Out:
   outthread = None

def initialize(appwin):
   Out.outthread = OutputThread(appwin)
   Out.outthread.start()


def terminate():
   t = Out.outthread
   t.terminate = True
   t.join()
   t.log.close()

   





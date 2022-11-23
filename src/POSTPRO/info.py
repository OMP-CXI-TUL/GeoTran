import datetime
import traceback
from sys import stderr

class Info:
   
   def __init__(self, process_id, process_name, outfile=stderr):
      self.ind = 0
      self.outfile = outfile
      self.process_id = process_id
      self.process_name = process_name
      self.start_times = []
      self.last_timespan = None

      
   def _gettime(self, start_time):
      s = str(datetime.datetime.now() - start_time).split(".")
      if len(s) == 1: return s[0]
      else: return s[0] + "." + s[1][:3]

   def start(self, s, reset=False):
      if reset:
         self.ind = 0
         self.start_times.clear()
      print(self.process_name + ": " + self.ind*".  " + chr(31) + " " + s + ' ...', file=self.outfile, flush=True)
      self.start_times.append(datetime.datetime.now())
      self.ind += 1

   def __call__(self, s):
      print(self.process_name + ": " + self.ind * ".  " + s, file=self.outfile, flush=True)

   def warning(self, s):
      print(self.process_name + ": " + self.ind * ".  " + "Warning: " + s, file=self.outfile, flush=True)

   def error(self, e):
      if self.ind > 0:
         print(self.process_name + ": " + self.ind*".  " + self._gettime(self.start_times[-1]) + " ERROR !", file=self.outfile)
      else: print(self.process_name + ": ERROR !", file=self.outfile)
      traceback.print_exc(file=self.outfile)
      self.ind = 0
      self.start_times.clear()
      self.outfile.flush()


   def OK(self, s=None):
      self.ind -= 1
      time = self._gettime(self.start_times.pop())
      s = " "+s+" " if s is not None else " "
      print(self.process_name + ": " + self.ind*".  " + chr(30) + " " + time + s + "OK.", file=self.outfile, flush=True)
      self.last_timespan = time


   def print_timespan(self):
      return "Total time: " + self.last_timespan


   def stop(self): 
      print("INFO_STOP", file=self.outfile, flush=True)
      




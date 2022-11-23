import numpy as np


class Balance:

   # ********** exceptions ******************

   class GT_phases_times_ordering_error(Exception):
      def __init__(self, pos, phase, time):
         super().__init__("position: {:d}, phase: {:d}, time: {:g}".format(pos, phase,time))

   class GT_phases_margin_times_option_error(Exception):
      pass


   # ************ initialize *********************

   def __init__(self, info, params):
      self.info = info
      self.params = params
      self.data = {}
      self.phase_count = 0
   

   # *********** data loading *******************

   def load_data(self, file_names):
      self.info.start("Loading balance data")
      with open(file_names[0], "r") as f:
         dtyp = self.data_types = f.readline().strip().replace('"','').split("\t")[3:]
      # ********* phases loading *******************
      for file_name in file_names:
         phase_i = self.phase_count
         with open(file_name, "r") as f:
            f.readline()
            for line in f:
               p = line.strip().replace('"','').split("\t")
               self.data.update({(phase_i, s.rstrip("0").rstrip(".") if "." in (s:="{:.3f}".format(float(p[0]) * self.params.time_coef)) else s, p[1], p[2], q) : float(v) for q, v in zip(dtyp, p[3:])})
            self.phase_count += 1         
         self.info('{:d}. phase from file "{:s}" loaded. OK.'.format(self.phase_count, file_name))
      # ********* times list **********************
      self.phases_times = list({k[:2] for k in self.data.keys()})
      self.phases_times.sort(key=lambda pt : (p, float(pt[1])))  
      # ******* regions and quantities list *******
      self.regions = {k[2] for k in self.data.keys()}
      self.quantities = {k[3] for k in self.data.keys()}
      self.info.OK()


   # *********** reporting general CSV *******************   

   def report_csv(self, col_list, times, exclude_phase_time, col_sep, dec_comma, phase_num_col, file_name):
      self.info.start('Calculating balance reportt to file "' + file_name + '"')
      if col_sep is None: col_sep = self.params.out_column_separator
      if dec_comma is None: dec_comma = self.params.out_decimal_comma
      # ******* head line *****************
      head = ["Phase"] if phase_num_col else []
      head.append("time [" + self.params.time_main_unit + "]")
      head += [(' '.join(c[2])+' '+' '.join(c[3])+' '+c[1]) if c[0] is None else c[0] for c in col_list]
      rows = [head]
      # ******** times preparing ********************
      if times is None: a = self.phases_times
      else: a = [p for p in self.phase_times if p[1] in times]
      if exclude_phase_time == "first":
         phase_times = [a[0]] + [p2 for p1, p2 in zip(a[:-1],a[1:]) if p1[0] == p2[0]]
      elif exclude_phase_time == "last":
         phase_times = [p1 for p1, p2 in zip(a[:-1],a[1:]) if p1[0] == p2[0]] + [a[-1]]
      elif exclude_phase_time is None:
         phase_times = a
      else:
         raise self.GT_phases_margin_times_option_error()
      # ************ requre data **************************
      for p, t in phase_times:
         row = ["{:d}".format(p)] if phase_num_col else []
         row.append(t)
         row += ["{:g}".format(sum(self.data[(p, t, r, q, dtyp)] for r in regs for q in quants)) for _, dtyp, regs, quants in col_list]
         rows.append(row)
         self.info("Phase {:d} time {:s} OK.".format(p, t))
      max_len = [max(len(r[col]) for r in rows) for col in range(len(head))]
      lines = [col_sep.join([s.rjust(m) for s, m in zip(cols, max_len)]) for cols in rows]
      if dec_comma:
         for i in range(1,len(lines)):
            lines[i] = lines[i].replace(".", ",")
      with open(file_name, "w") as f:
         for s in lines: print(s, file=f)      
      self.info.OK()
      return rows


   # ****************** questions ********************************

   def get_phases_count(self):
      return self.phase_count

   def get_regions(self):
      return sorted(self.regions)

   def get_quantities(self):
      return sorted(self.quantities)

   def get_data_types(self):
      return sorted(self.data_types)
   

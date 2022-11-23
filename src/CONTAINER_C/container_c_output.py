import numpy as np
import os

class OutputModel:

   def __init__(self, computingmodel):
      self.c = computingmodel
      n, a = self.c.get_isot_count(), self.c.get_bent_lay_count()
      # ********* alocate time outputs *********
      self.fuel_mol = np.zeros(n)
      self.fuel_kg = np.zeros(n)
      self.fuel_Bq = np.zeros(n)
      self.deg_mol = np.zeros(n)
      self.deg_kg = np.zeros(n)
      self.fuel_plus_deg_kg = np.zeros(n)
      self.cont_w_mol_m3 = np.zeros(n)
      self.cont_w_kg_m3 = np.zeros(n)
      self.cont_w_Bq = np.zeros(n)
      self.cont_w_Bq_m3 = np.zeros(n)
      self.cont_w_sat_pct = np.zeros(n)
      self.bent_lay_w_mol_m3 = np.zeros((a,n))
      self.bent_lay_w_kg_m3 = np.zeros((a, n))
      self.bent_w_kg = np.zeros(n)
      self.bent_r_kg = np.zeros(n)
      self.bent_kg = np.zeros(n)
      self.granit_mol = np.zeros(n)
      self.granit_kg = np.zeros(n)
      self.granit_cumsum_mol = np.zeros(n)
      self.granit_cumsum_kg = np.zeros(n)
      # ******** create columns list ******
      self.quant_arrays = {
         "fuel_n_mol":   self.fuel_mol, 
         "fuel_m_kg":    self.fuel_kg,
         "fuel_A_Bq":    self.fuel_Bq,
         "deg_n_mol":    self.deg_mol,
         "deg_m_kg":     self.deg_kg,
         "fuel+deg_m_kg": self.fuel_plus_deg_kg,
         "cont.water_c_mol/m3": self.cont_w_mol_m3,
         "cont.water_c_kg/m3":  self.cont_w_kg_m3,
         "cont.water_A_Bq":     self.cont_w_Bq,
         "cont.water_AV_Bq/m3": self.cont_w_Bq_m3,
         "cont.water_sat_%": self.cont_w_sat_pct,
         "bent.layers.water_c_mol/m3": self.bent_lay_w_mol_m3,
         "bent.layers.water_c_kg/m3": self.bent_lay_w_kg_m3,
         "bent.inner.bound.water_c_mol/m3": self.bent_lay_w_mol_m3[0],
         "bent.inner.bound.water_c_kg/m3": self.bent_lay_w_kg_m3[0],
         "bent.1/4.water_c_mol/m3": self.bent_lay_w_mol_m3[a // 4],
         "bent.1/4.water_c_kg/m3": self.bent_lay_w_kg_m3[a // 4],
         "bent.1/2.water_c_mol/m3": self.bent_lay_w_mol_m3[a // 2],
         "bent.1/2.water_c_kg/m3": self.bent_lay_w_kg_m3[a // 2],
         "bent.3/4.water_c_mol/m3": self.bent_lay_w_mol_m3[(3*a) // 4],
         "bent.3/4.water_c_kg/m3": self.bent_lay_w_kg_m3[(3*a) // 4],
         "bent.outer.bound.water_c_mol/m3": self.bent_lay_w_mol_m3[-1],
         "bent.outer.bound.water_c_kg/m3": self.bent_lay_w_kg_m3[-1],
         "bent.water_m_kg": self.bent_w_kg,
         "bent.rock_m_kg": self.bent_r_kg,         
         "bent_m_kg": self.bent_kg,
         "granit.water_n_mol": self.granit_mol,
         "granit.water_m_kg": self.granit_kg,
         "granit.water_n(cumsum)_mol": self.granit_cumsum_mol,
         "granit.water_m(cumsum)_kg": self.granit_cumsum_kg
      }
      # ******** alocate statistics *********************
      self.stat_cont_max_c = np.zeros(n)
      self.stat_cont_max_c_time = np.zeros(n)
      self.stat_bent_bound_max_c = np.zeros(n)
      self.stat_bent_bound_max_c_time = np.zeros(n)
      self.stat_granit_n = np.zeros(n)
      self.statistic_types = {
         "cont_max_c": self._write_stat_cont_max_c,
         "bent_bound_max_c": self._write_stat_bent_bound_max_c,
         "granit_inflow": self._write_stat_granit_inflow
      }


   # ********************* help methods  ****************

   def _get_col_desc(self, isot_name, quantity_name):
      place, quantity, unit = quantity_name.split("_")
      return isot_name + " " + place + " " + quantity + " [" + unit + "]"


   def _overwrite_file_question(self, file_name):
      # ************** pro ucely GEOTRAN GUI ********
      return True
      # *********************************************
      if os.path.exists(file_name):
         k = ""
         while not k in ("Y", "N"):
            k = input("\tFile '" + file_name + "' already exists.\n\tDo you want to overwrite it? [Y/N]").upper()
            if k == "N": return False
      return True


   # *********** init output ***********************

   def init_output(self):
      print("\tInitialize outputs ...")
      c = self.c
      isots = [(p_i, c.isot_names[p_i]) for p_i in self.isot_indexes]
      elems = [(i if type(i:=c.elem_isotopes[e_i]) == int else list(range(i.start,i.stop)) ,c.elem_names[e_i]) for e_i in self.elem_indexes]
      # ********* sorting names ******************
      if "name" in self.col_order: 
         def sort_key(p): return p[1]
         if self.isots_elems_order == "together":
            names = isots + elems
            names.sort(key=sort_key)
         else:
            isots.sort(key=sort_key)
            elems.sort(key=sort_key)
            names = isots + elems
      elif "initial_mount" in self.col_order: 
         def sort_key(p): return np.sum(c.init_fuel_mol[p[0]])
         if self.isots_elems_order == "together":
            names = isots + elems
            names.sort(key=sort_key)
         else:
            isots.sort(key=sort_key)
            elems.sort(key=sort_key)
            names = isots + elems
      else:
         names = isots + elems      
      if self.summary: names += [(c.isot_indexes, "summary")]
      self.cols = cols = []
      if self.col_order.startswith("quantity"):
         for q_i, q_name in enumerate(self.quantities):
            if q_name.startswith("bent.layers"):
               for i, name in names:
                  for lay_i, r in enumerate(c.bent_lay_r[:,0]):
                     cols.append([name, i, q_name.replace("layers","{:g}cm".format((r - c.cont_R) * 100)), q_i, self.quant_arrays[q_name][lay_i]])
            else:
               for i, name in names:
                  cols.append([name, i, q_name, q_i, self.quant_arrays[q_name]])
      else:
         for i, name in names:
            for q_i, q_name in enumerate(self.quantities):
               if q_name.startswith("bent.layers"):
                  for lay_i, r in enumerate(c.bent_lay_r[:,0]):
                     cols.append([name, i, q_name.replace("layers","{:g}cm".format((r - c.cont_R) * 100)), q_i, self.quant_arrays[q_name][lay_i]])
               else:
                  cols.append([name, i, q_name, q_i, self.quant_arrays[q_name]]) 
      # ************* line format **********************
      d = ["{:.6g}", "{:.6g}"] if self.deg_rate else []
      self.line_format = self.col_sep.join(["{:g}"] + d + ["{:"+self.number_format+"}"]*len(self.cols))
      # ************* create output file **********
      if not self._overwrite_file_question(self.file_name): return False
      d = ["deg. state [%]", "dissolved rate [%]"] if self.deg_rate else []
      table_head = ["time [year]"] + d + [self._get_col_desc(p, q) for p, p_i, q, q_i, a in self.cols]
      print("\t\tCreating empty output file '" + self.file_name + "' ...")
      try:
         with open(self.file_name, "w") as f: 
            print(self.col_sep.join(table_head), file=f)
         print("\t\tOutput file was created. OK.")
      except:
         print("Error: Output file was not created.")
         return False
      # ************* create empty statistics files *********
      if self.statistics is not None:
         print("\t\tCreating empty statistics files ...")
         for stat in self.statistics:
            file_name = self._get_filename_with_stat(stat)
            try:
               with open(file_name, "w") as f: pass
               print("\t\tStatistics file '" + file_name +"' was created. OK.")
            except:
               print("Error: Statistics file '" + file_name  + "' was not created.")
               return False
         print("\t\tEmpty statistics files were created. OK.")
      print("\tOutputs were initialized. OK.")
      return True    
   
  

   # ********** computing results and writing to file ********

   def write_before_deg(self, t):
      c = self.c
      self.fuel_mol[:] = c.fuel_mol
      self.fuel_kg[:] = c.fuel_mol * c.isot_M
      self.fuel_Bq[:] = c.fuel_mol * c.Na * c.isot_lambda / c.year_seconds
      self.deg_mol[:] = c.deg_mol
      self.deg_kg[:] = c.deg_mol * c.isot_M
      self.fuel_plus_deg_kg[:] = self.fuel_kg + self.deg_kg
      self.cont_w_mol_m3[:] = 0
      self.cont_w_kg_m3[:] = 0
      self.cont_w_Bq[:] = 0
      self.cont_w_Bq_m3[:] = 0
      self.cont_w_sat_pct[:] = 0
      self.bent_lay_w_kg_m3[:] = 0
      self.bent_lay_w_mol_m3[:] = 0
      self.bent_w_kg[:] = 0
      self.bent_r_kg[:] = 0
      self.granit_mol[:] = 0
      self.granit_kg[:] = 0
      self.granit_cumsum_mol[:] = 0
      self.granit_cumsum_kg[:] = 0
      self._write_time(t,  100*c.deg_ratio, 0)


   def write_deg(self, t):
      c = self.c
      self.fuel_mol[:] = c.fuel_mol
      self.fuel_kg[:] = c.fuel_mol * c.isot_M
      self.fuel_Bq[:] = c.fuel_mol * c.Na * c.isot_lambda / c.year_seconds
      self.deg_mol[:] = c.deg_mol
      self.deg_kg[:] = c.deg_mol * c.isot_M
      self.fuel_plus_deg_kg[:] = self.fuel_kg + self.deg_kg
      self.cont_w_mol_m3[:] = c.cont_w_mol / c.cont_w_m3
      self.cont_w_kg_m3[:] = self.cont_w_mol_m3 * c.isot_M
      self.cont_w_Bq[:] = c.cont_w_mol * c.Na * c.isot_lambda / c.year_seconds
      self.cont_w_Bq_m3[:] =  self.cont_w_Bq / c.cont_w_m3
      self.cont_w_sat_pct[:] = 100 * self.cont_w_mol_m3 / c.isot_c_max
      self.bent_lay_w_mol_m3[:] = c.bent_lay_w_mol / c.bent_lay_w_m3
      self.bent_lay_w_kg_m3[:] = self.bent_lay_w_mol_m3 * c.isot_M
      self.bent_w_kg[:] = np.sum(c.bent_lay_w_mol * c.isot_M, axis=0)
      self.bent_r_kg[:] = np.sum(c.bent_lay_r_mol * c.isot_M, axis=0)
      self.bent_kg[:] = self.bent_w_kg + self.bent_r_kg
      self.granit_mol[:] = c.granit_mol
      self.granit_kg[:] = c.granit_mol * c.isot_M
      self.granit_cumsum_mol[:] = c.granit_cumsum_mol
      self.granit_cumsum_kg[:] = c.granit_cumsum_mol * c.isot_M
      self._write_time(t, 100*c.deg_ratio, 100*c.dissolved_ratio)
      self._update_statistics(t)


   def write_after_deg(self, t):
      c = self.c
      self.fuel_mol[:] = 0
      self.fuel_kg[:] = 0
      self.fuel_Bq[:] = 0
      self.deg_mol[:] = c.deg_mol
      self.deg_kg[:] = c.deg_mol * c.isot_M
      self.fuel_plus_deg_kg[:] = self.deg_kg
      self.cont_w_mol_m3[:] = c.cont_w_mol / c.cont_w_m3
      self.cont_w_kg_m3[:] = self.cont_w_mol_m3 * c.isot_M
      self.cont_w_Bq[:] = c.cont_w_mol * c.Na * c.isot_lambda / c.year_seconds
      self.cont_w_Bq_m3[:] = self.cont_w_Bq / c.cont_w_m3
      self.cont_w_sat_pct[:] = 100 * self.cont_w_mol_m3 / c.isot_c_max
      self.bent_lay_w_mol_m3[:] = c.bent_lay_w_mol / c.bent_lay_w_m3
      self.bent_lay_w_kg_m3[:] = self.bent_lay_w_mol_m3 * c.isot_M      
      self.bent_w_kg[:] = np.sum(c.bent_lay_w_mol * c.isot_M, axis=0)
      self.bent_r_kg[:] = np.sum(c.bent_lay_r_mol * c.isot_M, axis=0)
      self.bent_kg[:] = self.bent_w_kg + self.bent_r_kg
      self.granit_mol[:] = c.granit_mol
      self.granit_kg[:] = c.granit_mol * c.isot_M
      self.granit_cumsum_mol[:] = c.granit_cumsum_mol
      self.granit_cumsum_kg[:] = c.granit_cumsum_mol * c.isot_M
      self._write_time(t, 100, 100*c.dissolved_ratio)
      self._update_statistics(t)


   # *********** time output *************************

   def _write_time(self, t, deg_pct, dissolve_pct):
      v = [x if x > 1e-300 else 0. for x in (np.sum(a[i_isots]) if type(i_isots) != int else a[i_isots] for _ , i_isots, _ , _ , a in self.cols)]
      if self.deg_rate:
         line = self.line_format.format(t, deg_pct, dissolve_pct, *v)
      else:
         line = self.line_format.format(t, *v)
      with open(self.file_name, "a") as f:
         print(line if not self.dec_comma_sep else line.replace(".", ","), file=f)

      
   # ************ statistics *************************

   def _update_statistics(self, t):
      b = self.stat_cont_max_c < self.cont_w_kg_m3
      self.stat_cont_max_c[b] = self.cont_w_kg_m3[b]
      self.stat_cont_max_c_time[b] = t
      b = self.stat_bent_bound_max_c < self.bent_lay_w_kg_m3[-1]
      self.stat_bent_bound_max_c[b] = self.bent_lay_w_kg_m3[-1,b]
      self.stat_bent_bound_max_c_time[b] = t
      
      
   def _get_filename_with_stat(self, sufix):
      s = self.file_name
      i = s.rfind(".")
      if s[i+1] in ("/","\\") or i == 0 : i = -1
      if i > -1: s = s[:i] + "_" + sufix + s[i:]
      else: s = s + "_" + sufix
      return s
      
    
   def _write_stat_cont_max_c(self, sufix):
      c = self.c
      d = [(c.isot_names[p_i], self.stat_cont_max_c[p_i], self.stat_cont_max_c_time[p_i]) for p_i in self.isot_indexes]
      def d_sort(isot): return isot[1]
      d.sort(key=d_sort, reverse=True)      
      with open(self._get_filename_with_stat(sufix), "w") as f:
         print("order", "isotope", "c max [kg/m3]", "time", sep=self.col_sep, file=f)
         line_format = self.col_sep.join(["{:d}", "{:s}", "{:"+self.number_format+"}", "{:G}"])
         for i, a in enumerate(d):
            line = line_format.format(i, *a)
            print(line.replace(".",",") if self.dec_comma_sep else line, file = f)
      return True


   def _write_stat_bent_bound_max_c(self, sufix):
      c = self.c
      d = [(c.isot_names[p_i], self.stat_bent_bound_max_c[p_i], self.stat_bent_bound_max_c_time[p_i]) for p_i in self.isot_indexes]
      def d_sort(isot): return isot[1]
      d.sort(key=d_sort, reverse=True)
      with open(self._get_filename_with_stat(sufix), "w") as f:
         print("order", "isotope", "c max [kg/m3]", "time", sep=self.col_sep, file=f)
         line_format = self.col_sep.join(["{:d}", "{:s}", "{:"+self.number_format+"}", "{:G}"])
         for i, a in enumerate(d):
            line = line_format.format(i, *a)
            print(line.replace(".",",") if self.dec_comma_sep else line, file = f)
      return True


   def _write_stat_granit_inflow(self, sufix):
      c = self.c
      d = [(c.isot_names[p_i], self.granit_kg[p_i]) for p_i in self.isot_indexes]
      def d_sort(isot): return isot[1]
      d.sort(key=d_sort, reverse=True)
      with open(self._get_filename_with_stat(sufix), "w") as f:
         print("order", "isotope", "granite inflow m [kg]", sep=self.col_sep, file=f)
         line_format = self.col_sep.join(["{:d}", "{:s}", "{:"+self.number_format+"}"])
         for i, a in enumerate(d):
            line = line_format.format(i, *a)
            print(line.replace(".",",") if self.dec_comma_sep else line, file = f)
      return True


   def write_statistics(self):
      if self.statistics is None: return
      print("Writing statistics ...")
      for stat in self.statistics:
         if self.statistic_types[stat](stat) is None:
            print("ERROR with writing statistic '" + stat + "'.")
      print("Statistics were writen. OK.")


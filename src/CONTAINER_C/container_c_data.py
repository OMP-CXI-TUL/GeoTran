
import numpy as np
import re

from sys import float_info

from container_c_base import BaseModel
from container_c_output import OutputModel

class DataModel(BaseModel):

   def __init__(self):
      self.Na = 6.02214076e23
      self.year_seconds = 3600 * 24 * 365


   # *********** mathematics ***********************

   def gen_general_fcn_scalar(self, times, values):
      K = (values[1:] - values[:-1]) / (times[1:] - times[:-1])
      t, t_max, dt, i = times[0], times[-1], self.dt, 0
      while t < t_max:
         while t >= times[i+1]: i += 1
         yield K[i] * (t - times[i]) + values[i]
         t += dt
      while True: yield values[-1]

   def gen_general_fcn_column(self, times, values):
      if len(values) > 1:
         K = (values[:,1:] - values[:,:-1]) / (times[1:] - times[:-1])
         t, t_max, dt, i = times[0], times[-1], self.dt, 0
         while t < t_max:
            while t >= times[i+1]: i += 1
            yield K[:,[i]] * (t - times[i]) + values[:,[i]]
            t += dt
      while True: yield values[:,[-1]]


   # ************ simulation params *****************

   def _load_simulation_params(self, main_key):
      print("\tLoading simulation parameters ...")
      if not self.readfloat(0.01, 1e4, main_key + ["dt"]): return False
      self.dt = self.lrvalue
      if not self.readint(1, 24, main_key + ["max_iter"]): return False
      self.max_iter = self.lrvalue
      if not self.readfloat(0.01, 1e12, main_key + ["time"]): return False
      if self.lrvalue < self.dt:
         self.error("\tSimulation time must be more or equal to dt.")
         return False
      self.sim_t_n = round(self.lrvalue / self.dt)
      if self.lrvalue != self.sim_t_n * self.dt:
         print("\tWarning: Simulation time was changed to {:g} years.".format(self.sim_t_n * self.dt))
      all_processes = ["conversion", "max_solubility", "diffusion", "sorption"]
      if not self.readlistofstrings(main_key + ["include_processes"], allowed=all_processes): return False
      self.processes = {a:a in self.lrvalue for a in all_processes}
      print("\tSimulation parameters were loaded. OK.")
      return True


   # ************ container ****************************

   def _load_container_params(self, main_key):
      print("\tLoading container params ...")
      if not self.readfloat(0.1, 2, main_key + ["radius"]): return False
      self.cont_R = self.lrvalue
      if not self.readfloat(0.1, 20, main_key + ["height"]): return False
      self.cont_h = self.lrvalue
      if not self.readfloat(0.001, 100, main_key + ["free_volume"]): return False
      self.cont_water_V_0 = self.lrvalue
      # ********* water inflow time ***************
      if not self.readfloat(0, float_info.max, main_key + ["T0_water_inflow_time"]): return False
      self.T_i_water_inflow = round(self.lrvalue / self.dt)
      if self.lrvalue != self.T_i_water_inflow * self.dt:
         print("\tWarning: Time of water inflow was changed to {:g} years.".format(self.T_i_water_inflow * self.dt))     
      # ******* direct outflow ****************
      if not self.readfloat(0, 99.99, main_key + ["direct_outflow_into_granite_%/year"]): return False
      self.cont_w_direct_outflow_rate = self.lrvalue / 100
      # **** contact area with bentonite *****************
      if not self._load_contact_area_fcn(main_key + ["bentonite_contact_area_function"]): return False
      print("\tContainer params were loaded. OK.")
      return True


   def _load_contact_area_fcn(self, main_key):
      # *********** times *************************
      if not self.readlistoffloats(0, float("inf"), main_key + ["times"], sorted="asc"): return False
      times = np.array(self.lrvalue)
      if times[0] != 0:
         self.error("First time must be equal to zero.")
         return False
      # ************ values *********************
      if not self.readlistoffloats(0, 100, main_key + ["values_%"], sorted="asc"): return False
      values = np.array(self.lrvalue) / 100    
      if len(values) != len(times):
         self.error("The values list must have same size as times list.")
         return False
      self.fcn_contact_area = self.gen_general_fcn_scalar(times, values)
      return True


   # ************ bentonite ************************

   def get_bent_lay_count(self):
      return len(self.bent_lay_r)


   def _load_bentonite_time_param(self, main_key, min_value, max_value, unit):
      if not self.readlistoffloats(0, 1e9, main_key + ["times"], sorted="asc"): return None
      times = np.array(self.lrvalue)
      if times[0] > 0:
         self.error("First time must be zero.")
         return None
      values = np.empty((self.get_bent_lay_count(), len(times)))
      for i, slc in enumerate(self.zone_layers):
         if not self.readlistoffloats(min_value, max_value, main_key + ["zone"+str(i+1)+"_"+unit]): return None
         if len(self.lrvalue) != len(times):
            self.error("Length of values list must be same as length of times list.")
            return None
         values[slc] = self.lrvalue
      return (times, values)


   def _load_bentonite_params(self, main_key):
      print("\tLoading bentonite params ...")
      if not self.readfloat(0.1, 10, main_key + ["width"]): return False
      self.bent_width = self.lrvalue
      if not self.readfloat(0.0001, 1, main_key + ["dr"]): return False
      self.bent_dr = self.lrvalue
      # ******** layers geometry ****************************
      r = np.arange(self.cont_R, self.cont_R + self.bent_width + 0.001, self.bent_dr)
      if abs(self.cont_R + self.bent_width - r[-1]) > 0.001:
         self.error("Value must be approximate divisible by bentonite width.")
         return False
      r = np.reshape(r, (len(r), 1))
      self.bent_lay_r = r[1:]
      self.bent_lay_geom_V = np.diff(np.pi * r ** 2 * self.cont_h, axis=0)
      # *********************************************
      if not self.readfloat(0, 10000, main_key + ["density"]): return False
      self.bent_density = self.lrvalue
      # ********* zones, times *************************
      if not self.readlistoffloats(0.001, 10, main_key + ["zones_outer_bound"], sorted="asc"): return False
      if self.lrvalue[-1] != self.bent_width:
         self.error("Last value must be equal to bentonite width.")
         return False
      self.zone_layers = []
      p = self.bent_lay_r[:,0] - self.cont_R
      i1 = 0
      for x in self.lrvalue:
         i2 = np.where(p < x + 1e-6)[0][-1] + 1
         self.zone_layers.append(slice(i1 ,i2))
         i1 = i2
      # ********* load functions for zones ************
      p = self._load_bentonite_time_param(main_key + ["De_b_modification"], 0, 200, "%")
      if p is None: return False
      self.fcn_bent_lay_mod_D_ef = self.gen_general_fcn_column(p[0], p[1] / 100)
      p = self._load_bentonite_time_param(main_key + ["porosity"], 0, 100, "%")
      if p is None: return False
      self.fcn_bent_lay_mod_porosity = self.gen_general_fcn_column(p[0], p[1] / 100)
      p = self._load_bentonite_time_param(main_key + ["Kd_b_modification"], 0, 300, "%")
      if p is None: return False
      self.fcn_bent_lay_mod_Kd = self.gen_general_fcn_column(p[0], p[1] / 100)
      # ********** outer bound ******************
      if not self.readstr_selection(["zero_conc", "granite_layer"], main_key + ["bound_model"]): return False
      self.bent_bound_conc_0 = self.lrvalue == "zero_conc"
      print("\tBentonite params were loaded. OK.")
      return True


   # ************ granite ****************************

   def _load_granite_layer_params(self, main_key):
      if not self.readfloat(1e-6, 10, main_key + ["width"]): return False
      self.granit_width = self.lrvalue
      if not self.readfloat(0, 100, main_key + ["conc_by_bentonite_bound_conc_%"]): return False
      self.granit_c_rate = self.lrvalue / 100
      if not self.readstr_selection(["De_g", "De_b_%"], main_key + ["De_source"]): return False
      self.granit_D_ef_source = self.lrvalue
      if self.granit_D_ef_source == "De_b_%":
         if not self.readfloat(0, 100, main_key + ["De_b_%"]): return False
         self.granit_D_ef_by_bent_rate = self.lrvalue / 100
      return True


   # ************* isotopes ***************************

   def get_isot_count(self):
      return len(self.isot_names)

   def get_elem_count(self):
      return len(self.elem_names)


   def _get_isotope_index(self, isotope_name):
      try:
         return self.isot_names.index(isotope_name)
      except ValueError:
         self.error("Isotope '" + isotope_name + "' was not found in isotopes list.")
         return None


   def _get_element_index(self, element_name):
      try:
         return self.elem_names.index(element_name)
      except ValueError:
         self.error("Element '" + element_name + "' was not found in isotopes list.")
         return None


   def _load_isotope_element_names(self, main_key):
      print("\tLoading isotope and element names ...")
      if not self.readlist(main_key): return False
      n = len(self.lrvalue)
      names = []
      for i in range(n):
         if not self.readstr(main_key + [i, "name"]): return False
         if names.count(self.lrvalue) > 0:
            self.error("Isotope with this name is already used.")
            return False
         if re.search("^[A-Za-z]+[0-9]*", self.lrvalue) is None:
            self.error("Isotope name format error.")
            return False
         names.append(self.lrvalue)
      isots = [[i_file, name, name[:re.search("^[A-Za-z]+",name).end()]] for i_file, name in enumerate(names)]
      isot_e = [p[2] for p in isots]
      for p in isots: p.append(isot_e.count(p[2]))
      def isots_sort(i): return i[3], i[2]
      isots.sort(key=isots_sort)
      self.isot_file_index = [p[0] for p in isots]
      self.isot_names = [p[1] for p in isots]
      i = 0
      self.elem_names, self.elem_isotopes = [], []
      while i < self.get_isot_count():
         self.elem_names.append(isots[i][2])
         n = isots[i][3]
         self.elem_isotopes.append(slice(i, i + n) if n > 1 else i)
         i += n
      print("\tNames of {:d} isotopes and {:d} chemical elements were loaded. OK.".format(self.get_isot_count(), len(self.elem_names)))
      return True


   def _load_isotopes_params(self, main_key):
      print("\tLoading basic isotopes params ...")
      n = self.get_isot_count()
      self.isot_M = np.zeros(n)
      self.isot_T_12 = np.full(n, np.inf)
      self.isot_lambda = np.zeros(n)
      self.isot_c_max = np.full(n, np.inf)
      self.isot_bent_D_ef_m2_s = np.zeros(n)
      self.isot_bent_Kd = np.zeros(n)
      self.isot_granit_D_ef_m2_s = np.zeros(n)
      self.isot_init_fuel_mol = np.zeros(n)
      self.isot_soluable_fuel_frac = np.zeros(n)
      init_v = ("init_A_Bq", "init_n_mol", "init_m_kg")
      for i, i_file in enumerate(self.isot_file_index):
         if not self.readfloat(0, 1e16, main_key + [i_file, "M_kg/mol"]): return False
         self.isot_M[i] = self.lrvalue
         if self.processes["conversion"]:
            if not self.readfloat(1e-100, float("inf"), main_key + [i_file, "T_1/2_year"]): return False
            self.isot_T_12[i] = self.lrvalue
            self.isot_lambda[i] = np.log(2) / self.isot_T_12[i]
         if self.processes["max_solubility"]:
            if not self.readfloat(1e-100, float("inf"), main_key + [i_file, "c_max_mol/m3"]): return False
            self.isot_c_max[i] = self.lrvalue
         # ********* bentonite parameters *************
         if self.processes["diffusion"]:
            if not self.readfloat(0, 1, main_key + [i_file, "De_b_m2/s"]): return False
            self.isot_bent_D_ef_m2_s[i] = self.lrvalue
         if self.processes["diffusion"] and self.processes["sorption"]:
            if not self.readfloat(0, 1000, main_key + [i_file, "Kd_b_m3/kg"]): return False
            self.isot_bent_Kd[i] = self.lrvalue
         if self.processes["diffusion"]:
            if self.granit_D_ef_source == "De_g":
               if not self.readfloat(0, 1, main_key + [i_file, "De_g_m2/s"]): return False
               self.isot_granit_D_ef_m2_s[i] = self.lrvalue
            else:
               self.isot_granit_D_ef_m2_s[i] = self.isot_bent_D_ef_m2_s[i] * self.granit_D_ef_by_bent_rate
         # ********* initial mount *******************
         v_count = 0
         for s in init_v:
            if self.key_exists_and_not_None(main_key + [i_file, s]):
               v_count += 1; v_name = s
         if v_count != 1:
            self.error("Just one of keys " + str(init_v) + " must be use as initial state of isotopes.", key = self.lrkey[:-1], value = "")
            return False
         if not self.readfloat(0, float_info.max, main_key + [i_file, v_name]): return False
         if v_name == init_v[0]:
            if self.isot_lambda[i] == 0:
               self.error("Initial state of stable isotope (T_1/2: inf) can not be set by '" + init_v[0] + "' key.")
               return False
            self.isot_init_fuel_mol[i] = self.lrvalue / self.isot_lambda[i] / self.Na * self.year_seconds
         elif v_name == init_v[1]:
            self.isot_init_fuel_mol[i] = self.lrvalue
         else: 
            self.isot_init_fuel_mol[i] = self.lrvalue / self.isot_M[i]
         if not self.readfloat(0, 100, main_key + [i_file, "irf_%"]): return False
         self.isot_soluable_fuel_frac[i] = self.lrvalue / 100
      print("\tBasic isotopes params were loaded. OK.")
      return True


   def _load_isotopes_conversions(self, main_key):
      print("\tLoading isotopes conversions ...")
      n = self.get_isot_count()
      self.isot_products_name = n * [None]
      self.isot_products_rate = n * [None]
      self.mat_lambda = np.diag( - self.isot_lambda)
      for from_i, from_i_file in enumerate(self.isot_file_index):
         conv_to_key = main_key + [from_i_file, "conversion_to"]
         if self.isot_lambda[from_i] > 0:
            # ***** load conversion ********************
            if not self.readvalue(conv_to_key): return False
            if type(self.lrvalue) == list:
               if not self.readlistofstrings(conv_to_key): return False
               new_isot = self.lrvalue
               if not self.readlistoffloats(0, 100, main_key + [from_i_file, "conversion_%"]): return False
               if len(self.lrvalue) != len(new_isot):
                  self.error("List of conversion rates must have same length as list in 'conversion_to' key.")
                  return False
               if abs(sum(self.lrvalue)-100) > 1e-100:
                  self.error("Sum of list must be equal to 100%.")
                  return False
               rate = [v / 100 for v in self.lrvalue]
            else:
               if not self.readstr(conv_to_key): return False
               new_isot, rate = [self.lrvalue], [1]
            # *********** set lambda matrix ***************
            for i, s in enumerate(new_isot):
               self.lrkey, self.lrvalue = conv_to_key, new_isot
               to_i = self._get_isotope_index(s)
               if to_i is None: return False
               if from_i == to_i:
                  self.error("Isotope '" + self.isot_names[from_i] + "' can not convert to same isotope.")
                  return False
               self.mat_lambda[from_i,to_i] = self.isot_lambda[from_i] * rate[i]
            self.isot_products_name[from_i] = new_isot
            self.isot_products_rate[from_i] = rate
         elif self.key_exists_and_not_None(conv_to_key):
            print("\t\tWarning: Key 'convert_to' of isotope '" + self.isot_names[from_i] + "' was ignored.")
      print("\tIsotopes conversions were loaded. OK.")
      return True


   def _load_elements_params(self):
      self.elem_c_max = np.array([self.isot_c_max[e.start if type(e) == slice else e] for e in self.elem_isotopes])
      for ei, e in enumerate(self.elem_names):
         if type(self.elem_isotopes) == slice:
            if len({self.isot_c_max[i] for i in self.elem_isotopes[ei]}) > 1:
               print("Isotopes of element '" + e + "' have different maximum sollubility.")
               return False
      return True


   # ************ degradation function *****************

   def _load_deg_fcn_user_def(self, main_key):
      # *********** times *************************
      if not self.readlistoffloats(0, np.inf, main_key + ["times"], sorted="asc"): return False
      if (times:=np.array(self.lrvalue))[0] != 0:
         self.error("First value must be equal zero.")
         return False
      # ************ values *********************\
      frac_name, frac_pct = "irf", self.soluable_frac * 100
      if not self.readlistoffloats(0, 100, main_key + ["values_%"], sorted="asc", names_dict={frac_name:frac_pct}): return False
      if self.lrvalue[0] != frac_pct:
         self.error("First value must be '" + frac_name + "' const, which is just soluable fraction.")
         return False
      values = np.array(self.lrvalue) / 100
      if len(values) != len(times):
         self.error("The values list must have same size as times list.")
         return False
      self.fcn_deg = self.gen_general_fcn_scalar(times, values)
      return True


   def _load_deg_fcn_power(self, main_key):
      # *********** loading params **************
      if not self.readfloat(0, float("inf"), main_key + ["total_degradation_time_span"]): return False
      T = self.lrvalue
      if not self.readfloat(0, float("inf"), main_key + ["power_factor"]): return False
      pow = self.lrvalue
      if not self.readfloat(0, float("inf"), main_key + ["time_step"]): return False
      step = self.lrvalue
      if step > self.sim_t_n * self.dt:
         self. error("Value must be less or equal than simulation time.")
         return False
      times = np.concatenate(( np.arange(0, T, step), [T] ))
      values = (times / T)**pow * (1 - self.soluable_frac) + self.soluable_frac
      self.fcn_deg = self.gen_general_fcn_scalar(times, values)
      return True


   def _load_degradation_function(self, main_key):
      print("\tLoanding degradation function ...")
      self.soluable_frac = np.sum(self.isot_soluable_fuel_frac * self.isot_init_fuel_mol) / np.sum(self.isot_init_fuel_mol)
      # ******* degradation model ******************
      deg_models = ["user_def", "power"]
      if not self.readstr_selection(deg_models, main_key + ["model"]): return False
      if self.lrvalue == deg_models[0]:
         if not self._load_deg_fcn_user_def(main_key + [deg_models[0]]): return False
      elif self.lrvalue == deg_models[1]:
         if not self._load_deg_fcn_power(main_key + [deg_models[1]]): return False
      print("\tDegradation function was loaded. OK.")
      return True

   
   # *********** output params **********************

   def _load_output_params(self, main_key):
      print("\tLoading output parameters ...")
      # ******** output step time ******************
      if not self.readfloat(0, float_info.max, main_key + ["step_time"]): return False
      if self.lrvalue < self.dt:
         self.error("\tOutput step time must be more or equal to dt value.")
         return False
      self.out_t_n_step = round(self.lrvalue / self.dt)
      if self.lrvalue != self.out_t_n_step * self.dt:
         print("\tWarning: Output step was changed to {:g} years.".format(self.out_t_n_step * self.dt))
      # ********** output object **************************
      out = self.out_model = OutputModel(self)
      # ********** quantities ***************************
      if not self.readlistofstrings(main_key + ["quantities"], allowed = out.quant_arrays.keys()): return False
      out.quantities = self.lrvalue
      # *********** isotopes outputs ************************
      if not self.readlistofstrings(main_key + ["isotopes"], min_items_count=0): return False
      if "all" in self.lrvalue:
         if len(self.lrvalue) > 1:
            self.error("List can not contain another items, when contain 'all' item.")
            return False
         out.isot_indexes = list(range(self.get_isot_count()))   
      else:
         out.isot_indexes = []
         for s in self.lrvalue:
            if (i := self._get_isotope_index(s)) is None: return False
            out.isot_indexes.append(i)
      # *********** elements outputs ************************
      if not self.readlistofstrings(main_key + ["elements"], min_items_count=0): return False
      if "all" in self.lrvalue:
         if len(self.lrvalue) > 1:
            self.error("List can not contain another items, when contain 'all' item.")
            return False
         out.elem_indexes = list(range(self.get_elem_count()))   
      else:
         out.elem_indexes = []
         for s in self.lrvalue:
            if (i := self._get_element_index(s)) is None: return False
            out.elem_indexes.append(i)
      # ********* column ordering **************************
      col_ord = ["quantity", "quantity/name", "quantity/initial_mount", "name/quantity", "initial_mount/quantity"]
      if not self.readstr_selection(col_ord, main_key + ["columns_ordering"]): return False
      out.col_order = self.lrvalue
      if out.col_order != "quantity":
         if not self.readstr_selection(["together","isotopes_elements"], main_key + ["name_ordering"]): return False
         out.isots_elems_order = self.lrvalue
      # ********* summary ************************
      if not self.readbool(main_key + ["summary_quantity"]): return False
      out.summary = self.lrvalue
      # ********* degradation rate ***************
      if not self.readbool(main_key + ["degradation_rate"]): return False
      out.deg_rate = self.lrvalue
      # ********* format **************************
      separators = {
          "dec._col,":(False, ","), 
          "dec._col;":(False, ";"),
          "dec,_col;":(True, ";"),
          "dec._colt":(False, "\t")
      }
      if not self.readdictvalue(separators, main_key + ["separators"]): return False
      out.dec_comma_sep, out.col_sep = self.lrvalue[1]
      if not self.readstr(main_key + ["number_format"]): return False
      out.number_format = self.lrvalue
      # ******** statistics ***********************
      if self.key_exists_and_not_None(main_key + ["statistics"]):
         if not self.readlistofstrings(main_key + ["statistics"], allowed = out.statistic_types.keys()): return False
         out.statistics = self.lrvalue
      else:
         out.statistics = None
      # ******** output file **********************
      if not self.readstr(main_key + ["file_name"]): return False
      if self.lrvalue[-1] == ".":
         self.error("Error of file name format.")
         return False
      out.file_name = self.lrvalue
      # ******* initialize output ******************
      if not out.init_output(): return False
      return True



   # *********** main ***********************************

   def load_data_model(self):
      print("Loading data model ...")
      if not self._load_simulation_params(["simulation_params"]): return False
      if not self._load_container_params(["container"]): return False
      if not self._load_bentonite_params(["bentonite"]): return False
      if not self._load_granite_layer_params(["granite_layer"]): return False
      if not self._load_isotope_element_names(["isotopes"]): return False
      if not self._load_isotopes_params(["isotopes"]): return False
      if not self._load_isotopes_conversions(["isotopes"]): return False
      if not self._load_elements_params(): return False
      if not self._load_degradation_function(["container", "fuel_degradation_function"]): return False
      if not self._load_output_params(["output"]): return False
      print("Data model was loaded. OK.")
      return True




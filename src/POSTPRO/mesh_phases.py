import sys

import subprocess as sp
import numpy as np
from threading import Thread

from mesh import Mesh_Err
from mesh_grid_eset_model import GEmodel_Err

class MP_Err:
   class Times_not_in_phases_error(Exception): pass
   class Value_int_error(Exception):
      def __init__(self, label, obj):
         super().__init__(self, "Value of '" + label + "' must be valid integer.")
         self.obj = obj
   class Value_float_error(Exception):
      def __init__(self, label):
         super().__init__(self, "Value of '" + label + "' must be valid float.")
         self.obj = obj
   class Value_equal_or_more_error(Exception):
      def __init__(self, label, obj, x):
         super().__init__(self, "Value of '{:s}' must be equal or more than {:s}".format(label, str(x)))
         self.obj = obj
   class Value_more_error(Exception):
      def __init__(self, label, obj, x):
         super().__init__(self, "Value of '{:s}' must be more than {:s}".format(label, str(x)))
         self.obj = obj



class MeshPhases:

   def __init__(self, info, params):
      self.info = info
      self.params = params
      self.phases = []

   # ********** inputs validation ****************

   def _valid_value_int(self, label, x):
      try: int(x)
      except: raise MP_Err.Value_int_error(label, None)

   def _valid_value_float(self, label, x):
      try: float(x)
      except: raise MP_Err.Value_loat_error(label, None)

   def _valid_value_equal_or_more(self, label, x0, x):
      if float(x) < float(x0): raise MP_Err.Value_equal_or_more_error(label, None, x0)

   def _valid_value_more(self, label, x0, x):
      if float(x) <= float(x0): raise MP_Err.Value_more_error(label, None, x0)




   # ********** processes reading ****************

   class InfoThread(Thread):
      def __init__(self, meshphases, phase):
         super().__init__()
         self.meshphases, self.phase, self.show = meshphases, phase, False
      def run(self):
         while (s := self.phase.stderr.readline()[:-1]) != "INFO_STOP":
            if self.show: self.meshphases.info(s)

   def _read_phases_info(self, sel_phases):
      thrs = [self.InfoThread(self, p) for p in sel_phases]
      thrs[0].show = True
      for th in thrs: th.start()
      for th in thrs:
         th.show = True
         th.join()

   def _read_phases_result(self, sel_phases):
      res = []
      for p in sel_phases:
         res.append([])
         while (s:=p.stdout.readline()[:-1]) != "END": res[-1].append(s)
      for p in res:
         if (r_typ:=p.pop(0)) == "ERROR":
            exec('raise {:s}("{:s} : {:s}")'.format(p[1], p[0], p[2]))
         elif r_typ != "RESULT":
            raise Exception("Ani RESULT ANI ERROR (" + r_typ + ")")
      return res


   # ********** process executing *******************

   def _terminate_phases(self):
      for p in self.phases: 
         p.terminate()
      self.phases.clear()

   def _create_phases(self, file_names, mesh_file_physicals_name):
      self.info.start("Creating {:d} mesh phases processes".format(len(file_names)))
      self._terminate_phases()
      for i, file_name in enumerate(file_names):
         cmd = ["python", self.params.postpro_dir+"mesh_grid_eset_computing.py", file_name, "No_external_physicals" if mesh_file_physicals_name is None else mesh_file_physicals_name[i], str(i), "phase "+str(i), self.params.time_main_unit]
         p = sp.Popen(cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, universal_newlines=True, creationflags=sp.BELOW_NORMAL_PRIORITY_CLASS)
         self.phases.append(p)
      for p in self.phases:
         if p.stdout.readline().strip() != "PROCESS_START":
            self._terminate_phases()
            raise Exception("Phase starting error !!")
      self._read_phases_info(self.phases)
      self._read_phases_result(self.phases)
      self.info.OK()


   def exec(self, cmd, args_for_all=None, args_per_phase=None, sel_phases=None):
      sel_p = self.phases if sel_phases is None else ((sel_phases,) if type(sel_phases) == sp.Popen else sel_phases)
      if args_for_all is None and args_per_phase is None: ags = len(sel_p) * (None,)
      elif args_for_all is not None and args_per_phase is None: ags = len(sel_p) * (args_for_all,)
      elif args_for_all is None and args_per_phase is not None: ags = args_per_phase
      else: raise Exception("exec: nelze zadat args_for_all a arbs_per_phase soucasne")
      str_a = ["" if ag is None else ",".join(['"'+a+'"' if type(a)==str else str(a) for a in ag]) for ag in ags]
      for p, a in zip(sel_p, str_a):
         print(cmd + "(" + a + ")", file=p.stdin, flush=True)
      self._read_phases_info(sel_p)
      result = self._read_phases_result(sel_p)
      return result if type(sel_phases) != sp.Popen else result[0]


   # ************** OPTIONS ***************************

   def set_OPTION(self, key, value):
      self.info.start("Setting option '{:s}' to value '{:s}'".format(key, str(value)))
      self.exec("out_set_OPTION", args_for_all=[key, value])
      self.info.OK()

   def update_OPTIONs(self):
      self.info.start("Updating options")
      self.exec("out_update_OPTIONs")
      self.info.OK()

   def get_OPTION_asstr(self, key):
      self.info.start("Getting value of option '{:s}'.".format(key))
      value = self.exec("out_get_OPTION", args_for_all=[key], sel_phases=self.phases[0])
      self.info.OK()
      return value[0]

   def set_OPTION_e2_e4_to_tria_by_physicals(self, physicals_name):
      self.info.start("Setting elements for surface elevations calculatig")
      self.exec("out_set_OPTION_e2_e4_to_tria_by_physicals", args_for_all=[physicals_name])
      self.info.OK()

   def get_physicals_OPTION_e2_e4_to_tria(self):
      self.info.start("Getting elements for surface calculation")
      phs = self.exec("out_get_physicals_OPTION_e2_e4_to_tria", sel_phases=self.phases[0])
      self.info.OK()
      return phs


   # ************** COMMANDS ************************

   def load_names_times_of_element_data(self, file_names):
      self.info.start("Loading names and times from $Elementsdata")
      if file_names is not None:
         p_nt = self.exec("out_load_names_times_of_element_data", args_per_phase = [(fn, self.params.time_coef) for fn in file_names])
      else: p_nt = self.exec("out_load_names_times_of_element_data", args_for_all = (None, self.params.time_coef))
      names, times = set(), set()
      for nt in p_nt:
         i = nt.index("")
         names.update(set(nt[:i]))
         times.update(set(nt[i+1:]))
      self.info.OK()
      return sorted(names), sorted(times, key=lambda t: float(t))


   def load_element_data(self, file_names, names, times):
      self.info.start("Loading elements data")
      if times is not None:
         times = [t if type(t) == str else str(t) for t in times]
      if file_names is not None:
         self.exec("out_try_load_element_data", args_per_phase = [(fn, names, times, self.params.time_coef) for fn in file_names])
      else: 
         self.exec("out_try_load_element_data", args_for_all = (None, names, times, self.params.time_coef))
      self.info.OK()
    

   def delete_element_data(self):
      self.info.start("Deleting loaded element data")
      self.exec("out_delete_loaded_element_data")
      self.info.OK()

   def create_grid_positions(self, step, weights_count, x0_y0_xmax_ymax):
      labs = ["Grid step", "IDW weights count", "min x", "min_y", "max x", "max_y"]
      self.info.start("Creating grid positions")
      self._valid_value_float(labs[0], step)
      self._valid_value_more(labs[0], 0, step)
      self._valid_value_int(labs[1], weights_count)
      self._valid_value_more(labs[1], 0, weights_count)
      if x0_y0_xmax_ymax is None:
         r = self.get_xyz_maximum_range()
         x0_y0_xmax_ymax = (r[0], r[1], r[3], r[4])
      else:
         for lb, v in zip(labs[2:], r:=x0_y0_xmax_ymax): self._valid_value_float(lb, v)
         self._valid_value_more(labs[4], r[0], r[2])
         self._valid_value_more(labs[5], r[1], r[3])
      self.exec("out_create_grid_positions", args_for_all=(step, weights_count, x0_y0_xmax_ymax))
      self.info.OK()

   def change_grid_weight_IDW_weight_count(self, c):
      self.info.start("Changing grid IDW weight count")
      self.exec("out_change_grid_IDW_weight_count", args_for_all=[c])
      self.info.OK()

   def add_grid_deep(self, deep, name):
      labs = ["deep"]
      self.info.start("Creating grid of deep")
      self._valid_value_float(labs[0], deep)
      self._valid_value_equal_or_more(labs[0], 0, deep)
      name = self.exec("out_add_grid_deep", args_for_all=(deep, name))
      self.info.OK()
      return name[0][0]

   def add_grid_level(self, z, name):
      labs = ["Level z1"]
      self.info.start("Creating grid of level")
      self._valid_value_float(labs[0], z)
      name = self.exec("out_add_grid_level", args_for_all=(z, name))
      self.info.OK()
      return name[0][0]

   def del_grid(self, name):
      self.info.start("Deleting grid with name '" + name + "'.")
      self.exec("out_del_grid", args_for_all=[name])
      self.info.OK()
 
   def add_eset_deep_range(self, deep1, deep2, name):
      labs = ["Deep 1", "Deep 2"]
      self.info.start("Creating elements set of deeps range")
      self._valid_value_float(labs[0], deep1)
      self._valid_value_equal_or_more(labs[0], 0, deep1)
      self._valid_value_float(labs[1], deep2)
      self._valid_value_more(labs[1], deep1, deep2)
      name = self.exec("out_add_eset_deep_range", args_for_all=(deep1, deep2, name))
      self.info.OK()
      return name[0][0]

   def add_eset_level_range(self, z1, z2, name):
      labs = ["Level z1", "Level z2"] 
      self.info.start("Creating elements set of levels range")
      self._valid_value_float(labs[0], z1)
      self._valid_value_float(labs[1], z2)
      self._valid_value_more(labs[1], z1, z2)
      name = self.exec("out_add_eset_level_range", args_for_all=(z1, z2, name))
      self.info.OK()
      return name[0][0]

   def add_eset_physicals_group(self, physicals_name, name):
      self.info.start("Creating elements set of physical group")
      name = self.exec("out_add_eset_physicals_group", args_for_all=(physicals_name, name))
      self.info.OK()
      return name[0][0]

   def del_eset(self, name):
      self.info.start("Deleting eset with name '" + name + "'.")
      self.exec("out_del_eset", args_for_all=[name])
      self.info.OK()


   # ************** QUERIES ********************************

   def get_phases_count(self):
      return len(self.phases)

   def get_phases_processes_id(self):
      return [p.pid for p in self.phases]
      
   def get_e_data_names_loaded(self):
      return self.exec("out_get_e_data_names", sel_phases=self.phases[0])

   def get_e_data_times_loaded(self):
      p_times = self.exec("out_get_e_data_times")
      return sorted({t for ts in p_times for t in ts}, key=lambda t: float(t))

   def get_e_data_names_times_loaded(self):      
      p = self.exec("out_get_e_data_names_times")
      p_ntcs = [list(zip(ntcs[:(i:=len(ntcs)//3)], ntcs[i:2*i], ntcs[2*i:])) for ntcs in p]
      p_nts = [[ntc[:2] for ntc in ntcs] for ntcs in p_ntcs]
      p_cs = [{ntcs[:2]:ntcs[2] for ntcs in ntcs} for ntcs in p_ntcs]
      names = sorted({n for nts in p_nts for n, _ in nts})
      rows = [[p_i, t] + [p_cs[p_i].get((n,t), "0%") for n in names] for p_i, nts in enumerate(p_nts) for _, t in nts]
      rows.insert(0, ["Phase", "time"] + names)
      max_col_len = [max(len(str(cols[c_i])) for cols in rows) for c_i in range(len(rows[0]))]
      str_rows = ["|".join([str(v).rjust(a) for v, a in zip(cols, max_col_len)]) for cols in rows]
      return rows, str_rows

   def get_esets_name(self):
      return self.exec("out_get_esets_name", sel_phases=self.phases[0])

   def is_grid_positions(self):
      return self.exec("out_is_grid_positions", sel_phases =self.phases[0])[0] == "True"

   def get_grids_name(self):
      return self.exec("out_get_grids_name", sel_phases=self.phases[0])

   def get_physicals_name_of_phase_0(self):
      self.info.start("Getting physical name of first phase")
      phs_names = self.exec("out_get_physicals_name", sel_phases=self.phases[0])
      self.info.OK()
      return phs_names

   def get_xyz_maximum_range(self):
      self.info.start("Getting maximum ranges of all phases")
      p_range = self.exec("out_get_xyz_constrains")
      c = np.array([np.frombuffer(bytes.fromhex(r[0]), np.float64) for r in p_range], np.float64)
      x_0, y_0, z_0 = c[:,:3].min(axis=0)
      x_max, y_max, z_max = c[:,3:].max(axis=0)
      self.info.OK()
      return x_0, y_0, z_0, x_max, y_max, z_max     




   # ************** REPORTS ********************************

   def _distribute_times_to_phases(self, times, exclude_phase_time):
      p_times = self.exec("out_get_e_data_times")
      if exclude_phase_time == "first":
         for tm, down_tm in zip(p_times[1:], p_times[:-1]): 
            if len(tm) == 0 or len(down_tm) == 0: continue
            if tm[0] == down_tm[-1]: tm.pop(0)
      elif exclude_phase_time == "last":
         for tm, up_tm in zip(p_times[:-1], p_times[1:]):
            if len(tm) == 0 or len(up_tm) == 0: continue
            if tm[-1] == up_tm[0]: tm.pop(-1)
      elif exclude_phase_time is not None: 
         raise Exception("Only 'first', 'last' or None")
      if times is None: 
         calc_p_times = p_times
      else:         
         calc_p_times = [[t for t in times if t in p] for p in p_times]
         times_without_phases = sorted(set(times) - {t for p in calc_p_times for t in p})
         if len(times_without_phases): raise MP_Err.Times_not_in_phases_error(times_without_phases)
      return calc_p_times

   def _write_lines_to_file(self, file_name, lines):
      self.info.start("writing file '" + file_name + "'")
      with open(file_name, "w") as f:
         for s in lines: print(s, file=f)
      self.info.OK()


   # ************** eset table reports *******************

   def _report_eset_time_table(self, function_name, esets_name, names, times, exclude_phase_time, col_sep, dec_comma, *add_args):
      if col_sep is None: col_sep = self.params.out_column_separator
      if dec_comma is None: dec_comma = self.params.out_decimal_comma
      if esets_name is None: esets_name = self.exec("out_get_esets_name", sel_phases=self.phases[0])
      if names is None: names = sorted({n for p in self.exec("out_get_e_data_names") for n in p})
      calc_p_times = self._distribute_times_to_phases(times, exclude_phase_time)
      p_args = [(esets_name, names, ts, col_sep, dec_comma, *add_args) for ts in calc_p_times if len(ts) > 0]
      p_sel = [p for p, ts in zip(self.phases, calc_p_times) if len(ts) > 0]
      p_lines = self.exec(function_name, args_per_phase=p_args, sel_phases=p_sel)
      return p_lines

   def report_eset_max_value(self, esets_name, names, times, exclude_phase_time, col_sep, dec_comma, file_name):
      self.info.start("Creating report of elements set maximum value")
      p_lines = self._report_eset_time_table("out_report_eset_max_value", esets_name, names, times, exclude_phase_time, col_sep, dec_comma)
      r = p_lines[0][:3] + [s for lines in p_lines for s in lines[3:]]
      if file_name is not None: self._write_lines_to_file(file_name, r)
      self.info.OK()
      return r

   def report_eset_max_value_difference(self, esets_name, names, times, exclude_phase_time, col_sep, dec_comma, base_eset_name, file_name):
      self.info.start("Creating report of elements sets maximum values difference")
      p_lines = self._report_eset_time_table("out_report_eset_max_value_difference", esets_name, names, times, exclude_phase_time, col_sep, dec_comma, base_eset_name)
      r = p_lines[0][:2] + [s for lines in p_lines for s in lines[2:]]
      if file_name is not None: self._write_lines_to_file(file_name, r)
      self.info.OK()
      return r

   def report_eset_quantiles(self, esets_name, names, times, exclude_phase_time, col_sep, dec_comma, quantiles, file_name):
      self.info.start("Creating report of elements set quantile values")
      p_lines = self._report_eset_time_table("out_report_eset_quantiles", esets_name, names, times, exclude_phase_time, col_sep, dec_comma, quantiles)
      r = p_lines[0][:3] + [s for lines in p_lines for s in lines[3:]]
      if file_name is not None: self._write_lines_to_file(file_name, r)
      self.info.OK()
      return r

   # ************** grid table reports *******************

   def _report_grid_time_table(self, function_name, grids_name, names, times, exclude_phase_time, col_sep, dec_comma, *add_args):
      if col_sep is None: col_sep = self.params.out_column_separator
      if dec_comma is None: dec_comma = self.params.out_decimal_comma
      if grids_name is None: grids_name = self.exec("out_get_grids_name", sel_phases=self.phases[0])
      if names is None: names = sorted({n for p in self.exec("out_get_e_data_names") for n in p})
      calc_p_times = self._distribute_times_to_phases(times, exclude_phase_time)
      p_args = [(grids_name, names, ts, col_sep, dec_comma, *add_args) for ts in calc_p_times if len(ts) > 0]
      p_sel = [p for p, ts in zip(self.phases, calc_p_times) if len(ts) > 0]
      p_lines = self.exec(function_name, args_per_phase=p_args, sel_phases=p_sel)
      return p_lines

   def report_grid_max_value(self, grids_name, names, times, exclude_phase_time, col_sep, dec_comma, file_name):
      self.info.start("Reporting grids maximum value")
      p_lines = self._report_grid_time_table("out_report_grid_max_value", grids_name, names, times, exclude_phase_time, col_sep, dec_comma)
      r = p_lines[0][:3] + [s for lines in p_lines for s in lines[3:]]
      if file_name is not None: self._write_lines_to_file(file_name, r)
      self.info.OK()
      return r

   def report_grid_max_value_difference(self, grids_name, names, times, exclude_phase_time, col_sep, dec_comma, base_grid_name, file_name):
      self.info.start("Reporting grids maximum values difference")
      p_lines = self._report_grid_time_table("out_report_grid_max_value_difference", grids_name, names, times, exclude_phase_time, col_sep, dec_comma, base_grid_name)
      r = p_lines[0][:2] + [s for lines in p_lines for s in lines[2:]]
      if file_name is not None: self._write_lines_to_file(file_name, r)
      self.info.OK()
      return r

   def report_grid_area_over_limits(self, grids_name, names, times, exclude_phase_time, col_sep, dec_comma, limits, file_name):
      self.info.start("Reporting grids area of limit value overflow")
      p_lines = self._report_grid_time_table("out_report_grid_area_over_limits", grids_name, names, times, exclude_phase_time, col_sep, dec_comma, limits)
      r = p_lines[0][:3] + [s for lines in p_lines for s in lines[3:]]
      if file_name is not None: self._write_lines_to_file(file_name, r)
      self.info.OK()
      return r

   def report_grid_quantiles(self, grids_name, names, times, exclude_phase_time, col_sep, dec_comma, quantiles, file_name):
      self.info.start("Creating report of grid quantile values")
      p_lines = self._report_grid_time_table("out_report_grid_quantiles", grids_name, names, times, exclude_phase_time, col_sep, dec_comma, quantiles)
      r = p_lines[0][:3] + [s for lines in p_lines for s in lines[3:]]
      if file_name is not None: self._write_lines_to_file(file_name, r)
      self.info.OK()
      return r


   # ********** grid spatial reports *********************

   def _exec_grid(self, function_name, grids_name, names, times, exclude_phase_time, *add_args):
      if grids_name is None: grids_name = self.exec("out_get_grids_name", sel_phases=self.phases[0])
      if names is None: names = sorted({n for p in self.exec("out_get_e_data_names") for n in p})
      calc_p_times = self._distribute_times_to_phases(times, exclude_phase_time)
      p_args = [(grids_name, names, ts, *add_args) for ts in calc_p_times if len(ts) > 0]
      p_sel = [p for p, ts in zip(self.phases, calc_p_times) if len(ts) > 0]
      p_res = self.exec(function_name, args_per_phase=p_args, sel_phases=p_sel)
      return p_res

   def get_grids_min_max_value(self, grids_name, names, times, exclude_phase_time):
      self.info.start("Searching minimum and maximum value of grids data")
      p_res = self._exec_grid("out_get_grid_min_max_value", grids_name, names, times, exclude_phase_time)
      x_min = min(np.frombuffer(bytes.fromhex(r[0]), np.float64)[0] for r in p_res)
      x_max = min(np.frombuffer(bytes.fromhex(r[0]), np.float64)[1] for r in p_res)
      self.info.OK()
      return x_min, x_max

   def report_grid_images(self, grids_name, names, times, exclude_phase_time, nan_color, colors, isolines, out_dir, file_prefix, file_extension):
      self.info.start("Reporting grid data as images")
      max_t_len = max(map(len, [t for ts in self.exec("out_get_e_data_times") for t in ts] if times is None else times))
      self._exec_grid("out_report_grid_images", grids_name, names, times, exclude_phase_time, nan_color, colors, isolines, max_t_len, out_dir, file_prefix, file_extension)
      self.info.OK()

   def report_grid_asc(self, grids_name, names, times, exclude_phase_time, value_instead_of_nan, out_dir, file_prefix):
      self.info.start("Reporting grid data as *.asc text file")
      max_t_len = max(map(len, [t for ts in self.exec("out_get_e_data_times") for t in ts] if times is None else times))
      self._exec_grid("out_report_grid_asc", grids_name, names, times, exclude_phase_time, value_instead_of_nan, max_t_len, out_dir, file_prefix)
      self.info.OK()

   def report_grid_difference_asc(self, grids_name, names, times, exclude_phase_time, base_grid_name, value_instead_of_nan, out_dir, file_prefix):
      self.info.start("Reporting grid data as *.asc text file")
      max_t_len = max(map(len, [t for ts in self.exec("out_get_e_data_times") for t in ts] if times is None else times))
      self._exec_grid("out_report_grid_difference_asc", grids_name, names, times, exclude_phase_time, base_grid_name, value_instead_of_nan, max_t_len, out_dir, file_prefix)
      self.info.OK()

   def report_grid_asc_as_pct(self, grids_name, names, times, exclude_phase_time, value_instead_of_nan, value_100pct, dec_num, out_dir, file_prefix):
      self.info.start("Reporting grid data as *.asc in percentiles form")
      max_t_len = max(map(len, [t for ts in self.exec("out_get_e_data_times") for t in ts] if times is None else times))
      self._exec_grid("out_report_grid_asc_as_pct", grids_name, names, times, exclude_phase_time, value_instead_of_nan, value_100pct, dec_num, max_t_len, out_dir, file_prefix)
      self.info.OK()

   def report_grid_difference_asc_as_pct(self, grids_name, names, times, exclude_phase_time, base_grid_name, value_instead_of_nan, dec_num, out_dir, file_prefix):
      self.info.start("Reporting grid difference data as *.asc in percentiles form")
      max_t_len = max(map(len, [t for ts in self.exec("out_get_e_data_times") for t in ts] if times is None else times))
      self._exec_grid("out_report_grid_difference_asc_as_pct", grids_name, names, times, exclude_phase_time, base_grid_name, value_instead_of_nan, dec_num, max_t_len, out_dir, file_prefix)
      self.info.OK()


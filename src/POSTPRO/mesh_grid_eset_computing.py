from sys import stdin, stdout, argv

import numpy as np
from matplotlib.pyplot import imsave

from info import Info
from mesh_grid_eset_model import MeshGridEsetModel


class GEComputing_Err:
   pass


class MeshGridEsetComputing(MeshGridEsetModel):

   def __init__(self, msh_file, msh_file_physicals_name, info, time_unit):
      super().__init__(msh_file, msh_file_physicals_name, info)
      self.time_unit = time_unit
      self._physicals_name_for_e2_e4_to_tria = sorted(self.physicals.keys())

   # ********* setings ******************************

   def out_set_OPTION(self, key, value):
      try: self.__dict__["OPTION_" + key]
      except: raise Exception("Key Option '"+ key + "' not exist")
      self.__dict__["OPTION_" + key] = value

   def out_update_OPTIONs(self):
      self.try_clear_bands_tria()
      self.try_clear_buf_bands()
      self.try_clear_e_planes()
      self.try_clear_grids_IDW_e_weights()

   def out_get_OPTION(self, key):
      try: self.__dict__["OPTION_" + key]
      except: raise Exception("Key Option '"+ key + "' not exist")
      return [str(self.__dict__["OPTION_" + key])]

   def out_set_OPTION_e2_e4_to_tria_by_physicals(self, physicals_name):
      self._physicals_name_for_e2_e4_to_tria = physicals_name
      self.OPTION_e2_to_tria = np.fromiter((e for n in physicals_name if (p:=self.physicals[n]).dim == 2 for e in p.elements), np.int32)
      self.OPTION_e4_to_tria = np.fromiter((e for n in physicals_name if (p:=self.physicals[n]).dim == 3 for e in p.elements), np.int32)

   def out_get_physicals_OPTION_e2_e4_to_tria(self):
      return self._physicals_name_for_e2_e4_to_tria


   # ********* questions ****************************

   def out_get_xyz_constrains(self):
      return [np.array([self.x_0, self.y_0, self.z_0, self.x_max, self.y_max, self.z_max]).tobytes().hex()]

   def out_is_grid_positions(self):
      return [str(self.is_grid_positions)]

   def out_get_esets_name(self):
      return sorted(self.esets)

   def out_get_grids_name(self):
      return sorted(self.grids)

   def out_get_physicals_name(self):
      phs = sorted(self.physicals.values(), key=lambda p: p.name)
      return [p.name for p in phs]

   def out_get_e_data_names(self):
      return sorted({n for n, _ in self.e_data})
      
   def out_get_e_data_times(self):
      return sorted({t for _, t in self.e_data}, key=lambda t: float(t))

   def out_get_e_data_names_times(self):
      a = sorted(self.e_data.keys(), key=lambda nt: float(nt[1]))
      n_t = [n for n, _ in a] + [t for _, t in a]
      v = ["Loaded OK." if (n:=np.sum(np.isnan(self.e_data[nt][1:]))) == 0 else "{:d} not loaded".format(n) for nt in a]
      return n_t + v


   # ********* model manipulatins *******************

   def out_load_names_times_of_element_data(self, file_name, time_conversion_coef):
      names, times = self.load_names_times_of_element_data(file_name, time_conversion_coef)
      return names + [""] + times

   def out_try_load_element_data(self, file_name, names, times, time_conversion_coef):
      self.try_load_element_data(file_name, names, times, time_conversion_coef)

   def out_delete_loaded_element_data(self):
      self.delete_loaded_element_data()

   def out_create_grid_positions(self, step, idw_weight_count, x0_y0_xmax_ymax):
      self.create_grid_positions(float(step), int(idw_weight_count), *map(float,x0_y0_xmax_ymax))
    
   def out_change_grid_IDW_weight_count(self, c):
      self.change_grid_IDW_weight_count(int(c))

   def out_add_grid_deep(self, deep, name):
      return [self.add_grid_deep(float(deep), name)]

   def out_add_grid_level(self, z, name):
      return [self.add_grid_level(float(z), name)]

   def out_del_grid(self, name):
      self.del_grid(name)

   def out_add_eset_deep_range(self, deep1, deep2, name):
      return [self.add_eset_deep_range(float(deep1), float(deep2), name)]

   def out_add_eset_level_range(self, z1, z2, name):
      return [self.add_eset_level_range(float(z1), float(z2), name)]

   def out_add_eset_physicals_group(self, physicals_name, name):
      return [self.add_eset_physicals_group(physicals_name, name)]

   def out_del_eset(self, name):
      self.del_eset(name)


   # *********** report private ***************************

   def dec_sep_to_comma(self, first_i, lines):
      for i in range(first_i, len(lines)):
         lines[i] = lines[i].replace(".", ",")


   # ************ eset table reports *********************

   def out_report_eset_max_value(self, esets_name, names, times, col_sep, dec_comma):
      self.info.start("Reporting maximum of element set.")
      head1 = ["", ""] + [eset_n for eset_n in esets_name for _ in names for _ in range(4)]
      head2 = ["", ""] + [n for _ in esets_name for n in names for _ in range(4)]
      head3 = ["phase","time ["+self.time_unit+"]"] + [v for _ in esets_name for _ in names for v in ["c (max)", "x [m]", "y [m]", "z [m]"]]
      rows = [head1, head2, head3]
      for time in times:         
         row = ["{:d}".format(self.info.process_id), "{:s}".format(time)]
         for eset_n in esets_name:
            elms = self.esets[eset_n].elms
            T = self.e_T[elms]
            for name in names:
               v = self.e_data[(name,time)][elms]
               i = np.nanargmax(v)
               row.append("{:g}".format(v[i]))
               row.append("{:.1f}".format(T[i,0]))
               row.append("{:.1f}".format(T[i,1]))
               row.append("{:.1f}".format(T[i,2]))
         rows.append(row)
         self.info("Time {:s} OK.".format(time))
      max_len = [max(len(r[col]) for r in rows) for col in range(len(head1))]
      lines = [col_sep.join([s.rjust(m) for s, m in zip(cols, max_len)]) for cols in rows]
      if dec_comma: self._dec_sep_to_comma(3, lines)
      self.info.OK()
      return lines


   def out_report_eset_max_value_difference(self, esets_name, names, times, col_sep, dec_comma, base_eset_name):
      self.info.start("Reporting maximum difference of element set from base element set.")
      head1 = ["", ""] + [eset_n for eset_n in esets_name for _ in names for _ in range(5)]
      head2 = ["", ""] + [n for _ in esets_name for n in names for _ in range(5)]
      head3 = ["phase","time ["+self.time_unit+"]"] + [v for _ in esets_name for _ in names for v in ["delta c_max [?]", "c_max [%]", "xy distance [m]", "z distance [m]", "distance [m]"]]
      rows = [head1, head2, head3]
      base_elms = self.esets[base_eset_name].elms
      T0 = self.e_T[base_elms]
      for time in times:         
         row = ["{:d}".format(self.info.process_id), "{:s}".format(time)]        
         for eset_n in esets_name:
            elms = self.esets[eset_n].elms
            T = self.e_T[elms]
            for name in names:
               v0 = self.e_data[(name,time)][base_elms]
               i0 = np.nanargmax(v0) 
               v = self.e_data[(name,time)][elms]
               i = np.nanargmax(v)
               x0, y0, z0, x, y, z = *T0[i0], *T[i]
               row.append("{:g}".format(v[i] - v0[i0]))
               row.append("{:.2g}".format(100 * v[i] / v0[i0]))
               row.append("{:.1f}".format(((x0-x)**2+(y0-y)**2)**0.5))
               row.append("{:.1f}".format(z - z0))
               row.append("{:.1f}".format(((x0-x)**2+(y0-y)**2+(z0-z)**2)**0.5))
         rows.append(row)
         self.info("Time {:s} OK.".format(time))
      max_len = [max(len(r[col]) for r in rows) for col in range(len(head1))]
      lines = [col_sep.join([s.rjust(m) for s, m in zip(cols, max_len)]) for cols in rows]
      if dec_comma: self._dec_sep_to_comma(3, lines)
      self.info.OK()
      return lines


   def out_report_eset_quantiles(self, esets_name, names, times, col_sep, dec_comma, pct_quantiles):
      self.info.start("Reporting quantiles of element set.")
      quantiles = [x/100 for x in map(float, pct_quantiles)]
      head1 = ["",""] + [eset_n for eset_n in esets_name for _ in names for _ in range(len(quantiles))]
      head2 = ["",""] + [n for _ in esets_name for n in names for _ in range(len(quantiles))]
      head3 = ["phase","time ["+self.time_unit+"]"] + [v for _ in esets_name for _ in names for v in ["quantile {:.2%}".format(q) for q in quantiles]]
      rows = [head1, head2, head3]
      for time in times:         
         row = ["{:d}".format(self.info.process_id), "{:s}".format(time)]
         for eset_n in esets_name:
            elms = self.esets[eset_n].elms
            for name in names:
               q = np.nanquantile(self.e_data[(name,time)][elms], quantiles)
               for v in q: row.append("{:g}".format(v))
         rows.append(row)
         self.info("Time {:s} OK.".format(time))
      max_len = [max(len(r[col]) for r in rows) for col in range(len(head1))]
      lines = [col_sep.join([s.rjust(m) for s, m in zip(cols, max_len)]) for cols in rows]
      if dec_comma: self._dec_sep_to_comma(3, lines)
      self.info.OK()
      return lines



   # *********** grid table reports *******************

   def out_report_grid_max_value(self, grids_name, names, times, col_sep, dec_comma):
      self.info.start("Reporting maximum of grids.")
      head1 = ["", ""] + [grid_n for grid_n in grids_name for _ in names for _ in range(6)]
      head2 = ["", ""] + [n for _ in grids_name for n in names for _ in range(6)]
      head3 = ["phase","time ["+self.time_unit+"]"] + [v for _ in grids_name for _ in names for v in ["c (max)", "xi", "yi", "x [m]", "y [m]", "z [m]"]]
      rows = [head1, head2, head3]
      for time in times:         
         row = ["{:d}".format(self.info.process_id), "{:s}".format(time)]
         for grid_n in grids_name:
            for name in names:
               d = self.get_grid_IDW_data(grid_n, name, time)
               i = np.nanargmax(d)
               xi, yi = self.grid_pos_xi[i], self.grid_pos_yi[i]
               row.append("{:g}".format(d[i]))
               row.append("{:d}".format(xi))
               row.append("{:d}".format(yi))
               row.append("{:.1f}".format(self.grid_x[xi]))
               row.append("{:.1f}".format(self.grid_y[yi]))
               row.append("{:.1f}".format(self.get_grid_pos_z(grid_n, i)))
            if len(grids_name) > 1: self.try_clear_grids_IDW_e_weights()
         rows.append(row)
         self.info("Time {:s} OK.".format(time))
      self.try_clear_grids_IDW_e_weights()
      max_len = [max(len(r[col]) for r in rows) for col in range(len(head1))]
      lines = [col_sep.join([s.rjust(m) for s, m in zip(cols, max_len)]) for cols in rows]
      if dec_comma: self._dec_sep_to_comma(3, lines)
      self.info.OK()
      return lines


   def out_report_grid_max_value_difference(self, grids_name, names, times, col_sep, dec_comma, base_grid_name):
      self.info.start("Reporting maximum difference of grids.")
      head1 = ["", ""] + [grid_n for grid_n in grids_name for _ in names for _ in range(5)]
      head2 = ["", ""] + [n for _ in grids_name for n in names for _ in range(5)]
      head3 = ["phase","time ["+self.time_unit+"]"] + [v for _ in grids_name for _ in names for v in ["delta c_max [?]", "c_max [%]", "xy distance [m]", "z distance [m]", "distance [m]"]]
      rows = [head1, head2, head3]
      data = np.empty(self.grid_pos_count)
      for time in times:         
         row = ["{:d}".format(self.info.process_id), "{:s}".format(time)]
         for grid_n in grids_name:
            for name in names:
               data[:] = self.get_grid_IDW_data(base_grid_name, name, time)
               self.try_clear_grids_IDW_e_weights()
               i0 = np.nanargmax(data)
               v0 = data[i0]
               xi0, yi0 = self.grid_pos_xi[i0], self.grid_pos_yi[i0]
               x0, y0, z0 = self.grid_x[xi0], self.grid_y[yi0], self.get_grid_pos_z(base_grid_name, i0)
               data[:] = self.get_grid_IDW_data(grid_n, name, time)
               self.try_clear_grids_IDW_e_weights()
               i = np.nanargmax(data)
               v = data[i]
               xi, yi = self.grid_pos_xi[i], self.grid_pos_yi[i]
               x, y, z = self.grid_x[xi], self.grid_y[yi], self.get_grid_pos_z(grid_n, i)
               row.append("{:g}".format(v - v0))
               row.append("{:.2g}".format(100 * v / v0))
               row.append("{:.1f}".format(((x0-x)**2+(y0-y)**2)**0.5))
               row.append("{:.1f}".format(z - z0))
               row.append("{:.1f}".format(((x0-x)**2+(y0-y)**2+(z0-z)**2)**0.5))
         rows.append(row)
         self.info("Time {:s} OK.".format(time))
      max_len = [max(len(r[col]) for r in rows) for col in range(len(head1))]
      lines = [col_sep.join([s.rjust(m) for s, m in zip(cols, max_len)]) for cols in rows]
      if dec_comma: self._dec_sep_to_comma(3, lines)
      self.info.OK()
      return lines


   def out_report_grid_area_over_limits(self, grids_name, names, times, col_sep, dec_comma, limits):
      self.info.start("Reporting grid area with limits overflow")
      limits = list(map(float, limits))
      head1 = ["",""] + [grid_n for grid_n in grids_name for _ in names for _ in range(2*len(limits))]
      head2 = ["",""] + [n for _ in grids_name for n in names for _ in range(2*len(limits))]
      head3 = ["phase","time ["+self.time_unit+"]"] + [v for _ in grids_name for _ in names for limit in limits for v in ["S [m2] (limit {:g})".format(limit), "rate [%] (limit {:g})".format(limit)]]
      rows = [head1, head2, head3]
      for time in times:         
         row = ["{:d}".format(self.info.process_id), "{:s}".format(time)]
         for grid_n in grids_name:
            for name in names:
               d = self.get_grid_IDW_data(grid_n, name, time)
               for limit in limits:  
                  a = np.sum((~np.isnan(d)) & (d > limit))
                  row.append("{:.0f}".format(a * self.grid_A_sqr))
                  row.append("{:.2f}".format(100 * a / self.grid_pos_count))
            if len(grids_name) > 1: self.try_clear_grids_IDW_e_weights()
         rows.append(row)
         self.info("Time {:s} OK.".format(time))
      self.try_clear_grids_IDW_e_weights()
      max_len = [max(len(r[col]) for r in rows) for col in range(len(head1))]
      lines = [col_sep.join([s.rjust(m) for s, m in zip(cols, max_len)]) for cols in rows]
      if dec_comma: self._dec_sep_to_comma(3, lines)
      self.info.OK()
      return lines


   def out_report_grid_quantiles(self, grids_name, names, times, col_sep, dec_comma, pct_quantiles):
      self.info.start("Reporting quantiles of grids")
      quantiles = [x/100 for x in map(float, pct_quantiles)]
      head1 = ["",""] + [grid_n for grid_n in grids_name for _ in names for _ in range(len(quantiles))]
      head2 = ["",""] + [n for _ in grids_name for n in names for _ in range(len(quantiles))]
      head3 = ["phase","time ["+self.time_unit+"]"] + [v for _ in grids_name for _ in names for v in ["quantile {:.2%}".format(q) for q in quantiles]]
      rows = [head1, head2, head3]
      for time in times:         
         row = ["{:d}".format(self.info.process_id), "{:s}".format(time)]
         for grid_n in grids_name:
            for name in names:
               q = np.nanquantile(self.get_grid_IDW_data(grid_n, name, time), quantiles)
               for v in q: row.append("{:g}".format(v))
            if len(grids_name) > 1: self.try_clear_grids_IDW_e_weights()
         rows.append(row)
         self.info("Time {:s} OK.".format(time))
      self.try_clear_grids_IDW_e_weights()
      max_len = [max(len(r[col]) for r in rows) for col in range(len(head1))]
      lines = [col_sep.join([s.replace(".",",").rjust(m) for s, m in zip(cols, max_len)]) for cols in rows]
      lines = [col_sep.join([s.rjust(m) for s, m in zip(cols, max_len)]) for cols in rows]
      if dec_comma: self._dec_sep_to_comma(3, lines)
      self.info.OK()
      return lines


   # ************ grid spatial reports *******************

   def out_get_grid_min_max_value(self, grids_name, names, times):
      self.info.start("Searching minimum and maximum of grid data")
      x_min, x_max = np.inf, - np.inf
      for g in grids_name:
         for n, t in ((n,t) for n in names for t in times):
            d = self.get_grid_IDW_data(g, n, t)
            d = d[np.logical_not(np.isnan(d))]
            if (a:=d.min()) < x_min: x_min = a
            if (a:=d.max()) > x_max: x_max = a
         self.try_clear_grids_IDW_e_weights()
      self.info.OK()
      return [np.array([x_min, x_max], np.float64).tobytes().hex()]


   def out_report_grid_images(self, grids_name, names, times, nan_color, colors, isolines, max_time_len, out_dir, file_prefix, file_extension):
      self.info.start("Creating grid images")
      isolines = list(map(float, isolines))
      max_grid_name_len = max(map(len, grids_name))
      max_name_len = max(map(len, names))
      img = np.empty((len(self.grid_y), len(self.grid_x), 3), np.ubyte)
      data = np.empty((len(self.grid_y), len(self.grid_x)), np.float64)
      for g in grids_name:
         for n, t in ((n,t) for n in names for t in times):
            img[:], data[:] = nan_color, np.nan
            data[self.grid_pos_yi,self.grid_pos_xi] = self.get_grid_IDW_data(g, n, t)
            if colors is not None:
               img[data < isolines[0]] = colors[0]
               for iso, c in zip(isolines, colors[1:]): img[data >= iso] = c
            elif len(isolines) == 2:
               b = data < isolines[0]
               img[b] = (0, 0, 255)
               b = (data >= isolines[0]) & (data < isolines[1])
               img[b,0] = (data[b] / isolines[1] * 255).astype(np.ubyte)
               img[b,1] = 0
               img[b,2] = 255 - img[b,0]
               b = data >= isolines[1]
               img[b] = (255, 0, 0)
            elif len(isolines) == 3:
               b = data < isolines[0]
               img[b] = (0, 0, 255)
               b = (data >= isolines[0]) & (data < isolines[1])
               img[b,0] = 0 
               img[b,1] = (data[b] / isolines[1] * 255).astype(np.ubyte)
               img[b,2] = 255 - img[b,1]
               b = (data >= isolines[1]) & (data < isolines[2])
               img[b,0] = (data[b] / isolines[2] * 255).astype(np.ubyte)
               img[b,1] = 255 - img[b,0]
               img[b,2] = 0
               b = data >= isolines[2]
               img[b] = (255, 0, 0)
            f_name = out_dir + "/" + "_".join([file_prefix, g.ljust(max_grid_name_len), n.ljust(max_name_len), t.zfill(max_time_len)]).replace(" ","_") + "." + file_extension
            img[:] = np.flip(img, axis=0)
            imsave(f_name, img)
            self.info("file '{:s}' writen".format(f_name))
         self.try_clear_grids_IDW_e_weights()
      self.info.OK()


   def _seve_asc_file(self, file_name, data, value_instead_of_nan, row_format):
      with open(file_name, "w") as f:
         f.write("ncols        {:g}\n".format(len(data[0])))
         f.write("nrows        {:g}\n".format(len(data)))
         f.write("xllcorner    {:g}\n".format(self.grid_x[0]))
         f.write("yllcorner    {:g}\n".format(self.grid_y[0]))
         f.write("cellsize     {:g}\n".format(self.grid_step))
         f.write("NODATA_value {:g}\n".format(value_instead_of_nan))
         data[np.isnan(data)] = value_instead_of_nan
         data[:] = np.flip(data, axis=0)
         for row in data: f.write(row_format.format(*row))


   def out_report_grid_asc(self, grids_name, names, times, value_instead_of_nan, max_time_len, out_dir, file_prefix):
      self.info.start("Creating grid as *.ASC file")
      value_instead_of_nan = float(value_instead_of_nan)
      max_grid_name_len = max(map(len, grids_name))
      max_name_len = max(map(len, names))
      data = np.empty((len(self.grid_y), len(self.grid_x)), np.float64)
      form_str = " ".join(len(self.grid_x)*["{:g}"]) + "\n"
      for g in grids_name:
         for n, t in ((n,t) for n in names for t in times):
            data[:] = np.nan
            data[self.grid_pos_yi, self.grid_pos_xi] = self.get_grid_IDW_data(g, n, t)
            f_name = out_dir + "/" + "_".join([file_prefix, g.ljust(max_grid_name_len), n.ljust(max_name_len), t.zfill(max_time_len)]).replace(" ","_") + ".asc"
            self._seve_asc_file(f_name, data, value_instead_of_nan, form_str)
            self.info("file '{:s}' writen".format(f_name))
         self.try_clear_grids_IDW_e_weights()
      self.info.OK()


   def out_report_grid_difference_asc(self, grids_name, names, times, base_grid_name, value_instead_of_nan, max_time_len, out_dir, file_prefix):
      self.info.start("Creating grid as *.ASC file")
      value_instead_of_nan = float(value_instead_of_nan)
      max_grid_name_len = max(map(len, grids_name))
      max_name_len = max(map(len, names))
      data = np.empty((len(self.grid_y), len(self.grid_x)), np.float64)
      form_str = " ".join(len(self.grid_x)*["{:g}"]) + "\n"     
      for n, t in ((n,t) for n in names for t in times):
         base = self.get_grid_IDW_data(base_grid_name, n, t)
         self.try_clear_grids_IDW_e_weights()
         for g in grids_name:
            data[:] = np.nan
            data[self.grid_pos_yi, self.grid_pos_xi] = self.get_grid_IDW_data(g, n, t) - base
            self.try_clear_grids_IDW_e_weights()
            f_name = out_dir + "/" + "_".join([file_prefix, g.ljust(max_grid_name_len), n.ljust(max_name_len), t.zfill(max_time_len)]).replace(" ","_") + ".asc"
            self._seve_asc_file(f_name, data, value_instead_of_nan, form_str)
            self.info("file '{:s}' writen".format(f_name))
      self.info.OK()


   def out_report_grid_asc_as_pct(self, grids_name, names, times, value_instead_of_nan, value_100pct, dec_num, max_time_len, out_dir, file_prefix):
      self.info.start("Creating grid in *.ASC file as percentiles")
      value_instead_of_nan = float(value_instead_of_nan)
      dec_num = int(dec_num)
      coef = 100 / float(value_100pct)
      max_grid_name_len = max(map(len, grids_name))
      max_name_len = max(map(len, names))
      data = np.empty((len(self.grid_y), len(self.grid_x)), np.float64)
      for g in grids_name:
         for n, t in ((n,t) for n in names for t in times):
            data[:] = np.nan
            data[self.grid_pos_yi, self.grid_pos_xi] = coef * self.get_grid_IDW_data(g, n, t)
            f_name = out_dir + "/" + "_".join([file_prefix, g.ljust(max_grid_name_len), n.ljust(max_name_len), t.zfill(max_time_len)]).replace(" ","_") + ".asc"
            form_str = " ".join(len(self.grid_x)*["{:."+str(dec_num)+"f}"]) + "\n"
            self._seve_asc_file(f_name, data, value_instead_of_nan, form_str)
            self.info("file '{:s}' writen".format(f_name))
         self.try_clear_grids_IDW_e_weights()
      self.info.OK()


   def out_report_grid_difference_asc_as_pct(self, grids_name, names, times, base_grid_name, value_instead_of_nan, dec_num, max_time_len, out_dir, file_prefix):
      self.info.start("Creating grid difference as *.ASC file in percetiles")
      value_instead_of_nan = float(value_instead_of_nan)
      dec_num = int(dec_num)
      max_grid_name_len = max(map(len, grids_name))
      max_name_len = max(map(len, names))
      data = np.empty((len(self.grid_y), len(self.grid_x)), np.float64)
      for n, t in ((n,t) for n in names for t in times):
         base = self.get_grid_IDW_data(base_grid_name, n, t)
         self.try_clear_grids_IDW_e_weights()
         for g in grids_name:
            d = self.get_grid_IDW_data(g, n, t)
            data[:] = np.nan
            with np.errstate(divide="ignore", invalid="ignore"):
               data[self.grid_pos_yi, self.grid_pos_xi] = \
                  np.where((base != 0) & (d != 0), 100 * d / base, 0)
            self.try_clear_grids_IDW_e_weights()
            f_name = out_dir + "/" + "_".join([file_prefix, g.ljust(max_grid_name_len), n.ljust(max_name_len), t.zfill(max_time_len)]).replace(" ","_") + ".asc"
            form_str = " ".join(len(self.grid_x)*["{:."+str(dec_num)+"f}"]) + "\n"
            self._seve_asc_file(f_name, data, value_instead_of_nan, form_str)
            self.info("file '{:s}' writen".format(f_name))
      self.info.OK()






# ********************************************************
# ************* mesh process *****************************

def mesh_process():
   # ************ creating mesh *******************
   try:
      print("PROCESS_START", flush=True)
      info = Info(int(argv[3]), argv[4])
      model = MeshGridEsetComputing(argv[1], None if argv[2] == "No_external_physicals" else argv[2], info, argv[5])
      info.stop()
      print("RESULT")
      print("END")
      stdout.flush()
   except Exception as e:
      info.error(e)
      info.stop()
      print("ERROR")
      print(info.process_name)
      print(e.__class__.__qualname__)
      print(e.with_traceback(None))
      print("END")
      stdout.flush()
      return
   # *********** methods calling ******************
   while True:
      cmd = stdin.readline().strip()
      try:
         result = eval("model." + cmd)
         info.stop()
         print("RESULT")     
         if result is not None:
            for s in result: print(s)
      except Exception as e:
         model.info.error(e)
         info.stop()
         print("ERROR")
         print(info.process_name)
         print(e.__class__.__qualname__)
         print(e.with_traceback(None))
      print("END")
      stdout.flush()

               
if __name__ == "__main__": mesh_process()
      



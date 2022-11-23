import gc
import numpy as np
from math import floor, inf
from statistics import mode

from mesh import Mesh

class Triangle:

   def __init__(self, n1, n2, n3, abc):
      self.n1, self.n2, self.n3 = n1, n2, n3
      self.abc = abc
      self.min_x, self.max_x = min(n1.x, n2.x, n3.x), max(n1.x, n2.x, n3.x)
      self.min_y, self.max_y = min(n1.y, n2.y, n3.y), max(n1.y, n2.y, n3.y)
      self.min_z, self.max_z = min(n1.z, n2.z, n3.z), max(n1.z, n2.z, n3.z)


# ****************************************************

class MeshBandModel(Mesh):

   def __init__(self, msh_file, msh_file_physicals_name, info):
      super().__init__(msh_file, msh_file_physicals_name, info)
      self.set_general_mesh_params()
      self.set_elements_T()     
      self.OPTION_band_xy_width = None
      self.OPTION_band_z_width = None
      self.OPTION_e2_to_tria = np.arange(self.e2_slice.start, self.e2_slice.stop, dtype=np.int32)
      self.OPTION_e4_to_tria = np.arange(self.e4_slice.start, self.e4_slice.stop, dtype=np.int32)
      self._buf_bands_e4_points = {}
      self._buf_bands_tria = {}
      self.OPTION_keep_bands_tria = True
      self.OPTION_keep_buf_bands = True


   # ********* creating bands - PRIVATE *****************

   def _set_params_of_bands_xy_creating(self):
      if "band_xy_width" in self.__dict__:
         if self._actual_band_xy_width == self.OPTION_band_xy_width: return
      self._actual_band_xy_width = self.OPTION_band_xy_width
      self.info.start("Setting params to bands xy creating")
      if self._actual_band_xy_width is None:
         self.info.start("Calculating automatic bands xy width ...")
         w = self.band_xy_width = min(mode(self.e_max_x[1:] - self.e_min_x[1:]), mode(self.e_max_y[1:] - self.e_min_y[1:]))
         self.info.OK()
      else:
         w = self.band_xy_width = self._actual_band_xy_width
      self.info("bands xy width: {:g}".format(w))     
      self.info("Number of bands along axis x:  {:d}".format(floor(self.x_range/w)+1))
      self.info("Number of bands along axis y:  {:d}".format(floor(self.y_range/w)+1))
      # ************* reset bands *************************
      self.bands_x_e1 = self.bands_x_e2 = self.bands_x_e4 = self.bands_x_tria = None
      self.bands_y_e1 = self.bands_y_e2 = self.bands_y_e4 = self.bands_y_tria = None
      self.clear_buf_bands()
      self.info.OK()


   def _set_params_of_bands_z_creating(self):
      if "band_z_width" in self.__dict__:
         if self._actual_band_z_width == self.OPTION_band_z_width: return
      self._actual_band_z_width = self.OPTION_band_z_width
      self.info.start("Setting params to bands z creating")
      if self._actual_band_z_width is None:
         self.info.start("Calculating automatic bands z width")
         w = self.band_z_width = mode(z for z in self.e_max_z[1:] - self.e_min_z[1:] if z != 0)
         self.info.OK()
      else:
         w = self.band_z_width = self._actual_band_z_width
      self.info("bands z width: {:g}".format(w)) 
      self.info("Number of bands along axis z: {:d}".format(floor(self.z_range/w)+1))          
      # ************* reset bands *************************
      self.bands_z_e1 = self.bands_z_e2 = self.bands_z_e4 = None
      self.clear_buf_bands()
      self.info.OK()

   def clear_bands_tria(self):
      self.bands_x_tria = self.bands_y_tria = None
      gc.collect()

   def try_clear_bands_tria(self):
      if not self.OPTION_keep_bands_tria: self.clear_bands_tria()


   def clear_buf_bands(self):
      self._buf_bands_e4_points.clear()
      self._buf_bands_tria.clear()
      gc.collect()

   def try_clear_buf_bands(self):
      if not self.OPTION_keep_buf_bands: self.clear_buf_bands()


   def _create_e1_xy_bands(self):
      if self.e1_count == 0: return
      if self.bands_x_e1 is not None and self.bands_y_e1 is not None: return
      self.info.start("Creating bands x, y of 1D elements (type 1 - lines)")
      w, x0, y0 = self.band_xy_width, self.x_0, self.y_0
      self.bands_x_e1 = bands_x = [set() for _ in range(floor(self.x_range/w)+1)]
      for e, i1, i2 in zip(range(self.e1_slice.start, self.e1_slice.stop), np.floor((self.e_min_x[self.e1_slice]-x0)/w).astype(int), np.floor((self.e_max_x[self.e1_slice]-x0)/w).astype(int)+1):
         for s in bands_x[i1:i2]: s.add(e)
      self.bands_y_e1 = bands_y = [set() for _ in range(floor(self.y_range/w)+1)]
      for e, i1, i2 in zip(range(self.e1_slice.start, self.e1_slice.stop), np.floor((self.e_min_y[self.e1_slice]-y0)/w).astype(int), np.floor((self.e_max_y[self.e1_slice]-y0)/w).astype(int)+1):
         for s in bands_y[i1:i2]: s.add(e)        
      self.info.OK()


   def _create_e1_z_bands(self):
      if self.e1_count == 0: return
      if self.bands_z_e1 is not None: return
      self.info.start("Creating bands z of 1D elements (type 1 - lines)")
      w, z0 = self.band_z_width, self.z_0
      self.bands_z_e1 = bands_z = [set() for _ in range(floor(self.z_range/w)+1)]
      for e, i1, i2 in zip(range(self.e1_slice.start, self.e1_slice.stop), np.floor((self.e_min_z[self.e1_slice]-z0)/w).astype(int), np.floor((self.e_max_z[self.e1_slice]-z0)/w).astype(int)+1):
         for s in bands_z[i1:i2]: s.add(e)
      self.info.OK()


   def _create_e2_xy_bands(self):
      if self.e2_count == 0: return
      if self.bands_x_e2 is not None and self.bands_y_e2 is not None: return
      self.info.start("Creating bands xy of 2D elements (type 2 - triangles)")
      w, x0, y0 = self.band_xy_width, self.x_0, self.y_0
      self.bands_x_e2 = bands_x = [set() for _ in range(floor(self.x_range/w)+1)]
      for e, i1, i2 in zip(range(self.e2_slice.start, self.e2_slice.stop), np.floor((self.e_min_x[self.e2_slice]-x0)/w).astype(int), np.floor((self.e_max_x[self.e2_slice]-x0)/w).astype(int)+1):
         for s in bands_x[i1:i2]: s.add(e)
      self.bands_y_e2 = bands_y = [set() for _ in range(floor(self.y_range/w)+1)]
      for e, i1, i2 in zip(range(self.e2_slice.start, self.e2_slice.stop), np.floor((self.e_min_y[self.e2_slice]-y0)/w).astype(int), np.floor((self.e_max_y[self.e2_slice]-y0)/w).astype(int)+1):
         for s in bands_y[i1:i2]: s.add(e)              
      self.info.OK()


   def _create_e2_z_bands(self):
      if self.e2_count == 0: return
      if self.bands_z_e2 is not None: return
      self.info.start("Creating bands z of 2D elements (type 1 - triangles)")
      w, z0 = self.band_z_width, self.z_0
      self.bands_z_e2 = bands_z = [set() for _ in range(floor(self.z_range/w)+1)]
      for e, i1, i2 in zip(range(self.e2_slice.start, self.e2_slice.stop), np.floor((self.e_min_z[self.e2_slice]-z0)/w).astype(int), np.floor((self.e_max_z[self.e2_slice]-z0)/w).astype(int)+1):
         for s in bands_z[i1:i2]: s.add(e)
      self.info.OK()


   def _create_e4_xy_bands(self):
      if self.e4_count == 0: return
      if self.bands_x_e4 is not None and self.bands_y_e4 is not None: return
      self.info.start("Creating bands xy of 3D elements (type 4 - tetrahedrons)")
      w, x0, y0 = self.band_xy_width, self.x_0, self.y_0
      self.bands_x_e4 = bands_x = [set() for _ in range(floor(self.x_range/w)+1)]
      for e, i1, i2 in zip(range(self.e4_slice.start, self.e4_slice.stop), np.floor((self.e_min_x[self.e4_slice]-x0)/w).astype(int), np.floor((self.e_max_x[self.e4_slice]-x0)/w).astype(int)+1):
         for s in bands_x[i1:i2]: s.add(e)
      self.bands_y_e4 = bands_y = [set() for _ in range(floor(self.y_range/w)+1)]
      for e, i1, i2 in zip(range(self.e4_slice.start, self.e4_slice.stop), np.floor((self.e_min_y[self.e4_slice]-y0)/w).astype(int), np.floor((self.e_max_y[self.e4_slice]-y0)/w).astype(int)+1):
         for s in bands_y[i1:i2]: s.add(e)        
      self.info.OK()


   def _create_e4_z_bands(self):
      if self.e4_count == 0: return
      if self.bands_z_e4 is not None: return
      self.info.start("Creating bands z of 3D elements (type 4 - tetrahedrons)")
      w, z0 = self.band_z_width, self.z_0
      self.bands_z_e4 = bands_z = [set() for _ in range(floor(self.z_range/w)+1)]
      for e, i1, i2 in zip(range(self.e4_slice.start, self.e4_slice.stop), np.floor((self.e_min_z[self.e4_slice]-z0)/w).astype(int), np.floor((self.e_max_z[self.e4_slice]-z0)/w).astype(int)+1):
         for s in bands_z[i1:i2]: s.add(e)
      self.info.OK()

      
   def _create_triangle_bands(self):
      if self.bands_x_tria is not None and self.bands_y_tria is not None:
         if np.all(self._actual_e2_to_tria == self.OPTION_e2_to_tria) and np.all(self._actual_e4_to_tria == self.OPTION_e4_to_tria): return
      self._actual_e2_to_tria, self._actual_e4_to_tria = self.OPTION_e2_to_tria, self.OPTION_e4_to_tria
      self.info.start("Creating bands of triangles to calculation of surface elevations")
      for n in self.nodes: n.xi, n.yi = floor((n.x-self.x_0)/self.band_xy_width), floor((n.y-self.y_0)/self.band_xy_width)
      self.set_nodes_elems_4()
      self.bands_x_tria = bands_x = [set() for _ in range(floor(self.x_range/self.band_xy_width)+1)]
      self.bands_y_tria = bands_y = [set() for _ in range(floor(self.y_range/self.band_xy_width)+1)]
      tria_from_e4 = set()
      if len(self._actual_e4_to_tria) > 0:
         n_typ_4 = 0
         e4_planes = (((1,2,3),0), ((0,2,3),1), ((0,1,3),2), ((0,1,2),3))
         e4_i0 = self.e4_slice.start
         for n1, n2, n3, p4, abc in ((e4n[i_123[0]], e4n[i_123[1]], e4n[i_123[2]], e4n[i_4], self.e4_planes_abc[e4-e4_i0][i_4]) for e4 in self._actual_e4_to_tria for i_123, i_4 in e4_planes if len(set((e4n:=self.e_nodes[e4].tolist())[i_123[0]].elems_4.tolist()).intersection(e4n[i_123[1]].elems_4.tolist(), e4n[i_123[2]].elems_4.tolist())) == 1):
            if abc[2] == 0: continue
            if abc[:2] @ (n1.x-p4.x, n1.y-p4.y) / abc[2] + n1.z < p4.z: continue
            t = Triangle(n1, n2, n3, abc)
            tria_from_e4.add(frozenset((n1, n2, n3)))
            for s in bands_x[min(n1.xi,n2.xi,n3.xi):max(n1.xi,n2.xi,n3.xi)+1]: s.add(t)
            for s in bands_y[min(n1.yi,n2.yi,n3.yi):max(n1.yi,n2.yi,n3.yi)+1]: s.add(t)
            n_typ_4 += 1
         self.info("Number of triangles given by 3D elements (type 4 - tetrahedrons): {:d}".format(n_typ_4))
      if len(self._actual_e2_to_tria) > 0:
         n_typ_2 = 0
         e2_i0 = self.e2_slice.start
         for n1, n2, n3, p4, abc in ((*e2n, (set(self.e_nodes[e4_nb.pop()]) - set(e2n)).pop() if len(e4_nb)==1 else None, self.e2_planes_abc[e2-e2_i0]) for e2 in self._actual_e2_to_tria if len(e4_nb:=set((e2n:=self.e_nodes[e2,:3].tolist())[0].elems_4.tolist()).intersection(e2n[1].elems_4.tolist(), e2n[2].elems_4.tolist())) < 2 and frozenset(e2n) not in tria_from_e4):
            if abc[2] == 0: continue
            if p4 is not None:
               if abc[:2] @ (n1.x-p4.x, n1.y-p4.y) / abc[2] + n1.z < p4.z: continue
            t = Triangle(n1, n2, n3, abc)
            for s in bands_x[min(n1.xi,n2.xi,n3.xi):max(n1.xi,n2.xi,n3.xi)+1]: s.add(t)
            for s in bands_y[min(n1.yi,n2.yi,n3.yi):max(n1.yi,n2.yi,n3.yi)+1]: s.add(t)
            n_typ_2 += 1
         self.info("Number of triangles given by 2D elements (type 2 - triangles) without same triangles given by 3D elements: {:d}".format(n_typ_2))
      for n in self.nodes: 
         delattr(n, "xi")
         delattr(n, "yi")            
      self.del_nodes_elems_4()
      self.info.OK()
      


   # ********* surface elevations calculation ************
      
   def init_get_surf_z(self):
      self.info.start("Initializing of params to surface elevations computing")
      self.set_elements_e2_planes()
      self.set_elements_e4_planes()
      self.set_elements_xy_range()
      self._set_params_of_bands_xy_creating()
      self._create_triangle_bands()
      self.try_clear_e_ranges()
      self.info.OK()


   def _set_triangle_lines_params(self, t):
      n1, n2, n3 = t.n1, t.n2, t.n3
      d1 = (a1 := n2.y - n3.y) * n2.x + (b1 := n3.x - n2.x) * n2.y
      if a1 * n1.x + b1 * n1.y < d1: a1, b1, d1 = -a1, -b1, -d1
      d2 = (a2 := n1.y - n3.y) * n1.x + (b2 := n3.x - n1.x) * n1.y
      if a2 * n2.x + b2 * n2.y < d2: a2, b2, d2 = -a2, -b2, -d2
      d3 = (a3 := n1.y - n2.y) * n1.x + (b3 := n2.x - n1.x) * n1.y
      if a3 * n3.x + b3 * n3.y < d3: a3, b3, d3 = -a3, -b3, -d3
      t.a1, t.a2, t.a3, t.b1, t.b2, t.b3, t.d1, t.d2, t.d3 = a1, a2, a3, b1, b2, b3, d1, d2, d3


   def get_surf_z(self, x, y):
      z_surf = -inf
      for t in self._buf_bands_tria[b] if (b:=(floor((x-self.x_0)/self.band_xy_width), floor((y-self.y_0)/self.band_xy_width))) in self._buf_bands_tria else self._buf_bands_tria.setdefault(b, tuple(set.intersection(self.bands_x_tria[b[0]], self.bands_y_tria[b[1]]))):
         if not (t.min_x <= x <= t.max_x and t.min_y <= y <= t.max_y): continue
         if "a1" not in t.__dict__: self._set_triangle_lines_params(t)
         if t.a1*x + t.b1*y < t.d1: continue
         if t.a2*x + t.b2*y < t.d2: continue
         if t.a3*x + t.b3*y < t.d3: continue
         if t.min_z <= (z := (t.abc[0]*(t.n1.x - x) + t.abc[1]*(t.n1.y - y)) / t.abc[2] + t.n1.z) <= t.max_z:
            if z > z_surf: z_surf = z
      return z_surf if z_surf > - inf else None



   # ********** finding elements of points ************

   def get_elems_by_points(self, points):
      self.info.start("Searching elements of {:d} points".format(len(points)))
      self.set_elements_e2_planes()
      self.set_elements_e4_planes()
      self.set_elements_xy_range()
      self.set_elements_z_range()
      self._set_params_of_bands_xy_creating()
      self._set_params_of_bands_z_creating()
      self._create_e1_xy_bands()
      self._create_e1_z_bands()
      self._create_e2_xy_bands()
      self._create_e2_z_bands()
      self._create_e4_xy_bands()
      self._create_e4_z_bands()
      self.try_clear_e_ranges()
      bands = self._buf_bands_e4_points
      for _, p in bands.values(): p.clear()
      x0, y0, z0, b_xy, b_z = self.x_0, self.y_0, self.z_0, self.band_xy_width, self.band_z_width
      for i, p in enumerate(points):
         if p[2] < z0: continue
         elif (b:=(floor((p[0]-x0)/b_xy), floor((p[1]-y0)/b_xy), floor((p[2]-z0)/b_z))) in bands: bands[b][1].append(i)
         else: bands[b] = (np.array(tuple(self.bands_x_e4[b[0]] & self.bands_y_e4[b[1]] & self.bands_z_e4[b[2]]),dtype="int32"), [i])
      abc, nd = self.e4_planes_abc, self.e4_planes_neg_d
      p_e = np.full(len(points), self.No_e, np.int32)
      for elms, pts_i in bands.values():
         e4, pts = elms - self.e4_start_index, points[pts_i].transpose()
         a0 = abc[e4,0] @ pts >= nd[e4,0,None]
         a1 = abc[e4,1] @ pts >= nd[e4,1,None]
         a2 = abc[e4,2] @ pts >= nd[e4,2,None]
         a3 = abc[e4,3] @ pts >= nd[e4,3,None]
         w = np.where(a0 & a1 & a2 & a3)
         for e, p_i in zip(elms[w[0]], (pts_i[i] for i in w[1])):
            p_e[p_i] = e
      self.try_clear_buf_bands()
      self.try_clear_e_planes()
      if (n:=len(np.where(p_e==self.No_e)[0])) > 0:
         self.info.warning("{:d} points are not in elements.".format(n))      
      self.info.OK()
      return p_e





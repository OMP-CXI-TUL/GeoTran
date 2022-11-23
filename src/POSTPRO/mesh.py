import gc
import numpy as np

class Physical:

   def __init__(self, id):
      self.id = id
      self.dim = None
      self.name = None
      self.elements = []


class Node:

   def __init__(self, id, xyz):
      self.id = id
      self.x, self.y, self.z = xyz

          
class Mesh_Err:
   class File_Open_Error(Exception): pass
   class No_Section_Error(Exception): pass
   class Physicals_Load_Error(Exception): pass
   class ElementData_Load_Error(Exception): pass


class Mesh:

   def __init__(self, msh_file, msh_file_physicals_name, info):
      self.info = info
      self._load_mesh(msh_file, msh_file_physicals_name)
      self.e_data = {}
      self.x_0 = self.y_0 = self.z_0 = None
      self.x_max = self.y_max = self.z_max = None
      self.e_min_x = self.e_min_y = self.e_min_z = None
      self.e_max_x = self.e_max_y = self.e_max_z = None
      self.e_T = None
      self.e2_planes_abc = self.e2_planes_d = None
      self.e4_planes_abc = self.e4_planes_neg_d = None
      self.OPTION_keep_e_ranges = False
      self.OPTION_keep_e_planes = True

           
   def get_e_type(self, e):
      if e >= self.e4_start_index: return 4
      elif e >= self.e2_start_index: return 2
      else: return 1


   # ********* mesh loading **************************
        
   def _open_file(self, file_name):
      try:
         f = open(file_name, "r")
      except:
         raise Mesh_Err.File_Open_Error("File '" + file_name + "' opening error")
      return f


   def _goto_section(self, f, section_name, raise_exception=True):
      s0 = section_name[0]
      for s in f:
         if s0 in s:
            if s[1:-1] == section_name[1:]: return True
      if raise_exception: 
         raise Mesh_Err.No_Section_Error("Mesh file: '{:s}'\nSection '{:s}' was not found.".format(f.name, section_name))
      else:
         return False


   def _load_nodes(self):
      self.info.start("Loading nodes from file '{:s}'".format(self.msh_file))
      self._nodes_dict = {}
      with self._open_file(self.msh_file) as f:
         self._goto_section(f, "$Nodes")
         for _ in range(int(f.readline())):
            p = f.readline().split()
            self._nodes_dict[id] = Node(id:=int(p[0]), tuple(map(float,p[1:])))
      self.info.OK("{:d} nodes were loaded.".format(len(self._nodes_dict)))


   def _load_nodes_elems_separation(self):
      self.info.start("Loading nodes with elements separation from file '{:s}'".format(self.msh_file))
      self._nodes_dict = {}
      with self._open_file(self.msh_file) as f:
         self._goto_section(f, "$Nodes")
         xyz_node = {}
         for _ in range(int(f.readline())):
            d, _, xyz = f.readline().strip().partition(" ")
            id = int(d)
            if xyz_node.get(xyz, None) is None:
               xyz_node[xyz] = Node(id, tuple(map(float, xyz.split())))
            self._nodes_dict[id] = xyz_node[xyz]
      self.info.OK("{:d} real nodes were loaded.".format(len(xyz_node)))


   def _load_elements_with_physicals(self):
      self.info.start("Loading elements with physicals from file '{:s}'".format(self.msh_file))
      # ***** load lines with elemennts from mesh file ************
      with self._open_file(self.msh_file) as f:
         self._goto_section(f, "$Elements")
         e_count = int(f.readline())
         lines = [tuple(map(int, f.readline().split())) for _ in range(e_count)]
      # ******** sort lines by elements types *************************
      lines.sort(key=lambda line: line[1])
      # ****** slice by elements type ************************
      self.No_e = 0
      c1 = self.e1_count = sum(1 if p[1]==1 else 0 for p in lines)
      c2 = self.e2_count = sum(1 if p[1]==2 else 0 for p in lines)
      c4 = self.e4_count = len(lines) - c1 - c2
      c_all = self.e_count = 1 + c1 + c2 + c4
      e1_start = self.e1_start_index = 1
      e2_start = self.e2_start_index = 1 + c1
      e4_start = self.e4_start_index = 1 + c1 + c2
      self.e1_slice = slice(e1_start, e2_start)
      self.e2_slice = slice(e2_start, e4_start)
      self.e4_slice = slice(e4_start, c_all)
      # ******** create elements structure ******************
      no_e_id = -1
      self.e_id = np.array([no_e_id] + [p[0] for p in lines], np.int32)
      d = self.e_nodes = np.full((c_all, 4 if c4 > 0 else 3), None)
      d[0,0] = Node(-1, (np.inf, np.inf, np.inf))
      if c1 > 0: d[self.e1_slice,:2] = [[self._nodes_dict[v] for v in p[(3+p[2]):]] for p in lines[:c1]]
      if c2 > 0: d[self.e2_slice,:3] = [[self._nodes_dict[v] for v in p[(3+p[2]):]] for p in lines[c1:c1+c2]]
      if c4 > 0: d[self.e4_slice,:4] = [[self._nodes_dict[v] for v in p[(3+p[2]):]] for p in lines[c1+c2:]]
      # ***** physicals **********************************
      self.physicals = {}
      for e, p in enumerate(lines, 1):
         (self.physicals[p[3]] if p[3] in self.physicals else self.physicals.setdefault(p[3], Physical(p[3]))).elements.append(e)
      for p in self.physicals.values():
         p.elements = np.array(p.elements, np.int32)
      # ***** node dict to node list *************************
      self.nodes = list(self._nodes_dict.values())
      del (self._nodes_dict)               
      # ***********************************************
      self.info("Number of elements by type (1, 2, 4): {:d},  {:d},  {:d}".format(c1, c2, c4))
      self.info.OK("{:d} elements in {:d} physicals were loaded.".format(len(self.e_id), len(self.physicals)))
     

   def _set_physicals_name(self):
      self.info.start("Setting physical names")
      if self.msh_file_physicals_name is None:
         self.info("Setting dimensions only without $PhysicalNames")
         for phs in self.physicals.values():
            e = next(e for e in phs.elements)
            if e < self.e2_start_index: phs.dim = 1
            elif e < self.e4_start_index: phs.dim = 2
            else: phs.dim = 3
            phs.name = "{:d}D_{:d}".format(phs.dim, phs.id)
      else:
         with self._open_file(self.msh_file_physicals_name) as f:
            self.info("Loading physicals names from file '{:s}'".format(f.name))
            self._goto_section(f, "$PhysicalNames", raise_exception=True)
            for _ in range(int(f.readline())):
               p = f.readline().replace('"','').split()
               phs = self.physicals.get(int(p[1]), None)
               if phs is not None:
                  phs.dim, phs.name = int(p[0]), " ".join(p[2:])
            for phs in self.physicals.values():
               if phs.name is None:
                  raise Mesh_Err.Physicals_Load_Error("Mesh file: '{:s}'\nPhysical with id {:d} has no item in $PhysicalNames section.".format(phs.id, self.f.name))
      self.physicals = {p.name:p for p in self.physicals.values()}
      self.info.OK()


   def _group_node_duplicites(self):
      self.nodes = list(set(self.nodes))
      

   def _test_physical_elems_type(self):
      self.info.start("Testing element types in physicals")
      dim_etyp = {1: 1, 2: 2, 3: 4}
      for phs in self.physicals.values():
         u = [(self.e_id, typ) for e in phs.elements if (typ:=self.get_e_type(e)) != dim_etyp[phs.dim]]
         if len(u) > 0:
            raise Mesh_Err.Physicals_Load_Error("Mesh file: '{:s}'\nElement {:d} of type {:d} canot be contain in physical {:d} of dimension {:d}.".format(self.f.name, u[0][0], u[0][1], phs.id, dim))
      self.info.OK()


   def _load_normal_mesh(self):
      self.info.start("Loading Mesh")
      self._load_nodes()
      self._load_elements_with_physicals()
      self._set_physicals_name()
      self._test_physical_elems_type()
      self.info.OK()
     

   def _load_mesh_with_elems_separation(self):
      self.info.start("Loading Mesh with separated elements")
      self._load_nodes_elems_separation()
      self._load_elements_with_physicals()
      self._group_node_duplicites()
      self._set_physicals_name()
      self._test_physical_elems_type()
      self.info.OK()


   def _load_mesh(self, msh_file, msh_file_physicals_name):
      self.msh_file, self.msh_file_physicals_name = msh_file, msh_file_physicals_name
      with self._open_file(msh_file) as f:
         self._goto_section(f, "$Nodes")
         nodes_count = int(f.readline())
         self._goto_section(f, "$Elements")
         elems_count = int(f.readline())
      if nodes_count < elems_count: self._load_normal_mesh()
      else: self._load_mesh_with_elems_separation()


   # ************* nodes elements ***************

   def set_nodes_elems_4(self):
      self.info.start("Setting elements type 4 (tetrahedrons) of nodes")
      list_0 = []
      for n in self.nodes: n.elems_4 = list_0
      for e4, n in enumerate(self.e_nodes[self.e4_slice], self.e4_start_index):
         if not len(n[0].elems_4): n[0].elems_4 = [e4]
         else: n[0].elems_4.append(e4)
         if not len(n[1].elems_4): n[1].elems_4 = [e4]
         else: n[1].elems_4.append(e4)
         if not len(n[2].elems_4): n[2].elems_4 = [e4]
         else: n[2].elems_4.append(e4)
         if not len(n[3].elems_4): n[3].elems_4 = [e4]
         else: n[3].elems_4.append(e4)
      for n in self.nodes:
         n.elems_4 = np.fromiter(n.elems_4, np.int32)
      self.info.OK()

   def del_nodes_elems_4(self):
      for n in self.nodes: delattr(n,"elems_4")

   def set_nodes_elems(self):
      self.info.start("Setting elements of nodes")
      for n in self.nodes: n.elems = []
      for e, n in enumerate(self.e_nodes[self.e1_slice],self.e1_start_index):
         n[0].elems.append(e)
         n[1].elems.append(e)
      for e, n in enumerate(self.e_nodes[self.e2_slice],self.e2_start_index):
         n[0].elems.append(e)
         n[1].elems.append(e)
         n[2].elems.append(e)
      for e, n in enumerate(self.e_nodes[self.e4_slice],self.e4_start_index):
         n[0].elems.append(e)
         n[1].elems.append(e)
         n[2].elems.append(e)
         n[3].elems.append(e)
      for n in self.nodes:
         n.elems = np.fromiter(n.elems, np.int32)
      self.info.OK()

   def del_nodes_elems(self):
      for n in self.nodes: delattr(n,"elems")


   # **** Elements geometric params *********

   def set_general_mesh_params(self):
      if self.x_0 is not None and self.y_0 is not None and self.z_0 is not None and self.x_max is not None and self.y_max is not None and self.z_max is not None: return
      self.info.start("Setting general mesh params")
      a = np.array([(n.x, n.y, n.z) for n in self.nodes])
      self.x_0, self.y_0, self.z_0 = np.min(a, axis=0)
      self.x_max, self.y_max, self.z_max = np.max(a, axis=0)
      self.x_range, self.y_range, self.z_range = self.x_max - self.x_0, self.y_max - self.y_0, self.z_max - self.z_0
      self.info("X axis (minimum, maximum, range): {:g}\t{:g}\t{:g}".format(self.x_0, self.x_max, self.x_range))
      self.info("Y axis (minimum, maximum, range): {:g}\t{:g}\t{:g}".format(self.y_0, self.y_max, self.y_range))
      self.info("Z axis (minimum, maximum, range): {:g}\t{:g}\t{:g}".format(self.z_0, self.z_max, self.z_range))
      self.info.OK()

   
   def set_elements_xy_range(self):
      if self.e_min_x is not None and self.e_max_x is not None and self.e_min_y is not None and self.e_max_y is not None: return
      self.info.start("Calculating elements x, y range")
      self.e_min_x = x1 = np.empty(self.e_count)
      self.e_max_x = x2 = np.empty(self.e_count)
      self.e_min_y = y1 = np.empty(self.e_count)
      self.e_max_y = y2 = np.empty(self.e_count)
      if self.e1_count > 0: 
         s = self.e1_slice
         x1[s] = np.fromiter((min(n[0].x, n[1].x) for n in self.e_nodes[s]), np.float64)
         x2[s] = np.fromiter((max(n[0].x, n[1].x) for n in self.e_nodes[s]), np.float64)
         y1[s] = np.fromiter((min(n[0].y, n[1].y) for n in self.e_nodes[s]), np.float64)
         y2[s] = np.fromiter((max(n[0].y, n[1].y) for n in self.e_nodes[s]), np.float64)
      if self.e2_count > 0: 
         s = self.e2_slice
         x1[s] = np.fromiter((min(n[0].x, n[1].x, n[2].x) for n in self.e_nodes[s]), np.float64)
         x2[s] = np.fromiter((max(n[0].x, n[1].x, n[2].x) for n in self.e_nodes[s]), np.float64)
         y1[s] = np.fromiter((min(n[0].y, n[1].y, n[2].y) for n in self.e_nodes[s]), np.float64)
         y2[s] = np.fromiter((max(n[0].y, n[1].y, n[2].y) for n in self.e_nodes[s]), np.float64)
      if self.e4_count > 0: 
         s = self.e4_slice
         x1[s] = np.fromiter((min(n[0].x, n[1].x, n[2].x, n[3].x) for n in self.e_nodes[s]), np.float64)
         x2[s] = np.fromiter((max(n[0].x, n[1].x, n[2].x, n[3].x) for n in self.e_nodes[s]), np.float64)
         y1[s] = np.fromiter((min(n[0].y, n[1].y, n[2].y, n[3].y) for n in self.e_nodes[s]), np.float64)
         y2[s] = np.fromiter((max(n[0].y, n[1].y, n[2].y, n[3].y) for n in self.e_nodes[s]), np.float64)
      self.info.OK()
  

   def set_elements_z_range(self):
      if self.e_min_z is not None and self.e_max_z is not None: return
      self.info.start("Calculating elements z range")
      self.e_min_z = z1 = np.empty(self.e_count)
      self.e_max_z = z2 = np.empty(self.e_count)
      if self.e1_count > 0: 
         s = self.e1_slice
         z1[s] = np.fromiter((min(n[0].z, n[1].z) for n in self.e_nodes[s]), np.float64)
         z2[s] = np.fromiter((max(n[0].z, n[1].z) for n in self.e_nodes[s]), np.float64)
      if self.e2_count > 0: 
         s = self.e2_slice
         z1[s] = np.fromiter((min(n[0].z, n[1].z, n[2].z) for n in self.e_nodes[s]), np.float64)
         z2[s] = np.fromiter((max(n[0].z, n[1].z, n[2].z) for n in self.e_nodes[s]), np.float64)
      if self.e4_count > 0: 
         s = self.e4_slice
         z1[s] = np.fromiter((min(n[0].z, n[1].z, n[2].z, n[3].z) for n in self.e_nodes[s]), np.float64)
         z2[s] = np.fromiter((max(n[0].z, n[1].z, n[2].z, n[3].z) for n in self.e_nodes[s]), np.float64)
      self.info.OK()
   

   def clear_e_ranges(self):
      self.e_min_x = self.e_max_x = None
      self.e_min_y = self.e_max_y = None
      self.e_min_z = self.e_max_z = None
      gc.collect()
      
   def try_clear_e_ranges(self):
      if not self.OPTION_keep_e_ranges: self.clear_e_ranges()


   def set_elements_T(self):
      if self.e_T is not None: return
      self.info.start("Calculating centers of elements")
      self.e_T = np.empty((self.e_count, 3), np.float64)
      self.e_T[0] = np.inf, np.inf, np.inf
      if self.e1_count > 0: self.e_T[self.e1_slice] = np.average([[(n[0].x, n[0].y, n[0].z), (n[1].x, n[1].y, n[1].z)] for n in self.e_nodes[self.e1_slice]], axis = 1)
      if self.e2_count > 0: self.e_T[self.e2_slice] = np.average([[(n[0].x, n[0].y, n[0].z), (n[1].x, n[1].y, n[1].z), (n[2].x, n[2].y, n[2].z)] for n in self.e_nodes[self.e2_slice]], axis = 1)
      if self.e4_count > 0: self.e_T[self.e4_slice] = np.average([[(n[0].x, n[0].y, n[0].z), (n[1].x, n[1].y, n[1].z), (n[2].x, n[2].y, n[2].z), (n[3].x, n[3].y, n[3].z)] for n in self.e_nodes[self.e4_slice]], axis = 1)
      self.info.OK()


   def set_elements_e2_planes(self):
      if self.e2_planes_abc is not None and self.e2_planes_d is not None: return
      self.info.start("Calculating planes params for 2D elemennts (type 2 - triangles)")
      p = np.array([[(n[0].x, n[0].y, n[0].z), (n[1].x, n[1].y, n[1].z), (n[2].x, n[2].y, n[2].z)] for n in self.e_nodes[self.e2_slice]])
      abc = self.e2_planes_abc = np.cross(p[:,1]-p[:,0], p[:,2]-p[:,0])
      self.e2_planes_d = - np.sum(abc * p[:,0], axis=1)
      self.info.OK()


   def set_elements_e4_planes(self):
      if self.e4_planes_abc is not None and self.e4_planes_neg_d is not None: return
      self.info.start("Calculating planes params for 3D elemennts (type 4 - tetrahedrons)")
      p = np.array([((n[0].x, n[0].y, n[0].z), (n[1].x, n[1].y, n[1].z), (n[2].x, n[2].y, n[2].z), (n[3].x, n[3].y, n[3].z)) for n in self.e_nodes[self.e4_slice]])
      abc = self.e4_planes_abc = np.empty((self.e4_count, 4, 3), np.float64)
      abc[:,0] = np.cross(p[:,2]-p[:,1], p[:,3]-p[:,1])
      abc[:,1] = np.cross(p[:,2]-p[:,0], p[:,3]-p[:,0])
      abc[:,2] = np.cross(p[:,1]-p[:,0], p[:,3]-p[:,0])
      abc[:,3] = np.cross(p[:,1]-p[:,0], p[:,2]-p[:,0])
      d = np.empty((self.e4_count, 4), np.float64)
      d[:,0] = - np.sum(abc[:,0] * p[:,1], axis=1)
      d[:,1] = - np.sum(abc[:,1] * p[:,0], axis=1)
      d[:,2] = - np.sum(abc[:,2] * p[:,0], axis=1)
      d[:,3] = - np.sum(abc[:,3] * p[:,0], axis=1)
      b = np.sum(abc * p, axis=2) < - d
      abc[b] *= -1; d[b] *= -1
      self.e4_planes_neg_d = - d
      self.info.OK()


   def clear_e_planes(self):
      self.e2_planes_abc = self.e2_planes_d = None
      self.e4_planes_abc = self.e4_planes_neg_d = None
      gc.collect()
      
   def try_clear_e_planes(self):
      if not self.OPTION_keep_e_planes: self.clear_e_planes()


   # *********** Element Data loading **********************

   def load_names_times_of_element_data(self, file_name, time_conversion_coef):
      if file_name is None: file_name = self.msh_file
      self.info.start("Getting $ElementData name and times from file '{:s}'".format(file_name))            
      names, times = [], []
      with self._open_file(file_name) as f:
         ed_raise = True
         while self._goto_section(f, "$ElementData", raise_exception=ed_raise):
            ed_raise = False
            f_names = [f.readline().strip()[1:-1] for _ in range(int(f.readline()))]
            if int(f.readline()) != 1:
               raise Mesh_Err.ElementData_Load_Error("Mesh file: '{:s}'\nHead of $ElementData must have just one float (time) value.".format(self.f.name))
            f_time = s.rstrip("0").rstrip(".") if "." in (s:="{:.3f}".format(float(f.readline()) * time_conversion_coef)) else s
            if int(f.readline()) != 3:
               raise self.ElementData_Load_Error("Mesh file: '{:s}'\nHead of $ElementData must have just 3 integer values.".format(self.f.name))
            f.readline()
            f.readline()
            f.readline()
            for n in f_names:
               if n not in names: names.append(n)
            if f_time not in times: times.append(f_time)
      self.info.OK()
      return names, times


   def try_load_element_data(self, file_name, names, times, time_conversion_coef):
      if file_name is None: file_name = self.msh_file
      self.info.start("Loading $ElementData from file '{:s}'".format(file_name))            
      id_e = {id:e for e, id in enumerate(self.e_id)}
      with self._open_file(file_name) as f:
         ed_raise, loaded, loaded_count = True, set(), 0
         while self._goto_section(f, "$ElementData", raise_exception=ed_raise):
            ed_raise = False
            if names is None: f_names = [f.readline().strip()[1:-1] for _ in range(int(f.readline()))]
            else: f_names = [s for _ in range(int(f.readline())) if (s:=f.readline().strip()[1:-1]) in names]
            if (f_names_count := len(f_names)) == 0: continue         
            if int(f.readline()) != 1:
               raise Mesh_Err.ElementData_Load_Error("Mesh file: '{:s}'\nHead of $ElementData must have just one float (time) value.".format(self.f.name))
            f_time = s.rstrip("0").rstrip(".") if "." in (s:="{:.3f}".format(float(f.readline()) * time_conversion_coef)) else s
            if times is not None:
               if f_time not in times: continue
            if int(f.readline()) != 3:
               raise self.ElementData_Load_Error("Mesh file: '{:s}'\nHead of $ElementData must have just 3 integer values.".format(self.f.name))
            f.readline()
            f.readline()
            f_values_count = int(f.readline())
            if f_names_count == 1:
               lines = [int(p[0]) if (p:=f.readline().strip().partition(" "))[2] == "0" else (int(p[0]), float(p[2])) for _ in range(f_values_count)]
               self.e_data[(nt:=(f_names[0],f_time))] = d = np.full(self.e_count, np.nan, np.float64)
               d[0] = 0
               for p in lines: 
                  if type(p) == int: d[id_e[p]] = 0.
                  else: d[id_e[p[0]]] = p[1]
               loaded.add(nt); loaded_count += 1
               self.info("{:d}. name: {:s}, time: {:s} was loaded.".format(loaded_count, *nt))
            else:
               s0 = " ".join(f_names_count * ["0"])
               lines = [int(p[0]) if (p:=f.readline().strip().partition(" "))[2] == s0 else (int(p[0]), *p[2].split()) for _ in range(f_values_count)]
               for i, f_name in enumerate(f_names, 1):
                  self.e_data[(nt:=(f_name,f_time))] = d = np.full(self.e_count, np.nan, np.float64)
                  d[0] = 0
                  for p in lines:
                     if type(p) == int: d[id_e[p]] = 0.
                     else: d[id_e[p[0]]] = float(p[i])
                  loaded.add(nt); loaded_count += 1
                  self.info("{:d}. name: {:s}, time: {:s} was loaded.".format(loaded_count, *nt))        
      self.info.OK()
      return loaded
      

   def delete_loaded_element_data(self):
      self.info.start("Deleting loaded element data")
      for nt in self.e_data: self.e_data[nt] = None
      self.e_data.clear()
      gc.collect()
      self.info.OK()

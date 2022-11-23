import gc
import numpy as np

from mesh_band_model import MeshBandModel


class GridDeep:
   def __init__(self, deep, name):
      self.deep, self.name = deep, name
      self.pos_IDW_e = self.pos_IDW_weights = None

class GridLevel:
   def __init__(self, z, name):
      self.z, self.name = z, name
      self.pos_IDW_e = self.pos_IDW_weights = None

class EsetDeepRange:
   def __init__(self, deep1, deep2, name):
      self.deep1, self.deep2, self.name = deep1, deep2, name

class EsetLevelRange:
   def __init__(self, z1, z2, name):
      self.z1, self.z2, self.name = z1, z2, name

class EsetPhysicalGroup:
   def __init__(self, physicals, name):
      self.physicals, self.name = physicals, name

class GEmodel_Err:
   class Grid_create_error(Exception): pass
   class Eset_create_error(Exception): pass


class MeshGridEsetModel(MeshBandModel):

   def __init__(self, msh_file, msh_file_physicals_name, info):      
      super().__init__(msh_file, msh_file_physicals_name, info)
      self.e_deep = None
      self.grids = {}
      self.esets = {}
      self.is_grid_positions = False
      self.OPTION_IDW_factor = 7
      self.OPTION_keep_IDW_weights = False


   # ******* private for grid positions ************************

   def _grid_pos_x(self):
      return np.fromiter((self.grid_x[xi] for xi in self.grid_pos_xi), np.float64)

   def _grid_pos_y(self):
      return np.fromiter((self.grid_y[yi] for yi in self.grid_pos_yi), np.float64)

   def _add_used_e_neighbors(self, elems):            
      self.info.start("Searching neighbours elements for IDW interpolations")
      search_elems = set(elems.tolist()) & {e for e, nbs in enumerate(self.used_e_neighbors) if nbs is None}
      e_nodes_sets = list(map(lambda s: set(s)-{None}, self.e_nodes))
      self.set_nodes_elems()
      c = self.idw_weight_count
      for e, nodes_set in zip(search_elems, (e_nodes_sets[s] for s in search_elems)):
         self.used_e_neighbors[e] = np.array((w := [e] + [p[1] for p in sorted(((len(nodes_set & e_nodes_sets[nb]), nb) for nb in set(self.e_nodes[e,0].elems.tolist()).union(*[n.elems.tolist() for n in self.e_nodes[e,1:] if n is not None]) - {e}), reverse=True)][:c-1]) + (c-len(w))*[0], np.int32)
      self.del_nodes_elems()
      self.info.OK()


   # ************ grid positions ******************

   def create_grid_positions(self, step, idw_weight_count, x_0=None, y_0=None, x_max=None, y_max=None):
      self.info.start("Creating grid positions with surface elevations")
      if x_0 is None: x_0 = self.x_0
      if y_0 is None: y_0 = self.y_0
      if x_max is None: x_max = self.x_max
      if y_max is None: y_max = self.y_max
      self.grid_x = np.arange(x_0 + step/2, x_max, step)
      self.grid_y = np.arange(y_0 + step/2, y_max, step)
      self.init_get_surf_z()
      pos = [(x_i, y_i, z_surf) for x_i, x in enumerate(self.grid_x) for y_i, y in enumerate(self.grid_y) if (z_surf:=self.get_surf_z(x,y)) is not None]
      self.try_clear_buf_bands()
      self.try_clear_bands_tria()
      self.grid_pos_xi = np.fromiter((p[0] for p in pos), np.int32)
      self.grid_pos_yi = np.fromiter((p[1] for p in pos), np.int32)
      self.grid_pos_surf_z = np.fromiter((p[2] for p in pos), np.float64)    
      self.grid_pos_count = len(self.grid_pos_xi)
      self.info("Number of grid positions to search: {:d}".format(len(self.grid_x)*len(self.grid_y)))
      self.info("Number of recently created grid positions with found surface elevations: {:d}".format(self.grid_pos_count))
      self.info("Minimum surface elevation: {:g}".format(self.grid_pos_surf_z.min()))
      self.info("Number of positions along x axis: {:g}".format(len(self.grid_x)))
      self.info("Number of positions along y axis: {:g}".format(len(self.grid_y)))
      self.info("Maximum surface elevation: {:g}".format(self.grid_pos_surf_z.max()))
      # ***** reset grid params ************
      self.grid_step = step
      self.grid_A_sqr = step**2
      self.grid_A_model = step**2 * self.grid_pos_count
      self.idw_weight_count = idw_weight_count
      self.used_e_neighbors = self.e_count * [None]
      self.used_e_neighbors[0] = np.zeros(idw_weight_count, np.int32)
      if len(self.grids) > 0:
         self.info.start("RE-create grids")
         gds = list(self.grids.values())
         self.grids.clear()
         for g in gds:
            if type(g) == GridDeep: self.add_grid_deep(g.deep, name=g.name)
            else: self.add_grid_level(g.z, name=g.name)
         self.info.OK()
      self.is_grid_positions = True
      self.info.OK()


   def change_grid_IDW_weight_count(self, c):
      for g in self.grids.values(): g.pos_IDW_e = g.pos_IDW_weights = None
      self.idw_weight_count = c
      self.used_e_neighbors[0] = np.zeros(c, np.int32)
      a = np.fromiter((e for e, nbs in enumerate(self.used_e_neighbors[1:], 1) if nbs is not None), np.int32)
      self._add_used_e_neighbors(a)


   # ******* grid layers manimpulation ****************************

   def add_grid_deep(self, deep, name=None):
      if name is None: name = "Grid deep {:g}m".format(deep)
      self.info.start("Creating grid deep with name '{:s}'".format(name))
      if name in self.grids: raise GEmodel_Err.Grid_create_error("Grid with name '{:s}' alredy exists.".format(name))
      self.grids[name] = gd = GridDeep(deep, name)
      gd.pos_e = self.get_elems_by_points(np.array([self._grid_pos_x(), self._grid_pos_y(), self.grid_pos_surf_z - deep]).transpose())
      self._add_used_e_neighbors(gd.pos_e)
      self.info.OK()
      return name


   def add_grid_level(self, z, name=None):
      if name is None: name = "Grid level {:g}m".format(z)
      self.info.start("Creating grid level with name '{:s}'".format(name))
      if name in self.grids: raise GEmodel_Err.Grid_create_error("Grid with name '{:s}' alredy exists.".format(name))
      self.grids[name] = gl = GridLevel(z, name)
      gl.pos_e = self.get_elems_by_points(np.array([self._grid_pos_x(), self._grid_pos_y(), np.full(self.grid_pos_count, z, np.float64)]).transpose())
      self._add_used_e_neighbors (gl.pos_e)
      self.info.OK()
      return name


   def del_grid(self, name):
      self.info.start("Deleting grid with name {:s}".format(name))
      self.grids.pop(name)
      self.info.OK()


   def get_grid_pos_z(self, grid_name, pos_i):
      return (self.grid_pos_surf_z[pos_i] - g.deep) if type(g:=self.grids[grid_name]) == GridDeep else g.z


   # **************** grid values *****************

   def set_grid_IDW_e_weights(self, grid): 
      self.info.start("Computing IDW weights for grid '" + grid.name + "'")
      grid.pos_IDW_e = np.array([self.used_e_neighbors[e] for e in grid.pos_e], np.int32)
      w = np.empty((self.grid_pos_count, self.idw_weight_count), np.float64)
      p = np.array([self._grid_pos_x(), self._grid_pos_y(), (self.grid_pos_surf_z - grid.deep) if type(grid) == GridDeep else np.full(self.grid_pos_count, grid.z, np.float64)]).transpose()
      for w_i in range(self.idw_weight_count):
         w[:,w_i] = (np.sum((p - self.e_T[grid.pos_IDW_e[:,w_i]])**2, axis=1)**0.5)**-self.OPTION_IDW_factor
      with np.errstate(divide="ignore", invalid="ignore"):
         grid.pos_IDW_weights = w / w.sum(axis=1)[:,None]
      self.info.OK()
   
   def get_grid_IDW_data(self, grid_name, name, time):
      grid = self.grids[grid_name]
      if grid.pos_IDW_e is None or grid.pos_IDW_weights is None:
         self.set_grid_IDW_e_weights(grid)
      data = np.sum(self.e_data[(name,time)][grid.pos_IDW_e] * grid.pos_IDW_weights, axis=1)
      return data

   def try_clear_grids_IDW_e_weights(self, grids_name=None):
      if not self.OPTION_keep_IDW_weights:
         if grids_name is None:
            for g in self.grids.values():
               g.pos_IDW_e = g.pos_IDW_weights = None
         else:
            for g in (self.grids[n] for n in grids_name):
               g.pos_IDW_e = g.pos_IDW_weights = None
         gc.collect()


   # ************ elems set **************************

   def set_elements_deep(self):
      if self.e_deep is not None: return
      self.info.start("Calculating deep of elements")
      self.init_get_surf_z()
      self.e_deep = np.array([- np.inf if (z:=self.get_surf_z(*p)) is None else z for p in self.e_T[1:,:2]]) - self.e_T[1:,2]
      self.try_clear_buf_bands()
      self.try_clear_bands_tria()
      if (n:=len(np.where(self.e_deep == - np.inf)[0])) > 0:
         s = "{:d} elemennts without deep".format(n)
         self.info.warning(s)
      self.info.OK()
  

   def add_eset_deep_range(self, deep1, deep2, name=None):
      if name is None: name = "Elements of deeps from {:g}m to {:g}m".format(deep1, deep2)
      self.info.start("Creating elements set with name '{:s}'".format(name))
      if name in self.esets: raise GEmodel_Err.Eset_create_error("Elements set with name '{:s}' alredy exists.".format(name))
      self.set_elements_deep()
      self.esets[name] = ed = EsetDeepRange(deep1, deep2, name)
      ed.elms = np.where((self.e_deep >= deep1) & (self.e_deep <= deep2))[0]
      self.info.OK("{:d} elements found.".format(len(ed.elms)))
      return name


   def add_eset_level_range(self, z1, z2, name=None):
      if name is None: name = "Elements of levels from {:g}m to {:g}m".format(z1, z2)
      self.info.start("Creating elements set with name '{:s}'".format(name))
      if name in self.esets: raise GEmodel_Err.Eset_create_error("Elements set with name '{:s}' alredy exists.".format(name))
      self.esets[name] = el = EsetLevelRange(z1, z2, name)
      el.elms = np.where((self.e_T[:,2] >= z1) & (self.e_T[:,2] <= z2))[0]
      self.info.OK("{:d} elements found.".format(len(el.elms)))
      return name


   def add_eset_physicals_group(self, physicals_name, name=None):
      if name is None: name = "Elements of physicals: " + " ".join(physicals_name)
      self.info.start("Creating elements set of physicals group with name '{:s}'".format(name))
      if name in self.esets: raise GEmodel_Err.Eset_create_error("Elements set with name '{:s}' alredy exists.".format(name))
      self.esets[name] = ep = EsetPhysicalGroup(physicals_name, name)
      ep.elms = np.fromiter((e for n in physicals_name for e in self.physicals[n].elements), np.int32)
      self.info.OK("{:d} elements found.".format(len(ep.elms)))
      return name

   def del_eset(self, name):
      self.info.start("Deleting elements set with name {:s}".format(name))
      self.esets.pop(name)
      self.info.OK()


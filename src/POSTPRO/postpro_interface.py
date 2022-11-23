import sys

from balance import Balance
from mesh_phases import MeshPhases
from info import Info
from postpro_params import PostProParams


class PostProInterface:

   def __init__(self, time_main_unit, info_out_stream=None):
      self.info = Info(None, "PostPro", outfile=(sys.stdout if info_out_stream is None else info_out_stream  ))
      self.params = PostProParams(time_main_unit)
      self.balance = None
      self.mesh_phases = None


   def load_balance(self, file_names):
      self.balance = Balance(self.info, self.params)
      self.balance.load_data(file_names)
      

   def load_mesh_phases(self, file_names, mesh_file_physicals_name):
      self.mesh_phases = p = MeshPhases(self.info, self.params)
      p._create_phases(file_names, mesh_file_physicals_name)


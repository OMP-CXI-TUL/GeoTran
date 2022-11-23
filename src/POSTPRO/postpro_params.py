

class PostProParams:

   def __init__(self, time_main_unit):
      self.time_main_unit = time_main_unit
      self.time_source_unit = time_main_unit
      self.time_coef = 1
      self.out_column_separator = ";"
      self.out_decimal_comma = False
      self.postpro_dir = "./"


   def set_time_source_unit(self, unit):
      c = {("s","s"):1, 
           ("y","s"):1/3600/24/365.25,
           ("1000.y","s"): 1/3600/24/365.25/1000}
      self.time_source_unit = unit
      self.time_coef = c[(self.time_main_unit, self.time_source_unit)]


   def set_out_column_separator(self, col_sep):
      self.out_column_separator = col_sep


   def set_out_decimal_comma(self, dec_comma):
      self.out_decimal_comma = dec_comma


   def set_postpro_dir(self, dir):
      self.postpro_dir = dir

      
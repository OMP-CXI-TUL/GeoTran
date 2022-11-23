import gc

from postpro_interface import PostProInterface

from mesh_grid_eset_computing import MeshGridEsetComputing

cesta = "D:/big_data/"
mesh_dunaj = [cesta+"data_dunaj/dunaj_hrad_sc1b_000_reach_2022_tul2.msh", cesta+"data_dunaj/dunaj_hrad_sc1b_005_reach_2022_tul2.msh"]
data_dunaj = [cesta+"data_dunaj/dunaj_hrad_scB1_000_mass_transport.msh",  cesta+"data_dunaj/dunaj_hrad_scB1_005_mass_transport.msh"]
mesh_LC = cesta+"data_LC_A5/labe_cert_sc1b_000_reach.msh"
data_LC_A5 = [cesta+"data_LC_A5/A5_out_"+t+"/mass_transport.msh" for t in ["000","025","050","075","100","125","150","175"]]
data_LC_C1 = [cesta+"data_LC_C1/11_C1_out_"+t+"/labe_cert_c1_"+t+"_mass_transport.msh" for t in (str(t).zfill(3) for t in range(0,200,5))]


mass_balance_LC_A5 = [cesta+"data_LC_A5/A5_out_"+t+"/mass_balance_dg.txt" for t in ["000","025","050","075","100","125","150","175"]]


def test_balance():
   ps = PostProInterface("1000.y")
   ps.params.set_time_source_unit("s")
   ps.load_balance(mass_balance_LC_A5)
   ps.balance.report_csv([[None,"flux",("geo_10_layer5",),("I129",)]], None, None, None, None, True, "mass.csv")


def test_load_data():
   ps = PostProInterface("1000.y")
   ps.params.set_time_source_unit("s")
   ps.load_mesh_phases(data_LC_A5, 8*[mesh_LC])
   mp = ps.mesh_phases
   n, t = mp.load_names_times_of_element_data(None)
   print(n)
   print(t)
#   mp.load_element_data(data_LC_C1, None, None)
#   _, lines = mp.get_e_data_names_times_loaded()
#   for s in lines: print(s)


def test_report_eset_table():
   ps = PostProInterface("1000.y")
   ps.params.set_time_source_unit("s")
   ps.load_mesh_phases(data_LC_A5, None)
   mp = ps.mesh_phases
   mp.load_element_data(data_LC_A5, None, [0,1,2])
   mp.add_eset_level_range(50, 100, None)
   mp.report_eset_quantiles(None, None, None, "first", ",", False, [0.1, 0.5, 0.9], "result.csv")


def test_report_grid_table():
   ps = PostProInterface("1000.y")
   ps.params.set_time_source_unit("s")
   ps.load_mesh_phases(data_LC_A5, None)   
   mp = ps.mesh_phases
   mp.load_element_data(data_LC_A5, None, None)
   mp.create_grid_positions(10, 6, None)
   mp.add_grid_deep(300)
   mp.report_grid_quantiles(None, None, None, "first", ";", False, "result.csv", [0.5, 0.95, 0.99])


def test_report_grid_images():
   ps = PostProInterface("1000.y")
   ps.params.set_time_source_unit("s")
   ps.load_mesh_phases(data_LC_A5, None)   
   mp = ps.mesh_phases
   mp.load_element_data(None, None, None)
   mp.create_grid_positions(10, 6, None)
   mp.add_grid_deep(500, None)
   mp.report_grid_images(None, None, None, [30,30,30], None, [0, 1, 30], "./output", "", "png")
   # mp.report_grid_asc(None, None, None, -9999, "./output", "")


def test_single_mesh():
   pass



test_report_eset_table()

gc.collect()
input("press ENTER to exit")



import os, sys

import tkinter as tk
from tkinter import messagebox

from pp_dialog_balance_files_selection import BalanceFileSelectionDialog
from pp_dialog_balance_outs_config import BalanceOutputConfigurationDialog
from pp_dialog_times_config import TimeConfigurationDialog
from pp_dialog_mesh_files_selection import MeshFileSelectionDialog
from pp_dialog_data_loading import DataLoadingDialog
from pp_dialog_grid_configuration import GridConfigurationDialog
from pp_dialog_grid_new_depth_level import NewDepthLevelGridDialog
from pp_dialog_grid_list import GridListDialog
from pp_dialog_eset_new_depth_level import NewDepthLevelEsetDialog
from pp_dialog_eset_new_regions import NewRegionsEsetDialog
from pp_dialog_eset_list import EsetListDialog
from pp_dialog_eset_reports import ReportEsetMaxValueDialog, ReportEsetMaxValuesDifferenceDialog, ReportEsetQuantilesDialog
from pp_dialog_grid_reports import ReportGridMaxValueDialog, ReportGridMaxValuesDifferenceDialog, ReportGridQuantilesDialog, ReportGridAreaOverLimitsDialog, ReportGridImagesDialog, ReportGridASCDialog, ReportGridDifferenceASCDialog, ReportGridASCasPctDialog, ReportGridDifferenceASCasPctDialog
from pp_dialog_container_c import ContainerCDialog
from pp_dialog_options import BalanceOptionsDialog, TransportOptionsDialog


textFiletypes = [('Text files', '*.txt'),('All files', '*')]
meshFiletypes = [('Mesh files', '*.msh'),('Mesh version 2 files', '*.msh2'),('All files', '*')]
rasterFiletypes = [('ASC raster', '*.asc'),('All files', '*')]
protocolFiletypes = [('Geotran protocol files', '*.gtp'),('Text files', '*.txt'), ('Log files', '*.log'),  ('All files', '*')]
balanceFiletypes = [('Text file', '*.txt'),('All files', '*')]
resultFiletypes = [('Mesh files', '*.msh'),('All files', '*')]

canceledInfo = 'The action was canceled by the user'

class GeotranMainmenuHandler():
    baseActionsHandlers = None
    menuStructureData = None

    def __init__(self, gtapp, parentWin, bas):
        self.postpro_balance = None
        self.postpro_meshphases = None
        self.last_grid_inputs = []
        self.gtapp = gtapp

        self.initialdir = os.path.abspath(os.curdir)
        self.protocolFiledir = self.initialdir
        self.protocolFilename = ''
        self.balanceFiledir = self.initialdir
        self.transportFiledir = self.initialdir
        self.outputFileDir = self.initialdir
        self.parentWin = parentWin
        self.baseActionsHandlers = bas
        self.initMenuStructure()


    def initMenuStructure(self):
        self.menuStructureData = \
            [["File",
              [("Save Protocol to File", self.doFileSave, None),
               ("Clean Protocol", self.doFileClear, None),
               "",
               ("Exit", self.doExitApp, None)
               ]
              ],
             # ["Mesh Generation",
             #  [(), (), (), ()]
             #  ],
             ["Balance Output Files Processing",
              [("Select Balance Files", self.doBalanceFilesSelection, ""),
               ("Save Balance Report", self.doBalanceSave, ""),
               ("Save Balance Summary Report", self.doBalanceSaveSum, ""),
               "",
               ("Options", self.doBalanceOptions, None)
              ]
              ],
             ["Transport Output Files Managing",
              [("Select Transport Output Files", self.doTransportFilesSelection, ""),
               ("Load All Transport Output Data", self.doAllTransportLoading, ""),
               ("Load Additional Selected Transport Output Data", self.doSelectTransportLoading, ""),
               ("Clear Loaded Output Data", self.doDeleteTransportLoading, ""),
               "",
               ("Point Grids Configuration", self.doCreateGrid, ""),
               ("Add Depth Grid", self.doAddGridDepth, ""),
               ("Add Level Grid", self.doAddGridLevel, ""),
               ("Show/Delete Grids", self.doDelGrid, ""),
               "",
               ("Add Element Set from Depth Range", self.doAddElsetDepth, ""),
               ("Add Element Set from Level Range", self.doAddElsetLevel, ""),
               ("Add Element Set from Regions Group", self.doAddElsetRegions, ""),
               ("Show/Delete Element Sets", self.doDelElset, ""),
               "",
               ("Options", self.doTransportOptions, None)]
              ],
             ["Transport Output Reports",
              [("Maximum at the Element Set", self.doMaxElset, ""),
               ("Maximum Difference between Element Sets", self.doMaxElsetDifference, ""),
               ("Quantile at the Element Set", self.doQuantileElset, ""),
               "",
               ("Maximum at the Grid", self.doMaxGrid, ""),
               ("Maximum Difference between Grids", self.doMaxGridDifference, ""),
               ("Area over Limit at the Grid", self.doAreaGrid, ""),
               ("Quantile at the Grid", self.doQuantileGrid, ""),
               "",
               ("Save Grid as Text File", self.doASCGrid, ""),
               ("Save Grid Difference as Text File", self.doASCGridDifference, ""),
               ("Save Grid as Text File by Percentiles Form", self.doASCGridasPct, ""),
               ("Save Grid Difference as Text File by Percentiles Form", self.doASCGridDifferenceasPct, ""),
               ("Save Grid as Image", self.doImageGrid, "")]
              ],
             ["Models",
              [("Container", self.doContainer_c, "")
              ]
              ],
             ["Help",
              [#("Show User Documentation", self.doHelpShowDoc, None),
               ("About", self.doHelpShowAbout, None)
               ]
              ]]
        

    from geotran_mainwin import GeotranApp

    def noHandlerFound(self, name=None):
        print("No method found to perform the action: ", name)
        # doposud nepodporovana operace
        # nebo chyba programatora
        # zobrazit dialogovy box s informaci nebo generovat vyjimku???
        

    def _wait(self, dialog):
        self.parentWin.wait_window(dialog.topWin)
        return dialog.btn_OK

    def _is_balance_prepare(self):
       if self.postpro_balance is None:
          tk.messagebox.showinfo("Info", "Balance files were not selected.")
          return False
       return True
    
    def _is_mesh_prepare(self, grid_pos=False, grids=False, esets=False, data=False):
       if self.postpro_meshphases is None:
          tk.messagebox.showinfo("Info", "Mesh files were not selected.")
          return False
       p = self.postpro_meshphases.mesh_phases
       if grid_pos:
          if not p.is_grid_positions():
             tk.messagebox.showinfo("Info", "Grid positions were not configured.")
             return False
       return True


    #-------------------------------------------------------------------
    # submenu Balance Output Files Processing  
    #-------------------------------------------------------------------
    @GeotranApp.perform_logged_action
    def doBalanceFilesSelection(self, senderApp=None, midata=None):
        # ************** seznam souboru **************************
        dlg_files = BalanceFileSelectionDialog(self.parentWin, "Balance files selection", balanceFiletypes, self.balanceFiledir)
        if not self._wait(dlg_files): return False
        self.balanceFiledir = dlg_files.currentDir
        # ******** casove jednotky **********
        dlg_time_u = TimeConfigurationDialog(self.parentWin, "Balance files selection", 's', '1000.y')
        if not self._wait(dlg_time_u): return False
        # ********** akce postpro *****************************   
        p = self.postpro_balance = PostProInterface(dlg_time_u.res_output_unit)
        p.params.set_time_source_unit(dlg_time_u.res_input_unit)
        p.load_balance(dlg_files.res_file_names)
        return ["Loaded files:"] + dlg_files.res_file_names + [p.info.print_timespan()]
        

    @GeotranApp.perform_logged_action
    def doBalanceSave(self, senderApp=None, midata=None):
        if not self._is_balance_prepare(): return False
        b = self.postpro_balance.balance
        regions, quantities, species = b.get_regions(), b.get_data_types(), b.get_quantities()
        dlg = BalanceOutputConfigurationDialog(self.parentWin, "Balance output confuguration", regions, quantities, species)
        if not self._wait(dlg): return False
        cols_list = [(None, c[1], c[0], (c[2],)) for c in dlg.res_columns]
        print(cols_list)
        b.report_csv(cols_list, None, dlg.res_exclude_phase_time, None, None, True, dlg.res_output_file_name)
        return ["Result file name: " + dlg.res_output_file_name,
                b.info.print_timespan()]
 

    @GeotranApp.perform_logged_action
    def doBalanceSaveSum(self, senderApp=None, midata=None):
        if not self._is_balance_prepare(): return False
        b = self.postpro_balance.balance
        regions, quantities, species = b.get_regions(), b.get_data_types(), b.get_quantities()
        dlg = BalanceOutputConfigurationDialog(self.parentWin, "Balance output confuguration", regions, quantities, species, regionMultisel=True)
        if not self._wait(dlg): return False
        cols_list = [(None, c[1], c[0], (c[2],)) for c in dlg.res_columns]
        b.report_csv(cols_list, None, dlg.res_exclude_phase_time, None, None, True, dlg.res_output_file_name)
        return ["Result file name: " + dlg.res_output_file_name,
                b.info.print_timespan()]


    def doBalanceOptions(self, senderApp=None, midata=None):
       if not self._is_balance_prepare(): return False
       dlg = BalanceOptionsDialog(self.parentWin, self.postpro_balance.balance)
       if not self._wait(dlg): return False



    #-------------------------------------------------------------------
    # submenu Transport Output Files Managing  
    #-------------------------------------------------------------------
    @GeotranApp.perform_logged_action
    def doTransportFilesSelection(self, senderApp=None, midata=None):
       # ************** seznam souboru **************************
        dlg_files = MeshFileSelectionDialog(self.parentWin, "Ressult mesh files selection", meshFiletypes, self.transportFiledir)
        if not self._wait(dlg_files): return False
        self.transportFiledir = dlg_files.currentDir
        # ******** casove jednotky **********
        dlg_time_u = TimeConfigurationDialog(self.parentWin, "Balance files selection", 's', '1000.y')
        if not self._wait(dlg_time_u): return False        
        # ********** akce postpro *****************************   
        p = self.postpro_meshphases = PostProInterface(dlg_time_u.res_output_unit)
        p.params.set_postpro_dir(postpro_dir)
        p.params.set_time_source_unit(dlg_time_u.res_input_unit)
        p.load_mesh_phases(dlg_files.res_file_names, dlg_files.res_file_names_with_physicals)
        return ["Loaded files:"] + dlg_files.res_file_names + [p.info.print_timespan()]


    @GeotranApp.perform_logged_action
    def doAllTransportLoading(self, senderApp=None, midata=None):
        if not self._is_mesh_prepare(): return False
        p = self.postpro_meshphases.mesh_phases
        p.load_element_data(None, None, None)
        _, loaded = p.get_e_data_names_times_loaded()
        return ["Element data loaded for these species and times:"] + loaded + [p.info.print_timespan()]


    @GeotranApp.perform_logged_action
    def doSelectTransportLoading(self, senderApp=None, midata=None):
        if not self._is_mesh_prepare(): return False
        p = self.postpro_meshphases.mesh_phases
        dlg = DataLoadingDialog(self.parentWin, p)
        if not self._wait(dlg): return False
        p.load_element_data(None, dlg.res_species, dlg.res_times)
        _, loaded = p.get_e_data_names_times_loaded()
        return ["Element data loaded for these species and times:"] + loaded + [p.info.print_timespan()]


    @GeotranApp.perform_logged_action
    def doDeleteTransportLoading(self, senderApp=None, midata=None):
        if not self._is_mesh_prepare(): return False
        if not messagebox.askyesno("Loaded data deleting", "Do you want delete loaded data from memory?"): return False
        (p:=self.postpro_meshphases.mesh_phases).delete_element_data()
        return ["All loaded element data were deleted from memory.", p.info.print_timespan()]
        

    
    # ----- sep --------------------

    @GeotranApp.perform_logged_action
    def doCreateGrid(self, senderApp=None, midata=None):
        if not self._is_mesh_prepare(): return False
        p = self.postpro_meshphases.mesh_phases
        dlg = GridConfigurationDialog(self.parentWin, p)
        if self.last_grid_inputs != []: dlg.set_inputs(self.last_grid_inputs)
        if not self._wait(dlg): return False
        if self.last_grid_inputs[:5] == [dlg.res_min_x, dlg.res_max_x, dlg.res_min_y, dlg.res_max_y, dlg.res_raster_step]:
           p.change_grid_weight_IDW_weight_count(dlg.res_max_interp_points)
        else:
           p.create_grid_positions(dlg.res_raster_step, dlg.res_max_interp_points, [dlg.res_min_x, dlg.res_min_y, dlg.res_max_x, dlg.res_max_y])
        self.last_grid_inputs = dlg.res_inputs
        return ["x range: " + dlg.res_min_x + ", " + dlg.res_max_x,
                "y range: " + dlg.res_min_y + ", " + dlg.res_max_y,           
                "Raster step: " + dlg.res_raster_step,
                "Max. interpolation points: " + dlg.res_max_interp_points,
                p.info.print_timespan()]
                

    @GeotranApp.perform_logged_action
    def doAddGridDepth(self, senderApp=None, midata=None):
       if not self._is_mesh_prepare(grid_pos=True): return False      
       p = self.postpro_meshphases.mesh_phases
       dlg = NewDepthLevelGridDialog(self.parentWin, "New depth grid", "Depth from surface")
       if not self._wait(dlg): return False
       name = p.add_grid_deep(dlg.res_value, dlg.res_name)
       return ["Grid name: " + name,
               "Grid depth: " + dlg.res_value,
               p.info.print_timespan()]


    @GeotranApp.perform_logged_action
    def doAddGridLevel(self, senderApp=None, midata=None):
       if not self._is_mesh_prepare(grid_pos=True): return False
       p = self.postpro_meshphases.mesh_phases
       dlg = NewDepthLevelGridDialog(self.parentWin, "New level grid", "z coordinate:")
       if not self._wait(dlg): return False
       name = p.add_grid_level(dlg.res_value, dlg.res_name)
       return ["Grid name: " + name,
               "Grid level: " + dlg.res_value,
               p.info.print_timespan()]


    @GeotranApp.perform_logged_action    
    def doDelGrid(self, senderApp=None, midata=None):
        if not self._is_mesh_prepare(grid_pos=True): return False
        dlg = GridListDialog(self.parentWin, self.postpro_meshphases.mesh_phases)
        self.parentWin.wait_window(dlg.topWin)
        if len(dlg.res_del) == 0: return ["No elements set was delete."]
        else: return ["deleted elements set:"] + dlg.res_del


    # ----- sep --------------------

    @GeotranApp.perform_logged_action
    def doAddElsetDepth(self, senderApp=None, midata=None):
       if not self._is_mesh_prepare(): return False
       p = self.postpro_meshphases.mesh_phases
       dlg = NewDepthLevelEsetDialog(self.parentWin, "New depth range elements set", "Min. depth", "Max. depth")
       if not self._wait(dlg): return False
       name = p.add_eset_deep_range(dlg.res_min_value, dlg.res_max_value, dlg.res_name)
       return ["Name of elements set: " + name,
               "Depth range: " + dlg.res_min_value + ", " + dlg.res_max_value,
               p.info.print_timespan()]



    @GeotranApp.perform_logged_action
    def doAddElsetLevel(self, senderApp=None, midata=None):
       if not self._is_mesh_prepare(): return False
       p = self.postpro_meshphases.mesh_phases
       dlg = NewDepthLevelEsetDialog(self.parentWin, "New level range elements set", "Min. z", "Max. z")
       if not self._wait(dlg): return False
       name = p.add_eset_level_range(dlg.res_min_value, dlg.res_max_value, dlg.res_name)
       return ["Name of elements set: " + name,
               "Level range: " + dlg.res_min_value + ", " + dlg.res_max_value,
               p.info.print_timespan()]


    @GeotranApp.perform_logged_action
    def doAddElsetRegions(self, senderApp=None, midata=None):
       if not self._is_mesh_prepare(): return False
       p = self.postpro_meshphases.mesh_phases
       dlg = NewRegionsEsetDialog(self.parentWin, "New regions group elements set", p.get_physicals_name_of_phase_0())
       if not self._wait(dlg): return False
       name = p.add_eset_physicals_group(dlg.res_regions_name, dlg.res_name)
       return ["Name of elements set: " + name,
               "Included regions: " + ", ".join(dlg.res_regions_name),
               p.info.print_timespan()]


    @GeotranApp.perform_logged_action
    def doDelElset(self, senderApp=None, midata=None):
        if not self._is_mesh_prepare(): return False
        dlg = EsetListDialog(self.parentWin, self.postpro_meshphases.mesh_phases)
        self.parentWin.wait_window(dlg.topWin)
        if len(dlg.res_del) == 0: return ["No grids was delete."]
        else: return ["deleted grids:"] + dlg.res_del


    def doTransportOptions(self, senderApp=None, midata=None):
       if not self._is_mesh_prepare(): return False
       dlg = TransportOptionsDialog(self.parentWin, self.postpro_meshphases.mesh_phases)
       if not self._wait(dlg): return False


    #-------------------------------------------------------------------
    # submenu Transport Output Reports         
    #-------------------------------------------------------------------
    @GeotranApp.perform_logged_action
    def doMaxElset(self, senderApp=None, midata=None):
        if not self._is_mesh_prepare(): return False
        dlg = ReportEsetMaxValueDialog(self.parentWin, p:=self.postpro_meshphases.mesh_phases, self.outputFileDir)
        if not self._wait(dlg): return False
        self.outputFileDir = dlg.output_dir
        p.report_eset_max_value(dlg.res_models, dlg.res_species, dlg.res_times, dlg.res_exclude_phase_time, None, None, dlg.res_output_file_name)
        return ["Result file: " + dlg.res_output_file_name,
                p.info.print_timespan()]


    @GeotranApp.perform_logged_action
    def doMaxElsetDifference(self, senderApp=None, midata=None):
        if not self._is_mesh_prepare(): return False
        dlg = ReportEsetMaxValuesDifferenceDialog(self.parentWin, p:=self.postpro_meshphases.mesh_phases, self.outputFileDir)
        if not self._wait(dlg): return False
        self.outputFileDir = dlg.output_dir
        p.report_eset_max_value_difference(dlg.res_models, dlg.res_species, dlg.res_times, dlg.res_exclude_phase_time, None, None, dlg.res_base_eset, dlg.res_output_file_name)
        return ["Result file: " + dlg.res_output_file_name,
                "Base elements set: " + dlg.res_base_eset,
                p.info.print_timespan()]


    @GeotranApp.perform_logged_action
    def doQuantileElset(self, senderApp=None, midata=None):
        if not self._is_mesh_prepare(): return False
        dlg = ReportEsetQuantilesDialog(self.parentWin, p:=self.postpro_meshphases.mesh_phases, self.outputFileDir)
        if not self._wait(dlg): return False
        self.outputFileDir = dlg.output_dir
        p.report_eset_quantiles(dlg.res_models, dlg.res_species, dlg.res_times, dlg.res_exclude_phase_time, None, None, dlg.res_quantiles, dlg.res_output_file_name)
        return ["Result file: " + dlg.res_output_file_name,
                "Quantiles [%]: " + ", ".join(dlg.res_quantiles),
                p.info.print_timespan()]


    # ----- sep --------------------

    @GeotranApp.perform_logged_action
    def doMaxGrid(self, senderApp=None, midata=None):
        if not self._is_mesh_prepare(): return False
        dlg = ReportGridMaxValueDialog(self.parentWin, p:=self.postpro_meshphases.mesh_phases, self.outputFileDir)
        if not self._wait(dlg): return False
        self.outputFileDir = dlg.output_dir
        p.report_grid_max_value(dlg.res_models, dlg.res_species, dlg.res_times, dlg.res_exclude_phase_time, None, None, dlg.res_output_file_name)
        return ["Result file: " + dlg.res_output_file_name,
                p.info.print_timespan()]


    @GeotranApp.perform_logged_action
    def doMaxGridDifference(self, senderApp=None, midata=None):
        if not self._is_mesh_prepare(): return False
        dlg = ReportGridMaxValuesDifferenceDialog(self.parentWin, p:=self.postpro_meshphases.mesh_phases, self.outputFileDir)
        if not self._wait(dlg): return False
        self.outputFileDir = dlg.output_dir
        p.report_grid_max_value_difference(dlg.res_models, dlg.res_species, dlg.res_times, dlg.res_exclude_phase_time, None, None, dlg.res_base_grid, dlg.res_output_file_name)
        return ["Result file: " + dlg.res_output_file_name,
                "Base grid: " + dlg.res_base_grid,
                p.info.print_timespan()]


    @GeotranApp.perform_logged_action
    def doAreaGrid(self, senderApp=None, midata=None):
        if not self._is_mesh_prepare(): return False
        dlg = ReportGridAreaOverLimitsDialog(self.parentWin, p:=self.postpro_meshphases.mesh_phases, self.outputFileDir)
        if not self._wait(dlg): return False
        self.outputFileDir = dlg.output_dir
        p.report_grid_area_over_limits(dlg.res_models, dlg.res_species, dlg.res_times, dlg.res_exclude_phase_time, None, None, dlg.res_limits, dlg.res_output_file_name)
        return ["Result file: " + dlg.res_output_file_name,
                "Limits: " + ", ".join(dlg.res_limits),
                p.info.print_timespan()]


    @GeotranApp.perform_logged_action
    def doQuantileGrid(self, senderApp=None, midata=None):
        if not self._is_mesh_prepare(): return False
        dlg = ReportGridQuantilesDialog(self.parentWin, p:=self.postpro_meshphases.mesh_phases, self.outputFileDir)
        if not self._wait(dlg): return False
        self.outputFileDir = dlg.output_dir
        p.report_grid_quantiles(dlg.res_models, dlg.res_species, dlg.res_times, dlg.res_exclude_phase_time, None, None, dlg.res_quantiles, dlg.res_output_file_name)
        return ["Result file: " + dlg.res_output_file_name,
                "Quantiles [%]: " + ", ".join(dlg.res_quantiles),
                p.info.print_timespan()]


    # ----- sep --------------------

    @GeotranApp.perform_logged_action
    def doImageGrid(self, senderApp=None, midata=None):
        if not self._is_mesh_prepare(): return False
        dlg = ReportGridImagesDialog(self.parentWin, p:=self.postpro_meshphases.mesh_phases, self.outputFileDir)
        if not self._wait(dlg): return False
        self.outputFileDir = dlg.output_dir
        p.report_grid_images(dlg.res_models, dlg.res_species, dlg.res_times, dlg.res_exclude_phase_time, (30,30,30), dlg.res_colors, dlg.res_limits, dlg.res_output_dir, dlg.res_file_prefix, dlg.res_file_ext)
        return ["Result directory: " + dlg.res_output_dir,
                "Result files prefix: " + dlg.res_file_prefix,
                "Result files type: " + dlg.res_file_ext,
                "Limits: " + ", ".join(dlg.res_limits),
                p.info.print_timespan()]


    @GeotranApp.perform_logged_action
    def doASCGrid(self, senderApp=None, midata=None):
        if not self._is_mesh_prepare(): return False
        dlg = ReportGridASCDialog(self.parentWin, p:=self.postpro_meshphases.mesh_phases, self.outputFileDir)
        if not self._wait(dlg): return False
        self.outputFileDir = dlg.output_dir
        p.report_grid_asc(dlg.res_models, dlg.res_species, dlg.res_times, dlg.res_exclude_phase_time, dlg.res_value_instead_of_nan, dlg.res_output_dir, dlg.res_file_prefix)
        return ["Result directory: " + dlg.res_output_dir,
                "Result files prefix: " + dlg.res_file_prefix,
                "No Value: " + dlg.res_value_instead_of_nan,
                p.info.print_timespan()]


    @GeotranApp.perform_logged_action
    def doASCGridDifference(self, senderApp=None, midata=None):
        if not self._is_mesh_prepare(): return False
        dlg = ReportGridDifferenceASCDialog(self.parentWin, p:=self.postpro_meshphases.mesh_phases, self.outputFileDir)
        if not self._wait(dlg): return False
        self.outputFileDir = dlg.output_dir
        p.report_grid_difference_asc(dlg.res_models, dlg.res_species, dlg.res_times, dlg.res_exclude_phase_time, dlg.res_base_grid, dlg.res_value_instead_of_nan, dlg.res_output_dir, dlg.res_file_prefix)
        return ["Result directory: " + dlg.res_output_dir,
                "Result files prefix: " + dlg.res_file_prefix,
                "Base grid: " + dlg.res_base_grid,
                "No Value: " + dlg.res_value_instead_of_nan,
                p.info.print_timespan()]


    @GeotranApp.perform_logged_action
    def doASCGridasPct(self, senderApp=None, midata=None):
        if not self._is_mesh_prepare(): return False
        dlg = ReportGridASCasPctDialog(self.parentWin, p:=self.postpro_meshphases.mesh_phases, self.outputFileDir)
        if not self._wait(dlg): return False
        self.outputFileDir = dlg.output_dir
        p.report_grid_asc_as_pct(dlg.res_models, dlg.res_species, dlg.res_times, dlg.res_exclude_phase_time, dlg.res_value_instead_of_nan, dlg.res_value_100pct, dlg.res_decnum, dlg.res_output_dir, dlg.res_file_prefix)
        return ["Result directory: " + dlg.res_output_dir,
                "Result files prefix: " + dlg.res_file_prefix,
                "Value of 100%: " + dlg.res_value_100pct,
                "No Value: " + dlg.res_value_instead_of_nan,
                p.info.print_timespan()]


    @GeotranApp.perform_logged_action
    def doASCGridDifferenceasPct(self, senderApp=None, midata=None):
        if not self._is_mesh_prepare(): return False
        dlg = ReportGridDifferenceASCasPctDialog(self.parentWin, p:=self.postpro_meshphases.mesh_phases, self.outputFileDir)
        if not self._wait(dlg): return False
        self.outputFileDir = dlg.output_dir
        p.report_grid_difference_asc_as_pct(dlg.res_models, dlg.res_species, dlg.res_times, dlg.res_exclude_phase_time, dlg.res_base_grid, dlg.res_value_instead_of_nan, dlg.res_decnum, dlg.res_output_dir, dlg.res_file_prefix)
        return ["Result directory: " + dlg.res_output_dir,
                "Result files prefix: " + dlg.res_file_prefix,
                "Base grid: " + dlg.res_base_grid,
                "No Value: " + dlg.res_value_instead_of_nan,
                p.info.print_timespan()]


    #-------------------------------------------------------------------
    # submenu Models                             
    #-------------------------------------------------------------------

    def doContainer_c(self, senderApp=None, midata=None):
        dlg = ContainerCDialog(self.parentWin, self.initialdir)
        self.parentWin.wait_window(dlg.topWin)
        self.initialdir = dlg.initialdir


    #-------------------------------------------------------------------
    # submenu Help                             
    #-------------------------------------------------------------------
    # dost mozna nebude treba dekorovat
    # neni treba kontrolovat senderApp a midata
    #@GeotranApp.perform_nonlogged_action
    def doHelpShowDoc(self, senderApp=None, midata=None):
        print("Displaying user documentation")
        pass

    #@GeotranApp.perform_nonlogged_action
    def doHelpShowAbout(self, senderApp=None, midata=None):
        print("Displaying about box")
        pass

    #-------------------------------------------------------------------
    # submenu File
    #-------------------------------------------------------------------
    @GeotranApp.perform_nonlogged_action
    def doFileSave(self, senderApp=None, midata=None):
        filepath = tk.filedialog.asksaveasfilename(
            parent=self.parentWin,
            title='Enter the protocol file',
            initialdir=self.protocolFiledir,
            defaultextension=protocolFiletypes[0][1],
            filetypes=protocolFiletypes)
        if (filepath == '') or (filepath == None):
            return False
        if os.path.isfile(filepath):
            if tk.messagebox.askquestion(
                    "Confirm rewriting existing file",
                    "The file exists.\nDo you really want to rewrite it?") == "no":
                return False
        try:
            fnToCall = self.baseActionsHandlers.get("protocol_filewriter",
                            lambda name="protocol_reader": self.noHandlerFound(name))
            fnToCall(filepath)
            self.protocolFiledir = os.path.dirname(filepath)
            self.protocolFilename = os.path.basename(filepath)
            # vypsat stavove informace
            return True
        except Exception as err:
            tk.messagebox.showerror('Error',
                                    'Error occured while saving protocol content to a disk file: {}'.format(err))
            return False
        

    @GeotranApp.perform_nonlogged_action
    def doFileClear(self, senderApp=None, midata=None):
        if senderApp.isProtocolChanged():
            if tk.messagebox.askquestion(
                    "Confirm protocol cleaning",
                    "The protocol content was changed after the last saving.\n" + \
                    "The unsaved information could be lost.\n" + \
                    "Do you really want to clean it without saving?") == "no":
                return False
        try:
            self.baseActionsHandlers.get("protocol_cleaner",
                                         lambda name="protocol_cleaner": self.noHandlerFound(name))()
            return True
        except Exception as err:
            tk.messagebox.showerror('Error',
                                    'Error occured while cleaning protocol content: {}'.format(err))
            return False
        


    def doExitApp(self, senderApp=None, midata=None):
        # senderApp musi byt !=None a typu GeotranApp
        print("Exit program")
        if senderApp.isProtocolChanged():
            if tk.messagebox.askquestion(
                    "Confirm follow-up to closing",
                    "The protocol content was changed. \nThe unsaved data could be lost.\nDo you really want to follow-up to closing?") == "no":
                return False
        # otestovat dalsi rozpracovanou praci, objekty postpro apod
        if tk.messagebox.askquestion(
                "Confirm closing",
                "Do you really want to close the session?") == "yes":
            self.baseActionsHandlers.get("app_terminator",
                lambda name="app_terminator": self.noHandlerFound(name))()
        



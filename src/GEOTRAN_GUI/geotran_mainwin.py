
import os
import time
import tkinter as tk
import tkinter
from tkinter import ttk
from tkinter import scrolledtext
from functools import partial
from functools import wraps
from builtins import isinstance
from datetime import datetime
import psutil

import geotran_mainwin_menu_handler

import geotran_standard_output

class GeotranApp ():
    rootWindow = None
    mainFrame = None
    mainMenu = None
    protocolRecorder = None
    topInfoPanel = None
    mainMenuHandler = None
    textInfoDim = (120, (5, 10, 0))
    protocolChanged = False
    iconFilepath = './icons/geotran_32_53.ico'

    def __init__(self):
        self.baseActionPerformers = {
            "app_terminator": getattr(self, "exitApp"),
            "state_writer": getattr(self, "showTopInfo"),
            "protocol_appender": getattr(self, "recordInProtocol"),
            "protocol_reader": getattr(self, "getProtocolContent"),
            "protocol_cleaner": getattr(self, "clearProtocolContent"),
            "protocol_filewriter": getattr(self, "saveProtocolContentToFile"),
        }
        self.rootWindow = tk.Tk()
        self.rootWindow.iconbitmap(bitmap=self.iconFilepath, default=self.iconFilepath)
        self.mainFrame = tk.Frame(self.rootWindow)
        self.mainFrame.pack(expand=False)
        self.rootWindow.title('GEOTRAN tools')
        # win theme
        # style = ttk.Style(self.rootWindow)
        # style.theme_use('xpnative')
        # menu settings
        self.mainMenuHandler = geotran_mainwin_menu_handler.GeotranMainmenuHandler(self, self.rootWindow, self.baseActionPerformers)
        self.setupMenu()
        self.initState()
        # desktop settings
        self.setupDesktop()
        self.mainFrame.pack()
        self.rootWindow.protocol("WM_DELETE_WINDOW", partial(self.mainMenuHandler.doExitApp, self))
        

    def setupMenu(self):
        self.mainMenu = tk.Menu(self.mainFrame)
        menuStructure = self.mainMenuHandler.menuStructureData
        for submenuData in menuStructure:
            submenu = tk.Menu(self.mainMenu, tearoff=0)
            #self.mainMenuItems.append(submenu)
            for mi in submenuData[1] :
                if isinstance(mi, str):
                    submenu.add_separator()
                elif len(mi) < 2:
                    pass
                else:
                    if callable(mi[1]) :
                        submenu.add_command(label=mi[0], command=partial(mi[1], self, mi))
            self.mainMenu.add_cascade(label=submenuData[0], menu=submenu)
            self.mainMenu.add_separator()
        self.rootWindow.config(menu=self.mainMenu)
        

    def setupDesktop(self):
        # nutno predelat a pouzit asi rozlozeni pomoci grid() a nikoli pack()
        self.topInfoPanel = tk.Text(self.rootWindow)
        self.topInfoPanel.configure(width=self.textInfoDim[0], height=self.textInfoDim[1][0])
        self.topInfoPanel.configure(relief=tk.RAISED, bg="light grey", fg='black')
        self.topInfoPanel.configure(state=tk.NORMAL)
        self.topInfoPanel.pack(fill=tk.X, side=tk.TOP) # anchor=tk.NW
        self.showTopInfo()

        self.protocolRecorder = tk.scrolledtext.ScrolledText(self.rootWindow)
        self.protocolRecorder.configure(width=self.textInfoDim[0], height=self.textInfoDim[1][1])
        self.protocolRecorder.configure(wrap=tk.NONE) #(wrap=tk.WORD) #(wrap='word')
        self.protocolRecorder.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        b = self.bottomInfoPanel = tk.Text(self.rootWindow, )
        self.bottomInfoPanel.configure(width=self.textInfoDim[0], height=self.textInfoDim[1][2])
        self.bottomInfoPanel.configure(relief=tk.SUNKEN, bg="light grey", fg='black')
        self.bottomInfoPanel.configure(state=tk.NORMAL)
        self.bottomInfoPanel.pack(fill=tk.X, side=tk.BOTTOM)
        
        
    def runApp(self):
        print("Running application ...")
        self.rootWindow.mainloop()
        

    def exitApp(self):
        print("Exiting application ...")
        self.rootWindow.destroy()
        

    def showTopInfo(self):
        (w := self.topInfoPanel).delete('1.0', 'end')
        pp = []
        if (a:=self.mainMenuHandler.postpro_balance) is not None:
           pp.append("Balances ({:d} phases)".format(a.balance.get_phases_count()))
        if (a:=self.mainMenuHandler.postpro_meshphases) is not None:
           pp.append("Transport ({:d} phases)".format(a.mesh_phases.get_phases_count()))
           p_mem = sum(psutil.Process(pid).memory_info().rss for pid in a.mesh_phases.get_phases_processes_id())
        else:
           p_mem = 0
        if len(pp) == 0: pp.append("No object")
        w.insert(tk.END, "Postprocessing objects:  " + ", ".join(pp) + "\n")
        b = p_mem + psutil.Process(os.getpid()).memory_info().rss
        w.insert(tk.END, "Used memory after last completed action: {:.0f} MB ({:d} bytes)\n".format(b / 1024**2, b))
        

    def recordInProtocol(self, lines=None, indent=0):
        indentStr = " " * indent
        if lines is not None:
            if isinstance(lines, str):
                self.protocolRecorder.insert(tk.END, indentStr + lines + "\n")
            else:
                for line in lines:
                    self.protocolRecorder.insert(tk.END, indentStr + line+"\n" )
            self.protocolRecorder.see(tk.END)
            self.protocolChanged = True
        

    def getProtocolContent(self):
        return self.protocolRecorder.get('1.0', 'end');

    def clearProtocolContent(self):
        print("Cleaning protocol ...")
        self.protocolRecorder.delete('1.0', 'end')
        self.protocolChanged = False
        

    def saveProtocolContentToFile(self, filepath):
        print("Printing protocol to file ...")
        if not isinstance(filepath, str):
            raise TypeError("Given filepath is not a string")
        with (open(filepath, "w")) as fout:
            fout.write(self.protocolRecorder.get('1.0', 'end'))
            self.protocolChanged = False
        

    def initState(self):
        self.protocolChanged = False
        

    def isProtocolChanged(self):
        return self.protocolChanged
        

    def protocolWasSavedToFile(self, path):
        self.protocolFilePathname = path
        self.protocolChanged = False
        

    #------------------------------------------------------------
    # decorators
    #------------------------------------------------------------
    @classmethod
    def perform_logged_action(cls, func):
        """
        Decorator to logging selected action
        :param func:
        :return:
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # gtApp object :  args[1]
            # menu item label :  args[2][0])
            # logging before action
            result = None
            try:
                gtApp = args[1]
                if gtApp is None:
                   raise TypeError("The senderApp is None")
                if isinstance(gtApp, GeotranApp):
                  raise TypeError("The senderApp is not GeotranApp")
                gtApp.recordInProtocol('----------------------------------------------')
                gtApp.recordInProtocol('Action: ' + args[2][0])
                deltaTime = time.time()
                result = func(*args, **kwargs)
                if not result:
                    gtApp.recordInProtocol('Action was not completed')
                    return
                deltaTime = time.time() - deltaTime
                date_time = datetime.utcfromtimestamp(deltaTime)
                timeStr = date_time.strftime("%H:%M:%S")
                # logging after the action
                gtApp.recordInProtocol('Action completed')
                if result is not None and result != True:
                    gtApp.recordInProtocol('Results: ')
                    if not isinstance(result, (list, tuple)): result = (result)
                    for res in result: gtApp.recordInProtocol(res, indent=2)
                gtApp.recordInProtocol("Duration of the action: {}".format(timeStr))
                gtApp.showTopInfo()
            except Exception as err:
                if err.__class__.__qualname__.split(".")[0] in {"Mesh_Err","GEModel_Err","GEComputing_Err","MP_Err"}:
                    tk.messagebox.showerror('Error',
                       str(err)[:-2].split('"')[-1])
                    gtApp.recordInProtocol('Action was not completed')
                else:
                    tk.messagebox.showerror('Error',
                        'No expected error occured during the action: {}'.format(err))
                    gtApp.recordInProtocol('Action was not completed')
                    raise err
            finally:
                gtApp.recordInProtocol('----------------------------------------------')
                gtApp.recordInProtocol(' ')
            return result
        return wrapper


    @classmethod
    def perform_nonlogged_action(cls, func):
        """
        Decorator to simple action
        :param func:
        :return:
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # gtApp object :  args[1]
            # menu item label :  args[2][0])
            # what to do before the action
            result = None
            try:
                gtApp = args[1]
                if gtApp == None:
                    raise TypeError("The senderApp is None")
                if isinstance(gtApp, GeotranApp):
                    raise TypeError("The senderApp is not GeotranApp")
                # gtApp.recordInProtocol('Nonlogged action: ' + args[2][0])
                # gtApp.recordInProtocol(' ')
                result = func(*args, **kwargs)
                # what to do after the action
            except Exception as err:
                tk.messagebox.showerror('Error',
                    'Error occured while performed selected action: {}'.format(err))
                raise err
            return result
        return wrapper

    pass # GeotranApp class


def runAsMain():
    geotranApp = GeotranApp()
    geotran_standard_output.initialize(geotranApp.rootWindow)
    geotranApp.runApp()
    geotran_standard_output.terminate()




# This is a main script od the software GEOTRANtools.
import sys

gui_dir = "./GEOTRAN_GUI/"
pp_dir = "./POSTPRO/"
cont_dir = "./CONTAINER_C/"
sys.path.append(gui_dir)
sys.path.append(pp_dir)
sys.path.append(cont_dir)

import GEOTRAN_GUI.mainwin as GT_mainwin

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    GT_mainwin.runAsMain()

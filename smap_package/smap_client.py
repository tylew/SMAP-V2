import pandas as pd
import numpy as np

from smap_package.src.mdc.mdcTool import MDC
from smap_package.src.aps.apsTool import APS
from smap_package.src.socr.socrTool import SOCr
from smap_package.src.efd.efdTool import EFD
from smap_package.src.ea.eaTool import EA

class SMAP_Client:

    def __init__(self, tools=['mdc', 'aps', 'socr', 'efd', 'ea'], project_name = 'My Project') -> None:
        # Initial project configuration
        self.project_name = project_name
        self.project_version = 0

        # Tool selection 
        if 'mdc' in tools:
            self.mdc = MDC(self)
        if 'aps' in tools:
            self.aps = APS(self)
        if 'socr' in tools:
            self.socr = SOCr(self)
        if 'efd' in tools:
            self.efd = EFD(self)
        if 'ea' in tools:
            self.ea = EA(self)

        # Output files
        self.baseline_load_profile = None # XLSX buffer obj. Set by MDC.run(). Consumed by APS
        self.aggregated_profile_spreadsheet = None #
        self.socr_spreadsheet = None

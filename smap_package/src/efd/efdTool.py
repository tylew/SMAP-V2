from smap_package.src.utils.BESS import BESS
from smap_package.src.utils.Tool import Tool
from smap_package.src.efd.efdHelpers import run_efd

class EFD(Tool):
    def __init__(self, smap_client) -> None:
        super().__init__(smap_client)
        self.bess = BESS()

        self.efd_master_df = None
        self.efd_critical_df = None

    # @override
    def is_complete(self) -> bool:
        pass
    
    # @override
    def generate_data(self, **kwargs):
        assert self.aggregated_profile_spreadsheet is not None, "Aggregated profile spreadsheet is not set"
        self.efd_master_df, self.efd_critical_df = run_efd(self.aggregated_profile_spreadsheet, self.bess)
    

    # @override
    def generate_plots(self, **kwargs):
        pass
    
    # @override
    def reset(self, **kwargs):
        pass

    # @override
    def reload_plots(self, **kwargs):
        pass

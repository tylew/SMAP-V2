from smap_package.src.utils.BESS import BESS
from smap_package.src.utils.Tool import Tool
from smap_package.src.ea.eaHelpers import run_ea

class EA(Tool):
    def __init__(self, smap_client) -> None:
        super().__init__(smap_client)

    # @override
    def is_complete(self) -> bool:
        pass
    
    # @override
    def generate_data(self, **kwargs):
        pass

    # @override
    def generate_plots(self, **kwargs):
        pass
    
    # @override
    def reset(self, **kwargs):
        pass

    # @override
    def reload_plots(self, **kwargs):
        pass

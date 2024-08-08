
from smap_package.src.utils.Tool import Tool
from smap_package.src.socr import socrHelpers
from smap_package.src.utils import generalHelpers

class SOCr(Tool):
    def __init__(self, smap_client) -> None:
        super().__init__(smap_client)
        # file inputs
        ## Tool@property aggregated_profile_spreadsheet
        # parameters + defaults
        self.charge_loss_percentage = 3.0
        self.discharge_loss_percentage = 3.0
        self.include_degradation = False
        self.years_until_replacement = 15
        self.annual_solar_degradation_percentage = 0.5
        self.annual_battery_degradation_percentage = 2.0

        # outputs
        self.socr_profile_df = None
        self.socr_curve_df = None

    # @override
    def generate_data(self, **kwargs):
        assert self.aggregated_profile_spreadsheet is not None, "Aggregated profile spreadsheet is not set"
        # run script
        self.socr_profile_df, self.socr_curve_df = socrHelpers.run_socr(
                                        self.aggregated_profile_spreadsheet,
                                        self.charge_loss_percentage,
                                        self.discharge_loss_percentage,
                                        self.include_degradation,
                                        self.years_until_replacement,
                                        self.annual_solar_degradation_percentage,
                                        self.annual_battery_degradation_percentage
                                    )
        self.generate_socr_spreadsheet()
    
    # @override
    def generate_plots(self, **kwargs):
        pass
    
    # @override
    def reload_plots(self, **kwargs):
        pass

    # @override
    def reset(self, **kwargs):
        self.socr_profile_df = None
        self.socr_curve_df = None

    # @override
    def is_complete(self) -> bool:
        return self.socr_spreadsheet is not None

    def generate_socr_spreadsheet(self):
        assert self.socr_profile_df is not None, 'SOCr profile not calculated'
        assert self.socr_curve_df is not None, 'SOCr curve not calculated'

        self.socr_spreadsheet = generalHelpers.make_excel_workbook(
            [self.socr_profile_df, self.socr_curve_df], 
            ['SOCr Profile', 'Max SOCr Curve']
        )

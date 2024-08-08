import numpy as np
import io
import pandas as pd

from smap_package.src.utils.Tool import Tool
from smap_package.src.aps import apsHelpers, apsPlotting

class APS(Tool):
    
    def __init__(self, smap_client) -> None:
        super().__init__(smap_client)
        # File inputs
        self.adjustment_load_profile = None
        self.solar_generation_profile = None
        # Parameter inputs + defaults
        self._adjustment_load_source = 'none'  # see @adjustment_load_source.setter
        self._critical_load_source = 'baseline'  # see @critical_load_source.setter
        self.critical_load_percentage = 10.0
        self._solar_generation_source = 'none'  # see @solar_generation_source.setter
        self.graph_selections = ['Master', 'Critical']
        # Outputs
        ## df
        self.aggregated_profile_df = None
        self.monthly_summary_df = pd.DataFrame()
       
        ## plots
        self.monthly_plotly = None
        self.daily_plotly = None

    # adjustment_load_source property
    @property
    def adjustment_load_source(self):
        return self._adjustment_load_source
    @adjustment_load_source.setter
    def adjustment_load_source(self, value):
        if value in ["None","2-Column xlsx"]:
            self._adjustment_load_source = value
        else:
            raise ValueError(f"adjustment_load_source must be 'None', or '2-Column xlsx: set to {value}'")

    # critical_load_source property
    @property
    def critical_load_source(self):
        return self._critical_load_source
    @critical_load_source.setter
    def critical_load_source(self, value):
        if value in ['baseline', 'master']:
            self._critical_load_source = value
        else:
            raise ValueError("critical_load_source must be 'baseline' or 'master'")

    # solar_generation_source property
    @property
    def solar_generation_source(self):
        return self._solar_generation_source
    @solar_generation_source.setter
    def solar_generation_source(self, value):
        if value in ['none', 'helioscope', '2-column']:
            self._solar_generation_source = value
        else:
            raise ValueError("solar_generation_source must be 'none', 'helioscope', or '2-column'")

    # @override
    def reload_plots(self):
        # self.full_year_plotly.update_layout(title={'text': self.project_name, 'x': 0.5})
        pass

    # @override
    def reset(self):
        # File inputs
        self.adjustment_load_profile = None
        self.solar_generation_profile = None
        # Parameter inputs + defaults
        self._adjustment_load_source = 'none'  # see @adjustment_load_source.setter
        self._critical_load_source = 'baseline'  # see @critical_load_source.setter
        self.critical_load_percentage = 10.0
        self._solar_generation_source = 'none'  # see @solar_generation_source.setter
        self.graph_selections = ['Master', 'Critical']
        # Outputs
        ## df
        self.aggregated_profile_df = None
        self.monthly_summary_df = pd.DataFrame()
        # self.aggregated_profile_spreadsheet = self.aggregated_profile_spreadsheet # copy ref from parent
        ## plots
        self.monthly_plotly = None
        self.daily_plotly = None

    # @override
    def generate_data(self, **kwargs):
        # Assertions
        assert self.baseline_load_profile is not None, 'Baseline load profile must be provided.'
        assert isinstance(self.critical_load_percentage, (int, float)), 'critical load percentage must be a number.'
        if self.solar_generation_source != 'none':
            assert self.solar_generation_profile is not None, "Solar generation profile must be provided to perform solar generation adjustment. set solar_generation_source to 'none' to skip solar generation adjustment."
        
        # Clear previous output
        # self.aggregated_profile_spreadsheet = Non
        # Generate output
        critical_array = np.array([self.critical_load_percentage] * 35040)
        # TODO: THIS FUNCTION BELOW NEEDS TWEAKING, 
        #       GET RID OF 'SOURCE' VARIABLES
        self.aggregated_profile_df = apsHelpers.build_aps(self.baseline_load_profile, 
                                        self.adjustment_load_profile,
                                        critical_array,
                                        self.critical_load_source,
                                        self.solar_generation_profile,
                                        self.solar_generation_source
                                    )
        
        ## Generate spreadsheets
        self.generate_monthly_summary_df()
        self.generate_aggregated_profile_spreadsheet()

    # @override
    def generate_plots(self, **kwargs):
        self.generate_monthly_bars_plotly()
        self.generate_daily_sum_plotly()

    def is_complete(self) -> bool:
        return self.aggregated_profile_spreadsheet is not None and self.monthly_plotly is not None and self.daily_plotly is not None

    def generate_aggregated_profile_spreadsheet(self):
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            
            workbook = writer.book
            workbook = apsHelpers.aps_write_summary_df_to_excel(workbook, 
                                                    "Monthly Summary - Selects",
                                                    self.aggregated_profile_df,
                                                    self.graph_selections,
                                                    self.project_name)
            
            workbook = apsHelpers.aps_write_summary_df_to_excel(workbook, 
                                                    "Monthly Summary - BAM",
                                                    self.aggregated_profile_df,
                                                    ["Baseline","Adjustment","Master"],
                                                    self.project_name)
            
            
            if self.solar_generation_profile == "None":
                workbook = apsHelpers.aps_write_summary_df_to_excel(workbook, 
                                                    "Monthly Summary - All",
                                                    self.aggregated_profile_df,
                                                    self.aggregated_profile_df.columns.tolist(),
                                                    self.project_name)
        self.aggregated_profile_spreadsheet = buffer
            
    def generate_monthly_summary_df(self):
        for i,profile in enumerate(self.graph_selections):
            #Monthy_summary_df = pd.concat([Monthy_summary_df,profile_summary_df(st.session_state['aps_df'],profile)],axis=0)
            df = apsHelpers.profile_summary_df(self.aggregated_profile_df,profile)
            df.columns = [f'{profile} {col}' for col in df.columns] 
            self.monthly_summary_df = pd.concat([self.monthly_summary_df,df],axis=1)

    def generate_monthly_bars_plotly(self):
        self.monthly_plotly = apsPlotting.monthly_bars_plotly(
                                        self.aggregated_profile_df, 
                                        self.graph_selections, 
                                        self.project_name)

    def generate_daily_sum_plotly(self):
        self.daily_plotly = apsPlotting.daily_sum_plotly(
                                        self.aggregated_profile_df,
                                        self.graph_selections,
                                        self.project_name)

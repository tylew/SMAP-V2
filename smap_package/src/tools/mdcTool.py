import io
import pandas as pd
import copy
from smap_package.src.utils.Tool import Tool
from smap_package.src.helpers.tools import mdcHelpers

class MDC(Tool):
    def __init__(self, smap_client) -> None:
        super().__init__(smap_client)
        # File inputs
        self.raw_meter_data = None
        # Parameter inputs + defaults
        self.annualize = True
        self.fix_near_values = False
        self.near_value_threshold = 0.25
        # Outputs
        ## files
        self.clean_df = None
        # Baseline load, see Tool@property baseline_load_profile
        ## plots
        self.full_year_plotly = None
        self.month_plotly = None
        self.day_of_week_plotly = None

    # @override
    def generate_data(self, **kwargs):
        # Assert parameters are set
        assert self.raw_meter_data is not None, 'Meter data must be provided.'
        assert type(self.fix_near_values) == bool, 'annualize value must be True or False.'
        if self.fix_near_values: 
            assert isinstance(self.near_value_threshold, (int, float)), 'near-value threshold must be a number.'
        # Clear previous output
        self.clean_df = None
        self.clean_excel_buffer = None
        # Generate clean meter data
        self.clean_df = mdcHelpers.clean_15min_meter_data(
                                copy.copy(self.raw_meter_data), 
                                self.annualize, 
                                self.fix_near_values, 
                                self.near_value_threshold
                            )
    
    # @override
    def generate_plots(self, **kwargs):
        #Generate plots (plotly)
        self.generate_full_year_plotly()
        self.generate_day_of_week_plotly()
        self.generate_month_plotly()
        # Generate baseline load profile (xlsx buffer)
        self.generate_baseline_load_profile()

    # @override
    def reload_plots(self):
        self.full_year_plotly.update_layout(title={'text': self.project_name, 'x': 0.5})
        # self.month_plotly = None
        # self.day_of_week_plotly = None

    # @override
    def reset(self):
        self.clean_df = None
        self.baseline_load_profile = None
        self.full_year_plotly = None
        self.month_plotly = None
        self.day_of_week_plotly = None

    # @override
    def is_complete(self) -> bool:
        return self.clean_df is not None and self.baseline_load_profile is not None
    
    ### Non-Override functions ###
    def generate_baseline_load_profile(self):
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer,engine='xlsxwriter') as writer:

            just_cleaned = self.clean_df
            just_cleaned = just_cleaned[['cleaned_kWh']]
            just_cleaned.to_excel(writer,sheet_name='Cleaned',index=True)
            self.clean_df.to_excel(writer,sheet_name='Cleaning History',index=True)

        self.baseline_load_profile = buffer
    
    def generate_full_year_plotly(self):
        self.full_year_plotly = mdcHelpers.full_year_plotly(self.clean_df,self.project_name,self.near_value_threshold,show_weekends=True)
    
    def generate_month_plotly(self):
        month_group = mdcHelpers.group_by_month(self.clean_df)
        self.month_plotly = mdcHelpers.month_plotly(month_group,self.project_name)
    
    def generate_day_of_week_plotly(self):
        dow_group = mdcHelpers.group_by_day_of_week(self.clean_df)
        self.day_of_week_plotly = mdcHelpers.day_of_week_plotly(dow_group,self.project_name)

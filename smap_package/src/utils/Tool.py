'''
Tool.py

Template class for SMAP tools.  
TODO: Revisit

Author: Tyler Lewis
Created: 2024-07-29
Last modified: 2024-08-04
'''

from abc import ABC, abstractmethod

class Tool(ABC):
    """
    Abstract base class for SMAP service tools.
    """
    def __init__(self, smap_client) -> None:
        # SMAP_Client parent object, !!lazy import to prevent circular imports!!
        from smap_package.smap_client import SMAP_Client
        assert isinstance(smap_client, SMAP_Client), "Must initialize using an instance of SMAP_Client."
        self.smap_client = smap_client

    # Access shared project_name
    @property 
    def project_name(self):
        return self.smap_client.project_name
    @project_name.setter
    def baseline_load_profile(self, value):
        self.smap_client.project_name = value
    
    # Access shared Baseline Load Profile Spreadsheet
    @property 
    def baseline_load_profile(self):
        return self.smap_client.baseline_load_profile
    @baseline_load_profile.setter
    def baseline_load_profile(self, value):
        self.smap_client.baseline_load_profile = value
    
    # Access shared Aggreated Profiles Spreadsheet
    @property
    def aggregated_profile_spreadsheet(self):
        return self.smap_client.aggregated_profile_spreadsheet 
    @aggregated_profile_spreadsheet.setter
    def aggregated_profile_spreadsheet(self, value):
        self.smap_client.aggregated_profile_spreadsheet = value

    # Access shared SOCr Spreadsheet
    @property
    def socr_spreadsheet(self):
        return self.smap_client.socr_spreadsheet
    @socr_spreadsheet.setter
    def socr_spreadsheet(self, value):
        self.smap_client.socr_spreadsheet = value

    def run(self):
        """
        Run the service.
        """
        self.generate_data()
        self.generate_plots()
        
    @abstractmethod
    def is_complete(self) -> bool:
        """Method to indicate completion of tool"""
        raise NotImplementedError("Subclasses must implement this method")
    
    @abstractmethod
    def generate_data(self, **kwargs):
        """Method to generate processed data"""
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def generate_plots(self, **kwargs):
        """Method to generate service's plots"""
        raise NotImplementedError("Subclasses must implement this method")
    
    @abstractmethod
    def reset(self, **kwargs):
        """Method to reset service's data to defaults"""
        raise NotImplementedError("Subclasses must implement this method")

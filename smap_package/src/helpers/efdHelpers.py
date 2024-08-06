import numpy as np
import pandas as pd
from smap_package.src.helpers.generalHelpers import df_from_file

from smap_package import CONFIG # imported from base/__init__.py

styles = CONFIG['styles']
excel_style = styles['excel-colors']

def run_efd(file, bess):
    df = df_from_file(file, parse_dates=['timestamp'],index_col= 'timestamp')
    return efd_engine(df, "Master", bess), efd_engine(df, "Critical", bess)

def efd_engine(df,profile,bess):
    '''
    
    '''
    df = df.copy()
    
    solar = df['Solar'].values
    load = df[profile].values
    
    solar_to_load       = np.zeros(len(df.index))
    excess_solar        = np.zeros(len(df.index))
    unserved_after_solar = np.zeros(len(df.index))
    unserved_after_bess = np.zeros(len(df.index))
    grid_import         = np.zeros(len(df.index))
    soc_begin           = np.zeros(len(df.index))
    soc_end             = np.zeros(len(df.index))
    bess_chg_dischg     = np.zeros(len(df.index))
    bess_chg_dischg_dc  = np.zeros(len(df.index))
    curtailed           = np.zeros(len(df.index))
    
    for t,timestamp in enumerate(df.index):
        
        if t>0:
            soc_begin[t] = soc_end[t-1]
        else:
            soc_begin[t] = bess.initial_soc
        
        
        # 1. PV to Load = the lower of load or solar generation

        solar_to_load[t] = min(solar[t], load[t])               # df[['Solar',profile]].min(axis=1)
        excess_solar[t] = solar[t] - solar_to_load[t]
        unserved_after_solar[t] = load[t] - solar_to_load[t]
        
        # 2. calculate the BESS energy contribution 
        # chg_limit and dischg_limit are the _AC_ power flow      
        dischg_limit    = min(bess.peak_discharge_rate,             # BESS inverter rating
                              unserved_after_solar[t],              # only discharge enought to serve remaining load
                              (soc_begin[t] - bess.soc_min)         # can only discharge what's stored in the battery; delivered AC power is lower
                              )
        
        chg_limit       = max(bess.peak_charge_rate,                   # BESS inverter rating; stored as a negative value
                              -(bess.soc_max - soc_begin[t]),          # can't over-charge the battery
                              -excess_solar[t]                         # can only charge from whatever excess solar is available
                              )   
        
        # discharging to serve some remaining load
        # bess_chg_dischg is positive (adds energy to the load)
        if unserved_after_solar[t] > 0:
            bess_chg_dischg[t] = dischg_limit                                       # This is the AC power to the load
            bess_chg_dischg_dc[t] = dischg_limit / bess.eta_discharge
            unserved_after_bess[t] = unserved_after_solar[t] - bess_chg_dischg[t]   # 
            soc_end[t] = soc_begin[t] - bess_chg_dischg[t]/(bess.eta_discharge)     # 
        
        # charging, but only from excess solar, never from grid
        else:
            bess_chg_dischg[t] = chg_limit                                          # This is the AC power to the battery
            bess_chg_dischg_dc[t] = chg_limit * bess.eta_charge
            unserved_after_bess[t] = unserved_after_solar[t]
            soc_end[t] = soc_begin[t] - bess_chg_dischg[t]*(bess.eta_charge)        # bess_chg_dischg is negative (draws energy)
        
        
        # 3. after solar and BESS, any unserved load must come from grid      
        grid_import[t] = unserved_after_bess[t]
                
        # 4. Calculate SoC at end of interval
        #soc_end[t] = soc_begin[t] - bess_chg_dischg[t]
        
        
    
    df['solar_to_load'] = solar_to_load
    df['excess_solar'] = excess_solar
    df['unserved_after_solar'] = unserved_after_solar
    df['bess_chg_dischg'] = bess_chg_dischg
    df['bess_chg_dischg_dc'] = bess_chg_dischg_dc
    df['battery_to_load'] = np.clip(bess_chg_dischg,0,10000)
    df['unserved_after_bess'] = unserved_after_bess
    df['grid_import'] = grid_import

    df['soc_begin'] = soc_begin
    df['soc_end'] = soc_end
    df['curtailed'] = curtailed  
    
    return df

def write_metadata_tab(workbook, bess, project_name):
    ''' Create a nicely formatted tab showing the BESS specs'''
    
    # Metadata could be expanded to include other project info
    # eg project location, date the EFD was created, username, etc
    metadata = {"Project Name": project_name}
    
    batt_spec = {"Battery Capacity": (bess.capacity_kwh, "kWh"),
                  "Discharge Power Rating": (bess.peak_discharge_rate,"kW"),
                  "Charge Power Rating": (bess.peak_charge_rate,"kW"),
                  "State of Charge Max": (bess.soc_max, "kWh"),
                  "State of Charge Min": (bess.soc_min, "kWh"),
                  "Initial State of Charge": (bess.initial_soc, "kWh"),
                  "Discharge Efficiency": (bess.eta_discharge, " -"),
                  "Charge Efficiency": (bess.eta_charge, " -")}
    
    # data = {"parameter": list(metadata.keys()) + [attr for attr in dir(bess) if not callable(getattr(bess, attr)) and not attr.startswith("__")],
    #         "value": list(metadata.values()) + [getattr(bess, attr) for attr in dir(bess) if not callable(getattr(bess, attr)) and not attr.startswith("__")],
    #         "units": ['Units','kWh','-','-','kWh','kW','kW','kWh','kWh']}
    
    
    #metadata_df = pd.DataFrame(data)
    #metadata_df.set_index('parameter', inplace=True)
    
    worksheet = workbook.add_worksheet("Battery Specifcations")
    
    # First column: Parameter Names
    parameter_col_fmt = workbook.add_format({"font":styles['font'],
                                            "align":"left",
                                             "valign":"vcenter",
                                            "fg_color":styles['label_gray'],
                                            "text_wrap":True})
    worksheet.set_column(0,0,24)
    worksheet.write_column('A2',batt_spec.keys(),parameter_col_fmt)


    # Second column: Values
    value_col_fmt = workbook.add_format({"font":styles['font'],
                                         "align":"center",
                                         "valign":"vcenter",
                                         "fg_color":styles['white'],
                                         "text_wrap":True})
    values = [v[0] for v in batt_spec.values()]
    worksheet.write_column('B2',values,value_col_fmt)
    
    # Third column: units
    value_col_fmt = workbook.add_format({"font":styles['font'],
                                         "align":"left",
                                         "valign":"vcenter",
                                         "fg_color":styles['white'],
                                         "text_wrap":True})
    units = [v[1] for v in batt_spec.values()]
    worksheet.write_column('C2',units,value_col_fmt)
    
    # First row 
    first_row_fmt = workbook.add_format({"font":styles['font'],
                                         "align":"center",
                                         "bold": True,
                                         "valign":"vcenter",
                                         "fg_color":styles['dark_gray'],
                                         "font_color":styles['white'],
                                         "text_wrap":True})
    
    
    worksheet.merge_range("A1:C1", f"Battery Specification: {project_name}", first_row_fmt)
    worksheet.set_row(0,20)


    return workbook


def write_efd_summary_tab(workbook, df, project_name):
    ''' Write nicely formatted summary of EFD annual sums'''
    print(df)
    
    worksheet = workbook.add_worksheet("EFD Summary Table")
    
    efd_summary_df = pd.DataFrame()
    
    # -------------------------------------------------------------------------
    # Write the header
    big_header_format = workbook.add_format(
        {
            #"bold":1,
            "border":1,
            "align":"center",
            "valign":"vcenter",
            "fg_color":styles['header_green'],
            "font_color":"black",
            "font":styles['font'],
            "font_size":12,
            
        })
    
    worksheet.merge_range(f"A1:G1", 
                          f"{project_name} - Master Load Profile Energy Flow Diagram (Year 1)" ,
                          big_header_format)
    worksheet.set_row(0,40)
    
    # -------------------------------------------------------------------------
    # Column Labels
    column_labels_fmt = workbook.add_format({"border":1,
                                     "align":"center",
                                     "valign":"bottom",
                                     "text_wrap":True,
                                     "fg_color":excel_style['header_light_blue'],
                                     "font": styles['font']})
    column_labels = [' ', 
                     'Total Annual Load\n(kWh)',
                     'Annual Solar Generation\n(kWh)',
                     'Total Solar to Load\n(kWh)',
                     'Total Battery to Load\n(kWh)',
                     'Total Solar Energy Discarded\n(kWh)',
                     'Total Load Unserved\n(kWh)']
    worksheet.write_row(1,0,column_labels, column_labels_fmt)
    worksheet.set_column(1,6,12)
    
    # -------------------------------------------------------------------------
    # Row Labels
    row_labels_fmt = workbook.add_format({"border":1,
                                     "align":"center",
                                     "valign":"bottom",
                                     "text_wrap":True,
                                     "fg_color":"#f2f2f2",
                                     "font": styles['font']})
    row_labels = ['Energy','Percentage of Total Annual Load','Percentage of Annual Solar Generation']
    worksheet.set_column(0,0,16)
    worksheet.set_row(2,30)
    worksheet.set_row(4,30)
    worksheet.write_column(2,0,row_labels, row_labels_fmt)
    
    # -------------------------------------------------------------------------
    # Write data
    kwh_fmt = workbook.add_format({"border":1,
                                   "num_format":"#,##0",
                                    "font":styles['font'],
                                    "align":"center",
                                    "valign":"vcenter",
                                    "fg_color":styles['white']})
    
    first_row = np.array([df['Master'].sum(),
                          df['Solar'].sum(),
                          df['solar_to_load'].sum(),
                          df['battery_to_load'].sum(),
                          df['curtailed'].sum(),
                          df['grid_import'].sum()
                          ])
    
    worksheet.write_row(2,1, first_row, kwh_fmt)
    
    
    pct_fmt = workbook.add_format({"border":1,
                                    "num_format":"###%",
                                    "font":styles['font'],
                                    "align":"center",
                                    "valign":"vcenter",
                                    "fg_color":styles['white']})
    
    small_pct_fmt = workbook.add_format({"border":1,
                                    "num_format":"#.##%",
                                    "font":styles['font'],
                                    "align":"center",
                                    "valign":"vcenter",
                                    "fg_color":styles['white']})
    
    # Second row - normalize by Master kWh
    second_row = first_row/df['Master'].sum()
    worksheet.write_row(3,1, second_row, pct_fmt)
    worksheet.write_row(3,4, second_row[3:5], small_pct_fmt)
    
    # Third row - normalize by solar kWh
    third_row = first_row/df['Solar'].sum()
    worksheet.write_row(4,1, third_row, pct_fmt)
    worksheet.write_row(4,4, third_row[3:5], small_pct_fmt)


    return workbook
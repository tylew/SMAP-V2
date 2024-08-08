import pandas as pd
import numpy as np
import datetime

from smap_package import CONFIG # imported from base/__init__.py

cc_style = CONFIG['styles']
colors = cc_style['plot-colors-dark']

def build_aps(baselineFile, adjustmentFile, critical_array, critical_source, solarFile, solar_source):

    try:
        
        # -----------------------
        # First, built independent timestamp range
        YYYY = int(datetime.datetime.now().year)-1 # deafult to the year before right now
        time_range = pd.date_range(start=f"1/1/{YYYY} 00:00", end=f"12/31/{YYYY} 23:45",freq='15min') #use 2022 to match Example data
        
        
        # ------------------------
        # Baseline
        # if(baseline_source == "UtilityAPI CSV (raw)"):
        #     bf = meter_data_cleaner_gui.runCleaner_returnDF(baselineFile, annual=True, zero=True)
        #     baseline = bf['interval_kWh']     

        # else:
        #     bf = pd.read_excel(baselineFile)
        #     baseline = bf.iloc[:, 1]
        bf = pd.read_excel(baselineFile)
        baseline = bf.iloc[:,1]
        
        try:
            bf = pd.read_excel(baselineFile)
            
            if len(bf) != 35040:
                print(f"Length of Baseline input is not correct. Expected 35,040 rows, found {len(bf)}")
                raise ValueError(f"Length of Baseline input is not correct. Expected 35,040 rows, found {len(bf)}")
            
        except:
            raise ValueError("Error opening Baseline file.")
            
        # ------------------------
        # Adjustment
        if(adjustmentFile is not None):
            af = pd.read_excel(adjustmentFile)
            adjustment = af.iloc[:, 1]

            #35040 values needs to be consistent as one year of data.
            # - need to check on this for leap years
            if len(baseline) != 35040 or len(adjustment) != 35040:

                raise ValueError("Length of columns is incorrect. Baseline:", len(baseline), "Adjustment:", len(adjustment))
        
        
        #If there is no adjustment file, then adjustment is zero values
        else:
            adjustment = np.zeros(len(baseline))
            
            if len(baseline) != 35040:
                raise ValueError("Length of Baseline incorrect. Baseline:", len(baseline))
            
        
        # ------------------------
        # Master
        #   Master profile represents the baseline with the adjustment added
        master = baseline + adjustment
        

        # ------------------------
        # Critical
        #   Create a Critical Load Profile
        if critical_source == "baseline":
            critical = (critical_array/100) * baseline
            
        elif critical_source == "master":
            critical = (critical_array/100) * master
            
        # TODO: Add
        # if critical_source == "2-Column xlsx":
        #     critical = critical_array
        
        
        result_df = pd.DataFrame({'timestamp': time_range, 'Baseline': baseline, 'Adjustment':adjustment, 'Master': master, 'Critical':critical})#, 'Solar':solar})
        result_df = result_df.set_index('timestamp') 
        
        
        
        # ------------------------
        # Solar
        #   Create Solar Generation Profile
        print(solar_source)  
        if(solar_source == '2-column'):    
            solar_df = pd.read_excel(solarFile)
            solar = solar_df.iloc[:, 1]
            
            result_df['Solar'] = solar.to_list()
            
        elif(solar_source == 'helioscope'):
            solar_df = unpack_helio(solarFile)
            solar = solar_df.iloc[:, 1]
            
            result_df['Solar'] = solar.to_list()
            
        #If there is no solar file, then solar is zero values
        else:
            solar = np.zeros(len(baseline))
                
            if len(baseline) != 35040:
                raise ValueError("Length of Baseline incorrect. Baseline:", len(baseline))
        
        # ------------------------
        #     

        
        
        print(" ")
        print(" --- APS df ---")
        print(result_df)
        
        return result_df

    #Error catching
    except FileNotFoundError:
        print("Error: One or both of the input files not found.")
    except KeyError:
        print("Error: One or both of the specified columns not found in the input files.")
    except ValueError as ve:
        print(str(ve))
    except pd.errors.EmptyDataError as ede:
        print(f"Error: The file  is empty or contains no data.\n{ede}")
    except UnicodeDecodeError as e:
        print(f"Error: There was an issue decoding the file .\n{e}")
    except pd.errors.ParserError as pe:
        print(f"Error: There was an issue parsing the file.\n{pe}")
    except Exception as e:
        print(f"Error: An unexpected error occurred while reading the file.\n{e}")

def unpack_helio(helio_file):

    # Read the CSV file into a DataFrame
    df = pd.read_csv(helio_file, parse_dates=['timestamp'], na_values=['', ' ', None, '-', ' -'], keep_default_na=False)

    # Extract the 'timestamp' and 'ac_power' columns
    df = df[['timestamp', 'grid_power']].copy()

    # Fill any remaining missing values with zeros
    df['grid_power'].fillna(0, inplace=True)

    # Set the year to 2018 for all timestamps
    df['timestamp'] = df['timestamp'].apply(lambda x: x.replace(year=2018))

    # Remove commas from numerics
    df['grid_power'] = df['grid_power'].replace({',': ''}, regex=True)
    
    # Divide the 'ac_power' values by 1000
    df['grid_power'] = pd.to_numeric(df['grid_power'], errors='coerce') / 1000

    oggp = df['grid_power'].sum()

    # Set the 'timestamp' column as the index
    df.set_index('timestamp', inplace=True)

    # Create a date range with 15-minute frequency for one entire annual year
    r15min = pd.date_range(start='2018-01-01 00:00:00', end='2018-12-31 23:45:00', freq='15min')

    # Reindex the DataFrame to fill missing timestamps
    df = df.reindex(r15min)
    

    # Forward-fill the 'grid_power' values to propagate the last valid value
    df = df.ffill()
    df = df.fillna(value=0)

    # Calculate the average value for each 15-minute segment
    df['average_power'] = df['grid_power'] / 4

    # Group the data into 15-minute segments and sum the 'average_power' values for each segment
    df['Solar'] = df.groupby(pd.Grouper(freq='15min')).transform('sum')['average_power']

    # Drop the 'average_power' column as it's no longer needed
    df.drop(columns=['average_power'], inplace=True)
    df.drop(columns=['grid_power'], inplace=True)

    #Margin of error calculations
    fgp = df['Solar'].sum()
    errMarg = abs(oggp - fgp)

    # Reset the index to have 'timestamp' as a column again
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'timestamp'}, inplace=True)


    return df

def profile_summary_df(aps_df,profile):
    ''' Generate a dataframe of monthly summary statistics from an annual (8760 or 35,040) APS DataFrame'''
    
    months = ['January','February','March','April','May','June','July','August','September','October','November','December']
    
    summary_df = aps_df.resample('M')[profile].agg(['sum'])#.reset_index()
    summary_df = summary_df.rename(columns={'sum':'Total Monthly Electricity Usage [kWh]'})
     
    summary_df.set_index(pd.Index(range(1,13)),inplace=True)
     
    summary_df["Max Daily Electricity Usage [kWh]"] = aps_df.groupby([aps_df.index.month, aps_df.index.day])[profile].sum().groupby(level=0).max()
    summary_df["Average Daily Electricity Usage [kWh]"] = aps_df.groupby([aps_df.index.month, aps_df.index.day])[profile].sum().groupby(level=0).mean()
    summary_df["Min Daily Electricity Usage [kWh]"] = aps_df.groupby([aps_df.index.month, aps_df.index.day])[profile].sum().groupby(level=0).min()
     
    
    summary_df['Month'] = months
    summary_df.set_index('Month',inplace=True)
    
    # Make the "totals and averages" row
    summary_df.loc["Totals and Averages"] = summary_df.mean().values # averages for Max, Avg, and Min columns
    summary_df.loc['Totals and Averages','Total Monthly Electricity Usage [kWh]'] = summary_df.iloc[:-1,0].sum() # sum for the "Total" column
    
    return summary_df

def aps_write_summary_df_to_excel(workbook, sheet_name, aps_df, graph_selections, project_name):
    
    worksheet = workbook.add_worksheet(sheet_name)
    
    # --------
    # Profile Groups: Total | Max | Avg | Min
    # Subheaders for each APS profile
    
    profile_excel_coords = {0:"C3:F3",
                            1:"G3:J3",
                            2:"K3:N3",
                            3:"O3:R3",
                            4:"S3:V3"}
    
    profile_header_dict = {"bold":      1,
                           "border":    1,
                           "align":     "center",
                           "fg_color":  "white",
                           "font": cc_style['font'],
                           "size": 11}
    
    # Profile Column Labels ("Baseline", "Adjustment", ...)
    profile_col_labels_dict = {"bottom":True,
                               "top":True,
                               "align":"center",
                               "valign":"vcenter",
                               "fg_color":cc_style['label_gray'],
                               "font":cc_style['font'],
                               "size": 10,
                               "text_wrap":True}
   
    profile_col_label_fmt = workbook.add_format(profile_col_labels_dict)
    
    #add right-side vertical bar to separate from the next profile
    profile_col_labels_dict_right = profile_col_labels_dict
    profile_col_labels_dict_right["right"] = True 
    profile_col_label_fmt_right = workbook.add_format(profile_col_labels_dict_right)

    
    
    data_fmt = workbook.add_format({"num_format":"#,##0",
                                    "font":cc_style['font'],
                                    "align":"center",
                                    "valign":"vcenter",
                                    "fg_color":cc_style['light_gray']})
    
    data_fmt_right = workbook.add_format({"num_format":"#,##0",
                                          "right": True,
                                          "font":cc_style['font'],
                                          "align":"center",
                                          "valign":"vcenter",
                                          "fg_color":cc_style['light_gray']})
    
    data_tot_avg_fmt = workbook.add_format({"num_format":"#,##0",
                                            "top":True,
                                            "bottom":True,
                                            "font":cc_style['font'],
                                            "align":"center",
                                            "valign":"vcenter",
                                            "fg_color":cc_style['light_gray']})
    
    data_tot_avg_fmt_right = workbook.add_format({"num_format":"#,##0",
                                                  "top":True,
                                                  "bottom":True,
                                                  "right": True,
                                                  "font":cc_style['font'],
                                                  "align":"center",
                                                  "valign":"vcenter",
                                                  "fg_color":cc_style['light_gray']})
    
    profile_header_formats = []
    for i, profile in enumerate(graph_selections):
        # header, changes color based on profile type
        profile_header_formats.append(workbook.add_format(profile_header_dict))
        profile_header_formats[i].set_fg_color(cc_style['cc_blue'])
        worksheet.merge_range(profile_excel_coords[i], profile, profile_header_formats[i])
        
        # column labels
        worksheet.write(3, 1+(i*4)+1, "Total Electricity Usage [kWh]",profile_col_label_fmt)
        worksheet.write(3, 1+(i*4)+2, "Max Daily Electricity Usage [kWh]",profile_col_label_fmt)
        worksheet.write(3, 1+(i*4)+3, "Avg Daily Electricity Usage [kWh]",profile_col_label_fmt)
        worksheet.write(3, 1+(i*4)+4, "Min Daily Electricity Usage [kWh]",profile_col_label_fmt_right)
        
        summary_df = profile_summary_df(aps_df,profile)
        # print("------------")
        # print(profile)
        # print(summary_df)
        
        # Monthly Data entries
        for c in range(4):
            if c==3:
                worksheet.write(16, (4*i) + c + 2, summary_df.iloc[-1,c], data_tot_avg_fmt_right)
            else:
                worksheet.write(16, (4*i) + c + 2, summary_df.iloc[-1,c], data_tot_avg_fmt)
        
            
            for r, value in enumerate(summary_df.iloc[:-1,c]):
                if c==3:
                    worksheet.write(4+r, (4*i) + c + 2, value, data_fmt_right) # right-most column gets right border
                else:
                    worksheet.write(4+r, (4*i) + c + 2, value, data_fmt) #left 3 cols get NO border

    # Column titles row should be extra tall
    worksheet.set_row(3,70)
        
    # --------
    # Main header spans bottom profle subheaders
    big_header_format = workbook.add_format(
        {
            #"bold":1,
            "border":1,
            "align":"center",
            "valign":"vcenter",
            "fg_color":cc_style['header_green'],
            "font_color":"black",
            "font":cc_style['font'],
            "font_size":12,
            
        })
    
    main_header_right_coord = profile_excel_coords[len(graph_selections)-1].split(":")[1][0] + "2" #right coord of the farthest-right profile header
    worksheet.merge_range(f"B2:{main_header_right_coord}", 
                          f"{project_name}: Total Monthly and Daily Max, Average, and Min Electricity Usage by Profile Type",
                          big_header_format)
    worksheet.set_row(1,20)


    # -------
    # Row labels (left-most column)
    # Set column width
    worksheet.set_column(1,1,10)
    
    # "Totals and Averages" label block
    tot_avg_fmt = workbook.add_format({"border":1,
                                       "align":"center",
                                       "valign":"vcenter",
                                       "font":cc_style['font'],
                                       "text_wrap":True,
                                       "num_format":"0",
                                       "fg_color":cc_style['label_gray']})
    
    worksheet.write(16,1, "Totals & Averages", tot_avg_fmt )
    
    # Month labels
    row_labels_fmt = workbook.add_format({"right":1,
                                         "left":1,
                                         "align":"left",
                                         "fg_color":cc_style['label_gray'],
                                         "font":cc_style['font']})

    row_labels = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    for i, row_label in enumerate(row_labels):
        worksheet.write(4+i, 1, row_label, row_labels_fmt)  # 1 corresponds to column B (0-indexed)
    
    
    # "Month" block
    month_fmt = workbook.add_format({"border":1,
                                     "align":"center",
                                     "valign":"bottom",
                                     "italic": True,
                                     "text_wrap":True,
                                     "fg_color":cc_style['label_gray'],
                                     "font": cc_style["font"]})
    worksheet.merge_range("B3:B4","Month",month_fmt)
    
    return workbook

def profile_summary_df(aps_df,profile):
    ''' Generate a dataframe of monthly summary statistics from an annual (8760 or 35,040) APS DataFrame'''
    
    months = ['January','February','March','April','May','June','July','August','September','October','November','December']
    
    summary_df = aps_df.resample('M')[profile].agg(['sum'])#.reset_index()
    summary_df = summary_df.rename(columns={'sum':'Total Monthly Electricity Usage [kWh]'})
     
    summary_df.set_index(pd.Index(range(1,13)),inplace=True)
     
    summary_df["Max Daily Electricity Usage [kWh]"] = aps_df.groupby([aps_df.index.month, aps_df.index.day])[profile].sum().groupby(level=0).max()
    summary_df["Average Daily Electricity Usage [kWh]"] = aps_df.groupby([aps_df.index.month, aps_df.index.day])[profile].sum().groupby(level=0).mean()
    summary_df["Min Daily Electricity Usage [kWh]"] = aps_df.groupby([aps_df.index.month, aps_df.index.day])[profile].sum().groupby(level=0).min()
     
    
    summary_df['Month'] = months
    summary_df.set_index('Month',inplace=True)
    
    # Make the "totals and averages" row
    summary_df.loc["Totals and Averages"] = summary_df.mean().values # averages for Max, Avg, and Min columns
    summary_df.loc['Totals and Averages','Total Monthly Electricity Usage [kWh]'] = summary_df.iloc[:-1,0].sum() # sum for the "Total" column
    
    return summary_df
"""
SMAP Economic Analysis tool

Provides economic analysis of solar microgrid.
"""

import pandas as pd

def run_ea(csv):
    csv = pd.read_csv(csv, header=None, nrows=110, skip_blank_lines=False)

    #, dtype = {'field':str, 'entry':object},
    #csv = pd.read_csv(csv, header=None, usecols=[0,3], nrows=110, names=['field','entry'], skip_blank_lines=False)


    print("\n--csv--")
    print(csv.head(10))
    print(" ")
    print(csv.iloc[0,0].split(":")[1].rstrip().lstrip())
    print("\n")


    #design_name = pd.read_csv(csv, header=None, usecols=[0], nrows=1).iloc[0,0].split(":")[1].rstrip().lstrip()
    #design_name = pd.read_csv(csv, header=None, usecols=[0], nrows=1).iloc[0,0].split(":")[1].rstrip().lstrip()
    design_name = csv.iloc[0,0].split(":")[1].rstrip().lstrip()
    print("\n----")
    print(f"design_name: {design_name}")
    
    
    #col0 = pd.read_csv(csv, header=None, usecols=[0],  names=['field'], nrows=120, skip_blank_lines=False)
    #col0 = col0.dropna()
    #col0 = csv.dropna()
    col0 = csv
    print("\n--col0--")
    print(col0.head(20))

    col0 = csv.iloc[:,0]                

    print("\n--meta--")
    meta = csv.iloc[2:9,[0,3]]
    print(meta)
    
    print("\n--design summary table")
    design_summary_table = csv.iloc[10:13,0:15]
    print(design_summary_table)
    
    print("\n--Facility")
    facility_pcud = csv.iloc[19:34,[0,3]]
    facility_solar = csv.iloc[19:29,[5,8]]
    facility_ess = csv.iloc[19:28, [10,13]]
    facility_ess = csv.iloc[19:23, [15,18]]
    
    print("\n -- Facility Proj Costs and Utility Data")
    print(facility_pcud)
    
    print("\n -- Facility Solar")
    print(facility_solar)
    
    print("\n -- Facility ESS")
    print(facility_solar)

    # print("\n -- Facility Location")
    # print(facility_location)
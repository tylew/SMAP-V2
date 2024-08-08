from smap_package.src.utils import generalHelpers
import io
import pandas as pd
import numpy as np

def run_socr( 
                aps_file, 
                chg_loss:float=0.3, 
                dischg_loss:float=0.3, 
                include_degradation:bool=True, 
                yura:int=15,
                solar_degrade_rate:float=0.5, 
                bess_degrade_rate:float=2.0):

    # socr_profile_df = None
    # socr_curve_df = None

    aps_df = generalHelpers.df_from_file(aps_file, parse_dates=['timestamp'],index_col= 'timestamp') 
    
    #TODO: add a check for the correct columns

    ## Create socr profile
    socr_profile_df = aps_df.copy()
    socr_profile_df['socr'] = calc_socr(aps_df['Solar'].values, aps_df['Critical'].values, chg_loss, dischg_loss)

## Calculate curves
    critical_points = (np.arange(0,101,1))
    socr_curve_df = pd.DataFrame(index=critical_points)
    socr_curve_df.index.name = "Critical_Pct"
    ### Baseline curve
    socr_curve_df['Max_SOCr_Baseline'] = critical_bess_curve(socr_profile_df['Solar'].values,
                                                            socr_profile_df['Baseline'].values,
                                                            chg_loss, dischg_loss)
    ### Master curve
    socr_curve_df['Max_SOCr_Master'] = critical_bess_curve(socr_profile_df['Solar'].values,
                                                           socr_profile_df['Master'].values, 
                                                           chg_loss, dischg_loss)
    
    # Optionally, include degradation calculations
    if include_degradation:
        solar_degrade_coeff = (1-(solar_degrade_rate))**yura
        degraded_solar = [s*solar_degrade_coeff for s in socr_profile_df['Solar'].values]
        
        bess_degrade_coeff = (1-(bess_degrade_rate))**yura
        
        
        
        socr_curve_df['Max_SOCr_Baseline, incl. degradation'] = critical_bess_curve(degraded_solar, 
                                                                                    socr_profile_df['Master'].values, 
                                                                                    chg_loss, 
                                                                                    dischg_loss)/(bess_degrade_coeff)
        
        socr_curve_df['Max_SOCr_Master, incl. degradation'] = critical_bess_curve(degraded_solar,
                                                                                    socr_profile_df['Master'].values, 
                                                                                    chg_loss, 
                                                                                    dischg_loss)/(bess_degrade_coeff)
    return socr_profile_df, socr_curve_df


def calc_socr(PV:list, T1_profile:list, chg_loss:float, dischg_loss:float)->list:
    '''
    The core process of the SOCr calculation. creates socr values for one set of solar and critical load profiles.

    Parameters
        PV: list
            Behind-the-meter generation at each interval. Used in calculating net load
        t1_profile: list
            Total critical load at each interval. Used in calculating net load
        chg_loss: float
            Charge loss percentage, in the range [0-1]
        dischg_loss: float
            Discharge loss percentage, in the range [0-1]

    Returns
        list: SOCr value for each interval

    '''
    
    
    Zn = [] # Zn will be the required storage energy (SOCr) calculated for each interval
    netgen = PV - T1_profile
    netgen = netgen[::-1] # reverse the netgen list for "reverse time"
    
    for index, _ in enumerate(netgen):
        # if its first iteration then we set to zero 
        # otherwise it's the previous Z value
        if(index == 0):
            lookBack = 0
    
        else:
            lookBack = Zn[-1]
    
        # The energy shortfall or surplus is added to the SOCr at the earlier
        # timestep. In this for loop we are working in "reverse time", so 
        # Zn[i-1] is earlier than Zn[i]
        if(netgen[index] < 0):
            #Energy Shortfall
            #soc = lookBack - netgen[index] * (1 + chg_loss)
            soc = lookBack - netgen[index] * (1 + dischg_loss)
    
        else:
            if((lookBack - netgen[index] * (1 - chg_loss)) < 0):
                #Battery is fully discharged. SOC cannot go below zero
                #print("soc is zero!")
                soc = 0
    
            else:
                #If load < PV, the surplus energy should charge the battery
                #The battery's SOC at the earlier timestep should be lower by the net generation including charge losses.
                soc = lookBack - netgen[index] * (1 - chg_loss)
        Zn.append(soc)
    
    return Zn[::-1]

def critical_bess_curve(solar_profile,critical_profile,chg_loss,dischg_loss,critical_points=None) -> np.array:
    '''
    Critical BESS Curve calculation

    Parameters
        solar_profile
        critical_profile
        chg_loss
        dischg_loss
        critical_points

    Returns
        np.array
    '''
    if critical_points == None:
        critical_points = np.concatenate((np.arange(0,21,1),
                                        np.arange(25,105,5)))
        
    # Get the max SOCr value (i.e., the minimum required BESS size) at each percentage of critical load
    socr_max = []
    for cp in critical_points:
        print(cp)
        socr_max.append(max(calc_socr(solar_profile,
                                        (cp/100)* critical_profile,
                                        chg_loss,
                                        dischg_loss)))
    
    # Interpret to be at each percentage 1%-100%    
    critical_pts_100 = np.arange(0,101,1)
    socr_max_interp = np.interp(critical_pts_100,critical_points,socr_max)
    
    # return a list of socr_max values for each percentage 1%-100%
    # to-do: allow variable output points
    return socr_max_interp




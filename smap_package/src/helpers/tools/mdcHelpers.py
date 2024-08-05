# ---------------------------------------------------------------------
# MDC OLD
# ---------------------------------------------------------------------

import math
import numpy as np
import pandas as pd
import io
pd.options.mode.copy_on_write = True
from pathlib import Path
import datetime
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = "browser"
from plotly.subplots import make_subplots

from smap_package import CONFIG # imported from base/__init__.py

cc_style = CONFIG['styles']
colors = cc_style['plot-colors-dark']

#plotly_config = {'toImageButtonOptions': {'height': None, 'width': None}}
pio.renderers['browser'].config['toImageButtonOptions'] = {'height': None, 'width': None}
pio.renderers['browser'].config['displayLogo'] = False

# Main func
def clean_15min_meter_data(meter_data,annualize,impute_near_zeros:bool,near_zero_threshold:float,):
    #raw_df = smap_helper.df_from_file(meter_data)
    raw_df = raw_utility_api_csv_to_df(meter_data)
    raw_df['interval_start'] = pd.to_datetime(raw_df['interval_start'], format='mixed')

    print("Flagging timepoints for fixing...")

    df_complete = flag_for_fixes(raw_df,impute_near_zeros, near_zero_threshold)
    
    print("Imputing data for flagged timepoints...")
    cleaned_df = impute_flagged_timepoints_indv(df_complete,k_neighbors=6, verbose=False)
    
    if annualize:
        print('Annualizing (force start to Jan 1)...')
        cleaned_df = annualize_last365(cleaned_df,verbose=False)
        
    print("Data Cleaning Completed")
    return cleaned_df

def raw_utility_api_csv_to_df(raw_file):
    print(raw_file)
    
    file_extension = (raw_file.name.split('.')[-1])
    if file_extension == "xlsx":
        raw_df = pd.read_excel(raw_file)
        raw_df.columns = ['interval_start','interval_kWh']
        print(raw_df.head())
        return raw_df
    elif file_extension == "csv":
        raw_df = pd.read_csv(raw_file)
        #raw_df['interval_start'] = pd.to_datetime(raw_df['interval_start'], format='mixed')
        raw_df['interval_start'] = pd.to_datetime(raw_df['interval_start'], format='mixed')
        # raw_df.columns = ['interval_start','interval_kWh']

        #raw_df = raw_df[::-1]

        return raw_df
    else:
        print('"Unrecognized file extension: {file_extension}')

def flag_for_fixes(df_raw,impute_near_zeros=True, near_zero_threshold=0.15):
    print('\n ------ Flag for Fixes ----- \n')
    df_raw = df_raw[['interval_start','interval_kWh']]
    #df_raw = df_raw.set_index('interval_start')
    #print(df_raw)
    
    # Flag duplicates
    df_raw['flag_dupe'] = df_raw.duplicated(subset='interval_start', keep=False)

    # Take the mean of duplicate values
    # note that groupby changes the index to be 'interval_start'
    df_raw = df_raw.groupby('interval_start').mean()

    first = df_raw.index.min()
    last = df_raw.index.max()
    
    #print('\n\n --- df_raw after groupby --- \n')
    #print(df_raw.index)

    # Guess the interval in seconds
    # Note change in index...
    delta_time = df_raw.index.to_series().diff().dt.total_seconds().dropna()
    diff_mode_seconds = delta_time.mode()[0] 
    interval_timedelta = pd.to_timedelta(diff_mode_seconds, unit='s')

    # Develop ideal timestamp range and cast our data unto it
    ideal_range = pd.date_range(start=first, end=last, freq=interval_timedelta)
    df_complete = df_raw.reindex(ideal_range, fill_value=pd.NA)
    
    # add day_of_week column
    df_complete['day_of_week'] = df_complete.index.dayofweek
    
    # used later for filling
    df_complete['ymdhm'] = df_complete.index.strftime('%y-%m-%d %HL:%M') 

    # Flag NA values
    df_complete['flag_na'] = df_complete['interval_kWh'].isna()
    
    # Flag zero values
    df_complete['flag_zero'] = 0
    if impute_near_zeros:
        print(f"  near_zero threshold: {near_zero_threshold}")
        df_complete['flag_zero'] = df_complete['interval_kWh']<= near_zero_threshold

    # Re-cast flag_dupe to be boolean
    # Done here rather than earlier because we get nan in the flag_dupe column where we had missing data
    df_complete['flag_dupe'] = df_complete['flag_dupe'].map({0.0: False, np.nan: False, 1.0: True})

    # "flag to fix" if either nan or dupe or zero
    df_complete['flag_to_fix'] = (df_complete['flag_na'] | df_complete['flag_dupe'] | df_complete['flag_zero'])
    
    return df_complete

def create_flagged_groups(df_complete):
    print('\n ------ Create Flagged Groups ----- \n')
    groups = df_complete[df_complete['flag_to_fix']].groupby((df_complete['flag_to_fix'] != df_complete['flag_to_fix'].shift()).cumsum())
    return groups

def impute_flagged_timepoints(df_complete, groups, k_neighbors, verbose=True):
    print('\n ------ Impute Flagged Timepoints ----- \n')
    k_neighbors = max(2, min(k_neighbors//2 * 2,12)) # k_neighbors should be even, in the range [2,10]
    if verbose: print(f"Imputation buffer is +/- {k_neighbors/2} weeks")
    
    weeks_buffer = list(range(-k_neighbors // 2, 0)) + list(range(1, k_neighbors // 2 + 1))
    
    df_complete['imputation'] = np.nan

    for seq_id, seq_to_fix in groups:    
        if verbose: print(f"\nFixing {seq_to_fix.index.values}")
        
        # "neighbors" is an array which will use to generate the KNN average
        # K = # of columns = length of weeks_buffer (eg K=6 for 3 weeks before, 3 weeks after)
        neighbors = np.full((len(seq_to_fix.index), len(weeks_buffer)), np.nan)
        
        if verbose: print(f'  neighbors.shape: {neighbors.shape}')
        
        # for each column, find the analogous data from df_complete_complete
        for i,week in enumerate(weeks_buffer):
            if verbose: print(f"  seq_to_fix.index: {seq_to_fix.index}")
            
            target_dates = seq_to_fix.index + pd.Timedelta(weeks=week)
            
            target_mdhm_series = pd.Series(target_dates.strftime('%y-%m-%d %HL:%M'))
            matching_rows = df_complete[df_complete['ymdhm'].isin(target_mdhm_series.values)]
            
            if verbose:
                print(f"  matching_rows: {matching_rows['interval_kWh']}")
            
            neighbors[:,i] = matching_rows['interval_kWh']
        
            if verbose:
                print(f"  {matching_rows['interval_kWh'].values} from {matching_rows['interval_kWh'].index.values} ({week} weeks)")
        
        imputation = np.mean(neighbors,axis=1)
        if verbose: print(f"  ----\n  {imputation} imputed for  {seq_to_fix.index.values}")

        df_complete.loc[seq_to_fix.index,'imputation'] = imputation

    # Finally, create the "cleaned_kWh" column. First preference is for the "imputation" column, but otherwise use "interval_kwh"
    df_complete['cleaned_kWh'] = np.where(df_complete['imputation'].notna(), df_complete['imputation'], df_complete['interval_kWh'])

    return df_complete


def impute_flagged_timepoints_indv(df_complete, k_neighbors, verbose=True):
    print('\n ------ Impute Flagged Timepoints ----- \n')
    
    k_neighbors = k_neighbors // 2 * 2
    if verbose: print(f"Imputation buffer is +/- {k_neighbors/2} weeks")
    
    weeks_buffer = list(range(-k_neighbors // 2, 0)) + list(range(1, k_neighbors // 2 + 1))

    x = df_complete.shift(7*96)['interval_kWh'].values
    
    neighbors = np.zeros((len(df_complete),k_neighbors)) # for example, shape = (35040, 6)
    
    for i, week_offset in enumerate(weeks_buffer):
        # pd.Series.shift(periods) shift the data right/down for positive "periods", left/up for negative "periods"
        # thus to look back 3 weeks, we would shift -3 * 7 * 96
        neighbors[:,i] = df_complete.shift(-week_offset*7*96)['interval_kWh'].values
        
        
    df_complete['imputation'] = np.nanmean(neighbors, axis=1)
    
    mask = df_complete['flag_to_fix']
    df_complete.loc[~mask,'imputation'] = np.nan
    
    df_complete['cleaned_kWh'] = df_complete['interval_kWh']
    df_complete.loc[mask, 'cleaned_kWh'] = df_complete.loc[mask, 'imputation']

    return df_complete
    
    


def annualize_last365(cleaned_df, verbose=True):
    ''' Annualize the final 365 days in the time series'''
    
    # This method assume a series with perfect 15-minute interval spacing
    #cleaned_df.reset_index(drop=False, inplace=True)
    
    print('\n ------ Annualize ----- \n')
    
    last_timestamp = cleaned_df.index[-1]
    last_minus1yr = last_timestamp - pd.DateOffset(years=1) + pd.DateOffset(minutes=15)
    
    dow_offset = last_timestamp.day_of_week - last_minus1yr.day_of_week

    df_1yr = cleaned_df.loc[last_minus1yr:]
    
    jan1_df = df_1yr[(df_1yr.index.month == 1) &
                     (df_1yr.index.day == 1) &
                     (df_1yr.index.hour == 0) &
                     (df_1yr.index.minute == 0)]
    jan1_timestamp = jan1_df.index[0]  # take the earlier Jan 1

    mte_first = last_minus1yr + pd.DateOffset(days=(1 + dow_offset))
    mte_last = jan1_timestamp + pd.DateOffset(days=1) - pd.DateOffset(minutes=15)
    
    if verbose: 
        print(f"  Last record:    {last_timestamp}")
        print(f"  Last minus 1yr: {last_minus1yr}")
        print('-- move_to_beginning --')
        print(f"  {jan1_timestamp}")
        print(f"  {mte_last}")
        print('-- move_to_end --')
        print(f"  {mte_first}")
        print(f"  {mte_last}")       
    
    move_to_beginning = df_1yr.loc[jan1_timestamp:,:]
    move_to_end = df_1yr.loc[mte_first: mte_last,:]

    if verbose: 
        print('\n -- Move to beginning --' )
        print(move_to_beginning)
        
        print('\n -- Move to end --' )
        print(move_to_end)
    
    concat_df = pd.concat([move_to_beginning, move_to_end])
    
    # create new "perfect" datetime index
    concat_df.set_index(pd.date_range(start=concat_df.index[0], periods=len(concat_df), freq='15min'), inplace=True)
    
    if verbose:
        print('\n ------ concat_df ----- \n')
        print(concat_df)
    
    return concat_df

def annualize(cleaned_df, verbose=True):

    # This method assume a series with perfect 15-minute interval spacing
    cleaned_df.reset_index(drop=False, inplace=True)

    
    first_timestamp = cleaned_df['index'][0]
    if verbose: print(f"  First record: {first_timestamp}")

    df_1yr = cleaned_df[:35040]
    
    print('\n ------ cleaned_df ----- \n')
    print(df_1yr)
    
    # find january 1
    # start with a DataFrame because we may find multiple Jan 1, 00:00 records
    jan1_df = df_1yr[(df_1yr['index'].dt.month == 1) &
                         (df_1yr['index'].dt.day == 1) &
                         (df_1yr['index'].dt.hour == 0) &
                         (df_1yr['index'].dt.minute == 0)]
    jan1_idx = jan1_df.index[0]  # take the earlier Jan 1
    
    
    print(f'jan1_idx: {jan1_idx}')
    

    
    #print('\n Move to beginning (orig):' )
    move_to_beginning = df_1yr[jan1_idx:]
    
    #print('\n Move to end (orig):' )
    move_to_end = df_1yr.iloc[96:jan1_idx+96]
    
    print('\n ------ concat_df ----- \n')
    concat_df = pd.concat([move_to_beginning, move_to_end])
    print(concat_df)
    
    print(f"start: {concat_df['index'].iloc[0]}")
    
    # create new "perfect" datetime index
    concat_df.set_index(pd.date_range(start=concat_df['index'].iloc[0], periods=len(concat_df), freq='15T'), inplace=True)
    
    concat_df = concat_df.drop(['index'], axis=1)
    
    
    print('\n --- df_1yr --- \n')
    print(concat_df)
    
    return concat_df

def annualize_old(cleaned_df, verbose=True):
    
    # First, cut anything beyond 1 year from our first timestamp
    first_timestamp = cleaned_df.index[0]
    if verbose: print(f"  First record: {first_timestamp}")
    idx_one_year_from_first = first_timestamp + pd.DateOffset(years=1)
    within_one_year = cleaned_df.index < idx_one_year_from_first
    if verbose: print(f"  Ignore records after: {idx_one_year_from_first}")
    
    df_1yr = cleaned_df[within_one_year]
    
    # find january 1
    # start with a DataFrame because we may find multiple Jan 1, 00:00 records
    jan1_df = df_1yr[(df_1yr.index.month==1) & 
                    (df_1yr.index.day==1) & 
                    (df_1yr.index.hour==0) & 
                    (df_1yr.index.minute==0)]
    jan1_idx = jan1_df.index[0] # take the earlier Jan 1
    
    print(f"jan1_idx: {jan1_idx} (dow= {jan1_idx.day_of_week})")
    
    ## move to end
    # we must grab an extra data to get to 365 days
    # thus the data from jan1 is actually repeated as Dec 31
    move_to_end = df_1yr.loc[first_timestamp + pd.DateOffset(days=1):jan1_idx + pd.DateOffset(days=1) - pd.DateOffset(minutes=15),:]
    #move_to_end = df_1yr.loc[:jan1_idx - pd.DateOffset(minutes=15),:]
    
    print('\n Move to end (orig):' )
    print(f'  {move_to_end.index[0]} ({move_to_end.index[0].day_of_week})')
    
    move_to_end.index = move_to_end.index + pd.DateOffset(years=1)
    print('\n Move to end (after offset):' )
    print(f'  {move_to_end.index[0]} ({move_to_end.index[0].day_of_week})')
    
    #print(f'  {move_to_end.index[-1]} ({move_to_end.index[-1].day_of_week})')
    
    
    # print(f"jan1_idx - dateOffset(years=1): {jan1_idx - pd.DateOffset(years=1)} (dow= {.day_of_week})")
    
    # pd.DateOffet automatically handles day-of-the-week issues
    move_to_beginning = df_1yr.loc[jan1_idx:,:]
    
    # print('\n Move to beginning (orig):' )
    # print(f'  {move_to_beginning.index[0]} ({move_to_beginning.index[0].day_of_week})')
    # print(f'  {move_to_beginning.index[-1]} ({move_to_beginning.index[-1].day_of_week})')
    
    # move_to_beginning.index = move_to_beginning.index - pd.DateOffset(years=1)
    
    # print('\n Move to beginning (- pd.DateOffset(years=1)):' )
    # print(f'  {move_to_beginning.index[0]} ({move_to_beginning.index[0].day_of_week})')
    # print(f'  {move_to_beginning.index[-1]} ({move_to_beginning.index[-1].day_of_week})')
    
        
    
    
    jan1_df = pd.concat([move_to_beginning, move_to_end])
    
    
    jan1_df = jan1_df.resample('15T').asfreq()
    
    
    if verbose: 
        print(jan1_df.head(100))
        print(jan1_df.tail(100))
    
    if verbose: print(f" Final range:\n  {jan1_df.index[0]}\n  {jan1_df.index[-1]}")
    
    if verbose: print(f'{len(jan1_df)} days in the jan1_df')
    
    return jan1_df


# ===========================================================================
# Plotting Functions
# ===========================================================================
def full_year_plotly(df,project_name, near_zero_threshold=0, show_weekends=True):
    '''Plots Raw, Imputation, and Cleaned data for the entire time series'''

    fig = make_subplots(specs=[[{'secondary_y': True}]])

    # Find and set y-axis max
    ymax = (df[['interval_kWh','cleaned_kWh']].max()).max()
    ymax = math.ceil(ymax / 20) * 20

    
    # cleaned data
    fig.add_trace(go.Scatter(x=df.index, y=df['cleaned_kWh'], mode='lines', line=dict(color='green', width=4), name='cleaned_kWh'))

    # Imputation data
    fig.add_trace(go.Scatter(x=df.index, y=df['imputation'], mode='lines+markers', line=dict(color='red'), name='Imputed'))
    # na_indices = df_complete[df_complete['flag_na']].index
    # for idx in na_indices:
    #     fig.add_vline(x=idx, line_width=2, line_dash="dash", line_color="red")

    # Original Interval Data
    fig.add_trace(go.Scatter(x=df.index, y=df['interval_kWh'], mode='lines', line=dict(color='blue',width=2), name='Raw Interval'))
    
    
    # Add horizontal line
    fig.add_shape(type="line",
                  x0=df.index[0],
                  y0=near_zero_threshold,
                  x1=df.index[-1],
                  y1=near_zero_threshold,
                  line=dict(color="black", width=1, dash="dash"),
                  row=1,
                  col=1,
                  secondary_y=False)

    
    # Add shaded areas for weekends
    if show_weekends:
        df['weekend'] = np.where((df.index.weekday == 5) | (df.index.weekday == 6), 1, 0 )
        fig.add_trace(go.Scatter(x=df.index, y=df.weekend.values*ymax,
                                fill = 'tonexty', fillcolor = 'rgba(99, 110, 250, 0.2)',
                                line_shape = 'hv', line_color = 'rgba(0,0,0,0)',
                                showlegend = False
                                ),
                    row = 1, col = 1, secondary_y=True)
    
    fig.update_layout(
        font_family=cc_style['font'], title_font_family=cc_style['font'],
        
        title=dict(text=f'Load data at {project_name}', 
                   xanchor='center', x=0.5,
                   font=dict(color='black', size=22)),
        
        xaxis=dict(title=' ', title_font=dict(color='black', size=14),
               tickfont=dict(color='black'),
               range=[df.index[0], df.index[-1]]),
        
        yaxis1=dict(title='Interval Load [kWh]', 
                   title_font=dict(color='black', size=14),
                   tickfont=dict(color='black'),
                   range=[0,ymax],
                   separatethousands= True,),
        yaxis2=dict(range=[0, ymax], showticklabels=False),
        
        legend=dict(yanchor="top", y=-0.1, xanchor="center", x=0.5, title='', traceorder="reversed",
                font=dict(size=12, color='black'),
                orientation="h"),
        
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=100, r=40, t=60, b=40),
        width=800, height=400
        
        )
    return fig

def group_by_month(df, verbose=False):
    month_names = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 
               7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}

    month_group = df['interval_kWh'].groupby([df.index.month, df.index.hour]).mean()
    month_group = month_group.unstack().transpose() # reshape to (12,24)
    
    month_group.columns = [month_names[col] for col in month_group.columns]
    
    if verbose:
        print('\n --- month_group --- \n')
        print(month_group)
    
    return month_group

def month_plotly(month_group,project_name):
    '''plots the average hourly value for each month 
    (12 lines, each with 24 points)'''
    
    fig = go.Figure()

    for col in month_group.columns:
        fig.add_trace(go.Scatter(x=month_group.index, y=month_group[col], mode='lines', name=col))


    fig.update_layout(xaxis=dict(tickmode='array', tickvals=[4, 8, 12, 16, 20, 24]))
    
    fig.update_layout(
        font_family=cc_style['font'], title_font_family=cc_style['font'],
        
        title=dict(text=f'Monthly Load at {project_name}', 
                   xanchor='center', x=0.5,
                   font=dict(color='black', size=22)),
        
        xaxis=dict(title=' ', title_font=dict(color='black', size=14),
               tickfont=dict(color='black'),
               range=[month_group.index[0], month_group.index[-1]]),
        
        yaxis1=dict(title='Mean Hourly Load [kWh]', 
                   title_font=dict(color='black', size=14),
                   tickfont=dict(color='black'),
                   separatethousands= True,),
        
        legend=dict(yanchor="top", y=-0.1, xanchor="center", x=0.5, title='',
                font=dict(size=12, color='black'),
                orientation="h"),
        
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=100, r=40, t=60, b=40),
        width=400, height=400
        
        )

    return fig

def group_by_day_of_week(df, verbose=False):
    day_names = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}

    dow_group = df['interval_kWh'].groupby([df.index.day_of_week, df.index.hour]).mean()
    dow_group = dow_group.unstack().transpose() # reshape to (7,24)
    
    dow_group.columns = [day_names[col] for col in dow_group.columns]
    
    if verbose:
        print('\n --- dow_group --- \n')
        print(dow_group)
    
    return dow_group

def day_of_week_plotly(dow_group, project_name):
    '''plots the average hourly value for each day of the week 
    (7 lines, each with 24 points)'''

    fig = go.Figure()

    for col in dow_group.columns:
        fig.add_trace(go.Scatter(x=dow_group.index, y=dow_group[col], mode='lines', name=col))


    fig.update_layout(xaxis=dict(tickmode='array', tickvals=[4, 8, 12, 16, 20, 24]))
   
    fig.update_layout(
        font_family=cc_style['font'], title_font_family=cc_style['font'],
        
        title=dict(text=f'Day-of-Week Load at {project_name}', 
                   xanchor='center', x=0.5,
                   font=dict(color='black', size=22)),
        
        xaxis=dict(title=' ', title_font=dict(color='black', size=14),
               tickfont=dict(color='black'),
               range=[dow_group.index[0], dow_group.index[-1]]),
        
        yaxis1=dict(title='Mean Hourly Load [kWh]', 
                   title_font=dict(color='black', size=14),
                   tickfont=dict(color='black'),
                   separatethousands= True,),
        
        legend=dict(yanchor="top", y=-0.1, xanchor="center", x=0.5, title='',
                font=dict(size=12, color='black'),
                orientation="h"),
        
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=100, r=40, t=60, b=40),
        width=400, height=400
        
        )
    return fig

# ===========================================================================
# Used for plotting in V1
# ===========================================================================

def group_by_month(df, verbose=False):
    month_names = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 
               7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}

    month_group = df['interval_kWh'].groupby([df.index.month, df.index.hour]).mean()
    month_group = month_group.unstack().transpose() # reshape to (12,24)
    
    month_group.columns = [month_names[col] for col in month_group.columns]
    
    if verbose:
        print('\n --- month_group --- \n')
        print(month_group)
    
    return month_group

def group_by_day_of_week(df, verbose=False):
    day_names = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}

    dow_group = df['interval_kWh'].groupby([df.index.day_of_week, df.index.hour]).mean()
    dow_group = dow_group.unstack().transpose() # reshape to (7,24)
    
    dow_group.columns = [day_names[col] for col in dow_group.columns]
    
    if verbose:
        print('\n --- dow_group --- \n')
        print(dow_group)
    
    return dow_group


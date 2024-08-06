import math
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from smap_package import CONFIG # imported from base/__init__.py

cc_style = CONFIG['styles']
# plot_style = cc_style['plot-colors-dark']


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


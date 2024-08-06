import plotly.graph_objects as go   
import math
from smap_package import CONFIG # imported from base/__init__.py

cc_style = CONFIG['styles']
colors = cc_style['plot-colors-dark']

def socr_graph(socr_df, project_name):
    
    fig = go.Figure()
          
    # Add traces in reverse order so that Baseline shows on top
    fig.add_trace(go.Scatter(x=socr_df.index, y=socr_df['socr'], mode='lines', name='SOCr', line_color=colors['bess']))
    fig.add_trace(go.Scatter(x=socr_df.index, y=socr_df['Solar'], mode='lines', name='Solar', line_color=colors['Solar']))
    fig.add_trace(go.Scatter(x=socr_df.index, y=socr_df['Critical'], mode='lines', name='Critical', line_color=colors['Critical']))
    fig.add_trace(go.Scatter(x=socr_df.index, y=socr_df['Master'], mode='lines', name='Master', line_color=colors['Master']))
    fig.add_trace(go.Scatter(x=socr_df.index, y=socr_df['Adjustment'], mode='lines', name='Adjustment', line_color=colors['Adjustment']))
    fig.add_trace(go.Scatter(x=socr_df.index, y=socr_df['Baseline'], mode='lines', name='Baseline', line_color=colors['Baseline']))
    
    # Add horizontal line for max socr
    fig.add_hline(y=socr_df['socr'].max(),line_width=3, line_dash="dash", line_color=colors['bess'])
    
    fig.update_layout(title='SOCr Profile with Aggregated Profiles',
                      xaxis_title='Date',
                      yaxis_title='Interval Energy [kWh]',
                      width=1100,  
                      height=700,
                      legend={'traceorder':'reversed'})
    

    
    #st.plotly_chart(fig)
    return fig

def socr_bess_size_graph(socr_curve_df, project_name):
    
    fig = go.Figure()
    
    # Baseline
    fig.add_trace(go.Scatter(x=socr_curve_df.index,y=socr_curve_df['Max_SOCr_Baseline'],name='Max SOCr - Baseline'))
    if 'Max_SOCr_Baseline, incl. degradation' in socr_curve_df.columns:
        fig.add_trace(go.Scatter(x=socr_curve_df.index,y=socr_curve_df['Max_SOCr_Baseline, incl. degradation'],name='Max SOCr - Baseline, incl. degradation'))
    
    # Master
    fig.add_trace(go.Scatter(x=socr_curve_df.index,y=socr_curve_df['Max_SOCr_Master'],name='Max SOCr - Master'))
    if 'Max_SOCr_Master, incl. degradation' in socr_curve_df.columns:
        fig.add_trace(go.Scatter(x=socr_curve_df.index,y=socr_curve_df['Max_SOCr_Master, incl. degradation'],name='Max SOCr - Master, incl. degradation'))
    
    # round up the nearest integer multiple of 500kWh
    # add 200 to ensure the horizontal line shows
    ymax = math.ceil(max(socr_curve_df.iloc[14,:])/500) * 500 + 251
    print(ymax)
    
    
    leg_ypos = (ymax+50)/ymax
    
    fig.update_layout(title='SOCr BESS Sizing',
                      xaxis_title='Critical Load Percentage',
                      yaxis_title='SOCr [kWh]',
                      width=1100,  
                      height=700,
                      xaxis=dict(range=[0, 20]),
                      yaxis=dict(range=[0,ymax]))
    
    fig.update_layout(
        font_family="Arial", title_font_family="Arial",
        
        title=dict(text=f'SOCr Curves: {project_name}', 
                   xanchor='center', x=0.5,
                   font=dict(color='black', size=22)),
            
        xaxis=dict(title='Load Percentage Served', title_font=dict(color='black', size=14),
               tickfont=dict(color='black')),
        xaxis_ticksuffix="%",
        
        yaxis=dict(title='BESS Capacity [kWh]', 
                   title_font=dict(color='black', size=14),
                   tickfont=dict(color='black')),
        yaxis_ticksuffix=" kWh",
        
        
        # legend=dict(yanchor="top",y=leg_ypos,xanchor="left",x=-0.07, title='',traceorder="reversed",
        #             font=dict(size=12,color='black')),
        #legend_bgcolor ='lightgray',
        
        legend=dict(yanchor="top",y=-0.14,xanchor="center",x=0.5, title='',orientation='h',
                    font=dict(size=12,color='black')),
        
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=80, r=40, t=80, b=80),
        width=1200, height=600
        
        )
    fig.update_layout(legend_orientation='h')
    
    fig.update_layout(hovermode='x unified')

    return fig
    
def degraded_socr_bess_size_graph(socr_curve_df,degraded_socr_curve_df,yura):
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=socr_curve_df['Critical_Pct'],y=socr_curve_df['Max_SOCr_Baseline'],name='Max SOCr - Baseline'))
    fig.add_trace(go.Scatter(x=socr_curve_df['Critical_Pct'],y=socr_curve_df['Max_SOCr_Master'],name='Max SOCr - Master'))
    
    fig.add_trace(go.Scatter(x=degraded_socr_curve_df['Critical_Pct'],y=degraded_socr_curve_df['Max_SOCr_Baseline'],name=f"Max SOCr - Baseline - Year {yura}"))
    fig.add_trace(go.Scatter(x=degraded_socr_curve_df['Critical_Pct'],y=degraded_socr_curve_df['Max_SOCr_Master'],name=f"Max SOCr - Master - Incl. Year {yura}"))
    
    # Add horizontal line for 1MWh
    fig.add_hline(y=1000,line_width=3, line_dash="dash", line_color='white')
    fig.add_annotation(text="1 MWh", xref="x", yref="y", x=2, y=1050, showarrow=False, font=dict(size=16))#,color=colors['bess']))
    
    # Add horizontal line for 2MWh
    fig.add_hline(y=2000,line_width=3, line_dash="dash", line_color='white')
    fig.add_annotation(text="2 MWh", xref="x", yref="y", x=2, y=2050, showarrow=False, font=dict(size=16))#,color=colors['bess']))
    
    fig.update_layout(title='SOCr BESS Sizing',
                      xaxis_title='Critical Load Percentage',
                      yaxis_title='SOCr [kWh]',
                      width=1100,  
                      height=700,
                      xaxis=dict(range=[0, 25]),
                      yaxis=dict(range=[0,2500]))
    
    fig.update_layout(hovermode='x unified')

    return fig
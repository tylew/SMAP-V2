import plotly.graph_objects as go

from smap_package import CONFIG # imported from base/__init__.py

styles = CONFIG['styles']
plot_style = styles['plot-colors-dark']

def efd_stacked_bar_1d(df,profile,project_name,bess):
    # Group by the new 'date' column and sum the values for each day
    df = df.copy()
    df['date'] = df.index.date  # Create a new column with the date
    df = df.groupby('date').sum()
    
    ymax = max(df[profile])*1.3
    
    #----------------------
    # Plotly Code

    fig = go.Figure()
    
    fig.add_trace(go.Bar(x=df.index, y=df['solar_to_load'],  name='Solar to Load',      marker_color=plot_style['Solar']))
    fig.add_trace(go.Bar(x=df.index, y=df['battery_to_load'],name='Battery to Load',    marker_color=plot_style['bess_to_load']))
    fig.add_trace(go.Bar(x=df.index, y=df['grid_import'],    name='Grid/Generator',marker_color=plot_style['grid_import']))
    #fig.add_trace(go.Bar(x=df.index, y=df['excess_solar'],    name='Grid Export',       marker_color=plot_style['grid_export']))
    fig.add_trace(go.Scatter(x=df.index, y=df['excess_solar'], mode='lines', name="Grid Export/Curtailed", line=dict(color=plot_style['grid_export'], width=2)))
    #fig.add_trace(go.Scatter(x=df.index, y=df[profile], mode='lines', name=profile, line=dict(color=plot_style[profile], width=2)))
    
    fig.update_layout(barmode='stack',bargap=0)
    
    fig.update_layout(
        font_family=styles['font'], title_font_family=styles['font'],
        
        #title=dict(text=f'Energy Flow Diagram: {project_name}<br><sup>{profile} Load Profile, {bess.capacity_kwh} kWh/{bess.peak_discharge_rate} kW BESS</sup>',
        title=dict(text=f'Energy Flow Diagram<br><sup>{profile} Load Profile, {bess.capacity_kwh} kWh/{bess.peak_discharge_rate} kW BESS</sup>',  
                   xanchor='center', x=0.5,
                   font=dict(color='black', size=22)),
        
        xaxis=dict(title=' ', title_font=dict(color='black', size=14),
                tickfont=dict(color='black')),
        
        yaxis=dict(title='Energy [kWh]', 
                   title_font=dict(color='black', size=14),
                   tickfont=dict(color='black'),
                   range=[0,ymax],
                   separatethousands= True,),
        
        legend=dict(yanchor="top",y=-0.1,xanchor="center",x=0.5, title='',traceorder="reversed",
                    font=dict(size=12,color='black')),
        
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=100, r=40, t=60, b=40),
        width=1200, height=600
        
        )
    
    fig.update_layout(legend_traceorder="reversed")
    fig.update_layout(legend_orientation='h')

    fig.update_xaxes(
        dtick='M1',
        tickformat='%b %d',
        tickmode='auto',ticklen=5)
    
    return fig

    # st.plotly_chart(fig)
    
    # image_bytes = fig.to_image(format="png")
    # image = Image.open(io.BytesIO(image_bytes))
  
    # return image


def efd_load_shed_1d(df, project_name):
    
    ix = df['Critical'].idxmax()
    ix_date = ix
    critical_ix= df.loc[ix,'Critical']
    master_ix = df.loc[ix,'Master']
    loadshed_ix = master_ix - critical_ix
    

    ymax = master_ix*1.3

    fig = go.Figure()

    # Add the "M" bar
    fig.add_trace(go.Bar(x=['Master'], y=[master_ix], name='Master', marker_color=plot_style['Master'], showlegend=False))

    # Add the stacked bar for "C" and "T"
    fig.add_trace(go.Bar(x=['Critical'], y=[critical_ix], name='Critical', marker_color=plot_style['Critical'], showlegend=False))
    fig.add_trace(go.Bar(x=['Load Shed'], y=[loadshed_ix], name='Load Shed', base=[critical_ix], marker_color="#7f7f7f", showlegend=False))

    # Customize the layout
    fig.update_layout(title='Load Shed Required at Max Critical Load',
                      xaxis_title='',
                      yaxis_title='Daily Energy [kWh]',
                      barmode='stack')
    
    
    fig.update_layout(
        font_family=styles['font'], title_font_family=styles['font'],
        
        title=dict(text=f'Load Shed Requirement: {project_name}<br><sup><i>Day of Max Critical Load</i></sup>', 
                   xanchor='center', x=0.5,
                   font=dict(color='black', size=22)),
        
        xaxis=dict(title=' ', title_font=dict(color='black', size=14),
               tickfont=dict(color='black')),
        
        yaxis=dict(title='Daily Energy Sum [kWh]', 
                   title_font=dict(color='black', size=14),
                   tickfont=dict(color='black'),
                   range=[0,ymax],
                   separatethousands= True,),
        
        # legend=dict(yanchor="top",y=-0.1,xanchor="center",x=0.5, title='',traceorder="reversed",
        #             font=dict(size=12,color='black')),
        
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=100, r=40, t=60, b=40),
        width=800, height=400
        
        )
    
    return fig, ix_date, master_ix, critical_ix, loadshed_ix
    

def efd_graph_15min(df,profile,project_name):   
    # colors = {"Baseline": "#0099C6",
    #           "Adjustment": "#109618",
    #           "Master": "#3366CC",
    #           "Critical": "#DC3912",
    #           "Solar": "#FF9900",
    #           "bess": "#990099",
    #           "curtailed":"#8C564B",
    #           "grid_import":"#E377C2"}    
    
    fig = go.Figure()
          
    # Add traces in reverse order so that Baseline shows on top
    
    fig.add_trace(go.Scatter(x=df.index, y=df[profile],                 mode='lines', name=profile,                 line=dict(color=plot_style[profile], width=8)))
    #fig.add_trace(go.Scatter(x=df.index, y=df['Solar'],                 mode='lines', name='Solar',                 line=dict(color=colors['Solar'], dash='dash')))
    fig.add_trace(go.Scatter(x=df.index, y=df['solar_to_load'],         mode='lines', name='Solar to Load',         line_color=plot_style['Solar']))
    #fig.add_trace(go.Scatter(x=df.index, y=df['excess_solar'],          mode='lines', name='Excess Solar',          line_color='orange'))
    #fig.add_trace(go.Scatter(x=df.index, y=df['unserved_after_solar'],  mode='lines', name='Unserved After Solar',  line_color='blue'))
    #fig.add_trace(go.Scatter(x=df.index, y=df['battery_to_load'],       mode='lines', name='Battery to Load',       line_color=colors['bess']))
    #fig.add_trace(go.Scatter(x=df.index, y=df['bess_chg_dischg'],       mode='lines', name='bess_chg_dischg',       line_color=colors['bess']))
    #fig.add_trace(go.Scatter(x=df.index, y=df['soc_begin'],             mode='lines', name='soc_begin',             line_color=colors['bess']))
    #fig.add_trace(go.Scatter(x=df.index, y=df['unserved_after_bess'],   mode='lines', name='Unserved After BESS',   line_color='green'))
    fig.add_trace(go.Scatter(x=df.index, y=df['grid_import'],           mode='lines', name='grid_import',           line_color='red'))
    
    
    fig.update_layout(title=f"Energy Flow Diagram - {project_name} - 15 minute Resolution<br>Profile: {profile}",
                      xaxis_title='Date',
                      yaxis_title='15min Interval Energy [kWh]',
                      width=1000,  
                      height=700,
                      legend={'traceorder':'reversed'},
                      plot_bgcolor='white',
                      paper_bgcolor='white')

    return fig


def efd_graph_1d(df,profile,project_name):

    # Group by the new 'date' column and sum the values for each day
    df = df.copy()
    df['date'] = df.index.date  # Create a new column with the date
    df = df.groupby('date').sum()
    
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df.index, y=df[profile],                 mode='lines', name=profile,                 line=dict(color="blue", width=8)))
    #fig.add_trace(go.Scatter(x=df.index, y=df['Solar'],                 mode='lines', name='Solar',                line=dict(color=colors['Solar'], dash='dash')))
    fig.add_trace(go.Scatter(x=df.index, y=df['solar_to_load'],         mode='lines', name='Solar to Load',         line_color=plot_style['Solar']))
    #fig.add_trace(go.Scatter(x=df.index, y=df['excess_solar'],          mode='lines', name='Excess Solar',          line_color='orange'))
    #fig.add_trace(go.Scatter(x=df.index, y=df['unserved_after_solar'],  mode='lines', name='Unserved After Solar',  line_color='blue'))
    fig.add_trace(go.Scatter(x=df.index, y=df['battery_to_load'],       mode='lines', name='Battery to Load',       line_color=plot_style['bess']))
    #fig.add_trace(go.Scatter(x=df.index, y=df['bess_chg_dischg'],       mode='lines', name='bess_chg_dischg',       line_color=colors['bess']))
    #fig.add_trace(go.Scatter(x=df.index, y=df['soc_begin'],             mode='lines', name='soc_begin',             line_color=colors['bess']))
    #fig.add_trace(go.Scatter(x=df.index, y=df['unserved_after_bess'],   mode='lines', name='Unserved After BESS',   line_color='green'))
    fig.add_trace(go.Scatter(x=df.index, y=df['grid_import'],           mode='lines', name='grid_import',           line_color='red'))
    

    fig.update_layout(
        font_family = "Cambria",
        title_font_family = "Cambria",
        
        title=dict(text='Your Title', font=dict(color='black', size=12)),
        xaxis=dict(title='X-axis Label', title_font=dict(color='black', size=14),
               tickfont=dict(color='black')),
        yaxis=dict(title='Y-axis Label', title_font=dict(color='black', size=14),
               tickfont=dict(color='black')),
        legend=dict(x=0.1,y=1.1, orientation='h'),
        legend_title_font_color='black',
        legend_font_color = 'black',
        plot_bgcolor='white',
        paper_bgcolor='white'
        )
    
    return fig
    

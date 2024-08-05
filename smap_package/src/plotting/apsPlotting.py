
import plotly.graph_objects as go
import pandas as pd

from smap_package import CONFIG # imported from base/__init__.py

cc_style = CONFIG['styles']
colors = cc_style['plot-colors-dark']


def monthly_bars_plotly(df_monthly,graph_selections,project_name):
 
    
    month_labels = ["Jan",'Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    
    df = df_monthly.copy()
    
    if 'Master' in df.columns.tolist():
        default_selections = ['Master','Solar']
    
    #graph_selections_unordered = st.multiselect('Select data to display', df.columns.tolist(), default = default_selections)
    #graph_selections = [column for column in df.columns.tolist() if column in graph_selections_unordered] # force plotting in same order

    df = df[graph_selections]
    df = df.resample('M').sum()
    
    if not df.empty:  # Check if DataFrame is empty
        ymax = df.max().max()*1.2
        fixed_width = 0.15
        
        fig = go.Figure()

        for i, column_name in enumerate(df.columns):
            fig.add_trace(go.Bar(x=month_labels,y=df[column_name],name=column_name, marker_color=colors[column_name],
                                 width=fixed_width))
        
        #fig.update_layout(bargroupgap=0.1)  # adds small gap between bars within each group

        
        fig.update_layout(
           font_family=cc_style['font'], title_font_family=cc_style['font'],
           
           title=dict(text=f'Monthly Energy Consumption at {project_name}', 
                      xanchor='center', x=0.5,
                      font=dict(color='black', size=22)),
           
           xaxis=dict(title=' ', title_font=dict(color='black', size=14),
                  tickfont=dict(color='black')),
           
           yaxis=dict(title='Monthly Energy [kWh]', 
                      title_font=dict(color='black', size=14),
                      tickfont=dict(color='black'),
                      range=[0,ymax]),
           
           legend=dict(yanchor="top",y=-0.1,xanchor="center",x=0.5, title='',orientation='h',
                       font=dict(size=12,color='black')),
           
           plot_bgcolor='white', paper_bgcolor='white',
           margin=dict(l=80, r=40, t=60, b=40),
           width=1200, height=600
           
           )
        
        fig.update_xaxes(
            #dtick='M1',
            tickformat='%b',
            tickmode='auto',ticklen=5)

        #st.plotly_chart(fig)

    return fig #, graph_selections
    
def daily_sum_plotly(df,graph_selections,project_name):
    
    #print(graph_selections)
    
    if graph_selections==None:
        graph_selections = ['Baseline','Adjustment','Master','Critical','Solar']
        
    df_daily = df.groupby(pd.Grouper(freq='D')).sum()
    
    fig = go.Figure()

    for column in graph_selections:
        fig.add_trace(go.Scatter(x=df_daily.index, y=df_daily[column], mode='lines', name=column, line_color=colors[column]))

    
    fig.update_layout(
       font_family=cc_style['font'], title_font_family=cc_style['font'],
       
       title=dict(text=f'Daily Energy Consumption at {project_name}', 
                  xanchor='center', x=0.5,
                  font=dict(color='black', size=22)),
       
       xaxis=dict(title=' ', title_font=dict(color='black', size=14),
              tickfont=dict(color='black'),
              tickmode='auto',ticklen=5),
       
       yaxis=dict(title='Daily Energy [kWh]', 
                  title_font=dict(color='black', size=14),
                  tickfont=dict(color='black')),
       
       legend=dict(yanchor="top",y=-0.1,xanchor="center",x=0.5, title='',orientation='h',
                   font=dict(size=12,color='black')),
       
       plot_bgcolor='white', paper_bgcolor='white',
       margin=dict(l=80, r=40, t=60, b=40),
       width=1200, height=600
       
       )

    #st.plotly_chart(fig)
    return fig


#Creates a graph of the sums of each column
# def monthly_bars_mpl(df_monthly, project_name):
    
#     st.subheader("Monthly Sums Graph")

#     # Make a copy so on reupdate theres no problems
#     df = df_monthly.copy()

#     #df.set_index(index, inplace=True)
    
#     if 'Master' in df.columns.tolist():
#         default_selections = ['Master','Solar']
    
#     graph_selections_unordered = st.multiselect('Select data to display', df.columns.tolist(), default = default_selections)
#     graph_selections = [column for column in df.columns.tolist() if column in graph_selections_unordered] # force plotting in same order
    
#     df = df[graph_selections]

#     df = df.resample('M').sum()
#     if not df.empty:  # Check if DataFrame is empty
#         fig, ax = plt.subplots(figsize=(12, 6))
        
#         # Get the month names from the timestamp index
#         months = df.index.strftime('%B')
#         x = np.arange(len(months))  # Create an array for x-axis positions
        
#         # Calculate the width of each bar group
#         if(df.shape[1] > 0):
#             #df.shape gets the num columns
#             bar_width = 0.8 / df.shape[1]
#         else:
#             #Don't divide by zero
#             bar_width = 0

#         # Loop through selected columns and plot with proper color
#         for i, column_name in enumerate(df.columns):
#             color = colors[column_name]
#             ax.bar(x + i * bar_width, df[column_name], width=bar_width, color=color, label=column_name)
            
#         #ax.set_xlabel('Month')
#         #ax.set_ylabel(yAxisName(graph_selections))
#         ax.set_ylabel(graph_selections)
#         ax.set_title(f'{project_name}: Monthly Data Comparison')
#         ax.set_xticks(x + (len(df.columns) - 1) * bar_width / 2)  # Position x-axis ticks at the center of bar groups
#         ax.set_xticklabels(months)
#         ax.legend()  # Show legend with column names

#         # Format y-axis labels with commas
#         ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: format(int(x), ',')))

#         st.pyplot(fig)

# def daily_sum_chart_mpl(df,project_name):
#     ''' Generate a "Load and Solar Daily Line Chart"", which shows the total daily energy for 365 days of the year'''
    
#     st.subheader("Daily Sums Line Chart")
    
#     # First we must groupby date 
#     df_daily = df.groupby(pd.Grouper(freq='D')).sum()
    
#     # Plot for each day of the year
#     fig, ax = plt.subplots(figsize=(14,6))

#     for column in df_daily.columns:
#         print(column)
#         plt.plot(df_daily.index, df_daily[column], label=column, color=colors[column])

#     # Customize the plot
#     plt.title(f"{project_name}: Load and Solar Daily Line Chart")
#     plt.xlabel('Date')
#     plt.ylabel('kWh/day')
#     plt.legend(loc='upper center',ncol=5,bbox_to_anchor=(0.5, 1.0))

#     ax.grid()
#     #ax.set_facecolor((0.83, 0.83, 0.83))

#     st.pyplot(fig)
        

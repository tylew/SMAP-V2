import streamlit as st
import uuid
from datetime import datetime

def already_uploaded_widget(file, no_name_label='Using cached file.'):
    if hasattr(file,'name'):
        st.info(f"{file.name}")
    else:
        st.info(no_name_label)
    if st.button('upload new file', key=str(uuid.uuid4())):
        file = None
        st.rerun()

def st_aps_gui():
    # Main area
    if st.session_state.smap_client.aps.is_complete():
        st_aps_main_area()
    else:
        page_data = st.session_state.page_data[2]
        instructions = page_data['instructions']
        st.markdown(f'> {instructions}')
    
    with st.sidebar:
        st_aps_sidebar()

def st_aps_sidebar():
    # Ref client
    smap_client = st.session_state.smap_client

    # Baseline
    st.markdown("## 1. Baseline Load")

    if smap_client.baseline_load_profile is None:
        st.caption("_Must be 2-Column xlsx, first tab_")
        smap_client.baseline_load_profile = st.file_uploader("Upload Baseline Profile Here")
    else:
        if hasattr(smap_client.baseline_load_profile,'name'):
            st.info(f"{smap_client.baseline_load_profile.name}")
        else:
            st.info("Using stored baseline load file from previous meter data cleaning run.")
        if st.button('upload new file', key='b1'):
            smap_client.baseline_load_profile = None
            st.rerun()

    # Adjustment
    st.markdown("## 2. Adjustment Load")
    smap_client.aps.adjustment_load_source = st.radio("**Adjustment Load Profile** from...",["None","2-Column xlsx"])
    
    if smap_client.aps.adjustment_load_source == "2-Column xlsx":
        if smap_client.aps.adjustment_load_profile is None:
            st.caption("_Must be 2-Column xlsx, first tab_")
            smap_client.aps.adjustment_load_profile = st.file_uploader("Upload Adjustment Profile Here", type=['.xlsx'])
        else:
            st.info(f'{smap_client.aps.adjustment_load_profile.name}')
            if st.button('upload new file', key='b2'):
                smap_client.aps.adjustment_load_profile = None
                
    # Critical Load Profile
    st.markdown("## 3. Critical Load")

    critical_source = st.radio("**Critical Load Profile** from...",["Percent of Baseline","Percent of Master"]) #,"2-Column xlsx"])
    
    if critical_source == "Percent of Baseline":
        smap_client.aps.critical_load_source = 'baseline'
        smap_client.critical_load_percentage = st.number_input("Enter Critical Load Percentage (of Baseline)", min_value=1.0, max_value=100.0, value = 10.0, step=1.0)
        
    if critical_source == "Percent of Master":
        smap_client.aps.adjustment_load_source = 'master'
        smap_client.critical_load_percentage = st.number_input("Enter Critical Load Percentage (of Master)", min_value=1.0, max_value=100.0, value = 10.0, step=1.0)

    # TODO: LOOK AT THIS OPTION
    ''' # Removed for time being....
    if critical_source == "2-Column xlsx":
        critical_file = st.file_uploader("Upload Critical Profile Here")
        critical_is_file = True
        # critical_array = read_critical_file(critical_file)
    '''   
        
    # ------------------------
    # Solar Generation Profile
    st.markdown("## 4. Solar Generation")
    #solar_file = st.file_uploader("Upload Solar Profile Here")
    
    solar_source = st.radio("**Solar Generation Profile** from...",["None","HelioScope CSV","2-Column xlsx"])
    if solar_source == "None":
        smap_client.aps.solar_generation_source = 'none'
    else:
        if smap_client.aps.solar_generation_profile is not None:
            already_uploaded_widget(smap_client.aps.solar_generation_profile)
        elif solar_source == "HelioScope CSV":
            smap_client.aps.solar_generation_source = 'helioscope'
            smap_client.aps.solar_generation_profile = st.file_uploader("Upload HelioScope CSV file here")    
        elif solar_source == "2-Column xlsx":
            smap_client.aps.solar_generation_source = '2-column'
            smap_client.aps.solar_generation_profile = st.file_uploader("Upload Solar Generation Profile Here")
    
    st.markdown('---')
    run_buttom = st.container()
    notify_area = st.empty()
    if run_buttom.button("Create APS"):
        # smap_client.mdc.reset()
        # st.rerun()
        try:
            notify_area.info("Running...")
            
            smap_client.aps.run()
            
            notify_area = st.empty()
            st.rerun()
        except Exception as e:
            notify_area.error(f'Error: {e}')
                        
def st_aps_main_area():
    # Ref client
    smap_client = st.session_state.smap_client

    download_container = st.container()
    dataframe_container = st.container()
    plots_container = st.container()

    plots_container.markdown('## Data visualization:')
    def callback_set_graph_selections():
        smap_client.aps.graph_selections = st.session_state.aps_graph_selections
        smap_client.aps.generate_monthly_bars_plotly()
        smap_client.aps.generate_daily_sum_plotly()

    plots_container.multiselect('Select data to display', 
                    smap_client.aps.aggregated_profile_df.columns.tolist(), 
                    default = smap_client.aps.graph_selections,
                    on_change=callback_set_graph_selections,
                    key='aps_graph_selections')


    # graph_selections = [column for column in st.session_state['aps_df'].columns.tolist() if column in graph_selections_unordered] # force plotting in same order


    # Monthly Bars Plot
    plots_container.markdown("**Monthly Sums Graph**")
    # fig_monthly_bars = monthly_bars_plotly(st.session_state['aps_df'], graph_selections, project_name=st.session_state['project_name'])
    # st.plotly_chart(fig_monthly_bars)
    plots_container.plotly_chart(smap_client.aps.monthly_plotly)
    
    # Daily Sums Line Chart
    plots_container.markdown("**Daily Sums Line Chart**")
    # fig_daily_sums = daily_sum_plotly(st.session_state['aps_df'],graph_selections,project_name=st.session_state['project_name'])
    plots_container.plotly_chart(smap_client.aps.daily_plotly)
    
    # st.session_state['aps_xlsx'] = aps_to_excel(graph_selections)
    download_container.markdown('## Output:')
    date = datetime.now().strftime('%d %B %Y')
    filename = f'{smap_client.project_name} (SMAP - Aggregated Profile Spreadsheet - {date}).xlsx'
    download_container.download_button(
        label="Download Aggregated Profile Spreadsheet as XLSX file",
        data = smap_client.aps.aggregated_profile_spreadsheet,
        file_name=filename,
        mime="application/vnd.ms-excel",
        type='primary')
    download_container.write(f'Filename: `{filename}`')

    dataframe_container.dataframe(smap_client.aps.monthly_summary_df,use_container_width=True,height=500)
    





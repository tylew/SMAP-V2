import streamlit as st
import datetime

def st_mdc_gui():

    mdc_init_st_state()

    with st.sidebar:
        st_mdc_sidebar()

    if st.session_state.smap_client.mdc.is_complete():
        st_mdc_main_area()

    else:
        page_data = st.session_state.page_data[1]
        instructions = page_data['instructions']
        st.markdown(f'> {instructions}')

def mdc_init_st_state():
    smap_client = st.session_state.smap_client
    # if 'full_year_plot' not in st.session_state:
    st.session_state.full_year_plot = smap_client.mdc.full_year_plotly
    
def st_mdc_main_area():
    smap_client = st.session_state.smap_client
    
    st.markdown("### Output:")

    date = datetime.datetime.now().strftime('%d %B %Y')
    filename = f'{smap_client.project_name} (SMAP - Baseline Load Profile - {date}).xlsx'
    st.download_button(
        label="Download Baseline Load Profile as XLSX file",
        data=smap_client.baseline_load_profile,
        file_name=filename,
        mime='text/csv',
    )
    st.write(f'Filename: `{filename}`')

    # st.markdown("### Data visualizations:")
    if st.session_state.full_year_plot is not None:
        st.write("   Full year plot:")
        st.plotly_chart(st.session_state.full_year_plot, use_container_width=True)

    col1, col2 = st.columns([0.49,0.49])

    col1.write("   Monthly plot:")
    col1.plotly_chart(smap_client.mdc.month_plotly, use_container_width=True)

    col2.write("   Day-of-week plot:")
    col2.plotly_chart(smap_client.mdc.day_of_week_plotly, use_container_width=True)

def st_mdc_sidebar():
    # Ref client
    smap_client = st.session_state.smap_client

    st.markdown('## 1. File Upload')
    filearea = st.container()
    if smap_client.mdc.raw_meter_data is None:
        smap_client.mdc.raw_meter_data = filearea.file_uploader('''Upload uncleaned file here (UtilityAPI csv or two-column xlsx)''')
        
    else:
        filearea.info(f'{smap_client.mdc.raw_meter_data.name}')
        if filearea.button('upload new file', key='b1'):
            smap_client.mdc.raw_meter_data = None
            st.rerun()

    st.markdown('## 2. Settings')
    smap_client.mdc.annualize = st.toggle("Annualize (Jan 1 - Dec 31)")

    fix_near_values = st.toggle("Fix Near-Zero Values")
    if fix_near_values:
        threshold = st.number_input("Near-Zero Threshold [kWh/interval]", min_value=0.0, max_value=10.0, value=0.0, step=0.05)
        smap_client.mdc.fix_near_values = True
        smap_client.mdc.near_value_threshold = round(threshold,2)
    else: 
        smap_client.mdc.fix_near_values = False
    
    run_buttom = st.container()
    notify_area = st.empty()
    if run_buttom.button("Clean Data"):
        # smap_client.mdc.reset()
        # st.rerun()
        try:
            notify_area.info("Removing time discrepancies")
            
            smap_client.mdc.run()
            # st.session_state['full_year_plot'] = smap_client.mdc.full_year_plotly
            notify_area = st.empty()
            st.rerun()
        except Exception as e:
            notify_area.error(f'Error: {e}')

    # if st.button("reset"):
    #     smap_client.mdc.reset()
    #     st.rerun()
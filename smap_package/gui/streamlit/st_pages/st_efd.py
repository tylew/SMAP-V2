import streamlit as st
from smap_package.src.utils.BESS import BESS
from smap_package.src.efd.efdPlotting import efd_load_shed_1d
import uuid

import io
import pandas as pd

from datetime import datetime, timezone, timedelta

def already_uploaded_widget(file, file_but_no_name_label='Using cached file.'):
    if hasattr(file,'name'):
        st.info(f"{file.name}")
    else:
        st.info(file_but_no_name_label)
    if st.button('upload new file', key=str(uuid.uuid4())):
        file = None
        st.rerun()

# Define BESS obj
bess = BESS()

def st_efd_gui():
    # Main area
    if st.session_state.smap_client.efd.is_complete():
        # assert st.session_state['efd_master_df'] is not None, "Error generating master profile / uninitialized"
        st_efd_main_area()
    else:
        page_data = st.session_state.page_data[4]
        instructions = page_data['instructions']
        st.markdown(f'> {instructions}')

    # Sidebar
    with st.sidebar:
        st_efd_sidebar()

def st_efd_sidebar():      
    # Ref client
    smap_client = st.session_state.smap_client

    st.markdown("## 1. File Upload")    

    if smap_client.aggregated_profile_spreadsheet is not None:
        if hasattr(smap_client.aggregated_profile_spreadsheet,'name'):
            st.info(f"{smap_client.aggregated_profile_spreadsheet.name}")
        else:
            st.info("Using stored file from previous run.")

        def reset_callback():
            smap_client.aggregated_profile_spreadsheet = None
            # st.rerun()
        st.button('upload new file', key=str(uuid.uuid4()), on_click=reset_callback)
            
    else:
        smap_client.aggregated_profile_spreadsheet = st.file_uploader("Upload Aggregated Profiles Spreadsheet", type=["xlsx"]) 

    st.markdown("## 2. Set Battery Specifications")
    
    # ---------
    # Define the BESS 
    bess = smap_client.efd.bess
    bess.capacity_kwh = st.number_input("Enter BESS Energy Rating [kWh]", min_value=0, max_value=10000, value = 1000, step=10)
    bess.peak_discharge_rate = st.number_input("Enter BESS Power Rating [kW]", min_value=0, max_value=5000, value = 500, step=10)
    bess.peak_charge_rate = -bess.peak_discharge_rate
    
    
    bess.eta_charge = 1-(st.number_input("Enter **Charge** Loss Percentage", min_value=0.0, max_value=100.0, value = 5.0, step=0.1)/100)
    bess.eta_discharge = 1-(st.number_input("Enter **Discharge** Loss Percentage", min_value=0.0, max_value=100.0, value = 5.0, step=0.1)/100)    
    

    # ---------
    # Define the BESS usage limits 
    initial_soc_pc = (st.number_input("Initial State of Charge Percentage [%]", min_value=0, max_value=100, value = 50, step=1)/100)
    bess.initial_soc = bess.capacity_kwh * initial_soc_pc

    max_soc_pc = (st.number_input("Maximum State of Charge Percentage [%]", min_value=0, max_value=100, value = 95, step=1)/100)
    bess.soc_max = bess.capacity_kwh * max_soc_pc

    min_soc_pc = (st.number_input("Minimum State of Charge Percentage [%]", min_value=0, max_value=100, value = 5, step=1)/100)
    bess.soc_min = bess.capacity_kwh * min_soc_pc        
            
    # if st.button():

        # if st.session_state['aps_file'] is None:
        #     st.error("Please select input files")

        # else:
        #     df = df_from_file(st.session_state['aps_file'], parse_dates=['timestamp'],index_col= 'timestamp')
        #     print(type(df))
        #     st.rerun()

    st.markdown('---')
    run_buttom = st.container()
    notify_area = st.empty()
    if run_buttom.button("Create Energy Flow Diagram"):
        try:
            notify_area.info("Running...")
            
            smap_client.efd.run()
            
            notify_area = st.empty()
            st.rerun()
        except Exception as e:
            notify_area.error(f'Error: {e}')

def st_efd_main_area():
    # st.markdown("Results:")

    fig_load_shed, ix_date, master_kwh, critical_kwh, loadshed_kwh = efd_load_shed_1d(st.session_state['efd_master_df'],st.session_state['project_name'])
    load_shed_text = f'''
            ### Load Shed
            
            **Max Critical Load:** {ix_date.strftime("%B %d, %Y")} \
            **Master Load:**   {round(master_kwh,1)} kWh\
            **Critical Load:** {round(critical_kwh,1)} kWh, {round((critical_kwh/master_kwh),4)*100}% of the master load \
            **Load Shed:**     {round(loadshed_kwh,1)} kWh, {round((loadshed_kwh/master_kwh),4)*100}% of the master load
            '''
    st.markdown(load_shed_text)
    st.plotly_chart(fig_load_shed)

    xlsx_buffer = export_xlsx()
    date_for_filename = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=-8)))
    
    st.download_button(
            label=f"Download EFD_{st.session_state['project_name']} (00_smap {date_for_filename.now().strftime('%d %B %Y')}).xlsx",
            data = xlsx_buffer,
            file_name=f"EFD_{st.session_state['project_name']} (00_smap {date_for_filename.now().strftime('%d %B %Y')}).xlsx",
            mime="application/vnd.ms-excel",
            type='primary')

def export_xlsx():
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        #metadata_df.to_excel(writer,sheet_name="Project and BESS Info",index=True)
        workbook = writer.book
        
        # Metadata tab has BESS specifications
        # workbook = write_metadata_tab(workbook, bess, st.session_state['project_name'])
        
        # EFD Summary tab has annual summary info
        # workbook = write_efd_summary_tab(workbook, st.session_state['efd_master_df'], st.session_state['project_name'])
        
        
        # Generate export data

        efd_master_daily_df = st.session_state['efd_master_df'].copy()
        efd_master_daily_df['date'] = efd_master_daily_df.index.date  # Create a new column with the date
        efd_master_daily_df = efd_master_daily_df.groupby('date').sum()
        
        efd_critical_daily_df = st.session_state['efd_critical_df'].copy()
        efd_critical_daily_df['date'] = efd_critical_daily_df.index.date  # Create a new column with the date
        efd_critical_daily_df = efd_critical_daily_df.groupby('date').sum()
        
        # 15-minute resolution: master and critical
        st.session_state['efd_master_df'].to_excel(writer, sheet_name='EFD Master 15min', index=True)
        st.session_state['efd_critical_df'].to_excel(writer, sheet_name='EFD Critical 15min', index=True)
        
    return buffer
    
import streamlit as st
from datetime import datetime,timedelta,timezone
import uuid

def already_uploaded_widget(file, no_name_label='Using cached file.'):
    if hasattr(file,'name'):
        st.info(f"{file.name}")
    else:
        st.info(no_name_label)
    if st.button('upload new file', key=str(uuid.uuid4())):
        file = None
        st.rerun()


def st_socr_gui():
    # Main area
    if st.session_state.smap_client.socr.is_complete():
        socr_main_area()
    else:
        page_data = st.session_state.page_data[3]
        instructions = page_data['instructions']
        st.markdown(f'> {instructions}')
    
    #Uploads and creation of profiles
    with st.sidebar:
        socr_sidebar()

def socr_sidebar():
    # Ref client
    smap_client = st.session_state.smap_client

    # APS uploader
    st.markdown('## 1. File Upload')
    if smap_client.aggregated_profile_spreadsheet is not None:
        if hasattr(smap_client.aggregated_profile_spreadsheet,'name'):
            st.info(f"{smap_client.aggregated_profile_spreadsheet.name}")
        else:
            st.info("Using stored file from previous run.")
        def reset_callback():
            smap_client.aggregated_profile_spreadsheet = None
        st.button('upload new file', key=str(uuid.uuid4()), on_click=reset_callback)
    else:
        smap_client.aggregated_profile_spreadsheet = st.file_uploader("Upload Aggregated Profile Spreadsheet file here") 
    # Loss Symmetry options
    st.markdown('## 2. Settings')
    smap_client.socr.charge_loss_percentage = st.number_input("Enter **Charge** Loss Percentage", min_value=0.0, max_value=100.0, value = 3.0, step=0.1)/100
    smap_client.socr.discharge_loss_percentage = st.number_input("Enter **Discharge** Loss Percentage", min_value=0.0, max_value=100.0, value = 3.0, step=0.1)/100
        
    # Degradation Calculation Option
    smap_client.socr.include_degradation = st.toggle("Include Degradation Calculations")

    if smap_client.socr.include_degradation:
        smap_client.socr.years_until_replacement = st.number_input("Years until replacement or augmentation", min_value=1, max_value=100, value = 15, step=1)
        # solar_degrade_rate is [0-1], even though the UI shows numbers [0-100]....note division at the end of these lines
        smap_client.socr.annual_solar_degradation_percentage = st.number_input("Annual solar degradation rate [%]", min_value=0.0, max_value=20.0, value = 0.5, step=0.1)/100
        smap_client.socr.annual_battery_degradation_percentage = st.number_input("Annual energy storage degradation rate [%]", min_value=0.0, max_value=20.0, value = 2.0, step=0.1)/100
        
        
    # --------------
    # Calculate
    st.markdown('---')
    run_buttom = st.container()
    notify_area = st.empty()
    if run_buttom.button("Create SOCr Profile"):
        try:
            notify_area.info("Running...")
            
            smap_client.socr.run()
            
            notify_area = st.empty()
            st.rerun()
        except Exception as e:
            notify_area.error(f'Error: {e}')

def socr_main_area():
    # Ref client
    smap_client = st.session_state.smap_client

    # col1, col2, col3 = st.columns([0.10,0.77,0.10])

    st.markdown("Results:", unsafe_allow_html=True)
    # col1.write('')
    
    # col2.write('')

    # After changes, activate the download button
    # date for filename. Using a static offset of 8 hours avoids need for library, eg. 
    # another libr
    # pst_offset = timedelta(hours=-8)
    # pst_timezone = timezone(pst_offset)
    # date_for_filename = datetime.now(timezone.utc).astimezone(pst_timezone)

    # download_container = st.container()
    
    # download_container.download_button(
    #     label=f"Download SOCr_{st.session_state['project_name']} (00_smap {date_for_filename.now().strftime('%d %B %Y')}).xlsx",
    #     #data=st.session_state['aps_csv'],
    #     data = st.session_state['socr_obj'].excel(),
    #     file_name=f"SOCr_{st.session_state['project_name']} (00_smap {date_for_filename.now().strftime('%d %B %Y')}).xlsx",
    #     mime="application/vnd.ms-excel",
    #     type='primary')
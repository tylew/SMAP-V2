import streamlit as st
from PIL import Image
from smap_package import CONFIG
from smap_package.gui.streamlit.st_modules import PageState, page_header
from smap_package.gui.streamlit.st_pages.st_mdc import st_mdc_gui
from smap_package.gui.streamlit.st_pages.st_aps import st_aps_gui

from smap_package.smap_client import SMAP_Client

def st_start():
    """
    Function to start the Streamlit GUI.
    """
    # Configure Streamlit
    init_st_state()
    # GUI
    display_base_sidebar()
    render_page()

def init_st_state():
    """
    This function initializes the Streamlit in-memory store with the necessary data.
    It loads the configuration file and assigns labels from the config.yaml.
    It also initializes null in-memory stores to cache smap data.
    """

    # Assign labels from YAML  to ST state
    st.set_page_config(
        page_title= CONFIG['st']['page_title'], 
        layout= CONFIG['st']['layout'] )
    
    ####### STREAMLIT STATE FIELDS #######
    # Retrieve & store page data (title, descriptions, etc.)

    if "smap_client" not in st.session_state:
        st.session_state.smap_client = SMAP_Client()



    if "page_data" not in st.session_state:
        st.session_state.page_data = CONFIG['page_data']
    # Initialize page state by using helper class PageState 
    if "page_state" not in st.session_state:
        st.session_state.page_state = PageState()

def render_page():
    """
    Function to display the selected page in the Streamlit GUI.
    """
    # Access state
    index = st.session_state.page_state
    page_data = st.session_state.page_data[index]
    page_header(page_data)
    # Dynamic page rendering
    if index == 0:
        None
    elif index == 1:
        st_mdc_gui()
    elif index == 2:
        st_aps_gui()
    elif index == 3:
        st.markdown(f'{index}')
    elif index == 4:
        st.markdown(f'{index}')
    elif index == 5:
        st.markdown(f'{index}')


def display_base_sidebar():
    """
    Function to create the sidebar for the Streamlit GUI.
    """
    # Header info
    st.sidebar.image(Image.open('smap_package/assets/logo.png'), use_column_width=True)
    st.sidebar.markdown("### Solar Microgrid Analysis Platform")
    # Access page labels using app state data
    page_data = st.session_state.page_data
    labels = [item['label'] for item in page_data.values()]

    def set_project_name():
        smap_client = st.session_state.smap_client
        smap_client.project_name = st.session_state.new_project_name
        # smap_client.reload_plots(tools=['mdc'])
        

    st.sidebar.text_input(
        "Set a project name", st.session_state.smap_client.project_name, on_change=set_project_name, key='new_project_name')

    # Create a dropdown menu for page selection
    selected_label = st.sidebar.selectbox("Select a tool", labels)
    # Find the index of the selected label in the labels list
    selected_index = labels.index(selected_label)
    # Store the selected index in session state
    st.session_state.page_state = selected_index

    st.sidebar.markdown("---")




import streamlit as st
import uuid

class PageState:
    """
    Class to manage active page state for smap_services.gui
    """
    def __init__(self):
        self._current_page = None

    @property
    def current_page(self):
        return self._current_page

    @current_page.setter
    def current_page(self, page):
        self._current_page = page

def already_uploaded_widget(file, file_but_no_name_label='Using cached file.'):
    if hasattr(file,'name'):
        st.info(f"{file.name}")
    else:
        st.info(file_but_no_name_label)
    if st.button('upload new file', key=str(uuid.uuid4())):
        file = None
        st.rerun()

def page_header(page_data):
    st.title(page_data['title'])
    st.markdown(page_data['description'])

    st.markdown("---")

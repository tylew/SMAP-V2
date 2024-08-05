"""
smap_services Streamlit GUI integration

Provides a Streamlit GUI for the smap_services package.
"""


from smap_package.gui.streamlit.st_start import st_start

# Specify what should be imported when "from smap_services.smap_streamlit import *" is used.
__all__ = [
    'st_start'
]

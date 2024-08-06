import streamlit as st

def st_ea_gui():
    #Uploads and creation of profiles
    with st.sidebar:
        
        #Upload an APS to start       
        st.markdown("## 1. File Upload")
        etb_csv = st.file_uploader("Upload ETB Output Spreadsheet")
        # if etb_csv:
        #     st.session_state.project_name = etb_csv.name.split(".")[0].split("_")[0]
        #     st.session_state.utilityapi_csv = etb_csv
            


        if st.button("Create Economic Profile"):
            None
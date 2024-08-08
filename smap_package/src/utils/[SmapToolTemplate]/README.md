# NEW SMAP TOOL TEMPLATE

### To add a new Tool:
1. Copy this template directory into `src/`
2. Replace filenames with tool code 
    - ex: Meter Data Cleaner uses tool code `mdc`, this code is consistent across the entire package.
3. Ensure to not delete any of the default functions provided in `[ToolCode]Tool.py`
4. Define assisting + operational functions in `[ToolCode]Helpers.py`, the main brute of code will be in this file. Make sure to refrence these functions appropriately in the base Tool file.
5. Define plotting functions in `[ToolCode]Plotting.py`. Reference these functions appropriately in the base Tool function `generate_plots(self, **kwargs)`, generate and set member variables to store plots.
6. **IMPORTANT:** Add reference of new tool to `smap_package/smap_client.py`

### To create (streamlit) GUI for new tool:
1. In `smap_package/config.yaml`, append `page_data` to include the information of your new tool. This is the text that displays in the SMAP GUI.
2. Define a new streamlit page in `smap_package/gui/streamlit/st_pages/`
3. Add a clause for the new tool in the `render_page()` function within `smap_package/gui/streamlit/st_start.py`


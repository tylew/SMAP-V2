# SMAP-V2

This repository contains SMAP Version 2

`smap_package/` directory contains the complete package env.

To run: `streamlit run streamlit.py `

### Package directory structure:
```plain text
smap_package/
│
├── README.md
├── LICENSE
├── requirements.txt
├── setup.py
├── .gitignore
│
├── gui/
│   ├── __init__.py
│   │   
│   ├── streamlit/
│   │   ├── st_modules.py
│   │   ├── st_start.py
│   │   │
│   │   ├── st_pages/
│   │   │   ├── st_mdc.py
│   │   │   ├── st_aps.py
│   │   │   ├── st_socr.py
│   │   │   ├── st_efd.py
│   │   │   ├── st_ea.py
│
├── src/
│   ├── __init__.py
│   ├── smap_client.py
│   ├── config.yaml
│   │   
│   ├── [ToolCode]/
│   │   ├── [ToolCode]Tool.py
│   │   ├── [ToolCode]Plotting.py
│   │   ├── [ToolCode]Helpers.py
│   │   
│   ├── utils/
│   │   ├── Tool.py
│   │   ├── BESS.py
│   │   ├── generalHelpers.py
│   │   ├── [SmapToolTemplate]/
│   │   │   ├── [Template Files]
```
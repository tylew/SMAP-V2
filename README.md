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
│   ├── tools/
│   │   ├── mdcTool.py
│   │   ├── apsTool.py
│   │   ├── socrTool.py
│   │   ├── efdTool.py
│   │   ├── eaTool.py
│   │   
│   ├── plotting/
│   │   ├── mdcPlotting.py
│   │   ├── apsPlotting.py
│   │   ├── socrPlotting.py
│   │   ├── efdPlotting.py
│   │   ├── eaPlotting.py
│   │   
│   ├── utils/
│   │   ├── Tool.py
│   │   ├── BESS.py
│   │   
│   ├── helpers/
│   │   ├── generalHelpers.py
│   │   ├── mdcHelpers.py
│   │   ├── apsHelpers.py
│   │   ├── socrHelpers.py
│   │   ├── efdHelpers.py
│   │   ├── eaHelpers.py
```
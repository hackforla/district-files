# GeoHub LA Data Collection
> **Note:** This repository is an off-shoot of the following repository: [https://github.com/parcheesime/geohub-datacollection](https://github.com/parcheesime/geohub-datacollection). It is issue [118 Create District Types](https://github.com/hackforla/data-science/issues/118#issuecomment-3276775698) for Hack for L.A. Data Science CoP.

## Overview
This project collects **district boundary files** for various political and administrative districts within Los Angeles County.  
The data is converted into both **raw JSON** and **GeoJSON** formats for easy use in civic tech projects.  
The processed data will be contributed to **Hack for LA**.

For questions or collaboration, reach out on GitHub: [@parcheesime](https://github.com/parcheesime).

---

## Districts Covered
- Assembly
- Senate
- Neighborhood Councils
- Supervisors
- Congressional
- City Clerk (BIDs)
- City Council

---

## Data Collection Process
The data collection process is facilitated using the [GeoHub LA County Website](https://geohub.lacity.org/search?collection=Dataset) and related ArcGIS APIs.

### Steps
1. **Authentication**: No key required.  
2. **Requesting Data**: Python script sends requests to API endpoints for each district.  
3. **Data Processing**: Responses are saved in two formats:
   - Raw ArcGIS JSON (`district.json`)
   - GeoJSON (`district.geojson`)
4. **Data Storage**: Output files are stored in `shapefiles_output/`.  
5. **Automation**: A GitHub Actions workflow will be configured to run this process on a weekly or monthly basis via update_shapefiles.yml.

---

## Repository Structure

geohubLA_data_collection/
│
├── main.py # Script to fetch and save district shapefiles
├── shapefiles_output/ # Folder where JSON and GeoJSON outputs are stored
├── example_usage.ipynb # Jupyter notebook demo of loading and plotting data
├── requirements.txt # Python dependencies
└── README.md # Project documentation


---

## Installation & Setup

### Clone the repository
```bash
git clone https://github.com/<your-org>/geohubLA_data_collection.git
cd geohubLA_data_collection
```
## Installation & Setup

### Create and activate a virtual environment 
```bash
python3 -m venv myenv
source myenv/bin/activate
```

### install requirements
```bash
pip install -r requirements.txt
```

# Run main and example usage
```bash
python main.py
jupyter notebook example_usage.ipynb
```
# Guarantee Data Comparison Project

This project compares guarantee data coming from two systems:

- LAWEB (legacy system)
- Salesforce (SF)

It checks:

✔ Column structure  
✔ Datatype differences  
✔ Primary Key (ID) mismatches  
✔ Row-level value mismatches  
✔ Generates an HTML report with highlights  

## Project Structure

See full project layout inside this repository. The `src/` folder contains all logic, and all generated reports go to `reports/html/`.


## Create a virtual environment
 python3 -m venv venv
## Activate the virtual environment (Linux / macOS) 
 source venv/bin/activate 
## How to install
 pip install -r requirements.txt   
## How to Run
 python3 src/main.py

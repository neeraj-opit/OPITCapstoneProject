# SF vs LAWEB Data Comparison Framework

A lightweight and flexible Python tool to compare data between **SF (Salesforce DataMart)** and **LAWEB (Legacy System)** tables.  
Supports column comparison, datatype validation, primary key checks, missing IDs, row-level mismatches, and generates HTML reports.

---

## 🚀 Features

- Compare **any two CSV files**  
- Case-insensitive column handling  
- Two usage modes:
  - **YAML table mode** (`--table`)  
  - **Direct CSV mode** (`--sf` / `--laweb`)  
- Optional Excel datatype mapping  
- Smart dtype inference when mapping is missing  
- Row mismatch sampling (up to 500 differences)  
- Clean HTML output reports  
- Easy to extend by editing the YAML config (no code change needed)

---

## 📁 Project Structure

```
OPITCapstoneProject/
│
├── config/
│   └── table_mapping.yaml
│
├── data/
│   └── raw/
│       ├── <table>_SF.csv
│       ├── <table>_LAWEB.csv
│       └── optional_dtype_map.xlsx
│
├── reports/
│   └── html/
│       └── <table_name>_comparison_report.html
│
├── src/
│   ├── main.py
│   ├── utils/
│   ├── compare/
│   └── README.md
```

---

## ⚙️ Installation

```bash
git clone https://github.com/neeraj-opit/OPITCapstoneProject
cd OPITCapstoneProject

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

---

## 🧩 Configuration

Tables are defined in:

```
config/table_mapping.yaml
```

Example entry:

```yaml
tables:
  Guarantee:
    sf: "data/raw/guarantee_sf.csv"
    laweb: "data/raw/guarantee_laweb.csv"
    primary_key: "ID"
    dtype_map: "data/raw/DTypes_GuaranteeTable_Sf_VS_Laweb.xlsx"
```

Add more tables simply by extending the YAML file.

---

## ▶️ Usage

### **1. Table Mode (recommended)**

```bash
python3 src/main.py --table Guarantee
```

### **2. Direct CSV Mode**

```bash
python3 src/main.py   --sf path/to/sf.csv   --laweb path/to/laweb.csv   --pk ID
```

---

## 📊 Output

Reports generated under:

```
reports/html/<table_name>_comparison_report.html
```

Includes:

- Missing columns  
- Datatype mismatches  
- Missing IDs  
- Row-level mismatches  
- Color-highlighted differences  

---

## 🛠 Tech Stack

- Python 3.10+
- Pandas
- PyYAML
- HTML/CSS

---

## 👤 Author

**Neeraj Kumar**  
GitHub: https://github.com/neeraj-opit
import pandas as pd
import json
import uuid
import os
from datetime import datetime
from trestle.oscal import OSCAL_VERSION

# Configuration
INPUT_FILE = 'data/csf2.xlsx'
OUTPUT_FILE = 'catalogs/NIST_CSF_v2.0/catalog.json'

def clean_id(text):
    """Converts text to OSCAL-compliant ID format.
    Examples:
    - 'GOVERN (GV): ...' -> 'govern-gv'
    - 'Organizational Context (GV.OC): ...' -> 'organizational-context-gv-oc'
    - 'Roles, Responsibilities, and Authorities (GV.RR): ...' -> 'roles-responsibilities-and-authorities-gv-rr'
    - 'GV.OC-01: ...' -> 'gv-oc-01'
    """
    if pd.isna(text): return ""
    # Take only the part before the colon
    text = text.split(':')[0].strip().lower()
    # Replace periods with hyphens
    text = text.replace(".", "-")
    # Remove parentheses, commas, and replace spaces with hyphens
    text = text.replace("(", "").replace(")", "").replace(",", "").replace(" ", "-")
    # Remove any double hyphens that might result
    while "--" in text:
        text = text.replace("--", "-")
    # Remove leading/trailing hyphens
    return text.strip("-")

def transform():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    # Load the CSF 2.0 tab, skipping the NIST header rows
    df = pd.read_excel(INPUT_FILE, sheet_name='CSF 2.0', skiprows=1)

    catalog = {
        "catalog": {
            "uuid": str(uuid.uuid4()),
            "metadata": {
                "title": "NIST Cybersecurity Framework (CSF) v2.0",
                "last-modified": datetime.utcnow().isoformat() + "Z",
                "version": "2.0",
                "oscal-version": OSCAL_VERSION
            },
            "groups": []
        }
    }

    current_func = None
    current_cat = None

    for _, row in df.iterrows():
        # 1. Functions -> Top Level Groups
        if pd.notna(row['Function']):
            current_func = {
                "id": clean_id(row['Function']),
                "class": "function",
                "title": row['Function'],
                "groups": []
            }
            catalog["catalog"]["groups"].append(current_func)

        # 2. Categories -> Nested Groups
        if pd.notna(row['Category']):
            current_cat = {
                "id": clean_id(row['Category']),
                "class": "category",
                "title": row['Category'],
                "controls": []
            }
            if current_func:
                current_func["groups"].append(current_cat)

        # 3. Subcategories -> Controls
        if pd.notna(row['Subcategory']):
            ctrl_id = clean_id(row['Subcategory'])
            parts = row['Subcategory'].split(':', 1)
            
            control = {
                "id": ctrl_id,
                "title": parts[0].strip(),
                "parts": [{
                    "id": f"{ctrl_id}-smt",
                    "name": "statement",
                    "prose": parts[1].strip() if len(parts) > 1 else ""
                }]
            }
            
            # Implementation Examples
            if pd.notna(row['Implementation Examples']):
                control["parts"].append({
                    "id": f"{ctrl_id}-eg",
                    "name": "example",
                    "prose": str(row['Implementation Examples'])
                })

            if current_cat:
                current_cat["controls"].append(control)

    # Ensure output directory exists and save
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(catalog, f, indent=2)
    
    print(f"Transformation complete. File saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    transform()
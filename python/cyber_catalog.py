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
    """Converts text to OSCAL-compliant ID format, extracting only the abbreviation part.
    Examples:
    - 'Organizational Context (GV.OC): ...' -> 'gv.oc'
    - 'Roles, Responsibilities, and Authorities (GV.RR): ...' -> 'gv.rr'
    - 'GV.OC-01: ...' -> 'gv.oc-01'
    
    Note: For top-level function groups, the abbreviation in parentheses (e.g., 'GV' from 'GOVERN (GV)')
    is extracted directly and used as the ID.
    """
    if pd.isna(text): return ""
    # Take only the part before the colon
    text = text.split(':')[0].strip()
    
    # If there's an abbreviation in parentheses, extract it
    if '(' in text and ')' in text:
        abbrev = text.split('(')[1].split(')')[0].strip().lower()
        return abbrev
    
    # Otherwise, just convert to lowercase (for subcategory IDs like "GV.OC-01")
    return text.lower()

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
            # Extract the abbreviation from parentheses (e.g., "GOVERN (GV)" -> "gv")
            func_text = row['Function']
            func_id = clean_id(func_text)
            # If there's an abbreviation in parentheses, use it as the ID
            if '(' in func_text and ')' in func_text:
                abbrev = func_text.split('(')[1].split(')')[0].strip().lower()
                func_id = abbrev
            
            current_func = {
                "id": func_id,
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
                    "id": f"{ctrl_id}_smt",
                    "name": "statement",
                    "prose": parts[1].strip() if len(parts) > 1 else ""
                }]
            }
            
            # Implementation Examples
            if pd.notna(row['Implementation Examples']):
                control["parts"].append({
                    "id": f"{ctrl_id}_eg",
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
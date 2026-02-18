import pandas as pd
import json
import os

def load_catalog_control_ids(catalog_path):
    """
    Load all control IDs from an OSCAL catalog JSON file.
    Returns a set of control IDs found in the catalog.
    """
    if not os.path.exists(catalog_path):
        print(f"Warning: Catalog file not found: {catalog_path}")
        return set()
    
    with open(catalog_path, 'r') as f:
        catalog_data = json.load(f)
    
    control_ids = set()
    
    def extract_control_ids(obj):
        """Recursively extract control IDs from catalog structure."""
        if isinstance(obj, dict):
            # Check if this is a control with an ID
            if 'id' in obj and 'title' in obj:
                control_ids.add(obj['id'])
            # Recursively process all values
            for value in obj.values():
                extract_control_ids(value)
        elif isinstance(obj, list):
            for item in obj:
                extract_control_ids(item)
    
    extract_control_ids(catalog_data)
    return control_ids

def transform_csf_id(csf_id):
    """
    Transform CSF IDs to match catalog format.
    Examples: 'GV.OC-01' -> 'gv.oc-01', 'DE.AE-02' -> 'de.ae-02'
    """
    if pd.isna(csf_id):
        return ""
    
    # Convert to string, strip whitespace, and lowercase
    csf_id = str(csf_id).strip().lower()
    
    # Keep periods as-is (catalog uses dots in IDs)
    
    return csf_id

def transform_control_id(control_id):
    """
    Transform 800-53 control IDs to OSCAL catalog format.
    Examples: 'AC-01' -> 'ac-1', 'AC-2(1)' -> 'ac-2.1'
    """
    if pd.isna(control_id):
        return ""
    
    # Convert to string and strip whitespace and any trailing commas
    control_id = str(control_id).strip().rstrip(',')
    
    # Convert to lowercase
    control_id = control_id.lower()
    
    # Remove leading zeros from numbers (AC-01 -> ac-1)
    # Split on hyphen, process the numeric part
    parts = control_id.split('-')
    if len(parts) == 2:
        family = parts[0]
        number_part = parts[1]
        
        # Handle enhancements in parentheses: ac-2(1) -> ac-2.1
        if '(' in number_part:
            base, enhancement = number_part.split('(')
            enhancement = enhancement.rstrip(')')
            # Remove leading zeros
            base = str(int(base)) if base.isdigit() else base
            enhancement = str(int(enhancement)) if enhancement.isdigit() else enhancement
            control_id = f"{family}-{base}.{enhancement}"
        else:
            # Just remove leading zeros from the number
            number_part = str(int(number_part)) if number_part.isdigit() else number_part
            control_id = f"{family}-{number_part}"
    
    return control_id

# 1. Define the structure (Hardcoded from the SOC2 template example)
column_names = [
    '$$Source_Resource', 
    '$$Target_Resource', 
    '$$Map_Source_ID_Ref_list', 
    '$$Map_Target_ID_Ref_list', 
    '$$Map_Relationship', 
    '$Map_Confidence_Score', 
    '$Map_Coverage'
]

column_descriptions = [
    'A reference to a resource that has the source controls of a mapping.',
    'A reference to a resource that has the target controls of a mapping.',
    'A list of source reference IDs.',
    'A list of target reference IDs.',
    'The relationship type for the mapping entry.',
    'An estimation of the confidence that this mapping is correct and accurate expressed as percentage.',
    'An estimation of the percentage coverage of the targets by the sources.'
]

# 2. Set file names
input_xlsx = 'data/Cybersecurity_Framework_v2-0_Concept_Crosswalk_800-53_5_2_0_draft.xlsx'
output_csv = 'content/csf2_to_800-53_crosswalk.csv'
target_catalog = 'catalogs/NIST_SP-800-53_rev5/catalog.json'

# 3. Load valid control IDs from target catalog
print(f"Loading control IDs from {target_catalog}...")
valid_control_ids = load_catalog_control_ids(target_catalog)
print(f"Found {len(valid_control_ids)} controls in target catalog")

# 4. Read the Excel file
# The data is located in the 'Relationships' sheet. 
# Note: Ensure 'openpyxl' is installed (pip install openpyxl) to read .xlsx files.
df = pd.read_excel(input_xlsx, sheet_name='Relationships')

# 4. Filter and clean data
# The original file has column names with newline characters: 'Focal Document\nElement'
source_col = 'Focal Document\nElement'
target_col = 'Reference Document\nElement'

# Only keep rows where a mapping (target element) exists
df_mapped = df[df[target_col].notna()].copy()

# Clean control IDs (remove leading/trailing spaces or newlines)
df_mapped[source_col] = df_mapped[source_col].astype(str).str.strip()
df_mapped[target_col] = df_mapped[target_col].astype(str).str.strip()

# Filter out category-level entries (e.g., "RS.MA", "RC.RP") - keep only controls with numbers
# CSF controls have format like "GV.OC-01", categories are just "GV.OC"
# After the period, there should be letters, a hyphen, and digits
df_mapped = df_mapped[df_mapped[source_col].str.match(r'^[A-Z]{2}\.[A-Z]{2}-\d+$', na=False)].copy()

# Transform source CSF IDs to match catalog format (GV.OC-01 -> gv-oc-01)
df_mapped[source_col] = df_mapped[source_col].apply(transform_csf_id)

# Transform target control IDs to OSCAL catalog format (AC-01 -> ac-1)
df_mapped[target_col] = df_mapped[target_col].apply(transform_control_id)

# Validate that transformed control IDs exist in the target catalog
invalid_controls = []
for control_id in df_mapped[target_col].unique():
    if control_id and control_id not in valid_control_ids:
        invalid_controls.append(control_id)

if invalid_controls:
    print(f"\nWarning: {len(invalid_controls)} control IDs not found in target catalog:")
    for ctrl in sorted(invalid_controls)[:10]:  # Show first 10
        print(f"  - {ctrl}")
    if len(invalid_controls) > 10:
        print(f"  ... and {len(invalid_controls) - 10} more")
    print("\nThese controls will still be included in the mapping but may need review.")
else:
    print("\nAll target control IDs validated successfully!")

# 5. Group target IDs by unique source IDs
# Create a mapping of source ID -> list of target IDs
# Use space-separated format (OSCAL standard), not comma-separated
grouped = df_mapped.groupby(source_col)[target_col].apply(
    lambda x: ' '.join([id.rstrip(',') for id in x.unique() if id])
).reset_index()

# Build the data rows according to the template
data_rows = pd.DataFrame({
    '$$Source_Resource': ["catalogs/NIST_CSF_v2.0/catalog.json"] * len(grouped),
    '$$Target_Resource': ["catalogs/NIST_SP-800-53_rev5/catalog.json"] * len(grouped),
    '$$Map_Source_ID_Ref_list': grouped[source_col].values,
    '$$Map_Target_ID_Ref_list': grouped[target_col].values,
    '$$Map_Relationship': ["superset-of"] * len(grouped),
    '$Map_Confidence_Score': ["100%"] * len(grouped),
    '$Map_Coverage': [""] * len(grouped)
})

# Ensure the columns follow the template order exactly
data_rows = data_rows[column_names]

# 6. Create the final output including the description row
# Row 1: Column Names (handled by to_csv header)
# Row 2: Column Descriptions
final_df = pd.DataFrame([column_descriptions], columns=column_names)
final_df = pd.concat([final_df, data_rows], ignore_index=True)

# 7. Identify unmapped CSF controls and add them to CSV
print("\n" + "="*80)
print("UNMAPPED CSF CONTROLS ANALYSIS")
print("="*80)

# Load all CSF control IDs from the catalog
source_catalog = 'catalogs/NIST_CSF_v2.0/catalog.json'
print(f"\nLoading all CSF controls from {source_catalog}...")
all_csf_controls = load_catalog_control_ids(source_catalog)
print(f"Found {len(all_csf_controls)} total CSF controls in catalog")

# Get the set of mapped CSF controls from our output
mapped_csf_controls = set(grouped[source_col].values)
print(f"Found {len(mapped_csf_controls)} CSF controls with mappings to 800-53")

# Find unmapped controls
unmapped_controls = all_csf_controls - mapped_csf_controls

# Filter out category-level entries (e.g., "de", "gv.oc") - keep only actual controls
# CSF controls have format like "gv.oc-01", categories are just "gv.oc" or "gv"
filtered_unmapped = []
for control in unmapped_controls:
    # Must have a hyphen followed by digits to be a control (not a category)
    if '-' in control and control.split('-')[-1].isdigit():
        filtered_unmapped.append(control)

print(f"\nFound {len(filtered_unmapped)} CSF controls NOT mapped to 800-53")

if filtered_unmapped:
    # Sort the unmapped controls for better readability
    sorted_unmapped = sorted(filtered_unmapped)
    
    # Group by function/category for organized output
    from collections import defaultdict
    grouped_unmapped = defaultdict(list)
    
    for control in sorted_unmapped:
        # Extract function.category (e.g., 'gv.oc' from 'gv.oc-01')
        if '.' in control and '-' in control:
            category = control.rsplit('-', 1)[0]  # Get everything before the last hyphen
            grouped_unmapped[category].append(control)
        else:
            grouped_unmapped['other'].append(control)
    
    # Print grouped results
    for category in sorted(grouped_unmapped.keys()):
        controls = grouped_unmapped[category]
        print(f"  {category.upper()}: ({len(controls)} controls)")
    
    # Add unmapped controls to the CSV with empty targets
    # This allows csv-to-oscal-mc to populate source-gap-summary
    unmapped_rows = pd.DataFrame({
        '$$Source_Resource': ["catalogs/NIST_CSF_v2.0/catalog.json"] * len(sorted_unmapped),
        '$$Target_Resource': ["catalogs/NIST_SP-800-53_rev5/catalog.json"] * len(sorted_unmapped),
        '$$Map_Source_ID_Ref_list': sorted_unmapped,
        '$$Map_Target_ID_Ref_list': [""] * len(sorted_unmapped),  # Empty target = unmapped
        '$$Map_Relationship': [""] * len(sorted_unmapped),
        '$Map_Confidence_Score': [""] * len(sorted_unmapped),
        '$Map_Coverage': [""] * len(sorted_unmapped)
    })
    
    # Append unmapped controls to the data
    data_rows = pd.concat([data_rows, unmapped_rows], ignore_index=True)
    print(f"\n✓ Added {len(sorted_unmapped)} unmapped controls to CSV")
else:
    print("\n✓ All CSF controls are mapped to 800-53!")

print("="*80)

# 8. Create the final output including the description row
# Row 1: Column Names (handled by to_csv header)
# Row 2: Column Descriptions
final_df = pd.DataFrame([column_descriptions], columns=column_names)
final_df = pd.concat([final_df, data_rows], ignore_index=True)

# 9. Save to CSV
final_df.to_csv(output_csv, index=False)

print(f"\n✓ Successfully converted {input_xlsx} to {output_csv}")
print(f"  - Mapped controls: {len(mapped_csf_controls)}")
print(f"  - Unmapped controls: {len(unmapped_controls)}")
print(f"  - Total rows in CSV: {len(data_rows)}")
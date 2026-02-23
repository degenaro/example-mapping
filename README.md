# oscal-mapping-collections

This repo comprises oscal mapping collections.

-----

### CSF v2 to Nist 800-53 rev5

To produce this OSCAL mapping collection run `make csf`.

##### Provenance
- [Cybersecurity-Framework-v2.0-to-SP-800-53-Rev-5-2-0 Informative Reference Details](https://csrc.nist.gov/projects/olir/informative-reference-catalog/details?referenceId=186#/)

##### Create OSCAL mapping collection
1. Build CSF catalog:
    - input: 
        - [data/csf2.xlsx](data/csf2.xlsx)
    - output: 
        - [catalogs/NIST_CSF_v2.0/catalog.json](catalogs/NIST_CSF_v2.0/catalog.json)
    
2. Build CSF to 800-53 mapping CSV file:
    - input: 
        - [catalogs/NIST_CSF_v2.0/catalog.json](catalogs/NIST_CSF_v2.0/catalog.json)
        - [data/Cybersecurity_Framework_v2-0_Concept_Crosswalk_800-53_5_2_0_draft.xlsx](data/Cybersecurity_Framework_v2-0_Concept_Crosswalk_800-53_5_2_0_draft.xlsx)
    - output: 
        - [content/csf2_to_800-53_crosswalk.csv](content/csf2_to_800-53_crosswalk.csv)
        
3. Build CSF to 800-53 mapping collection json file:
    - input: 
        - [content/csf2_to_800-53_crosswalk.csv](content/csf2_to_800-53_crosswalk.csv)
    - output:
        - [mapping-collections/NIST_CSF_v2.0-to-NIST_SP-800-53_rev5/mapping-collection.json](mapping-collections/NIST_CSF_v2.0-to-NIST_SP-800-53_rev5/mapping-collection.json)

-----

### Nist 800-53 rev5 to Nist 800-53 rev4

To produce this OSCAL mapping collection run `make nist`.

##### Provenance
- [NIST SP 800-53 Rev. 5](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final)
    - See Analysis of updates between 800-53 Rev. 5 and Rev. 4

##### Create OSCAL mapping collection        
1. Build Nist 800-53 rev5 to Nist 800-53 rev4 mapping CSV file:
    - input: 
        - [data/sp800-53r4-to-r5-comparison-workbook.xlsx](data/sp800-53r4-to-r5-comparison-workbook.xlsx)
    - output: 
        - [content/nist_rev5_to_nist_rev4_crosswalk.csv](content/nist_rev5_to_nist_rev4_crosswalk.csv)
        
2. Build CSF to 800-53 mapping collection json file:
    - input: 
        - [content/nist_rev5_to_nist_rev4_crosswalk.csv](content/nist_rev5_to_nist_rev4_crosswalk.csv)
    - output:
        - [mapping-collections/NIST_SP-800-53_rev5-to-NIST_SP-800-53_rev4/mapping-collection.json](mapping-collections/NIST_SP-800-53_rev5-to-NIST_SP-800-53_rev4/mapping-collection.json)
        
-----

### Harmonized

<img src="images/MappingCollections.drawio.png" width="500" height="200">

    

# NIST SP 800-53 Rev 5 to Rev 4 Comparison Summary

## Overview

Total controls analyzed: **1189**

## OSCAL Relationship Distribution (Excel Analysis)

| Relationship | Count | Percentage |
|--------------|-------|------------|
| equal-to | 130 | 10.9% |
| equivalent-to | 172 | 14.5% |
| intersects-with | 369 | 31.0% |
| no-relationship | 267 | 22.5% |
| restored5 | 1 | 0.1% |
| subset-of | 4 | 0.3% |
| superset-of | 65 | 5.5% |
| withdrawn4 | 91 | 7.7% |
| withdrawn5 | 90 | 7.6% |

## CSV Mapping Statistics

- **Mapped controls**: 740 (controls with active Rev5↔Rev4 relationships)
- **Source gaps**: 268 (new or restored in Rev5)
  - New controls (no-relationship): 267
  - Restored controls (restored5): 1
- **Excluded**: 181 (withdrawn/withdrawn5 controls not in CSV)
- **Total CSV rows**: 1008

## Relationship Definitions

- **equal-to**: No changes at all between Rev 5 and Rev 4
- **equivalent-to**: Cosmetic or discussion-only changes; same substance
- **superset-of**: Rev 5 added requirements (Rev 5 ⊃ Rev 4)
- **subset-of**: Rev 5 removed requirements (Rev 5 ⊂ Rev 4)
- **intersects-with**: Overlapping changes in both directions
- **no-relationship**: New Rev 5 control; no Rev 4 counterpart
- **withdrawn**: Withdrawn in both Rev 4 and Rev 5
- **withdrawn4**: Withdrawn in Rev 4, does not appear in Rev 5
- **restored5**: Withdrawn in Rev 4, restored in Rev 5
- **withdrawn5**: Withdrawn in Rev 5, did not appear in Rev 4 (or was active in Rev 4)

## Notes

- Controls with **restored5** relationship are included in the CSV as source gaps
- Controls with **withdrawn**, **withdrawn4**, and **withdrawn5** relationships are excluded from the CSV/JSON output

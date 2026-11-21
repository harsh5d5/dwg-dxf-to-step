Submarine compartment conversion outputs
========================================

Two models are included. Use the DETAILED model for internal components.

Source drawings (in source/):
- submarine_compartment_2D.dxf                 : original 2D drawing
- submarine_compartment_detailed_drawings.pdf  : 45-sheet part list used as a guide


1) DETAILED MODEL (recommended for inner components)
----------------------------------------------------
Files:
- submarine_compartment_detailed.step     : 44 named components with internal parts (STEP, mm)
- submarine_compartment_detailed.stl      : same detailed geometry as a mesh
- submarine_compartment_detailed-preview.png : rendered isometric preview
- submarine_compartment_detailed_manifest.json : per-component labels, layers, sizes, volumes, source view IDs
- submarine_compartment_detailed_report.json   : validation summary and component counts

What is modelled:
- HULL-H1, BULKHEAD-FWD/AFT, DECK-D1
- TANK-T1/T2, MOTOR-M1/M2, BATTERY-B1..B4
- FRAME-F1..F7, PUMP-P1..P4, VALVE-V1..V8
- PIPE-L1..L9, HANGER-H1..H4

Counts from the manifest:
  HULL 1, BULKHEAD 2, DECK 1, TANK 2, MOTOR 2, BATTERY 4,
  FRAME 7, PUMP 4, VALVE 8, PIPE 9, HANGER 4  (44 components total)

Validation:
- STEP re-read: valid compound, 84 watertight solids, 0 invalid solids.
- Overall bounds: 8000.0 x 5999.75 x 5999.51 mm.
- Pumps and valves are multi-solid assemblies (3 and 5 solids respectively);
  all solids are individually valid.

Method:
1. submarine_compartment_detailed_drawings.pdf was inspected: 45 sheets, 44 item sheets.
   It lists the same component names/layers that already exist in the DXF.
2. The stock analyzer's 500-profile cap was raised; the DXF yielded 3227 profiles.
3. The three drawing regions were mapped to model coordinates:
     front view = (X, Z)
     top view   = (X, Y + 7000)
     side view  = (Y + 11000, Z)
4. Each component was rebuilt by intersecting the extrusion of its three views,
   then cutting holes/cavities shown in those views. Near-coincident DXF polyline
   points were simplified and degenerate zero-volume solids were removed so the
   exported STEP remains valid.

Limitation:
This is a geometric reconstruction from 2D drawings. It does not include manufacturing
tolerances, threads, material specifications, weld details, or full assembly fasteners.
Do not treat it as manufacturing-ready without engineering review.


2) HULL-ONLY MODEL (earlier result)
-----------------------------------
Files:
- submarine_compartment.step : outer hull envelope only (STEP, mm)
- submarine_compartment.stl  : same hull as a mesh
- preview.png                : rendered preview
- report.json                : geometry validation report

This was built from only the HULL layer's three views. It is a valid single solid,
bounds 8000 x 6000 x 6000 mm, but it does NOT contain internal components.

PCI Bracket Blank - 2D DXF to 3D
================================

Files
- source/PCI Bracket Blank.dxf        : original 2D drawing
- pci_bracket_blank.step              : 3D solid (STEP, mm)
- pci_bracket_blank.stl               : same solid as a mesh
- pci_bracket_blank-preview.png       : isometric preview
- pci_bracket_blank-top.png           : top/flat preview showing the cutouts
- pci_bracket_blank_report.json       : validation summary and assumptions
- pci_bracket_blank_parameters.json   : derived profile/hole data
- parameters.json                     : editable build parameters (thickness)
- build_bracket.py                    : reproducible build script
- analysis.json                       : DXF analysis used by the build script

What the DXF contained
- Layer "bracket cut": one closed outer contour.
- Layer "holes": five closed cutouts (two large slots/rectangles and three round holes).
- Units: millimetres.
- No dimensions, thickness, material, tolerances, or bend notes were present.

Important assumption
The DXF is a flat 2D blank with no thickness dimension. The model was extruded
0.8 mm normal to the drawing plane (+Z). This is a common PC/PCI bracket sheet
gauge (~0.032 in / 0.81 mm), but it is still an assumption. To use a different
thickness, edit "thickness_mm" in parameters.json and rerun build_bracket.py
with the project's Python environment.

Validation
- STEP re-read: valid, single solid.
- Bounds: 21.59 x 132.43 x 0.8 mm.
- Volume: 1583.663 mm3, exactly matching the expected net-profile area x thickness.
- All five hole profiles were cut through the sheet.

Limitations
This is a flat blank only. It does not include formed bends, tabs, surface finish,
material, tolerances, or secondary machining not shown in the DXF.

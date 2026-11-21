SPINDLE - 2D image to 3D
========================

Files
- spindle.step            : 3D solid (STEP, mm)
- spindle.stl             : same solid as a mesh
- spindle-preview.png     : isometric preview
- spindle-front.png       : front/profile preview
- spindle_report.json     : validation, dimensions and assumptions
- spindle_summary.json    : derived model summary
- parameters.json         : editable interpreted dimensions
- build_spindle.py        : reproducible build script
- source/1_spindle_clean.png : source image
- source/image_ocr.txt    : text/dimensions read from the image

How the image was read
The PNG is a drawing sheet with FRONT VIEW, SIDE VIEW and ISOMETRIC VIEW.
Text/dimensions extracted from it:
  85.00, 75.00, 58.34, 16.66, 15.00, 10.00
  33.00, 25.00, 24.00, 15.00
  2XR3.00
  TITLE SPINDLE / MATERIAL EN19 / SCALE 1:2 / SHEET A4
  RAW MATERIAL D36 x 88 / ALL DIMENSIONS ARE IN MM

Interpreted model (mm)
- Overall length: 85.00
- Flange: D33 x 10.00
- Main body: D25 x 58.34, followed by a derived 1.66 mm shoulder
  (because 16.66 - 15.00 = 1.66)
- Tip: D24 x 15.00
- Through bore: D15 (from the concentric D15 circle in the side view)
- Two R3 external fillets (D33 flange shoulder and D24 tip outer edge)

Validation
- STEP re-read: valid, single solid.
- Bounds: 33.0 x 33.0 x 85.0 mm.
- Volume: 29440.921 mm3.

Important limitations
This was reconstructed from a raster image, not from the original CAD file. The
image has no hidden lines, so the bore depth and the exact R3 fillet locations
are interpretations. Material EN19 and raw stock D36x88 are drawing notes only;
no material is assigned in the STEP file. If you have the original DXF/DWG or a
clearer view with hidden lines, send it and I can tighten the reconstruction.

To change any interpreted dimension, edit parameters.json and rerun
build_spindle.py with the project Python environment.

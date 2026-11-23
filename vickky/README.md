# vickky — local workspace

This folder keeps local launcher changes, inserted drawings, component libraries, and generated outputs organized in self-contained project folders.

## Layout

```
vickky/
├── launch.ps1          # local launcher: starts Ollama + repo server, opens the UI
├── 開啟本地AI.cmd       # double-click entry point for launch.ps1
├── front_knuckle/      # suspension upright knuckle: source PDF + build script + STEP/STL outputs
├── pci_bracket/        # PCI bracket blank: source DXF + reproducible build + STEP/STL outputs
├── piping_assembly/    # Ship Piping System SP-001: 10-sheet drawings + assembly & component CAD
├── spindle/            # lathe spindle: source drawing/OCR + reproducible build + STEP/STL outputs
├── submarine/          # submarine compartment: source DXF + multiview reconstructed models
└── studio-data/        # session history and drawing analysis caches
```

Each project folder keeps its **source/** drawings together with the build script, parameters, reports, and exported STEP/STL/preview files, so a part can be rebuilt without hunting for its inputs. See each project's files for assumptions, parameters, and verification notes.

## Projects

1. **front_knuckle**:
   - Source: `source/2_front_knuckle_clean.pdf`
   - Script: `build_front_knuckle.py`
   - Exports: `front_knuckle.step`, `front_knuckle.stl`, and rendered previews.
2. **piping_assembly**:
   - Source: `source/Piping_Assembly_Detailed_Drawings.pdf`, `source/piping_assembly.jpg`
   - Scripts: `build_piping_assembly.py`, `build_detailed_assembly.py`, `render_detailed_views.py`
   - Exports: `piping_assembly_detailed.step`, `piping_assembly_detailed.stl`, and individual component models in `components/`.
3. **pci_bracket**:
   - Source: `source/PCI Bracket Blank.dxf`
   - Script: `build_bracket.py`
   - Exports: `pci_bracket_blank.step`, `pci_bracket_blank.stl`.
4. **spindle**:
   - Source: `source/1_spindle_clean.png`, `source/image_ocr.txt`
   - Script: `build_spindle.py`
   - Exports: `spindle.step`, `spindle.stl`.
5. **submarine**:
   - Source: `source/submarine_compartment_2D.dxf`
   - Exports: `submarine_compartment_detailed.step`, `submarine_compartment_detailed.stl`.

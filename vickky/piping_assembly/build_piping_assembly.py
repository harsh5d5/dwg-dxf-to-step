"""Rebuild Ship Piping System / Piping Assembly from SP-001 drawing.

Faithfully reconstructed from the engineering drawing:
- Project: Ship Piping System
- Drawing Title: Piping Assembly – 2D Drawing
- Drawing No.: SP-001
- Date: 2025-11-20
- Printed Dimensions:
    - Overall Length: 2500.0 mm (600 mm + 1200 mm + 700 mm)
    - Overall Height: 1200.0 mm (from ground Z=0 to top flange & handwheel)
    - Transverse Span: 900.0 mm (including Tee branch flange)
    - Flange Diameter: 400.0 mm (8 bolt holes, PCD 320 mm)
    - Main Pipe Diameter: DN200 (OD 220 mm, ID 200 mm)
- Parts List (BOM Parts 1-9):
    1. Pipe (Carbon Steel) - Main horizontal spool
    2. Elbow 90° (Carbon Steel) - Long radius 90° elbow
    3. Flange (Carbon Steel) - Ø400 mm, 8 bolt holes
    4. Motor / Drive (Cast Iron) - Finned housing, terminal box, fan cowl, mounting feet
    5. Reducer (Carbon Steel) - Conical reducer transition
    6. Valve (Carbon Steel) - Gate valve body, bonnet, gland
    7. Support (Carbon Steel) - Support 1 stanchion (X=600) + Support 2 A-frame (X=1800)
    8. Tee (Carbon Steel) - 90° branch outlet with flange (X=1350)
    9. Handwheel (Carbon Steel) - 4-spoke control wheel at Z=1200 mm
"""
import os
import json
import math
from pathlib import Path

ROOT = Path(__file__).parent
os.environ['CADGEN_CACHE_DIR'] = str(ROOT / '.cache')
from cadgen import build123d as b

P = json.loads((ROOT / 'parameters.json').read_text(encoding='utf8'))
D = P['printed_dimensions']
A = b.Align


def box(x, y, z, dx, dy, dz):
    return b.Box(dx, dy, dz, align=(A.MIN, A.MIN, A.MIN)).moved(b.Location((x, y, z)))


def cylinder_x(x, y, z, radius, length):
    c = b.Cylinder(radius, length, rotation=b.Rotation(0, 90, 0), align=(A.CENTER, A.CENTER, A.CENTER))
    return c.moved(b.Location((x, y, z)))


def cylinder_y(x, y, z, radius, length):
    c = b.Cylinder(radius, length, rotation=b.Rotation(90, 0, 0), align=(A.CENTER, A.CENTER, A.CENTER))
    return c.moved(b.Location((x, y, z)))


def cylinder_z(x, y, z, radius, height):
    c = b.Cylinder(radius, height, align=(A.CENTER, A.CENTER, A.MIN))
    return c.moved(b.Location((x, y, z)))


def make_flange(x, y, z, axis='x', od=400, id_bore=200, thickness=36, pcd=320, n_bolts=8, bolt_dia=25):
    """Create standard ANSI/DIN 8-bolt flange."""
    if axis == 'x':
        fl = cylinder_x(x, y, z, od / 2.0, thickness)
        fl = fl.cut(cylinder_x(x, y, z, id_bore / 2.0, thickness + 4))
        for i in range(n_bolts):
            ang = 2 * math.pi * i / n_bolts
            by = y + (pcd / 2.0) * math.cos(ang)
            bz = z + (pcd / 2.0) * math.sin(ang)
            fl = fl.cut(cylinder_x(x, by, bz, bolt_dia / 2.0, thickness + 4))
    elif axis == 'y':
        fl = cylinder_y(x, y, z, od / 2.0, thickness)
        fl = fl.cut(cylinder_y(x, y, z, id_bore / 2.0, thickness + 4))
        for i in range(n_bolts):
            ang = 2 * math.pi * i / n_bolts
            bx = x + (pcd / 2.0) * math.cos(ang)
            bz = z + (pcd / 2.0) * math.sin(ang)
            fl = fl.cut(cylinder_y(bx, y, bz, bolt_dia / 2.0, thickness + 4))
    elif axis == 'z':
        fl = cylinder_z(x, y, z - thickness / 2.0, od / 2.0, thickness)
        fl = fl.cut(cylinder_z(x, y, z - thickness / 2.0 - 2, id_bore / 2.0, thickness + 4))
        for i in range(n_bolts):
            ang = 2 * math.pi * i / n_bolts
            bx = x + (pcd / 2.0) * math.cos(ang)
            by = y + (pcd / 2.0) * math.sin(ang)
            fl = fl.cut(cylinder_z(bx, by, z - thickness / 2.0 - 2, bolt_dia / 2.0, thickness + 4))
    return fl


def model():
    Z_pipe = 450.0  # Centerline elevation of horizontal pipe run
    r_pipe = 110.0  # Outer radius of DN200 pipe (Ø220 mm)
    r_bore = 100.0  # Inner radius of DN200 pipe (Ø200 mm)

    # -------------------------------------------------------------
    # 1. Vertical Inlet Spool & Top Flange (Part 3) at Z = 1200 mm
    # -------------------------------------------------------------
    flange_inlet = make_flange(100.0, 0.0, 1200.0 - 18.0, axis='z', od=400, id_bore=200, thickness=36)
    inlet_pipe = cylinder_z(100.0, 0.0, 750.0, r_pipe, 1164.0 - 750.0)
    inlet_pipe = inlet_pipe.cut(cylinder_z(100.0, 0.0, 745.0, r_bore, 1170.0 - 745.0))
    assembly = flange_inlet.fuse(inlet_pipe).clean()

    # -------------------------------------------------------------
    # 2. 90° Long Radius Elbow (Part 2) connecting (100, 750) to (400, 450)
    # -------------------------------------------------------------
    with b.BuildPart() as elbow_outer:
        with b.BuildLine(b.Plane.XZ) as path:
            b.RadiusArc((400.0, Z_pipe), (100.0, 750.0), radius=300.0)
        with b.BuildSketch(b.Plane.YZ.offset(400.0)):
            with b.Locations((0.0, Z_pipe)):
                b.Circle(r_pipe)
        b.sweep(path=path.line)

    with b.BuildPart() as elbow_inner:
        with b.BuildLine(b.Plane.XZ) as path:
            b.RadiusArc((400.0, Z_pipe), (100.0, 750.0), radius=300.0)
        with b.BuildSketch(b.Plane.YZ.offset(400.0)):
            with b.Locations((0.0, Z_pipe)):
                b.Circle(r_bore)
        b.sweep(path=path.line)

    elbow = elbow_outer.part.cut(elbow_inner.part).clean()
    assembly = assembly.fuse(elbow).clean()

    # -------------------------------------------------------------
    # 3. Flanged Joint at Elbow Outlet (Part 3)
    # -------------------------------------------------------------
    flange_elbow_out = make_flange(400.0 + 18.0, 0.0, Z_pipe, axis='x', od=400, id_bore=200, thickness=36)
    flange_valve_in = make_flange(400.0 + 54.0, 0.0, Z_pipe, axis='x', od=400, id_bore=200, thickness=36)
    assembly = assembly.fuse(flange_elbow_out).fuse(flange_valve_in).clean()

    # Short spool between flange and valve
    spool1 = cylinder_x((472.0 + 650.0) / 2.0, 0.0, Z_pipe, r_pipe, 650.0 - 472.0)
    spool1 = spool1.cut(cylinder_x((472.0 + 650.0) / 2.0, 0.0, Z_pipe, r_bore, 660.0 - 462.0))
    assembly = assembly.fuse(spool1).clean()

    # -------------------------------------------------------------
    # 4. Support 1 (Part 7) at X = 600 mm (Stanchion column + saddle)
    # -------------------------------------------------------------
    sup1_base = box(600.0 - 100.0, -100.0, 0.0, 200.0, 200.0, 20.0)
    sup1_col = cylinder_z(600.0, 0.0, 20.0, 45.0, Z_pipe - r_pipe - 20.0 + 5.0)
    sup1_saddle = cylinder_x(600.0, 0.0, Z_pipe, r_pipe + 15.0, 80.0)
    sup1_saddle = sup1_saddle.cut(cylinder_x(600.0, 0.0, Z_pipe, r_pipe, 90.0))
    sup1_saddle = sup1_saddle.cut(box(600.0 - 50.0, -150.0, Z_pipe, 100.0, 300.0, 200.0))
    support1 = sup1_base.fuse(sup1_col).fuse(sup1_saddle).clean()
    assembly = assembly.fuse(support1).clean()

    # -------------------------------------------------------------
    # 5. Gate Valve (Part 6) & Handwheel (Part 9)
    # -------------------------------------------------------------
    flange_v_left = make_flange(650.0 + 18.0, 0.0, Z_pipe, axis='x', od=400, id_bore=200, thickness=36)
    flange_v_right = make_flange(850.0 - 18.0, 0.0, Z_pipe, axis='x', od=400, id_bore=200, thickness=36)
    valve_body = cylinder_x(750.0, 0.0, Z_pipe, 140.0, 850.0 - 650.0)
    valve_body = valve_body.cut(cylinder_x(750.0, 0.0, Z_pipe, r_bore, 860.0 - 640.0))

    valve_bonnet = cylinder_z(750.0, 0.0, Z_pipe + 100.0, 80.0, 1050.0 - (Z_pipe + 100.0))
    valve_gland = cylinder_z(750.0, 0.0, 1050.0, 110.0, 50.0)
    valve_stem = cylinder_z(750.0, 0.0, 1100.0, 20.0, 1200.0 - 1100.0)

    hw_hub = cylinder_z(750.0, 0.0, 1175.0, 40.0, 25.0)
    hw_rim_outer = cylinder_z(750.0, 0.0, 1175.0, 180.0, 25.0)
    hw_rim_inner = cylinder_z(750.0, 0.0, 1170.0, 155.0, 35.0)
    hw_rim = hw_rim_outer.cut(hw_rim_inner)
    spoke_x = box(750.0 - 165.0, -12.0, 1175.0, 330.0, 24.0, 20.0)
    spoke_y = box(750.0 - 12.0, -165.0, 1175.0, 24.0, 330.0, 20.0)
    handwheel = hw_hub.fuse(hw_rim).fuse(spoke_x).fuse(spoke_y).clean()

    valve_assembly = valve_body.fuse(flange_v_left).fuse(flange_v_right).fuse(valve_bonnet).fuse(valve_gland).fuse(valve_stem).fuse(handwheel).clean()
    assembly = assembly.fuse(valve_assembly).clean()

    # Flange connecting valve to main pipe
    flange_main_in = make_flange(850.0 + 18.0, 0.0, Z_pipe, axis='x', od=400, id_bore=200, thickness=36)
    assembly = assembly.fuse(flange_main_in).clean()

    # -------------------------------------------------------------
    # 6. Main Horizontal Pipe Spool (Part 1) & Tee Branch (Part 8)
    # -------------------------------------------------------------
    # Main horizontal run from X = 868 to X = 1800
    main_pipe = cylinder_x((868.0 + 1800.0) / 2.0, 0.0, Z_pipe, r_pipe, 1800.0 - 868.0)
    main_bore = cylinder_x((868.0 + 1800.0) / 2.0, 0.0, Z_pipe, r_bore, 1810.0 - 858.0)
    main_pipe = main_pipe.cut(main_bore)

    # Tee branch at X = 1350 mm extending into -Y direction
    tee_x = 1350.0
    tee_y_end = -300.0
    tee_branch = cylinder_y(tee_x, tee_y_end / 2.0, Z_pipe, r_pipe, abs(tee_y_end))
    tee_bore = cylinder_y(tee_x, (tee_y_end - 10.0) / 2.0, Z_pipe, r_bore, abs(tee_y_end) + 20.0)
    tee_branch = tee_branch.cut(tee_bore)
    tee_flange = make_flange(tee_x, tee_y_end - 18.0, Z_pipe, axis='y', od=400, id_bore=200, thickness=36)
    tee_assembly = tee_branch.fuse(tee_flange).clean()

    main_spool = main_pipe.fuse(tee_assembly).clean()
    main_spool = main_spool.cut(cylinder_x(tee_x, 0.0, Z_pipe, r_bore, 300.0))
    assembly = assembly.fuse(main_spool).clean()

    # -------------------------------------------------------------
    # 7. Support 2 (Part 7) at X = 1800 mm (A-frame legs + cradle)
    # -------------------------------------------------------------
    flange_sup2_left = make_flange(1800.0 - 18.0, 0.0, Z_pipe, axis='x', od=400, id_bore=200, thickness=36)
    flange_sup2_right = make_flange(1800.0 + 18.0, 0.0, Z_pipe, axis='x', od=400, id_bore=200, thickness=36)
    assembly = assembly.fuse(flange_sup2_left).fuse(flange_sup2_right).clean()

    sup2_base = box(1800.0 - 60.0, -180.0, 0.0, 120.0, 360.0, 20.0)
    leg1 = box(1800.0 - 20.0, -140.0, 20.0, 40.0, 35.0, Z_pipe - r_pipe - 20.0 + 5.0)
    leg2 = box(1800.0 - 20.0, 105.0, 20.0, 40.0, 35.0, Z_pipe - r_pipe - 20.0 + 5.0)
    cradle = cylinder_x(1800.0, 0.0, Z_pipe, r_pipe + 15.0, 80.0)
    cradle = cradle.cut(cylinder_x(1800.0, 0.0, Z_pipe, r_pipe, 90.0))
    cradle = cradle.cut(box(1800.0 - 45.0, -150.0, Z_pipe, 90.0, 300.0, 200.0))
    support2 = sup2_base.fuse(leg1).fuse(leg2).fuse(cradle).clean()
    assembly = assembly.fuse(support2).clean()

    # -------------------------------------------------------------
    # 8. Conical Reducer (Part 5) from X = 1836 to X = 2000 mm
    # -------------------------------------------------------------
    with b.BuildPart() as red_part:
        with b.BuildSketch(b.Plane.YZ.offset(1836.0)):
            with b.Locations((0.0, Z_pipe)):
                b.Circle(110.0)
        with b.BuildSketch(b.Plane.YZ.offset(2000.0)):
            with b.Locations((0.0, Z_pipe)):
                b.Circle(80.0)
        b.loft()
    reducer = red_part.part
    with b.BuildPart() as red_bore_part:
        with b.BuildSketch(b.Plane.YZ.offset(1834.0)):
            with b.Locations((0.0, Z_pipe)):
                b.Circle(100.0)
        with b.BuildSketch(b.Plane.YZ.offset(2002.0)):
            with b.Locations((0.0, Z_pipe)):
                b.Circle(70.0)
        b.loft()
    reducer = reducer.cut(red_bore_part.part).clean()
    flange_reducer = make_flange(2000.0 - 15.0, 0.0, Z_pipe, axis='x', od=340, id_bore=140, thickness=30, pcd=280, n_bolts=8, bolt_dia=20)
    reducer = reducer.fuse(flange_reducer).clean()
    assembly = assembly.fuse(reducer).clean()

    # -------------------------------------------------------------
    # 9. Motor / Drive Unit (Part 4) from X = 2000 to X = 2500 mm
    # -------------------------------------------------------------
    motor_flange = cylinder_x(2015.0, 0.0, Z_pipe, 170.0, 30.0)
    motor_body = cylinder_x(2235.0, 0.0, Z_pipe, 160.0, 410.0)
    fins = []
    for i in range(12):
        ang = 2 * math.pi * i / 12
        if 0.3 * math.pi < ang < 0.7 * math.pi:
            continue
        if 1.3 * math.pi < ang < 1.7 * math.pi:
            continue
        fy = 165.0 * math.cos(ang)
        fz = Z_pipe + 165.0 * math.sin(ang)
        fin = box(2050.0, fy - 6.0, fz - 6.0, 370.0, 12.0, 12.0)
        fins.append(fin)
    for fin in fins:
        motor_body = motor_body.fuse(fin)

    term_box = box(2180.0, -60.0, Z_pipe + 155.0, 120.0, 120.0, 75.0)
    term_lid = box(2175.0, -65.0, Z_pipe + 225.0, 130.0, 130.0, 15.0)
    term_box = term_box.fuse(term_lid)

    # Motor feet resting on ground Z=0, extending up into motor stator body
    foot_left_bracket = box(2080.0, -170.0, 20.0, 310.0, 40.0, 400.0)
    foot_right_bracket = box(2080.0, 130.0, 20.0, 310.0, 40.0, 400.0)
    foot_left_pad = box(2050.0, -200.0, 0.0, 370.0, 90.0, 20.0)
    foot_right_pad = box(2050.0, 110.0, 0.0, 370.0, 90.0, 20.0)
    motor_feet = foot_left_bracket.fuse(foot_right_bracket).fuse(foot_left_pad).fuse(foot_right_pad).clean()

    fan_cowl = cylinder_x(2470.0, 0.0, Z_pipe, 155.0, 60.0)
    fan_dome = cylinder_x(2495.0, 0.0, Z_pipe, 140.0, 10.0)
    fan_cowl = fan_cowl.fuse(fan_dome)

    motor = motor_flange.fuse(motor_body).fuse(term_box).fuse(motor_feet).fuse(fan_cowl).clean()
    assembly = assembly.fuse(motor).clean()

    # Direct export STEP and STL
    step_path = ROOT / 'piping_assembly.step'
    stl_path = ROOT / 'piping_assembly.stl'
    b.export_step(assembly, str(step_path))
    b.export_stl(assembly, str(stl_path), tolerance=0.0005)

    bounds = assembly.bounding_box().size
    solid_count = len(assembly.solids())
    is_valid = bool(assembly.is_valid if isinstance(assembly.is_valid, bool) else assembly.is_valid())
    volume = round(assembly.volume, 2)

    report = {
        'title': P['title'],
        'project': P['project'],
        'drawing_no': P['drawing_no'],
        'date': P.get('date', '2025-11-20'),
        'drawn_by': P.get('drawn_by', 'Rohit Shimpi'),
        'units': 'mm',
        'printed_dimensions': D,
        'bounds_mm': [round(bounds.X, 2), round(bounds.Y, 2), round(bounds.Z, 2)],
        'solid_count': solid_count,
        'valid': is_valid,
        'volume_mm3': volume,
        'parts_list': P['parts_list']
    }
    (ROOT / 'piping_assembly_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf8')
    print(f'Piping Assembly Built Successfully: {bounds.X:.1f} x {bounds.Y:.1f} x {bounds.Z:.1f} mm, Solids={solid_count}, Volume={volume:.1f} mm3')
    return assembly


if __name__ == '__main__':
    model()

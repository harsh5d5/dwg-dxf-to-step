"""Build 3D CAD models for Ship Piping System from Piping_Assembly_Detailed_Drawings.pdf.

Builds both:
1. Individual high-precision CAD models for each component (Items 1 to 9).
2. Complete unified Ship Piping System assembly (SP-001).

Faithfully parameterized from the 10-Sheet detailed drawings booklet:
- Sheet 01: Assembly SP-001 (Overall 2500 mm length, 1200 mm height, CL=400 mm)
- Sheet 02: Item 1 - PIPE (Flanged spool, L=900 mm, Ø220x10 wall, Ø340 flanges)
- Sheet 03: Item 2 - ELBOW 90° (R250 CL radius, Ø220x10 wall, 660 mm x 880 mm legs)
- Sheet 04: Item 3 - FLANGE (Ø340 OD, t=30 mm, 12x Ø22 on PCD Ø295, Ø200 bore)
- Sheet 05: Item 4 - MOTOR (L=440 mm, Ø400 body, Ø360 cowl, base 400x420x25 mm, CL=400 mm)
- Sheet 06: Item 5 - REDUCER (L=170 mm, Ø220->Ø170 OD, Ø340 flange to Ø285 flange)
- Sheet 07: Item 6 - VALVE (L=300 mm, Ø340 flanges, Ø280 body, Ø160 bonnet, Ø36 stem, H=700 mm)
- Sheet 08: Item 7 - SUPPORT (H=290 mm to saddle, Ø100 column, 220x220 base pad, 4x Ø18 holes)
- Sheet 09: Item 8 - TEE (L=600 mm run, 300 mm branch, Ø220x10 wall, Ø200 bore)
- Sheet 10: Item 9 - HANDWHEEL (Ø350 OD, Ø300 ID, 6 spokes 14 mm wide, Ø70 hub, Ø36 bore)
"""
import os
import json
import math
from pathlib import Path

ROOT = Path(__file__).parent
COMP_DIR = ROOT / 'components'
COMP_DIR.mkdir(parents=True, exist_ok=True)

os.environ['CADGEN_CACHE_DIR'] = str(ROOT / '.cache')
from cadgen import build123d as b

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


# =========================================================================
# Item 3: Standard Flange (Sheet 4)
# =========================================================================
def make_standard_flange(x=0, y=0, z=0, axis='x', od=340.0, id_bore=200.0, thickness=30.0, pcd=295.0, n_bolts=12, bolt_dia=22.0):
    """Sheet 4: Standard Flange Ø340, t=30, 12x Ø22 on PCD 295, Ø200 bore."""
    if axis == 'x':
        fl = cylinder_x(x, y, z, od / 2.0, thickness)
        fl = fl.cut(cylinder_x(x, y, z, id_bore / 2.0, thickness + 4.0))
        for i in range(n_bolts):
            ang = 2 * math.pi * i / n_bolts
            by = y + (pcd / 2.0) * math.cos(ang)
            bz = z + (pcd / 2.0) * math.sin(ang)
            fl = fl.cut(cylinder_x(x, by, bz, bolt_dia / 2.0, thickness + 4.0))
    elif axis == 'y':
        fl = cylinder_y(x, y, z, od / 2.0, thickness)
        fl = fl.cut(cylinder_y(x, y, z, id_bore / 2.0, thickness + 4.0))
        for i in range(n_bolts):
            ang = 2 * math.pi * i / n_bolts
            bx = x + (pcd / 2.0) * math.cos(ang)
            bz = z + (pcd / 2.0) * math.sin(ang)
            fl = fl.cut(cylinder_y(bx, y, bz, bolt_dia / 2.0, thickness + 4.0))
    elif axis == 'z':
        fl = cylinder_z(x, y, z - thickness / 2.0, od / 2.0, thickness)
        fl = fl.cut(cylinder_z(x, y, z - thickness / 2.0 - 2.0, id_bore / 2.0, thickness + 4.0))
        for i in range(n_bolts):
            ang = 2 * math.pi * i / n_bolts
            bx = x + (pcd / 2.0) * math.cos(ang)
            by = y + (pcd / 2.0) * math.sin(ang)
            fl = fl.cut(cylinder_z(bx, by, z - thickness / 2.0 - 2.0, bolt_dia / 2.0, thickness + 4.0))
    return fl


# =========================================================================
# Item 1: Pipe (Sheet 2)
# =========================================================================
def build_item1_pipe():
    """Sheet 2: Flanged Pipe Spool L=900 mm, Ø220x10 wall, Ø340 flanges."""
    L = 900.0
    t_flange = 30.0
    r_pipe = 110.0
    r_bore = 100.0

    body = cylinder_x(L / 2.0, 0, 0, r_pipe, L - 2 * t_flange)
    flange_left = make_standard_flange(t_flange / 2.0, 0, 0, axis='x')
    flange_right = make_standard_flange(L - t_flange / 2.0, 0, 0, axis='x')
    pipe = body.fuse(flange_left).fuse(flange_right).clean()
    pipe = pipe.cut(cylinder_x(L / 2.0, 0, 0, r_bore, L + 20.0))
    return pipe.clean()


# =========================================================================
# Item 2: Elbow 90° (Sheet 3)
# =========================================================================
def build_item2_elbow():
    """Sheet 3: Elbow 90°, R250 centerline, Ø220x10 wall, 660 mm x 880 mm."""
    r_pipe = 110.0
    r_bore = 100.0
    R_cl = 250.0

    # Horizontal leg straight: 660 - 250 = 410 mm
    # Vertical leg straight: 880 - 250 = 630 mm
    with b.BuildPart() as elbow_outer:
        with b.BuildLine(b.Plane.XZ) as path:
            l1 = b.Line((R_cl + 410.0, 0.0), (R_cl, 0.0))
            a1 = b.RadiusArc((R_cl, 0.0), (0.0, R_cl), radius=R_cl)
            l2 = b.Line((0.0, R_cl), (0.0, R_cl + 630.0))
        with b.BuildSketch(b.Plane.YZ.offset(R_cl + 410.0)):
            with b.Locations((0.0, 0.0)):
                b.Circle(r_pipe)
        b.sweep(path=path.line)

    with b.BuildPart() as elbow_inner:
        with b.BuildLine(b.Plane.XZ) as path:
            l1 = b.Line((R_cl + 415.0, 0.0), (R_cl, 0.0))
            a1 = b.RadiusArc((R_cl, 0.0), (0.0, R_cl), radius=R_cl)
            l2 = b.Line((0.0, R_cl), (0.0, R_cl + 635.0))
        with b.BuildSketch(b.Plane.YZ.offset(R_cl + 415.0)):
            with b.Locations((0.0, 0.0)):
                b.Circle(r_bore)
        b.sweep(path=path.line)

    elbow = elbow_outer.part.cut(elbow_inner.part).clean()
    return elbow


# =========================================================================
# Item 4: Motor (Sheet 5)
# =========================================================================
def build_item4_motor():
    """Sheet 5: Motor unit L=440 mm, Ø400 body, Ø360 fan cover, base 400x420x25 mm."""
    # Stator center at (190, 0, 400)
    # Total length: 20 flange + 340 body + 80 fan cover = 440 mm
    flange = cylinder_x(10.0, 0, 400.0, 285.0 / 2.0, 20.0)
    body = cylinder_x(20.0 + 170.0, 0, 400.0, 200.0, 340.0)
    cowl = cylinder_x(360.0 + 40.0, 0, 400.0, 180.0, 80.0)

    # Base: 400 wide (Y: -200 to 200) x 420 long (X: 10 to 430) x 25 thick (Z: 0 to 25)
    base_plate = box(10.0, -200.0, 0.0, 420.0, 400.0, 25.0)

    # Mounting legs from base (Z=20) to stator body (Z=400)
    leg_left = box(30.0, -180.0, 20.0, 380.0, 60.0, 380.0)
    leg_right = box(30.0, 120.0, 20.0, 380.0, 60.0, 380.0)

    # Terminal box 140 x 140 x 70 on top of stator (Z: 595 to 670)
    tbox = box(20.0 + 100.0, -70.0, 595.0, 140.0, 140.0, 75.0)

    motor = flange.fuse(body).fuse(cowl).fuse(base_plate).fuse(leg_left).fuse(leg_right).fuse(tbox).clean()
    return motor


# =========================================================================
# Item 5: Reducer (Sheet 6)
# =========================================================================
def build_item5_reducer():
    """Sheet 6: Reducer L=170 mm, Ø220->Ø170 OD, Ø340 flange to Ø285 flange."""
    # Flange 1: at X=0 to 30 mm, OD 340 mm, bore 200 mm
    flange_large = make_standard_flange(15.0, 0, 0, axis='x', od=340.0, id_bore=200.0, thickness=30.0)

    # Conical body: from X=30 to 140 mm (length 110 mm)
    with b.BuildPart() as cone_outer:
        with b.BuildSketch(b.Plane.YZ.offset(30.0)):
            b.Circle(110.0)
        with b.BuildSketch(b.Plane.YZ.offset(140.0)):
            b.Circle(85.0)
        b.loft()

    with b.BuildPart() as cone_inner:
        with b.BuildSketch(b.Plane.YZ.offset(28.0)):
            b.Circle(100.0)
        with b.BuildSketch(b.Plane.YZ.offset(142.0)):
            b.Circle(75.0)
        b.loft()

    cone = cone_outer.part.cut(cone_inner.part).clean()

    # Flange 2: at X=140 to 170 mm, OD 285 mm, bore 150 mm
    flange_small = cylinder_x(155.0, 0, 0, 285.0 / 2.0, 30.0)
    flange_small = flange_small.cut(cylinder_x(155.0, 0, 0, 75.0, 35.0))

    reducer = flange_large.fuse(cone).fuse(flange_small).clean()
    return reducer


# =========================================================================
# Item 6: Valve (Sheet 7)
# =========================================================================
def build_item6_valve():
    """Sheet 7: Valve L=300 mm, Ø340 flanges, Ø280 body, Ø160 bonnet, Ø120 yoke, Ø36 stem, H=700 mm."""
    L = 300.0
    r_bore = 100.0

    # Flanges on both ends
    flange_in = make_standard_flange(15.0, 0, 0, axis='x')
    flange_out = make_standard_flange(L - 15.0, 0, 0, axis='x')

    # Body Ø280
    body = cylinder_x(L / 2.0, 0, 0, 140.0, L - 60.0)
    body = body.cut(cylinder_x(L / 2.0, 0, 0, r_bore, L + 20.0))

    # Bonnet Ø160, from Z=135 to 280 mm
    bonnet = cylinder_z(L / 2.0, 0, 135.0, 80.0, 150.0)

    # Yoke Ø120, from Z=275 to 400 mm
    yoke = cylinder_z(L / 2.0, 0, 275.0, 60.0, 130.0)

    # Stem Ø36, from Z=395 to 530 mm (overall height 530 from CL = 700 from bottom)
    stem = cylinder_z(L / 2.0, 0, 395.0, 18.0, 140.0)

    valve = flange_in.fuse(flange_out).fuse(body).fuse(bonnet).fuse(yoke).fuse(stem).clean()
    return valve


# =========================================================================
# Item 7: Support (Sheet 8)
# =========================================================================
def build_item7_support():
    """Sheet 8: Support H=290 mm to saddle, Ø100 column, 220x220 base pad, 4x Ø18 holes."""
    # Base pad 220 x 220 x 16 mm with 4x Ø18 holes on 160 x 160 mm pitch
    pad = box(-110.0, -110.0, 0.0, 220.0, 220.0, 16.0)
    for sx in (-80.0, 80.0):
        for sy in (-80.0, 80.0):
            hole = cylinder_z(sx, sy, -2.0, 9.0, 20.0)
            pad = pad.cut(hole)

    # Column Ø100 mm from Z=16 to Z=274 mm
    col = cylinder_z(0, 0, 16.0, 50.0, 258.0)

    # Saddle top: 100 long in X x 220 wide in Y x 30 mm thick, curved for Ø220 pipe (R=110)
    saddle = box(-50.0, -110.0, 260.0, 100.0, 220.0, 40.0)
    pipe_cut = cylinder_x(0, 0, 400.0 - (400.0 - 290.0 - 110.0 + 400.0), 110.0, 120.0)
    # The cradle radius R=110 at Z=400:
    saddle_cut = cylinder_x(0, 0, 400.0, 110.0, 120.0)
    saddle = saddle.cut(saddle_cut)

    support = pad.fuse(col).fuse(saddle).clean()
    return support


# =========================================================================
# Item 8: Tee (Sheet 9)
# =========================================================================
def build_item8_tee():
    """Sheet 9: Tee L=600 mm run, 300 mm branch, Ø220x10 wall, Ø200 bore."""
    r_pipe = 110.0
    r_bore = 100.0

    # Main run along X: 600 mm
    main_run = cylinder_x(300.0, 0, 0, r_pipe, 600.0)
    main_bore = cylinder_x(300.0, 0, 0, r_bore, 620.0)
    main_run = main_run.cut(main_bore)

    # Branch run along Y: 300 mm from centerline
    branch = cylinder_y(300.0, -150.0, 0, r_pipe, 300.0)
    branch_bore = cylinder_y(300.0, -150.0, 0, r_bore, 310.0)
    branch = branch.cut(branch_bore)

    tee = main_run.fuse(branch).clean()
    tee = tee.cut(cylinder_x(300.0, 0, 0, r_bore, 620.0))
    return tee.clean()


# =========================================================================
# Item 9: Handwheel (Sheet 10)
# =========================================================================
def build_item9_handwheel():
    """Sheet 10: Handwheel Ø350 OD, Ø300 ID, 6 spokes 14 mm wide, Ø70 hub, Ø36 bore, H=60 mm."""
    # Hub: Ø70 OD, Ø36 bore, height 60 mm (Z: -17.5 to 42.5)
    hub = cylinder_z(0, 0, -17.5, 35.0, 60.0)
    hub = hub.cut(cylinder_z(0, 0, -20.0, 18.0, 65.0))

    # Rim: Ø350 OD, Ø300 ID, height 25 mm (Z: 0 to 25)
    rim_outer = cylinder_z(0, 0, 0, 175.0, 25.0)
    rim_inner = cylinder_z(0, 0, -2.0, 150.0, 29.0)
    rim = rim_outer.cut(rim_inner)

    # 6 Spokes: 14 mm wide, 25 mm high, spaced at 60°
    spokes = []
    for i in range(3):
        ang = i * 60.0
        spoke = b.Box(350.0, 14.0, 25.0, align=(A.CENTER, A.CENTER, A.MIN)).rotate(b.Axis.Z, ang)
        spokes.append(spoke)

    handwheel = hub.fuse(rim)
    for sp in spokes:
        handwheel = handwheel.fuse(sp)
    handwheel = handwheel.cut(cylinder_z(0, 0, -20.0, 18.0, 65.0))
    return handwheel.clean()


# =========================================================================
# Complete Full Assembly (Sheet 1: SP-001)
# =========================================================================
def build_full_assembly():
    """Build the complete Ship Piping System assembly (Sheet 1: SP-001)."""
    Z_CL = 400.0  # Horizontal centerline elevation above ground
    r_pipe = 110.0
    r_bore = 100.0

    print("Building full Ship Piping System assembly...")

    # 1. Elbow Item 2 at the inlet:
    # Vertical inlet riser is at X=100. Centerline bend radius R=250.
    # Center of bend: (100 + 250, 0, Z_CL + 250) = (350, 0, 650)
    # Horizontal run comes out at Z = 400 mm, pointing along +X from X=350 + (660-250) = 760 mm?
    # Let's align with the overall dimensions:
    # Overall Length = 2500 mm (600 mm elbow to sup1, 1200 mm sup1 to sup2, 700 mm sup2 to end)

    # Inlet Flange (Item 3) at top of vertical riser (Z = 1200 mm):
    flange_inlet = make_standard_flange(100.0, 0.0, 1200.0 - 15.0, axis='z')

    # Vertical pipe from Z = 650 to 1185 mm
    vert_pipe = cylinder_z(100.0, 0.0, 650.0, r_pipe, 1185.0 - 650.0)
    vert_pipe = vert_pipe.cut(cylinder_z(100.0, 0.0, 645.0, r_bore, 1195.0 - 645.0))

    # 90° Elbow (Item 2) from (100, 0, 650) to (350, 0, 400):
    with b.BuildPart() as elbow_outer:
        with b.BuildLine(b.Plane.XZ) as path:
            b.RadiusArc((350.0, Z_CL), (100.0, 650.0), radius=250.0)
        with b.BuildSketch(b.Plane.YZ.offset(350.0)):
            with b.Locations((0.0, Z_CL)):
                b.Circle(r_pipe)
        b.sweep(path=path.line)

    with b.BuildPart() as elbow_inner:
        with b.BuildLine(b.Plane.XZ) as path:
            b.RadiusArc((350.0, Z_CL), (100.0, 650.0), radius=250.0)
        with b.BuildSketch(b.Plane.YZ.offset(350.0)):
            with b.Locations((0.0, Z_CL)):
                b.Circle(r_bore)
        b.sweep(path=path.line)

    elbow = elbow_outer.part.cut(elbow_inner.part).clean()
    assembly = flange_inlet.fuse(vert_pipe).fuse(elbow).clean()

    # Flange at elbow outlet (X = 350 to 380 mm)
    flange_elbow_out = make_standard_flange(350.0 + 15.0, 0.0, Z_CL, axis='x')
    flange_valve_in = make_standard_flange(380.0 + 15.0, 0.0, Z_CL, axis='x')
    assembly = assembly.fuse(flange_elbow_out).fuse(flange_valve_in).clean()

    # Valve (Item 6): face-to-face 300 mm (X: 395 to 695 mm)
    # Centered at X = 545 mm
    valve_body = cylinder_x(545.0, 0.0, Z_CL, 140.0, 240.0)
    valve_body = valve_body.cut(cylinder_x(545.0, 0.0, Z_CL, r_bore, 260.0))
    valve_bonnet = cylinder_z(545.0, 0.0, Z_CL + 140.0, 80.0, 140.0)
    valve_yoke = cylinder_z(545.0, 0.0, Z_CL + 280.0, 60.0, 120.0)
    valve_stem = cylinder_z(545.0, 0.0, Z_CL + 400.0, 18.0, 270.0)  # Reaches Z = 1070 mm

    flange_valve_out = make_standard_flange(695.0 + 15.0, 0.0, Z_CL, axis='x')
    flange_pipe_in = make_standard_flange(725.0 + 15.0, 0.0, Z_CL, axis='x')

    # Handwheel (Item 9) on top of valve stem at Z = 1070 mm
    hw_hub = cylinder_z(545.0, 0.0, Z_CL + 670.0 - 30.0, 35.0, 60.0)
    hw_rim_out = cylinder_z(545.0, 0.0, Z_CL + 670.0 - 10.0, 175.0, 25.0)
    hw_rim_in = cylinder_z(545.0, 0.0, Z_CL + 670.0 - 15.0, 150.0, 35.0)
    hw_rim = hw_rim_out.cut(hw_rim_in)
    spokes = []
    for i in range(3):
        ang = i * 60.0
        sp = b.Box(350.0, 14.0, 25.0, align=(A.CENTER, A.CENTER, A.MIN)).rotate(b.Axis.Z, ang).moved(
            b.Location((545.0, 0.0, Z_CL + 670.0 - 10.0)))
        spokes.append(sp)
    handwheel = hw_hub.fuse(hw_rim)
    for sp in spokes:
        handwheel = handwheel.fuse(sp)

    valve_assembly = valve_body.fuse(valve_bonnet).fuse(valve_yoke).fuse(valve_stem).fuse(flange_valve_out).fuse(flange_pipe_in).fuse(handwheel).clean()
    assembly = assembly.fuse(valve_assembly).clean()

    # Support 1 (Item 7) at X = 600 mm (under the valve/spool run)
    sup1 = build_item7_support().moved(b.Location((600.0, 0.0, 0.0)))
    assembly = assembly.fuse(sup1).clean()

    # Main Pipe Spool (Item 1): from X = 740 to 1800 mm
    # Incorporates Tee (Item 8) at X = 1270 mm
    pipe_left = cylinder_x((740.0 + 1120.0) / 2.0, 0.0, Z_CL, r_pipe, 1120.0 - 740.0)
    pipe_left = pipe_left.cut(cylinder_x((740.0 + 1120.0) / 2.0, 0.0, Z_CL, r_bore, 1130.0 - 730.0))

    # Tee at X = 1270 mm (length 300 mm run, 300 mm branch into -Y)
    tee_run = cylinder_x(1270.0, 0.0, Z_CL, r_pipe, 300.0)
    tee_run = tee_run.cut(cylinder_x(1270.0, 0.0, Z_CL, r_bore, 310.0))
    tee_branch = cylinder_y(1270.0, -150.0, Z_CL, r_pipe, 300.0)
    tee_branch = tee_branch.cut(cylinder_y(1270.0, -150.0, Z_CL, r_bore, 310.0))
    tee_flange = make_standard_flange(1270.0, -300.0 - 15.0, Z_CL, axis='y')
    tee = tee_run.fuse(tee_branch).fuse(tee_flange).clean()
    tee = tee.cut(cylinder_x(1270.0, 0.0, Z_CL, r_bore, 320.0))

    pipe_right = cylinder_x((1420.0 + 1800.0) / 2.0, 0.0, Z_CL, r_pipe, 1800.0 - 1420.0)
    pipe_right = pipe_right.cut(cylinder_x((1420.0 + 1800.0) / 2.0, 0.0, Z_CL, r_bore, 1810.0 - 1410.0))

    assembly = assembly.fuse(pipe_left).fuse(tee).fuse(pipe_right).clean()

    # Support 2 (Item 7) at X = 1800 mm
    sup2 = build_item7_support().moved(b.Location((1800.0, 0.0, 0.0)))
    assembly = assembly.fuse(sup2).clean()

    # Flange pair at Support 2 / Reducer inlet (X = 1800 to 1860 mm)
    flange_sup2_l = make_standard_flange(1800.0 - 15.0, 0.0, Z_CL, axis='x')
    flange_sup2_r = make_standard_flange(1800.0 + 15.0, 0.0, Z_CL, axis='x')
    assembly = assembly.fuse(flange_sup2_l).fuse(flange_sup2_r).clean()

    # Reducer (Item 5): from X = 1860 to 2030 mm (length 170 mm)
    reducer = build_item5_reducer().moved(b.Location((1860.0, 0.0, Z_CL)))
    assembly = assembly.fuse(reducer).clean()

    # Motor (Item 4): from X = 2030 to 2470 mm (length 440 mm)
    motor = build_item4_motor().moved(b.Location((2030.0, 0.0, 0.0)))
    assembly = assembly.fuse(motor).clean()

    return assembly.clean()


def run():
    print("=" * 60)
    print("BUILDING DETAILED COMPONENTS (Items 1 to 9)")
    print("=" * 60)

    components = {
        'item1_pipe': build_item1_pipe,
        'item2_elbow': build_item2_elbow,
        'item3_flange': make_standard_flange,
        'item4_motor': build_item4_motor,
        'item5_reducer': build_item5_reducer,
        'item6_valve': build_item6_valve,
        'item7_support': build_item7_support,
        'item8_tee': build_item8_tee,
        'item9_handwheel': build_item9_handwheel,
    }

    comp_reports = {}
    for name, builder in components.items():
        part = builder()
        step_file = COMP_DIR / f'{name}.step'
        stl_file = COMP_DIR / f'{name}.stl'
        b.export_step(part, str(step_file))
        b.export_stl(part, str(stl_file), tolerance=0.0005)
        bb = part.bounding_box().size
        valid = bool(part.is_valid if isinstance(part.is_valid, bool) else part.is_valid())
        comp_reports[name] = {
            'step': f'components/{name}.step',
            'stl': f'components/{name}.stl',
            'bounds_mm': [round(bb.X, 2), round(bb.Y, 2), round(bb.Z, 2)],
            'volume_mm3': round(part.volume, 2),
            'solids': len(part.solids()),
            'valid': valid
        }
        print(f"  [OK] {name}: {bb.X:.1f} x {bb.Y:.1f} x {bb.Z:.1f} mm, Volume={part.volume:.1f} mm3, Solids={len(part.solids())}")

    (COMP_DIR / 'components_manifest.json').write_text(json.dumps(comp_reports, indent=2), encoding='utf8')

    print("=" * 60)
    print("BUILDING FULL SHIP PIPING SYSTEM ASSEMBLY (SP-001)")
    print("=" * 60)
    assembly = build_full_assembly()
    step_out = ROOT / 'piping_assembly_detailed.step'
    stl_out = ROOT / 'piping_assembly_detailed.stl'
    b.export_step(assembly, str(step_out))
    b.export_stl(assembly, str(stl_out), tolerance=0.0005)

    bounds = assembly.bounding_box().size
    valid = bool(assembly.is_valid if isinstance(assembly.is_valid, bool) else assembly.is_valid())
    assembly_report = {
        'title': 'Ship Piping System - Detailed Production Assembly',
        'drawing_no': 'SP-001 (Sheets 1 to 10)',
        'source_pdf': 'vickky/Piping_Assembly_Detailed_Drawings.pdf',
        'overall_bounds_mm': [round(bounds.X, 2), round(bounds.Y, 2), round(bounds.Z, 2)],
        'volume_mm3': round(assembly.volume, 2),
        'solid_count': len(assembly.solids()),
        'valid': valid,
        'components': comp_reports
    }
    (ROOT / 'assembly_report_detailed.json').write_text(json.dumps(assembly_report, indent=2), encoding='utf8')
    print(f"Assembly Complete: {bounds.X:.1f} x {bounds.Y:.1f} x {bounds.Z:.1f} mm, Solids={len(assembly.solids())}, Volume={assembly.volume:.1f} mm3, Valid={valid}")


if __name__ == '__main__':
    run()

"""Rebuild FRONT KNUCKLE from source/2_front_knuckle_clean.png / 2_front_knuckle_clean.pdf.

Reconstructed faithfully from the engineering drawing:
- Part: FRONT KNUCKLE (Suspension Upright)
- Material: AL 7075 T6
- Raw Material Dimensions: 105 x 130 x 80 mm
- Printed Dimensions:
    - Overall Height: 129.66 mm
    - Top Width: 28.00 mm
    - Main Bearing Bore: Ø25.00 mm
    - Caliper Mounting Holes (2x): Ø8.00 mm
"""
import os
import json
from pathlib import Path

ROOT = Path(__file__).parent
os.environ['CADGEN_CACHE_DIR'] = str(ROOT / '.cache')
(ROOT / '.cache').mkdir(parents=True, exist_ok=True)

from cadgen import build123d as b, step, stl

P = json.loads((ROOT / 'parameters.json').read_text(encoding='utf8'))
D = P['printed_dimensions']
I = P['interpreted_dimensions']
A = b.Align


def box(x, y, z, dx, dy, dz):
    return b.Box(dx, dy, dz, align=(A.MIN, A.MIN, A.MIN)).moved(b.Location((x, y, z)))


def cylinder_y(x, y, z, radius, length):
    """Cylinder oriented along the Y axis (depth / wheel spindle axis)."""
    c = b.Cylinder(radius, length,
                   rotation=b.Rotation(90, 0, 0),
                   align=(A.CENTER, A.CENTER, A.CENTER))
    return c.moved(b.Location((x, y, z)))


def cylinder_z(x, y, z, radius, height):
    """Cylinder oriented along the Z axis (vertical)."""
    c = b.Cylinder(radius, height, align=(A.CENTER, A.CENTER, A.MIN))
    return c.moved(b.Location((x, y, z)))


@step(out='front_knuckle.step')
@stl(out='front_knuckle.stl', mesh_tolerance=0.0003)
def model():
    # 1. Main C-shaped Upright Spine in YZ plane, extruded across width 28 mm (X from -14 to +14 mm)
    pts_yz = [
        (32.0, 0.0), (18.0, 14.0), (7.0, 32.0), (0.0, 52.0),
        (0.0, 117.66), (3.0, 125.0), (8.0, 128.5), (14.0, 129.66),
        (42.0, 129.66), (52.0, 127.0), (56.0, 122.16), (52.0, 116.5),
        (42.0, 114.66), (26.0, 114.66), (26.0, 68.0), (28.0, 52.0),
        (34.0, 32.0), (42.0, 16.0), (46.0, 12.0), (52.0, 10.0),
        (56.0, 6.0), (52.0, 2.0), (46.0, 0.0), (32.0, 0.0)
    ]
    with b.BuildSketch(b.Plane.YZ) as s_spine:
        b.Polygon(pts_yz)
    spine = b.extrude(s_spine.sketch, amount=I['spine_width_mm'] / 2.0, both=True)

    # 2. Central Bearing Hub (OD 48 mm, width 26 mm, centered at X=0, Z=96.66 mm)
    hub = cylinder_y(0.0, I['spine_thickness_mm'] / 2.0, I['main_hub_center_z_mm'],
                     I['main_hub_outer_diameter_mm'] / 2.0, I['spine_thickness_mm'])
    body = spine.fuse(hub).clean()

    # 3. Brake Caliper Mounting Ears (left side: X < 0, Y from 0 to 10 mm)
    with b.BuildSketch(b.Plane.XZ) as s_ears:
        pts = [
            (-14.0, 115.0),
            (-28.0, 119.0), (-37.0, 110.0), (-30.0, 103.0),
            (-20.0, 91.0),
            (-32.0, 80.0), (-40.0, 72.5), (-31.0, 63.5),
            (-14.0, 65.0), (-14.0, 115.0)
        ]
        b.Polygon(pts)
    ears_solid = b.extrude(s_ears.sketch, amount=-I['caliper_ear_thickness_mm'], both=False)
    ear1_boss = cylinder_y(I['caliper_upper_hole_x_mm'], I['caliper_ear_thickness_mm'] / 2.0,
                           I['caliper_upper_hole_z_mm'], 9.0, I['caliper_ear_thickness_mm'])
    ear2_boss = cylinder_y(I['caliper_lower_hole_x_mm'], I['caliper_ear_thickness_mm'] / 2.0,
                           I['caliper_lower_hole_z_mm'], 9.0, I['caliper_ear_thickness_mm'])
    ears_solid = ears_solid.fuse(ear1_boss).fuse(ear2_boss).clean()
    body = body.fuse(ears_solid).clean()

    # 4. Steering Arm & Double-Shear Clevis Fork (right side: X > 0)
    arm_base = box(14.0, 6.0, I['steering_clevis_bottom_z_mm'],
                   26.0, 26.0, I['steering_clevis_top_z_mm'] - I['steering_clevis_bottom_z_mm'])
    prong_top_z = I['steering_clevis_top_z_mm'] - I['steering_clevis_prong_thickness_mm']
    prong_top = box(40.0, 6.0, prong_top_z, 18.0, 26.0, I['steering_clevis_prong_thickness_mm'])
    prong_bot = box(40.0, 6.0, I['steering_clevis_bottom_z_mm'],
                    18.0, 26.0, I['steering_clevis_prong_thickness_mm'])
    prong_tip_top = cylinder_z(I['steering_clevis_hole_x_mm'], I['steering_clevis_hole_y_mm'],
                               prong_top_z, 13.0, I['steering_clevis_prong_thickness_mm'])
    prong_tip_bot = cylinder_z(I['steering_clevis_hole_x_mm'], I['steering_clevis_hole_y_mm'],
                               I['steering_clevis_bottom_z_mm'], 13.0, I['steering_clevis_prong_thickness_mm'])
    clevis_solid = arm_base.fuse(prong_top).fuse(prong_bot).fuse(prong_tip_top).fuse(prong_tip_bot).clean()

    # U-slot cut between prongs
    slot_bot_z = I['steering_clevis_bottom_z_mm'] + I['steering_clevis_prong_thickness_mm']
    slot_height = I['steering_clevis_slot_height_mm']
    u_box = box(38.0, 4.0, slot_bot_z, 30.0, 30.0, slot_height)
    u_cyl = cylinder_y(38.0, 19.0, slot_bot_z + slot_height / 2.0, 9.0, 32.0)
    clevis_solid = clevis_solid.cut(u_box).cut(u_cyl).clean()
    body = body.fuse(clevis_solid).clean()

    # 5. Through-holes
    # Wheel bearing bore: Ø25.00 through hub along Y
    bore = cylinder_y(0.0, 13.0, I['main_hub_center_z_mm'],
                      D['main_hole_diameter_mm'] / 2.0, 50.0)
    # Caliper ear mounting holes: Ø8.00 through ears along Y
    hole_ear1 = cylinder_y(I['caliper_upper_hole_x_mm'], 5.0,
                           I['caliper_upper_hole_z_mm'], D['mount_hole_diameter_mm'] / 2.0, 30.0)
    hole_ear2 = cylinder_y(I['caliper_lower_hole_x_mm'], 5.0,
                           I['caliper_lower_hole_z_mm'], D['mount_hole_diameter_mm'] / 2.0, 30.0)
    # Upper A-arm ball joint mounting hole: Ø8.00 vertical along Z
    hole_top_lug = cylinder_z(0.0, I['top_lug_hole_y_mm'], 110.0,
                              D['mount_hole_diameter_mm'] / 2.0, 30.0)
    # Lower A-arm ball joint mounting hole: Ø8.00 vertical along Z
    hole_bot_lug = cylinder_z(0.0, I['bottom_lug_hole_y_mm'], -5.0,
                              D['mount_hole_diameter_mm'] / 2.0, 25.0)
    # Steering tie-rod clevis hole: Ø8.00 vertical through both prongs
    hole_clevis = cylinder_z(I['steering_clevis_hole_x_mm'], I['steering_clevis_hole_y_mm'],
                             30.0, D['mount_hole_diameter_mm'] / 2.0, 45.0)

    body = body.cut(bore).cut(hole_ear1).cut(hole_ear2).cut(hole_top_lug).cut(hole_bot_lug).cut(hole_clevis).clean()

    if len(body.solids()) != 1:
        raise ValueError(f'front knuckle is not a single solid: {len(body.solids())}')
    valid = body.is_valid if isinstance(body.is_valid, bool) else body.is_valid()
    if not valid or body.volume <= 0:
        raise ValueError('front knuckle solid is invalid')
    body.label = 'FRONT_KNUCKLE_AL7075T6'

    # Direct export guarantee
    b.export_step(body, str(ROOT / 'front_knuckle.step'))
    b.export_stl(body, str(ROOT / 'front_knuckle.stl'), tolerance=0.0003)

    bounds = body.bounding_box().size
    report = {
        'source': P['source_image'],
        'title': P['title'],
        'material_note': P['material_note'],
        'stock_dimensions_mm': P['raw_material_note'],
        'units': 'mm',
        'printed_dimensions': D,
        'bounds_mm': [round(bounds.X, 3), round(bounds.Y, 3), round(bounds.Z, 3)],
        'solid_count': len(body.solids()),
        'valid': bool(valid),
        'volume_mm3': round(body.volume, 3),
        'feature_summary': {
            'height_mm': round(bounds.Z, 2),
            'spindle_bore_dia_mm': D['main_hole_diameter_mm'],
            'caliper_holes_dia_mm': D['mount_hole_diameter_mm'],
            'caliper_ear_count': 2,
            'clevis_fork_hole_dia_mm': D['mount_hole_diameter_mm'],
            'upper_balljoint_hole_dia_mm': D['mount_hole_diameter_mm'],
            'lower_balljoint_hole_dia_mm': D['mount_hole_diameter_mm']
        },
        'interpretations': P['interpretation_notes'],
    }
    (ROOT / 'front_knuckle_report.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
    print(f'Built Front Knuckle successfully: {len(body.solids())} solid, '
          f'{bounds.X:.2f} x {bounds.Y:.2f} x {bounds.Z:.2f} mm, '
          f'volume={body.volume:.1f} mm3')
    return body


if __name__ == '__main__':
    model()

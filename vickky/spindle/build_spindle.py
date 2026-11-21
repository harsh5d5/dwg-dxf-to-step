"""Rebuild the spindle from source/1_spindle_clean.png.

Interpreted dimensions (mm):
  overall 85 = 10 flange + 58.34 main + 1.66 transition + 15 tip
  diameters: D33 flange, D25 main, D24 tip, D15 through bore
  two R3 external shoulder fillets
"""
import json
from pathlib import Path

from cadgen import build123d as b, step, stl

ROOT = Path(__file__).parent
P = json.loads((ROOT / 'parameters.json').read_text(encoding='utf8'))
A = b.Align


def cylinder(radius, height, z):
    return b.Cylinder(radius, height, align=(A.CENTER, A.CENTER, A.MIN)).moved(
        b.Location((0, 0, z)))


def circular_edge(body, radius, z):
    matches = []
    for edge in body.edges():
        try:
            edge_radius = edge.radius
        except Exception:
            continue
        center = edge.bounding_box().center()
        if (abs(edge_radius - radius) < 1e-3 and abs(center.Z - z) < 1e-3
                and abs(center.X) < 1e-3 and abs(center.Y) < 1e-3):
            matches.append(edge)
    if len(matches) != 1:
        raise ValueError(f'expected one R{radius} edge at z={z}, found {len(matches)}')
    return matches[0]


@step(out='spindle.step')
@stl(out='spindle.stl', mesh_tolerance=0.0003)
def model():
    flange = cylinder(P['flange_diameter_mm'] / 2, P['flange_length_mm'], 0)
    main_len = P['main_length_mm'] + P['transition_length_mm']
    main_z = P['flange_length_mm']
    tip_z = main_z + main_len
    main = cylinder(P['main_diameter_mm'] / 2, main_len, main_z)
    tip = cylinder(P['tip_diameter_mm'] / 2, P['tip_length_mm'], tip_z)

    body = flange.fuse(main).fuse(tip).clean()

    # The two R3 callouts are applied to the external shoulder edges.
    edges = [
        circular_edge(body, P['flange_diameter_mm'] / 2, main_z),
        circular_edge(body, P['tip_diameter_mm'] / 2,
                      tip_z + P['tip_length_mm']),
    ]
    body = body.fillet(P['fillet_radius_mm'], edges).clean()

    # D15 concentric circle in the side view is interpreted as a through bore.
    total_length = (P['flange_length_mm'] + main_len + P['tip_length_mm'])
    bore = cylinder(P['bore_diameter_mm'] / 2, total_length + 2, -1)
    body = body.cut(bore).clean()

    if len(body.solids()) != 1 or body.volume <= 0:
        raise ValueError('spindle is not a single solid')
    valid = body.is_valid if isinstance(body.is_valid, bool) else body.is_valid()
    if not valid:
        raise ValueError('spindle solid is invalid')
    body.label = 'SPINDLE_EN19'

    bounds = body.bounding_box().size
    summary = {
        'source': P['source_image'],
        'title': P['title'],
        'material_note': P['material_note'],
        'raw_stock_note': P['raw_stock_note'],
        'units': 'mm',
        'overall_length_mm': round(bounds.Z, 3),
        'max_diameter_mm': round(max(bounds.X, bounds.Y), 3),
        'bore_diameter_mm': P['bore_diameter_mm'],
        'fillet_radius_mm': P['fillet_radius_mm'],
        'fillet_count': P['fillet_count'],
        'interpretation': P['interpretation'],
        'volume_mm3': round(body.volume, 3),
    }
    (ROOT / 'spindle_summary.json').write_text(
        json.dumps(summary, indent=2), encoding='utf8')
    print(f'built spindle: {len(body.solids())} solid, '
          f'L={bounds.Z:.2f} mm, D={bounds.X:.2f} mm, volume={body.volume:.1f} mm3')
    return body


if __name__ == '__main__':
    model()

"""Build the PCI bracket blank as a thin extruded sheet with through holes.

The DXF contains one outer contour on layer "bracket cut" and five cutouts on
layer "holes". No thickness is dimensioned, so THICKNESS_MM in parameters.json
is used and recorded as an assumption.
"""
import json
from pathlib import Path

from shapely.geometry import Polygon
from cadgen import build123d as b, step, stl

ROOT = Path(__file__).parent
PARAMETERS = json.loads((ROOT / 'parameters.json').read_text(encoding='utf8'))
ANALYSIS = json.loads((ROOT / 'analysis.json').read_text(encoding='utf8'))
THICKNESS = float(PARAMETERS['thickness_mm'])


def clean_profile(profile):
    poly = Polygon(profile['outer'], profile['holes']).buffer(0)
    poly = poly.simplify(0.01, preserve_topology=True)
    if poly.geom_type != 'Polygon' or poly.is_empty:
        raise ValueError(f"invalid profile {profile['id']}")
    return poly


def wire_from_polygon(poly):
    return b.Wire.make_polygon(list(poly.exterior.coords)[:-1], close=True)


def hole_wires(poly):
    return [b.Wire.make_polygon(list(ring.coords)[:-1], close=True)
            for ring in poly.interiors]


@step(out='pci_bracket_blank.step')
@stl(out='pci_bracket_blank.stl', mesh_tolerance=0.0005)
def model():
    outer_profile = next(p for p in ANALYSIS['profiles']
                         if p['layer'] == PARAMETERS['outer_layer'])
    hole_profiles = [p for p in ANALYSIS['profiles']
                     if p['layer'] == PARAMETERS['hole_layer']]

    outer = clean_profile(outer_profile)
    holes = [clean_profile(p) for p in hole_profiles]
    for index, hole in enumerate(holes, 1):
        if not outer.buffer(1e-6).contains(hole):
            raise ValueError(f'hole {index} is not fully inside the outer contour')

    face = b.Face(wire_from_polygon(outer))
    body = b.extrude(face, amount=THICKNESS, dir=(0, 0, 1))
    for index, hole in enumerate(holes, 1):
        cutter = b.extrude(b.Face(wire_from_polygon(hole)),
                           amount=THICKNESS + 0.2, dir=(0, 0, 1))
        cutter = cutter.moved(b.Location((0, 0, -0.1)))
        body = body - cutter
        if body.volume <= 0:
            raise ValueError(f'hole {index} removed the entire bracket')
    body = body.clean()
    body.label = 'PCI_BRACKET_BLANK'

    if not body.solids() or body.volume <= 0:
        raise ValueError('empty PCI bracket solid')
    valid = body.is_valid if isinstance(body.is_valid, bool) else body.is_valid()
    if not valid:
        raise ValueError('invalid PCI bracket solid')

    summary = {
        'source_dxf': PARAMETERS['source'],
        'units': 'mm',
        'thickness_mm': THICKNESS,
        'thickness_basis': PARAMETERS['thickness_basis'],
        'outer_layer': PARAMETERS['outer_layer'],
        'hole_layer': PARAMETERS['hole_layer'],
        'hole_count': len(hole_profiles),
        'outer_area_mm2': round(outer.area, 3),
        'hole_area_mm2': round(sum(h.area for h in holes), 3),
        'net_area_mm2': round(outer.area - sum(h.area for h in holes), 3),
        'expected_volume_mm3': round((outer.area - sum(h.area for h in holes)) * THICKNESS, 3),
        'bounds_mm': [round(v, 3) for v in outer.bounds],
        'note': 'The extrusion thickness is an assumption; the DXF contains only a flat 2D profile.'
    }
    (ROOT / 'bracket_parameters.json').write_text(
        json.dumps(summary, indent=2), encoding='utf8')
    print(f'built PCI bracket blank: {len(body.solids())} solid, {len(hole_profiles)} holes, '
          f'thickness {THICKNESS} mm')
    return body


if __name__ == '__main__':
    model()

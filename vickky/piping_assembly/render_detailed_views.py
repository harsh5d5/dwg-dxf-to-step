import struct
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from pathlib import Path

root = Path('vickky/piping_assembly')

def load_stl(path):
    with open(path, 'rb') as f:
        f.read(80)
        n_tris = struct.unpack('<I', f.read(4))[0]
        dtype = np.dtype([
            ('normal', '<f4', (3,)),
            ('v0', '<f4', (3,)),
            ('v1', '<f4', (3,)),
            ('v2', '<f4', (3,)),
            ('attr', '<u2')
        ])
        data = np.fromfile(f, dtype=dtype, count=n_tris)
    verts = np.stack([data['v0'], data['v1'], data['v2']], axis=1)
    normals = data['normal']
    return verts, normals

def render_mesh(verts, normals, out_path, elev, azim, figsize=(10, 6), xlim=None, ylim=None, zlim=None):
    light = np.array([0.4, -0.6, 0.7])
    light /= np.linalg.norm(light)
    shade = np.clip(np.sum(normals * light, axis=1), 0.15, 1.0)
    grey_colors = np.zeros((len(normals), 4))
    for i in range(3):
        grey_colors[:, i] = shade * 0.65 + 0.25
    grey_colors[:, 3] = 1.0

    fig = plt.figure(figsize=figsize, dpi=160)
    ax = fig.add_subplot(111, projection='3d')
    ax.view_init(elev=elev, azim=azim)
    mesh = Poly3DCollection(verts, facecolors=grey_colors, edgecolors='#333333', linewidths=0.04)
    ax.add_collection3d(mesh)

    if xlim is None:
        min_pt = verts.min(axis=(0, 1))
        max_pt = verts.max(axis=(0, 1))
        mid_x = (min_pt[0] + max_pt[0]) / 2.0
        mid_y = (min_pt[1] + max_pt[1]) / 2.0
        mid_z = (min_pt[2] + max_pt[2]) / 2.0
        max_range = max(max_pt[0] - min_pt[0], max_pt[1] - min_pt[1], max_pt[2] - min_pt[2]) / 2.0 * 1.05
        ax.set_xlim(mid_x - max_range, mid_x + max_range)
        ax.set_ylim(mid_y - max_range, mid_y + max_range)
        ax.set_zlim(mid_z - max_range, mid_z + max_range)
    else:
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_zlim(zlim)

    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(out_path, bbox_inches='tight', pad_inches=0.02, facecolor='white')
    plt.close()
    print(f'Saved {out_path.name}')

def main():
    stl_path = root / 'piping_assembly_detailed.stl'
    if not stl_path.exists():
        print(f"Error: {stl_path} does not exist.")
        return

    verts, normals = load_stl(stl_path)
    print(f"Loaded full assembly STL with {len(verts)} triangles")

    # Render Assembly Views
    render_mesh(verts, normals, root / 'detailed_preview_iso.png', elev=24, azim=-62, figsize=(10, 6))
    render_mesh(verts, normals, root / 'detailed_preview_front.png', elev=0, azim=-90, figsize=(12, 5.5),
                xlim=(-150, 2600), ylim=(-1375, 1375), zlim=(-50, 1325))
    render_mesh(verts, normals, root / 'detailed_preview_top.png', elev=90, azim=-90, figsize=(12, 5.5),
                xlim=(-150, 2600), ylim=(-650, 725), zlim=(-687, 687))
    render_mesh(verts, normals, root / 'detailed_preview_side.png', elev=0, azim=0, figsize=(6, 8),
                xlim=(0, 2600), ylim=(-650, 650), zlim=(-50, 1250))

    # Render Component Thumbnails
    comp_dir = root / 'components'
    for stl_f in sorted(comp_dir.glob('*.stl')):
        try:
            cv, cn = load_stl(stl_f)
            out_img = comp_dir / f"{stl_f.stem}.png"
            render_mesh(cv, cn, out_img, elev=25, azim=-55, figsize=(6, 5))
        except Exception as e:
            print(f"Failed rendering {stl_f.name}: {e}")

if __name__ == '__main__':
    main()

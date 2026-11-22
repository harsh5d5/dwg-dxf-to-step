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

verts, normals = load_stl(root / 'piping_assembly.stl')
print(f'Loaded STL with {len(verts)} triangles')

light = np.array([0.4, -0.6, 0.7])
light /= np.linalg.norm(light)
shade = np.clip(np.sum(normals * light, axis=1), 0.15, 1.0)
grey_colors = np.zeros((len(normals), 4))
for i in range(3):
    grey_colors[:, i] = shade * 0.65 + 0.25
grey_colors[:, 3] = 1.0

# 1. Isometric View
fig = plt.figure(figsize=(10, 6), dpi=160)
ax = fig.add_subplot(111, projection='3d')
ax.view_init(elev=24, azim=-62)
mesh = Poly3DCollection(verts, facecolors=grey_colors, edgecolors='#333333', linewidths=0.04)
ax.add_collection3d(mesh)
mid_x, mid_y, mid_z = 1200.0, -50.0, 600.0
max_range = 1400.0
ax.set_xlim(mid_x - max_range, mid_x + max_range)
ax.set_ylim(mid_y - max_range, mid_y + max_range)
ax.set_zlim(mid_z - max_range, mid_z + max_range)
ax.set_axis_off()
plt.tight_layout()
plt.savefig(root / 'preview_iso.png', bbox_inches='tight', pad_inches=0.02, facecolor='white')
plt.close()
print('Saved preview_iso.png')

# 2. Front View (Elev=0, Azim=-90)
fig = plt.figure(figsize=(12, 5.5), dpi=160)
ax = fig.add_subplot(111, projection='3d')
ax.view_init(elev=0, azim=-90)
mesh = Poly3DCollection(verts, facecolors=grey_colors, edgecolors='#333333', linewidths=0.04)
ax.add_collection3d(mesh)
ax.set_xlim(-150, 2600)
ax.set_ylim(-1375, 1375)
ax.set_zlim(-50, 1325)
ax.set_axis_off()
plt.tight_layout()
plt.savefig(root / 'preview_front.png', bbox_inches='tight', pad_inches=0.02, facecolor='white')
plt.close()
print('Saved preview_front.png')

# 3. Top View (Elev=90, Azim=-90)
fig = plt.figure(figsize=(12, 5.5), dpi=160)
ax = fig.add_subplot(111, projection='3d')
ax.view_init(elev=90, azim=-90)
mesh = Poly3DCollection(verts, facecolors=grey_colors, edgecolors='#333333', linewidths=0.04)
ax.add_collection3d(mesh)
ax.set_xlim(-150, 2600)
ax.set_ylim(-650, 725)
ax.set_zlim(-687, 687)
ax.set_axis_off()
plt.tight_layout()
plt.savefig(root / 'preview_top.png', bbox_inches='tight', pad_inches=0.02, facecolor='white')
plt.close()
print('Saved preview_top.png')

# 4. Right Side View (Elev=0, Azim=0)
fig = plt.figure(figsize=(6, 8), dpi=160)
ax = fig.add_subplot(111, projection='3d')
ax.view_init(elev=0, azim=0)
mesh = Poly3DCollection(verts, facecolors=grey_colors, edgecolors='#333333', linewidths=0.04)
ax.add_collection3d(mesh)
ax.set_xlim(0, 2600)
ax.set_ylim(-650, 650)
ax.set_zlim(-50, 1250)
ax.set_axis_off()
plt.tight_layout()
plt.savefig(root / 'preview_side.png', bbox_inches='tight', pad_inches=0.02, facecolor='white')
plt.close()
print('Saved preview_side.png')

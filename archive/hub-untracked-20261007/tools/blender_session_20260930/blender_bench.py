"""Benchmark Cycles on this machine: how many portrait renders can we actually do?

Answers the throughput question with a number instead of an estimate, and it
uses a deliberately NON-trivial scene -- a subdivided figure with a
subsurface-scattering skin shader, a key area light, a fill, and a rim -- so
the timing reflects something close to a real portrait rather than a sphere.
"""
import bpy, sys, time, os

RES_X, RES_Y = 1024, 1360
SAMPLES = 64
OUT = os.path.join(os.path.dirname(__file__), "bench_cycles.png")

t_start = time.time()

# --- clear ------------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
scn.render.engine = "CYCLES"
scn.cycles.device = "GPU"
scn.cycles.samples = SAMPLES
scn.cycles.use_denoising = True
scn.render.resolution_x = RES_X
scn.render.resolution_y = RES_Y
scn.render.resolution_percentage = 100
scn.render.image_settings.file_format = "PNG"
scn.render.filepath = OUT

# --- device -----------------------------------------------------------------
prefs = bpy.context.preferences.addons["cycles"].preferences
chosen = None
for t in ("ONEAPI", "OPTIX", "CUDA", "HIP"):
    try:
        prefs.compute_device_type = t
        prefs.get_devices()
        if [d for d in prefs.devices if d.type == t]:
            for d in prefs.devices:
                d.use = (d.type == t)
            chosen = t
            break
    except Exception:
        continue
print("BENCH device:", chosen or "none (CPU fallback)")
if chosen is None:
    scn.cycles.device = "CPU"
else:
    scn.cycles.device = "GPU"

# --- subject: a form with enough subdivision to exercise SSS ----------------
# Built without relying on bpy.context for the DATA reference: under
# --factory-startup with use_empty=True, bpy.context.object is not reliably
# the object the operator just created, and torso.data.materials then has no
# .new(). Everything below reads from bpy.data by name instead.
bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=64, radius=1.0,
                                    location=(0, 0, 0))
torso = bpy.data.objects.get("Sphere")
if torso is None:
    torso = [o for o in bpy.data.objects if o.type == "MESH"][0]
bpy.context.view_layer.objects.active = torso
torso.select_set(True)

sub = torso.modifiers.new("subs", "SUBSURF")
sub.levels = 2
sub.render_levels = 2
for p in torso.data.polygons:
    p.use_smooth = True

# print("DBG objects:", [(o.name, o.type) for o in bpy.data.objects])
# print("DBG torso:", torso, "type:", getattr(torso, "type", "?"), "data:", type(torso.data))
# print("DBG data dir:", [a for a in dir(torso.data) if "mat" in a.lower()][:6])
skin = bpy.data.materials.new("skin")
torso.data.materials.append(skin)
skin.use_nodes = True
b = skin.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (0.62, 0.36, 0.27, 1.0)
b.inputs["Roughness"].default_value = 0.42
if "Subsurface Weight" in b.inputs:
    b.inputs["Subsurface Weight"].default_value = 0.28
    b.inputs["Subsurface Radius"].default_value = (1.0, 0.22, 0.12)
    b.inputs["Subsurface Scale"].default_value = 0.03
if "Specular IOR Level" in b.inputs:
    b.inputs["Specular IOR Level"].default_value = 0.45

# --- light: key, fill, rim --------------------------------------------------
def area(name, loc, energy, size, color=(1, 1, 1), rot=(0, 0, 0)):
    d = bpy.data.lights.new(name, "AREA")
    d.energy = energy
    d.size = size
    d.color = color
    o = bpy.data.objects.new(name, d)
    o.location = loc
    o.rotation_euler = rot
    bpy.context.collection.objects.link(o)
    return o

area("key",  (-2.2, -2.4, 2.6), 420, 2.0, (1.0, 0.90, 0.80), (1.05, 0, -0.72))
area("fill", ( 2.6, -1.8, 0.6),  55, 3.0, (0.62, 0.74, 1.0), (1.35, 0, 0.75))
area("rim",  ( 1.4,  3.0, 2.2), 260, 1.2, (0.80, 0.90, 1.0), (-1.15, 0, 0.2))

# --- world: dim, so the light does the work ---------------------------------
w = bpy.data.worlds.new("w")
scn.world = w
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.02, 0.025, 0.035, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.12

# --- camera: a portrait lens, not a wide -----------------------------------
cam_d = bpy.data.cameras.new("cam")
cam_d.lens = 85
cam = bpy.data.objects.new("cam", cam_d)
cam.location = (0, -4.2, 0.15)
cam.rotation_euler = (1.5708, 0, 0)
scn.collection.objects.link(cam)
scn.camera = cam

print(f"BENCH scene: {RES_X}x{RES_Y}, {SAMPLES} samples, {chosen or 'CPU'}")
t0 = time.time()
bpy.ops.render.render(write_still=True)
dt = time.time() - t0
print(f"BENCH render_seconds: {dt:.1f}")
print(f"BENCH total_seconds: {time.time() - t_start:.1f}")
print(f"BENCH per_image_at_64spp: {dt:.1f}s")
print(f"BENCH images_per_hour_at_64spp: {3600 / dt:.0f}")


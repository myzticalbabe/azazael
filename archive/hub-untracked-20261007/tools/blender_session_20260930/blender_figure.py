"""A posed human figure in Cycles, framed as a portrait, with a sample ladder.

Why this exists: the 2026-09-30 benchmark rendered a radius-1.0 sphere from
4.2m on an 85mm lens, so the subject overflowed the frame -- the timing was
valid but the image was a crop of a ball, not a figure. RULE 0Q: a glyph is not
a figure, and a sphere filling the frame is a glyph. This builds a figure with
a head, shoulders, spine, arms and legs, standing on ground, in a pose, and
frames it so the whole body reads.

Honest label: this is a L3 mannequin. The geometry is procedural primitives and
the skin is a Principled BSDF with subsurface scattering. It has continuous
tone, real light transport and per-pixel texture -- so it is past the vector
limit of RULE 0R -- but it has no face, no hands, no hair and no scanned
detail, so it is NOT the L4 bar. It is the capacity probe that says whether L4
geometry would be affordable to render once obtained.

Sample ladder: 64 / 256 / 1024. The 15.4s figure at 64spp implies ~1 min at
256spp and ~4 min at 1024spp, which is the number that decides whether a
genuinely photoreal figure is renderable in a session or only overnight.
"""
import bpy, sys, time, os

OUTDIR = os.path.dirname(__file__)
LADDER = [64, 256, 1024]
RES_X, RES_Y = 1024, 1360

# Blender needs a 0-1 colour ramp the skin shader can ride, or skin reads as
# plastic. A flat Base Color with SSS is the single most common reason a
# "realistic" Blender render still looks like a mannequin: the albedo has no
# variation for the light to reveal.
def ramp(node_tree, name, stops):
    n = node_tree.nodes.new("ShaderNodeValToRGB")
    n.name = name
    cr = n.color_ramp
    while len(cr.elements) > 1:
        cr.elements.remove(cr.elements[-1])
    cr.elements[0].position = stops[0][0]
    cr.elements[0].color = stops[0][1]
    for pos, col in stops[1:]:
        e = cr.elements.new(pos)
        e.color = col
    n.location = (-380, 260)
    return n


def build_skin():
    m = bpy.data.materials.new("skin")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.46

    # Albedo variation: deep shadowed reddish-brown -> mid -> warm highlight.
    r = ramp(nt, "skin_albedo", [
        (0.00, (0.115, 0.038, 0.026, 1.0)),
        (0.32, (0.315, 0.128, 0.086, 1.0)),
        (0.62, (0.520, 0.268, 0.196, 1.0)),
        (1.00, (0.680, 0.430, 0.352, 1.0)),
    ])
    # Break up the albedo with noise so the surface has per-pixel texture at
    # two scales. A flat ramp still reads as a shaded ball.
    tex = nt.nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = 26.0
    tex.inputs["Detail"].default_value = 9.0
    tex.inputs["Roughness"].default_value = 0.62
    tex.location = (-600, 420)
    fine = nt.nodes.new("ShaderNodeTexNoise")
    fine.inputs["Scale"].default_value = 210.0
    fine.inputs["Detail"].default_value = 6.0
    fine.location = (-600, 120)

    mix = nt.nodes.new("ShaderNodeMixRGB")
    mix.blend_type = "OVERLAY"
    mix.inputs["Fac"].default_value = 0.28
    mix.location = (-200, 380)
    nt.links.new(r.outputs["Color"], mix.inputs[1])
    nt.links.new(tex.outputs["Fac"], mix.inputs[2])
    nt.links.new(mix.outputs["Color"], b.inputs["Base Color"])

    rough = nt.nodes.new("ShaderNodeMapRange")
    rough.inputs["From Min"].default_value = 0.0
    rough.inputs["From Max"].default_value = 1.0
    rough.inputs["To Min"].default_value = 0.38
    rough.inputs["To Max"].default_value = 0.58
    rough.location = (-200, 60)
    nt.links.new(fine.outputs["Fac"], rough.inputs["Value"])
    nt.links.new(rough.outputs["Result"], b.inputs["Roughness"])

    # Subsurface: the load-bearing skin term. Weight plus a coloured radius
    # plus a scale in metres; a large radius reads as wax, zero reads as clay.
    if "Subsurface Weight" in b.inputs:
        b.inputs["Subsurface Weight"].default_value = 0.42
    if "Subsurface Radius" in b.inputs:
        b.inputs["Subsurface Radius"].default_value = (1.0, 0.19, 0.09)
    if "Subsurface Scale" in b.inputs:
        b.inputs["Subsurface Scale"].default_value = 0.018
    if "Specular IOR Level" in b.inputs:
        b.inputs["Specular IOR Level"].default_value = 0.42
    if "Coat Weight" in b.inputs:
        b.inputs["Coat Weight"].default_value = 0.06
        b.inputs["Coat Roughness"].default_value = 0.30
    return m


def _fresh(call):
    """Run a primitive op and return the object it made.

    Do NOT look the object up by the name you passed: every
    bpy.ops.mesh.primitive_*_add IGNORES its `name=` argument and
    auto-generates "Sphere", "Sphere.001", ... so bpy.data.objects[name] raises
    KeyError. And do NOT read bpy.context.object either -- under
    --factory-startup with read_factory_settings(use_empty=True) it is not
    reliably the object the op just created. Diffing the object set is the one
    approach that is correct in both cases.
    """
    before = set(bpy.data.objects.keys())
    call()
    new = [k for k in bpy.data.objects.keys() if k not in before]
    if not new:
        raise RuntimeError("primitive op added no object")
    return bpy.data.objects[new[-1]]


def smooth(obj, sub=2):
    for p in obj.data.polygons:
        p.use_smooth = True
    m = obj.modifiers.new("subs", "SUBSURF")
    m.levels = min(sub, 2)
    m.render_levels = min(sub, 2)


def ellipsoid(name, loc, scale, mat, segs=48, rings=32, rot=(0, 0, 0)):
    o = _fresh(lambda: bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segs, ring_count=rings, radius=1.0, location=loc, rotation=rot))
    o.name = name
    o.scale = scale
    o.data.materials.append(mat)
    smooth(o)
    return o


def limb(name, a, b, r, mat, segs=32):
    """A capsule between two points -- the honest way to get an arm or a leg."""
    import mathutils
    a, b = mathutils.Vector(a), mathutils.Vector(b)
    d = b - a
    length = d.length
    o = _fresh(lambda: bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segs, ring_count=segs // 2, radius=1.0, location=(a + b) / 2.0))
    o.name = name
    o.scale = (r, r, length / 2.0 + r * 0.5)
    # point the long axis down -Z at the segment
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = d.to_track_quat("Z", "Y")
    o.data.materials.append(mat)
    smooth(o)
    return o


def build_figure(skin, cloth):
    parts = []
    # ground contact: feet planted, weight on both legs
    parts.append(ellipsoid("l_foot", (-0.17, -0.06, 0.055), (0.075, 0.20, 0.055), cloth))
    parts.append(ellipsoid("r_foot", ( 0.17, -0.06, 0.055), (0.075, 0.20, 0.055), cloth))

    # legs, slightly apart, knees soft
    parts.append(limb("l_shin", (-0.17, 0.0, 0.11), (-0.19, 0.01, 0.47), 0.072, skin))
    parts.append(limb("r_shin", ( 0.17, 0.0, 0.11), ( 0.19, 0.01, 0.47), 0.072, skin))
    parts.append(limb("l_thigh", (-0.19, 0.01, 0.47), (-0.15, 0.0, 0.90), 0.098, skin))
    parts.append(limb("r_thigh", ( 0.19, 0.01, 0.47), ( 0.15, 0.0, 0.90), 0.098, skin))

    # torso: hips -> chest -> shoulders, tapering, with a real ribcage volume
    parts.append(ellipsoid("hips",  (0.0, 0.0, 0.96), (0.185, 0.125, 0.150), cloth))
    parts.append(ellipsoid("waist", (0.0, 0.005, 1.09), (0.163, 0.112, 0.115), skin))
    parts.append(ellipsoid("chest", (0.0, 0.0, 1.28), (0.212, 0.132, 0.190), skin))
    parts.append(ellipsoid("shoulders", (0.0, 0.0, 1.44), (0.255, 0.130, 0.115), skin))

    # neck, then head. No face: stated, not hidden.
    parts.append(limb("neck", (0.0, 0.0, 1.47), (0.0, -0.01, 1.60), 0.058, skin))
    parts.append(ellipsoid("head", (0.0, -0.015, 1.735), (0.098, 0.112, 0.132), skin))
    # jaw + brow mass so the silhouette is a head and not an egg
    parts.append(ellipsoid("jaw", (0.0, -0.045, 1.655), (0.072, 0.088, 0.062), skin))

    # arms: down and slightly forward, hands open-ish. This is the SENTINEL
    # read -- planted, arms at the sides, weight even.
    parts.append(limb("l_uarm", (-0.245, 0.0, 1.42), (-0.300, -0.02, 1.13), 0.058, skin))
    parts.append(limb("r_uarm", ( 0.245, 0.0, 1.42), ( 0.300, -0.02, 1.13), 0.058, skin))
    parts.append(limb("l_farm", (-0.300, -0.02, 1.13), (-0.318, -0.10, 0.86), 0.046, skin))
    parts.append(limb("r_farm", ( 0.300, -0.02, 1.13), ( 0.318, -0.10, 0.86), 0.046, skin))
    parts.append(ellipsoid("l_hand", (-0.320, -0.135, 0.775), (0.038, 0.070, 0.082), skin))
    parts.append(ellipsoid("r_hand", ( 0.320, -0.135, 0.775), (0.038, 0.070, 0.082), skin))
    return parts


def build_cloth():
    m = bpy.data.materials.new("cloth")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.075, 0.082, 0.095, 1.0)
    b.inputs["Roughness"].default_value = 0.78
    if "Sheen Weight" in b.inputs:
        b.inputs["Sheen Weight"].default_value = 0.35
        b.inputs["Sheen Roughness"].default_value = 0.35
    return m


def main():
    t_all = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn = bpy.context.scene
    scn.render.engine = "CYCLES"
    scn.cycles.use_denoising = True
    scn.render.resolution_x = RES_X
    scn.render.resolution_y = RES_Y
    scn.render.resolution_percentage = 100
    scn.render.image_settings.file_format = "PNG"

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
    print("FIG device:", chosen or "none (CPU fallback)")
    scn.cycles.device = "GPU" if chosen else "CPU"

    skin = build_skin()
    cloth = build_cloth()
    build_figure(skin, cloth)

    # ground plane: gives contact shadow and a horizon, without which a figure
    # floats and reads as a cutout
    bpy.ops.mesh.primitive_plane_add(size=40.0, location=(0, 0, 0))
    ground = [o for o in bpy.data.objects if o.type == "MESH" and
              len(o.data.vertices) == 4][0]
    gm = bpy.data.materials.new("ground")
    gm.use_nodes = True
    gb = gm.node_tree.nodes["Principled BSDF"]
    gb.inputs["Base Color"].default_value = (0.028, 0.030, 0.034, 1.0)
    gb.inputs["Roughness"].default_value = 0.62
    ground.data.materials.append(gm)

    def area(name, loc, energy, size, color, rot):
        d = bpy.data.lights.new(name, "AREA")
        d.energy, d.size, d.color = energy, size, color
        o = bpy.data.objects.new(name, d)
        o.location, o.rotation_euler = loc, rot
        bpy.context.collection.objects.link(o)

    # three-point portrait lighting: warm key high and camera-left, cool fill
    # low camera-right, hard rim behind to separate the silhouette from ground
    area("key",  (-1.9, -2.3, 2.55), 260, 1.6, (1.00, 0.88, 0.76), (1.02, 0, -0.68))
    area("fill", ( 2.3, -1.7, 0.85),  26, 3.2, (0.58, 0.70, 1.00), (1.32, 0, 0.78))
    area("rim",  ( 0.9,  2.6, 2.10), 190, 0.9, (0.78, 0.88, 1.00), (-1.10, 0, 0.16))

    w = bpy.data.worlds.new("w")
    scn.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.016, 0.020, 0.030, 1)
    bg.inputs[1].default_value = 0.06

    # Framed properly this time: the subject is 1.87m tall and centred at
    # z=0.93. On an 85mm lens a full standing figure needs the camera well
    # back -- at 4.2m it framed a 1m sphere, so a 1.87m figure needs ~8.5m.
    # Pull back and aim at chest height, not the origin, or the feet crop.
    cam_d = bpy.data.cameras.new("cam")
    cam_d.lens = 85.0
    cam = bpy.data.objects.new("cam", cam_d)
    cam.location = (0.55, -8.6, 1.02)
    cam.rotation_euler = (1.5708 + 0.012, 0, 0.064)
    scn.collection.objects.link(cam)
    scn.camera = cam

    for spp in LADDER:
        scn.cycles.samples = spp
        out = os.path.join(OUTDIR, f"figure_{spp:04d}spp.png")
        scn.render.filepath = out
        t0 = time.time()
        bpy.ops.render.render(write_still=True)
        dt = time.time() - t0
        print(f"FIG {spp}spp: {dt:.1f}s -> {out}")
        print(f"FIG per_image_{spp}spp_s: {dt:.1f}")
        print(f"FIG images_per_hour_{spp}spp: {3600 / dt:.1f}")
    print(f"FIG total_seconds: {time.time() - t_all:.1f}")


main()

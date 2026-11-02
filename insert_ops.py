src = open('Project_SHARDEX/ops.py', encoding="utf-8").read()
needle = '    raise OpError("unhandled op'
idx = src.find(needle)

new_ops = '''    if kind == "ripple":
        cx = float(op["cx"])
        cy = float(op["cy"])
        amp = float(op["amp"])
        freq = float(op["freq"])
        decay = float(op["decay"])
        for node in neurons:
            dx = float(node[0]) - cx
            dy = float(node[1]) - cy
            dist = (dx * dx + dy * dy) ** 0.5
            if dist < 1e-9:
                continue
            # Wave propagation: sine wave radiating outward, decaying with distance
            turn = (dist * freq) % 1.0
            wave = table[int(turn * SINE_ENTRIES) % SINE_ENTRIES] / 32767.0
            falloff = 1.0 / (1.0 + decay * dist)
            node[2] = float(node[2]) + amp * wave * falloff
        return _pack(mesh, neurons, synapses)

    if kind == "attract":
        cx = float(op["cx"])
        cy = float(op["cy"])
        strength = float(op["strength"])
        radius = float(op["radius"])
        r2 = radius * radius
        for node in neurons:
            dx = cx - float(node[0])
            dy = cy - float(node[1])
            d2 = dx * dx + dy * dy
            if d2 > r2 or d2 < 1e-9:
                continue
            # Gravity well: pull toward center, stronger when closer
            force = strength / (1.0 + d2)
            node[0] = float(node[0]) + force * dx
            node[1] = float(node[1]) + force * dy
        return _pack(mesh, neurons, synapses)

    if kind == "twist":
        cx = float(op["cx"])
        cy = float(op["cy"])
        angle = float(op["angle"])
        radius = float(op["radius"])
        r2 = radius * radius
        import math as _math
        cos_a = _math.cos(angle)
        sin_a = _math.sin(angle)
        for node in neurons:
            dx = float(node[0]) - cx
            dy = float(node[1]) - cy
            d2 = dx * dx + dy * dy
            if d2 > r2:
                continue
            # Rotate around center, falloff with distance
            falloff = 1.0 - (d2 / r2)
            new_x = cx + dx * cos_a * falloff - dy * sin_a * falloff
            new_y = cy + dx * sin_a * falloff + dy * cos_a * falloff
            node[0] = new_x
            node[1] = new_y
        return _pack(mesh, neurons, synapses)

'''

src = src[:idx] + new_ops + src[idx:]
open('Project_SHARDEX/ops.py', 'w', encoding='utf-8').write(src)
print('inserted new operators')
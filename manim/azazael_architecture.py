import math

import manimgx as m


class AzazaelArchitecture(m.Scene):
    """Hub-and-spoke map of the Azazael agent fleet."""

    def construct(self) -> None:
        title = m.Text("AZAZAEL", font_size=56, color=m.YELLOW)
        title.to_edge(m.UP, buff=0.4)
        subtitle = m.Text("agent fleet architecture", font_size=26)
        subtitle.next_to(title, m.DOWN, buff=0.15)
        self.play(m.Write(title), m.Write(subtitle))

        hub = m.Circle(
            radius=0.85, color=m.WHITE, fill_opacity=0.15, stroke_width=3
        )
        hub_label = m.Text("CORE", font_size=28)
        hub_label.scale_to_fit_width(1.2)
        hub_label.move_to(hub.get_center())
        self.play(m.Create(hub), m.Write(hub_label))

        nodes = [
            ("WORMS", "226 worms, 35 categories", 120, m.BLUE),
            ("CLUSTERS", "ClusterWORMZ, MetaCluster", 60, m.GREEN),
            ("MEMORY", "PAMS, DirectMemory, .audit", 0, m.ORANGE),
            ("INFERENCE", "11+ free providers", -60, m.RED),
            ("COMPLIANCE", "RULE 0A-0Z, gates", -120, m.PURPLE),
            ("TOOLS", "azazael_ctl, skills", 180, m.TEAL),
        ]
        hub_center = hub.get_center()
        radius = 2.6
        y_offset = -0.55
        built = []
        for name, detail, angle_deg, color in nodes:
            angle = math.radians(angle_deg)
            center = [
                radius * math.cos(angle),
                radius * math.sin(angle) + y_offset,
                0,
            ]
            box = m.Rectangle(
                width=2.7, height=1.05, color=color,
                fill_opacity=0.12, stroke_width=2,
            )
            box.move_to(center)
            name_text = m.Text(name, font_size=24, color=color)
            name_text.scale_to_fit_width(2.4)
            detail_text = m.Text(detail, font_size=13)
            detail_text.scale_to_fit_width(2.4)
            label = m.VGroup(name_text, detail_text)
            label.arrange(m.DOWN, buff=0.08)
            label.move_to(center)
            direction = [
                center[0] - hub_center[0],
                center[1] - hub_center[1],
                0,
            ]
            length = math.hypot(direction[0], direction[1])
            unit = [direction[0] / length, direction[1] / length, 0]
            arrow_start = [
                hub_center[0] + 1.0 * unit[0],
                hub_center[1] + 1.0 * unit[1],
                0,
            ]
            arrow_end = [
                center[0] - 1.55 * unit[0],
                center[1] - 1.55 * unit[1],
                0,
            ]
            arrow = m.Arrow(arrow_start, arrow_end, buff=0, color=color)
            built.append(
                m.AnimationGroup(
                    m.Create(box), m.Write(label), m.Create(arrow)
                )
            )
        self.play(m.LaggedStart(*built, lag_ratio=0.15))

        caption = m.Text(
            "src/CORE  ·  WORMS  ·  ORCHESTRATION  ·  state/",
            font_size=16,
        )
        caption.to_edge(m.DOWN, buff=0.25)
        self.play(m.FadeIn(caption, shift=m.UP))
        self.wait(1.5)

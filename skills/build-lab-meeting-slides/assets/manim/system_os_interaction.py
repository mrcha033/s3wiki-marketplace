"""Quiet OS interaction scenes for build-lab-meeting-slides."""

import os

from manim import (
    AnimationGroup,
    Arrow,
    Circle,
    CurvedArrow,
    DashedVMobject,
    FadeIn,
    MoveAlongPath,
    Rectangle,
    Scene,
    Text,
    VGroup,
    config,
)


BACKGROUND = os.getenv("LABDECK_BACKGROUND", "#FFFFFF")
SURFACE = os.getenv("LABDECK_SURFACE", "#FFFFFF")
INK = os.getenv("LABDECK_INK", "#001233")
MUTED = os.getenv("LABDECK_MUTED", "#5C677D")
PRIMARY = os.getenv("LABDECK_PRIMARY", "#0353A4")
FOCUS = os.getenv("LABDECK_FOCUS", "#2269FE")
SOFT = os.getenv("LABDECK_SOFT", "#D2E1FE")

config.background_color = BACKGROUND


def component(label: str, width: float = 2.15) -> VGroup:
    box = Rectangle(
        width=width,
        height=1.15,
        color=PRIMARY,
        fill_color=SURFACE,
        fill_opacity=1,
        stroke_width=2.5,
    )
    text = Text(label, font="Arial", font_size=31, color=INK)
    return VGroup(box, text)


class SyscallPath(Scene):
    """User-space request crossing kernel and storage layers."""

    def construct(self) -> None:
        labels = ["User", "Syscall", "VFS", "Page Cache", "Device"]
        widths = [1.8, 1.85, 1.7, 2.4, 1.85]
        nodes = VGroup(
            *(component(label, width) for label, width in zip(labels, widths))
        )
        nodes.arrange(buff=0.42).move_to([0, 0.25, 0])
        arrows = VGroup(
            *[
                Arrow(
                    nodes[index].get_right(),
                    nodes[index + 1].get_left(),
                    buff=0.08,
                    color=PRIMARY,
                    stroke_width=3,
                    max_tip_length_to_length_ratio=0.16,
                )
                for index in range(len(nodes) - 1)
            ]
        )
        kernel_nodes = VGroup(*nodes[1:4])
        boundary = Rectangle(
            width=kernel_nodes.width + 0.35,
            height=1.65,
            color=MUTED,
            stroke_width=1.5,
            stroke_opacity=0.7,
        ).move_to(kernel_nodes.get_center())
        boundary_label = Text("Kernel", font="Arial", font_size=27, color=MUTED)
        boundary_label.next_to(boundary, direction=[0, 1, 0], buff=0.12)
        completion_path = CurvedArrow(
            nodes[-1].get_bottom(),
            nodes[0].get_bottom(),
            angle=-1.05,
            color=MUTED,
            stroke_width=2.2,
            tip_length=0.16,
        )
        completion = DashedVMobject(
            completion_path.copy(),
            num_dashes=24,
        )
        completion_label = Text("Completion", font="Arial", font_size=27, color=MUTED)
        completion_label.next_to(completion, direction=[0, -1, 0], buff=0.18)
        request = Circle(
            radius=0.12,
            color=FOCUS,
            fill_color=FOCUS,
            fill_opacity=1,
            stroke_width=0,
        ).move_to(nodes[0].get_center())

        self.add(boundary, boundary_label, nodes, arrows, completion, completion_label)
        self.wait(0.3)
        self.play(FadeIn(request))
        for index, arrow in enumerate(arrows, 1):
            self.play(
                AnimationGroup(
                    MoveAlongPath(request, arrow),
                    nodes[index][0].animate.set_fill(SOFT, opacity=1),
                ),
                run_time=0.65,
            )
            self.bring_to_front(*(node[1] for node in nodes), request, boundary_label)
            if index > 1:
                self.play(
                    nodes[index - 1][0].animate.set_fill(SURFACE, opacity=1),
                    run_time=0.12,
                )
                self.bring_to_front(*(node[1] for node in nodes), request, boundary_label)
        self.play(
            MoveAlongPath(request, completion_path),
            nodes[-1][0].animate.set_fill(SURFACE, opacity=1),
            nodes[0][0].animate.set_fill(SOFT, opacity=1),
            run_time=0.8,
        )
        self.bring_to_front(
            *(node[1] for node in nodes),
            request,
            boundary_label,
            completion_label,
        )
        self.wait(0.4)
        self.wait(0.65)

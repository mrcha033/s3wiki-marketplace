"""Quiet AI-serving interaction scenes for build-lab-meeting-slides."""

import os

from manim import (
    AnimationGroup,
    Arrow,
    Circle,
    FadeIn,
    LaggedStart,
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


def component(label: str, width: float) -> VGroup:
    box = Rectangle(
        width=width,
        height=1.1,
        color=PRIMARY,
        fill_color=SURFACE,
        fill_opacity=1,
        stroke_width=2.5,
    )
    text = Text(label, font="Arial", font_size=31, color=INK)
    return VGroup(box, text)


class ServingBatchFlow(Scene):
    """Requests join a live batch and leave as token streams."""

    def construct(self) -> None:
        router = component("Router", 1.65).move_to([-5.2, 0.5, 0])
        queue = component("Queue", 2.05).move_to([-2.75, 0.5, 0])
        scheduler = component("Scheduler", 2.15).move_to([0.05, 0.5, 0])
        gpu = component("GPU", 1.8).move_to([2.75, 0.5, 0])
        tokens = component("Tokens", 1.75).move_to([5.15, 0.5, 0])
        nodes = VGroup(router, queue, scheduler, gpu, tokens)
        arrows = VGroup(
            *[
                Arrow(
                    left.get_right(),
                    right.get_left(),
                    buff=0.08,
                    color=PRIMARY,
                    stroke_width=3,
                    max_tip_length_to_length_ratio=0.16,
                )
                for left, right in zip(nodes, nodes[1:])
            ]
        )
        edge_labels = VGroup(
            *[
                Text(label, font="Arial", font_size=30, color=MUTED).move_to(
                    [arrow.get_center()[0], -0.38, 0]
                )
                for label, arrow in zip(
                    ("Admit", "Select", "Run", "Stream"),
                    arrows,
                )
            ]
        )
        batch_lane = Rectangle(
            width=4.9,
            height=0.72,
            color=MUTED,
            fill_color=SURFACE,
            fill_opacity=1,
            stroke_width=1.5,
        ).move_to([0.05, -1.25, 0])
        batch_label = Text("Live Batch", font="Arial", font_size=28, color=MUTED)
        batch_label.next_to(batch_lane, direction=[0, -1, 0], buff=0.14)
        requests = VGroup(
            *[
                Circle(
                    radius=0.12,
                    color=FOCUS,
                    fill_color=FOCUS,
                    fill_opacity=1,
                    stroke_width=0,
                ).move_to(router.get_center() + [0, offset, 0])
                for offset in (-0.23, 0, 0.23)
            ]
        )

        self.add(nodes, arrows, edge_labels, batch_lane, batch_label)
        self.wait(0.3)
        self.play(FadeIn(requests))
        self.play(
            LaggedStart(
                *(MoveAlongPath(request, arrows[0]) for request in requests),
                lag_ratio=0.12,
            ),
            queue[0].animate.set_fill(SOFT, opacity=1),
            run_time=0.8,
        )
        self.bring_to_front(*(node[1] for node in nodes), requests, batch_label)
        self.play(
            requests.animate.arrange(buff=0.34).move_to(batch_lane.get_center()),
            queue[0].animate.set_fill(SURFACE, opacity=1),
            scheduler[0].animate.set_fill(SOFT, opacity=1),
            run_time=0.65,
        )
        self.bring_to_front(*(node[1] for node in nodes), requests, batch_label)
        self.play(
            AnimationGroup(
                requests.animate.move_to(gpu.get_center()),
                scheduler[0].animate.set_fill(SURFACE, opacity=1),
                gpu[0].animate.set_fill(SOFT, opacity=1),
            ),
            run_time=0.75,
        )
        self.bring_to_front(*(node[1] for node in nodes), requests, batch_label)
        self.play(
            requests.animate.arrange(buff=0.18).move_to(tokens.get_center() + [0, -1.05, 0]),
            gpu[0].animate.set_fill(SURFACE, opacity=1),
            tokens[0].animate.set_fill(SOFT, opacity=1),
            run_time=0.75,
        )
        self.bring_to_front(*(node[1] for node in nodes), requests, batch_label)
        self.wait(0.65)
        self.wait(0.65)

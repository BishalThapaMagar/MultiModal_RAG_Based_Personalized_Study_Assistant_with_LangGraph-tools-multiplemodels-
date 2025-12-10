# manim -pql file.py SceneName

from manim import *

class SceneName(Scene):
    def construct(self):
        self.camera.background_color = '#1e1e2f'

        # Title
        title = Text("Forward and Backpropagation", color=YELLOW, font_size=36)
        self.play(Write(title))
        self.wait(2)

        # Neural Network Structure
        input_layer = [Circle(radius=0.3, color=GREEN).shift(LEFT * 3 + UP * 2), Circle(radius=0.3, color=GREEN).shift(LEFT * 3), Circle(radius=0.3, color=GREEN).shift(LEFT * 3 + DOWN * 2)]
        hidden_layer = [Circle(radius=0.3, color=BLUE).shift(UP * 1), Circle(radius=0.3, color=BLUE).shift(DOWN * 1)]
        output_layer = Circle(radius=0.3, color=RED).shift(RIGHT * 3)

        for i in input_layer: self.play(Create(i), run_time=1)
        for h in hidden_layer: self.play(Create(h), run_time=1)
        self.play(Create(output_layer), run_time=1)

        # Connections
        connections_1 = [Line(input_layer[i].get_right(), hidden_layer[j].get_left()) for i in range(3) for j in range(2)]
        connections_2 = [Line(hidden_layer[i].get_right(), output_layer.get_left()) for i in range(2)]

        for c in connections_1: self.play(Create(c), run_time=0.5)
        for c in connections_2: self.play(Create(c), run_time=0.5)

        # Forward Propagation Animation
        dots_forward = [Dot(input_layer[i].get_center(), color=WHITE) for i in range(3)]
        for dot in dots_forward:
            self.play(MoveAlongPath(dot, connections_1[0]), run_time=2)
            self.play(MoveAlongPath(dot, connections_2[0]), run_time=2)

        # Backpropagation Animation (Illustrative)
        arrow_1 = Arrow(output_layer.get_left(), hidden_layer[0].get_right(), color=YELLOW)
        arrow_2 = Arrow(hidden_layer[0].get_left(), input_layer[0].get_right(), color=YELLOW)

        self.play(Create(arrow_1), Create(arrow_2), run_time=2)

        # Summary Text
        summary = Text("Forward prop: Input -> Output. Backprop: Error correction.", color=WHITE, font_size=28)
        self.play(Write(summary))
        self.wait(3)

        self.play(*[FadeOut(mob) for mob in self.mobjects])
        self.wait(2)

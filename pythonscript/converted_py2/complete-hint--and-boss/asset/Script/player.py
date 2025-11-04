from typing import Optional, Any
try:
    from py4godot import gdclass, signal
    from py4godot.core import *
except Exception:
    from godot import exposed as gdclass, signal
    from godot import *  # type: ignore


@gdclass
class Player(CharacterBody2D):
    def __init__(self):
        super().__init__()
        self.animated_sprite: Optional[AnimatedSprite2D] = None
        self.is_interacting: bool = False
        self.can_move: bool = True
        self.speech_label: Optional[Label] = None
        self.random_talk_timer: Optional[Timer] = None
        self.hide_timer: Optional[Timer] = None
        self.is_intro_finished: bool = False
        self.rng: RandomNumberGenerator = RandomNumberGenerator.new()
        self.font = load("res://asset/font/2005_iannnnnCPU.ttf")
        self.wait_time: float = 8.0
        self.SPEED: float = 200.0
        self.JUMP_VELOCITY: float = -400.0
        self.text_lines = [
            "นั่นเสียงอะไรน่ะ...",
            "ฉันเห็นอะไรอยู่ตรงนั้นหรือเปล่า...",
            "หรือว่าฉันแค่คิดไปเอง...",
            "ที่นี่มันเงียบเกินไปไหม...",
            "ทำไมรู้สึกเหมือนมีใครมองอยู่...",
            "แปลกจัง... อุณหภูมิลดลงหรือเปล่า...",
            "เรามาอยู่ที่นี่ได้ยังไงกัน...",
            "นี่เราควรไปทางนั้นจริง ๆ เหรอ...",
            "หรือว่า... ดวงจันทร์กำลังพูดกับฉัน?"
        ]

    def _ready(self) -> None:
        self.add_to_group("player")
        self.animated_sprite = self.get_node_or_null("AnimatedSprite2D")
        self._create_speech_label()
        self._create_timers()
        self.rng.randomize()
        self.wait_time = self.rng.randf_range(5.0, 10.0)
        self.is_intro_finished = True
        self._restart_random_talk_timer()

    def set_movement_locked(self, locked: bool) -> None:
        self.can_move = not locked
        self.is_interacting = locked
        self.velocity = Vector2.ZERO
        if locked and self.animated_sprite:
            self.animated_sprite.play("idle")

    def _physics_process(self, delta: float) -> None:
        if not self.can_move:
            self.velocity = Vector2.ZERO
            self.move_and_slide()
            return

        gravity = float(ProjectSettings.get_setting("physics/2d/default_gravity", 980.0))
        if not self.is_on_floor():
            self.velocity.y += gravity * delta

        dir = 0
        if Input.is_action_pressed("ui_right"):
            dir += 1
        if Input.is_action_pressed("ui_left"):
            dir -= 1

        if Input.is_action_just_pressed("jump") and self.is_on_floor():
            self.velocity.y = self.JUMP_VELOCITY

        if self.animated_sprite:
            if dir > 0:
                self.animated_sprite.flip_h = False
            elif dir < 0:
                self.animated_sprite.flip_h = True

            if self.is_on_floor():
                if dir == 0:
                    self.animated_sprite.play("idle")
                else:
                    self.animated_sprite.play("run")
            else:
                self.animated_sprite.play("jump")

        if dir != 0:
            self.velocity.x = dir * self.SPEED
        else:
            self.velocity.x = move_toward(self.velocity.x, 0, self.SPEED)

        self.move_and_slide()

    def _create_speech_label(self) -> None:
        self.speech_label = Label.new()
        self.speech_label.visible = False
        self.speech_label.autowrap_mode = TextServer.AUTOWRAP_WORD
        self.speech_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
        self.speech_label.size = Vector2(200, 0)
        self.speech_label.position = Vector2(-100, -60)
        if self.font:
            self.speech_label.add_theme_font_override("font", self.font)
        self.speech_label.add_theme_font_size_override("font_size", 18)
        self.speech_label.add_theme_constant_override("outline_size", 2)
        self.speech_label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 1))
        self.speech_label.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.6))
        self.speech_label.add_theme_constant_override("shadow_offset_x", 2)
        self.speech_label.add_theme_constant_override("shadow_offset_y", 2)
        self.add_child(self.speech_label)

    def _create_timers(self) -> None:
        self.random_talk_timer = Timer.new()
        self.random_talk_timer.one_shot = True
        self.random_talk_timer.timeout.connect(self._on_random_talk_timeout)
        self.add_child(self.random_talk_timer)

        self.hide_timer = Timer.new()
        self.hide_timer.one_shot = True
        self.hide_timer.timeout.connect(self._on_hide_timeout)
        self.add_child(self.hide_timer)

    def _restart_random_talk_timer(self) -> None:
        if not self.is_intro_finished or not self.random_talk_timer:
            return
        self.wait_time = self.rng.randf_range(5.0, 10.0)
        self.random_talk_timer.start(self.wait_time)

    def _on_random_talk_timeout(self) -> None:
        if not self.is_intro_finished or self.is_interacting:
            self._restart_random_talk_timer()
            return
        if not self.speech_label or len(self.text_lines) == 0:
            self._restart_random_talk_timer()
            return
        idx = int(self.rng.randi() % len(self.text_lines))
        self.speech_label.text = self.text_lines[idx]
        self.speech_label.visible = True
        if self.hide_timer:
            self.hide_timer.start(3.5)
        self._restart_random_talk_timer()

    def _on_hide_timeout(self) -> None:
        if self.speech_label:
            self.speech_label.visible = False

from typing import Optional, List
try:
    from py4godot import gdclass
    from py4godot.core import *
except Exception:
    from godot import exposed as gdclass
    from godot import *  # type: ignore


@gdclass
class RandomTalker(Node2D):
    def __init__(self):
        super().__init__()
        self.delay_min: float = 6.0
        self.delay_max: float = 12.0
        self.text_speed: float = 0.04
        self.stay_time: float = 2.0
        self.is_intro_finished: bool = False
        self.speech_label: Optional[Label] = None
        self._timer_random: Optional[Timer] = None
        self._timer_type: Optional[Timer] = None
        self._timer_hide: Optional[Timer] = None
        self.random_lines: List[str] = [
            "นั่นเสียงอะไรน่ะ...",
            "ฉันเห็นอะไรอยู่ตรงนั้นหรือเปล่า...",
            "ที่นี่มันเงียบเกินไปไหม...",
            "เรามาอยู่ที่นี่ได้ยังไงกัน...",
            "หรือว่าฉันแค่จินตนาการไปเอง...",
            "มีบางอย่าง...ไม่ถูกต้อง",
            "เธอได้ยินเหมือนฉันไหม...",
            "นี่เราควรไปทางนั้นจริง ๆ เหรอ...",
            "แปลกจัง...",
            "ทำไมรู้สึกว่าดวงจันทร์มันใกล้เกินไป...",
            "เสียงเมื่อกี้... มาจากไหนกันแน่...",
            "ฉันรู้สึกเหมือนมีบางอย่างอยู่ข้างหลัง...",
            "จะได้เกรดเท่าไหร่นะ",
            "ทำไมอากาศถึงเย็นขึ้นกะทันหัน...",
            "แสงนั่น... มันกำลังขยับอยู่หรือเปล่า...",
            "เหมือนจะได้ยินเสียงใครเรียกชื่อฉัน...",
            "มีบางอย่างไม่ถูกต้องกับที่แห่งนี้...",
            "ดวงจันทร์นั่น... ทำไมมันดูใกล้ขนาดนั้น...",
            "ที่นี่เคยมีคนอยู่มาก่อนจริง ๆ เหรอ...",
            "ถ้าออกไปจากที่นี่ไม่ได้... จะเกิดอะไรขึ้นนะ..."
        ]
        self._rng: RandomNumberGenerator = RandomNumberGenerator.new()
        self._current_line: str = ""
        self._type_index: int = 0

    def _ready(self) -> None:
        self._rng.randomize()
        self._create_label()
        self._create_timers()
        self._schedule_next()

    def start_random_talks(self) -> None:
        self.is_intro_finished = True
        self._schedule_next()

    def _create_label(self) -> None:
        self.speech_label = Label.new()
        self.speech_label.visible = False
        self.speech_label.autowrap_mode = TextServer.AUTOWRAP_WORD
        self.speech_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
        self.speech_label.add_theme_font_size_override("font_size", 18)
        self.speech_label.size = Vector2(220, 0)
        self.speech_label.position = Vector2(-110, -70)
        self.add_child(self.speech_label)

    def _create_timers(self) -> None:
        self._timer_random = Timer.new()
        self._timer_random.one_shot = True
        self._timer_random.timeout.connect(self._on_random_timeout)
        self.add_child(self._timer_random)

        self._timer_type = Timer.new()
        self._timer_type.one_shot = False
        self._timer_type.wait_time = self.text_speed
        self._timer_type.timeout.connect(self._on_type_tick)
        self.add_child(self._timer_type)

        self._timer_hide = Timer.new()
        self._timer_hide.one_shot = True
        self._timer_hide.timeout.connect(self._on_hide_timeout)
        self.add_child(self._timer_hide)

    def _schedule_next(self) -> None:
        if not self._timer_random:
            return
        wait = self._rng.randf_range(self.delay_min, self.delay_max)
        self._timer_random.start(max(0.01, float(wait)))

    def _on_random_timeout(self) -> None:
        if not self.is_intro_finished or not self.random_lines:
            self._schedule_next()
            return
        self._current_line = self.random_lines[int(self._rng.randi() % len(self.random_lines))]
        self._type_index = 0
        if self.speech_label:
            self.speech_label.visible = True
            self.speech_label.text = ""
        if self._timer_type:
            self._timer_type.wait_time = self.text_speed
            self._timer_type.start()

    def _on_type_tick(self) -> None:
        if not self.speech_label:
            if self._timer_type:
                self._timer_type.stop()
            self._schedule_next()
            return
        if self._type_index < len(self._current_line):
            self.speech_label.text += self._current_line[self._type_index]
            self._type_index += 1
        else:
            if self._timer_type:
                self._timer_type.stop()
            if self._timer_hide:
                self._timer_hide.start(max(0.01, float(self.stay_time)))

    def _on_hide_timeout(self) -> None:
        if self.speech_label:
            self.speech_label.visible = False
        self._schedule_next()

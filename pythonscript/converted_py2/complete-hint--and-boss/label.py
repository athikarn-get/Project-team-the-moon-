# --- Godot Python bridge imports (py4godot primary) ---
from typing import Optional, Any

try:
    # py4godot (Godot 4.x Pluginscript)
    from py4godot import gdclass, signal
    from py4godot.core import *  # import all core Godot classes (Node2D, AcceptDialog, Area2D, Label, Button, etc.)
except Exception:
    # Fallback: godot-python (experimental for Godot 4, signatures may differ)
    from godot import exposed as gdclass, signal
    from godot import *  # type: ignore

@gdclass
class Label(Node):
    def __init__(self):
        super().__init__()
        self.delay_min = None  # @export
        self.delay_max = None  # @export
        self.text_speed = None  # @export
        self.stay_time = None  # @export
        self.speech_label = None
        self.random_talk_timer = None
        self.is_intro_finished = None
        self.random_lines = None
        self.line = random_lines[randi() % random_lines.size()]
        self.wait = None

    def _ready(self) -> None:
        pass



    # -------------------------
    # รายชื่อประโยคสั้นเชิงสงสัย
    # -------------------------
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
    	"จะได้เกรดเื่าไหร่นะ",
    	"ทำไมอากาศถึงเย็นขึ้นกะทันหัน...",
    	"แสงนั่น... มันกำลังขยับอยู่หรือเปล่า...",
    	"เหมือนจะได้ยินเสียงใครเรียกชื่อฉัน...",
    	"มีบางอย่างไม่ถูกต้องกับที่แห่งนี้...",
    	"ดวงจันทร์นั่น... ทำไมมันดูใกล้ขนาดนั้น...",
    	"ที่นี่เคยมีคนอยู่มาก่อนจริง ๆ เหรอ...",
    	"ถ้าออกไปจากที่นี่ไม่ได้... จะเกิดอะไรขึ้นนะ..."

    ]

    # -------------------------
    # เริ่มต้น
    # -------------------------

    def _ready(self):
    	randomize()
    	_create_label()
    	_create_timer()

    # -------------------------
    # ฟังก์ชันเรียกจาก Player เมื่อ intro พูดจบ
    # -------------------------

    def start_random_talks(self):
    	is_intro_finished = True
    	_restart_timer()

    # -------------------------
    # สร้าง Label สำหรับแสดงข้อความ
    # -------------------------

    def _create_label(self):
    	speech_label = Label.new()
    	speech_label.visible = False
    	speech_label.autowrap_mode = TextServer.AUTOWRAP_WORD
    	speech_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    	speech_label.add_theme_font_size_override("font_size", 18)
    	speech_label.size = Vector2(220, 0)
    	speech_label.position = Vector2(-110, -70)
    	add_child(speech_label)

    # -------------------------
    # สร้าง Timer สำหรับสุ่มบทพูด
    # -------------------------

    def _create_timer(self):
    	random_talk_timer = Timer.new()
    	random_talk_timer.one_shot = True
    	random_talk_timer.timeout.connect(_on_random_talk_timeout)
    	add_child(random_talk_timer)

    # -------------------------
    # เมื่อถึงเวลาพูดสุ่ม
    # -------------------------

    def _on_random_talk_timeout(self):
    	if not is_intro_finished:
    		return  # ❌ ยังอยู่ในฉากเปิดเกม
    # TODO: convert awaiting: 	await _speak_line(line)
    	_restart_timer()

    # -------------------------
    # พิมพ์ข้อความทีละตัว
    # -------------------------

    def _speak_line(self, line):
    	speech_label.visible = True
    	speech_label.text = ""
    	for c in line:
    		speech_label.text += c
    # TODO: convert awaiting: 		await get_tree().create_timer(text_speed).timeout
    # TODO: convert awaiting: 	await get_tree().create_timer(stay_time).timeout
    	speech_label.visible = False

    # -------------------------
    # ตั้งเวลาใหม่แบบสุ่ม
    # -------------------------

    def _restart_timer(self):
    	random_talk_timer.start(wait)

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
class Player(CharacterBody2D):
    def __init__(self):
        super().__init__()
        self.animated_sprite: Any = None  # onready; set in _ready
        self.is_interacting = None
        self.can_move =  True
        self.speech_label = None
        self.random_talk_timer = None
        self.is_intro_finished = None
        self.random_lines = None
        self.dir = None
        self.font = load("res://asset/font/2005_iannnnnCPU.ttf")
        self.timer = None
        self.skip = None
        self.wait_time = randf_range(5.0, 10.0) # พูดทุก 10–20 วิ
        self.text = random_lines[randi() % random_lines.size()]

    def _ready(self) -> None:
        self.animated_sprite = self.get_node(\"\1\")

    const SPEED := 200.0
    const JUMP_VELOCITY := -400.0



    # ประโยคสุ่มสั้น ๆ เชิงสงสัย
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


    def set_movement_locked(self, locked):
    	can_move = not locked
    	is_interacting = locked      # ✅ บอกสถานะว่ากำลัง interact อยู่
    	velocity = Vector2.ZERO
    	if locked and animated_sprite:
    		animated_sprite.play("idle")



    def _ready(self):
    	add_to_group("player")
    	_create_speech_label()
    	_create_random_talk_timer()

    	# ---------- บทพูดเปิดเกม ----------
    # TODO: convert awaiting: 	await speak_start([
    		"ยินดีต้อนรับสู่ The Moon...",
    		"นี่ไม่ใช่โปรเจ็กต์ใหญ่จากบริษัทไหน...",
    		"แต่มันคือผลงานเล็ก ๆ จากนักศึกษากลุ่มหนึ่ง...",
    		"สร้างขึ้นเพื่อส่งในวิชา PSCP",
    		"และเพื่อจุดประกายให้ใครสักคนอยากเรียนรู้ Python มากขึ้น",
    		"เราอยากให้ทุกคนได้เห็นว่า... การเขียนโค้ดก็สามารถเป็นเรื่องสนุกได้",
    		"เกมนี้ถูกเขียนด้วยความตั้งใจ และความเหนื่อยที่อยากให้กลายเป็นแรงบันดาลใจ",
    		"มันอาจยังมีข้อผิดพลาด มีจุดที่ยังไม่สมบูรณ์",
    		"และก็อาจจะยังมีบั๊กต่างๆ",
    		"หากทุกคนได้อะไรกลับไปจากเกมนี้ นั่นก็คือสิ่งที่เราหวังไว้",
    		"ขอบคุณที่เข้ามาทดลองเล่นเกมนี้",
    		"ฉันชื่อ Snow... ยินดีที่ได้รู้จัก :)"
    	], 3.5)

    	# ---------- เริ่มสุ่มพูดหลัง intro ----------
    	is_intro_finished = True
    	_restart_random_talk_timer()



    def _physics_process(self, delta):
    	if not can_move:
    		velocity = Vector2.ZERO
    		move_and_slide()
    		return

    	if not is_on_floor():
    		velocity += get_gravity() * delta

    	if Input.is_action_just_pressed("jump") and is_on_floor():
    		velocity.y = JUMP_VELOCITY


    	if dir > 0:
    		animated_sprite.flip_h = False
    	elif dir < 0:
    		animated_sprite.flip_h = True

    	if is_on_floor():
    		if dir == 0:
    			animated_sprite.play("idle")
    		else:
    			animated_sprite.play("run")
    	else:
    		animated_sprite.play("jump")

    	if dir != 0:
    		velocity.x = dir * SPEED
    	else:
    		velocity.x = move_toward(velocity.x, 0, SPEED)

    	move_and_slide()


    # ------------------- SPEECH SYSTEM -------------------


    def _create_speech_label(self):
    	speech_label = Label.new()
    	speech_label.visible = False
    	speech_label.autowrap_mode = TextServer.AUTOWRAP_WORD
    	speech_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER   # ✅ จัดชิดซ้าย
    	speech_label.size = Vector2(200, 0)  # ✅ แคบลงให้พอดีกับหัว
    	speech_label.position = Vector2(-100, -60)  # ✅ เลื่อนให้อยู่ใกล้หัวฝั่งซ้าย (ลองปรับค่า X,Y ได้)

    	# โหลดฟอนต์
    	speech_label.add_theme_font_override("font", font)

    	# ✅ ทำตัวอักษรเล็กลง
    	speech_label.add_theme_font_size_override("font_size", 18)

    	# ✅ เพิ่มขอบให้อ่านง่าย
    	speech_label.add_theme_constant_override("outline_size", 2)
    	speech_label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 1))

    	# ✅ เพิ่มเงา (optional)
    	speech_label.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.6))
    	speech_label.add_theme_constant_override("shadow_offset_x", 2)
    	speech_label.add_theme_constant_override("shadow_offset_y", 2)

    	add_child(speech_label)




    def speak_start(self, lines, per_line= 1.8):
    	set_movement_locked(True)
    	speech_label.visible = True

    	for t in lines:
    		speech_label.text = t

    		while timer < per_line:
    # TODO: convert awaiting: 			await get_tree().process_frame
    			timer += get_process_delta_time()

    			# ถ้ากด Space หรือ Enter (ui_accept) → ข้ามไปประโยคถัดไปทันที
    			if Input.is_action_just_pressed("ui_accept"):
    				skip = True
    				break

    		if skip:
    			continue  # ไปบรรทัดถัดไปทันทีโดยไม่รอเวลาจบของบรรทัดนี้

    	speech_label.visible = False
    	set_movement_locked(False)



    # ------------------- RANDOM TALK SYSTEM -------------------


    def _create_random_talk_timer(self):
    	random_talk_timer = Timer.new()
    	random_talk_timer.one_shot = True
    	random_talk_timer.timeout.connect(_on_random_talk_timeout)
    	add_child(random_talk_timer)



    def _restart_random_talk_timer(self):
    	if not is_intro_finished:
    		return
    	random_talk_timer.start(wait_time)



    def _on_random_talk_timeout(self):
    	if not is_intro_finished or is_interacting:
    		_restart_random_talk_timer()
    		return

    # TODO: convert awaiting: 	await speak_line(text)
    	_restart_random_talk_timer()




    def speak_line(self, text, speed= 0.05):
    	speech_label.visible = True
    	speech_label.text = ""
    	for c in text:
    		speech_label.text += c
    # TODO: convert awaiting: 		await get_tree().create_timer(speed).timeout
    # TODO: convert awaiting: 	await get_tree().create_timer(3.5).timeout
    	speech_label.visible = False

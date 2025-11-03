extends CharacterBody2D

const SPEED := 200.0
const JUMP_VELOCITY := -400.0

@onready var animated_sprite: AnimatedSprite2D = $AnimatedSprite2D

var is_interacting := false
var can_move: bool = true
var speech_label: Label
var random_talk_timer: Timer
var is_intro_finished := false

# ประโยคสุ่มสั้น ๆ เชิงสงสัย
var random_lines := [
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

func set_movement_locked(locked: bool) -> void:
	can_move = not locked
	is_interacting = locked      # ✅ บอกสถานะว่ากำลัง interact อยู่
	velocity = Vector2.ZERO
	if locked and animated_sprite:
		animated_sprite.play("idle")


func _ready() -> void:
	add_to_group("player")
	_create_speech_label()
	_create_random_talk_timer()

	# ---------- บทพูดเปิดเกม ----------
	await speak_start([
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
	is_intro_finished = true
	_restart_random_talk_timer()


func _physics_process(delta: float) -> void:
	if not can_move:
		velocity = Vector2.ZERO
		move_and_slide()
		return

	if not is_on_floor():
		velocity += get_gravity() * delta

	if Input.is_action_just_pressed("jump") and is_on_floor():
		velocity.y = JUMP_VELOCITY

	var dir := Input.get_axis("walk_l", "walk_r")

	if dir > 0:
		animated_sprite.flip_h = false
	elif dir < 0:
		animated_sprite.flip_h = true

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

func _create_speech_label() -> void:
	speech_label = Label.new()
	speech_label.visible = false
	speech_label.autowrap_mode = TextServer.AUTOWRAP_WORD
	speech_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER   # ✅ จัดชิดซ้าย
	speech_label.size = Vector2(200, 0)  # ✅ แคบลงให้พอดีกับหัว
	speech_label.position = Vector2(-100, -60)  # ✅ เลื่อนให้อยู่ใกล้หัวฝั่งซ้าย (ลองปรับค่า X,Y ได้)

	# โหลดฟอนต์
	var font: Font = load("res://asset/font/2005_iannnnnCPU.ttf")
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



func speak_start(lines: Array[String], per_line: float = 1.8) -> void:
	set_movement_locked(true)
	speech_label.visible = true

	for t in lines:
		speech_label.text = t
		var timer := 0.0
		var skip := false

		while timer < per_line:
			await get_tree().process_frame
			timer += get_process_delta_time()

			# ถ้ากด Space หรือ Enter (ui_accept) → ข้ามไปประโยคถัดไปทันที
			if Input.is_action_just_pressed("ui_accept"):
				skip = true
				break

		if skip:
			continue  # ไปบรรทัดถัดไปทันทีโดยไม่รอเวลาจบของบรรทัดนี้

	speech_label.visible = false
	set_movement_locked(false)



# ------------------- RANDOM TALK SYSTEM -------------------

func _create_random_talk_timer() -> void:
	random_talk_timer = Timer.new()
	random_talk_timer.one_shot = true
	random_talk_timer.timeout.connect(_on_random_talk_timeout)
	add_child(random_talk_timer)


func _restart_random_talk_timer() -> void:
	if not is_intro_finished:
		return
	var wait_time = randf_range(5.0, 10.0) # พูดทุก 10–20 วิ
	random_talk_timer.start(wait_time)


func _on_random_talk_timeout() -> void:
	if not is_intro_finished or is_interacting:
		_restart_random_talk_timer()
		return

	var text = random_lines[randi() % random_lines.size()]
	await speak_line(text)
	_restart_random_talk_timer()



func speak_line(text: String, speed: float = 0.05) -> void:
	speech_label.visible = true
	speech_label.text = ""
	for c in text:
		speech_label.text += c
		await get_tree().create_timer(speed).timeout
	await get_tree().create_timer(3.5).timeout
	speech_label.visible = false

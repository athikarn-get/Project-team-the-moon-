extends Node2D

# === Quiz config ==============================================================
@export var quiz_question := "🧩 ข้อที่ 2 — Algorithm (Recursion แบบแบ่งครึ่ง)\n\nสถานการณ์:\nให้ฟังก์ชัน strange_sum(arr, l, r) ทำงานแบบแบ่งครึ่งอาเรย์และรวมผลแบบมีเงื่อนไขความยาวช่วง\n\npython\n def strange_sum(arr, l, r):\n     if l == r:\n         return arr[l]\n     m = (l + r) // 2\n     left = strange_sum(arr, l, m)\n     right = strange_sum(arr, m + 1, r)\n     if (r - l + 1) % 2 == 0:\n         return left + right\n     else:\n         return left - right\n\nคำอธิบายโจทย์:\n- ฟังก์ชันจะแบ่งช่วง [l, r] ออกเป็นซ้ายและขวาจนเหลือสมาชิกเดียว\n- ถ้าความยาวช่วงเป็นเลขคู่ ให้บวกซ้ายกับขวา\n- ถ้าเป็นเลขคี่ ให้ลบซ้ายกับขวา\n- สุดท้ายรวมผลลัพธ์และพิมพ์ออกมา\n\nอินพุตตัวอย่าง:\narr = [2, -3, 4, 1, 5]\nprint(strange_sum(arr, 0, len(arr) - 1))"
@export var quiz_answer := "-11"
@export var blocker_path: NodePath
@export var show_hint_text := true

# === Internals ================================================================
var _player: Node = null
var _in_range := false
var _done := false
var _quiz = QuizOverlayLite.new()
var _area: InteractArea

@onready var boss_label: Label = $bossdialog2   # <<< Label ของบอสตัวที่ 2

func _ready() -> void:
	# --- Label ของบอสให้ซ่อนไว้ก่อน ---
	if boss_label:
		boss_label.visible = false
		# กันกลับหัวเวลาสไปรต์พลิก (ถ้าไม่จำเป็นจะปิดบรรทัดนี้ได้)
		# boss_label.top_level = true
	else:
		push_error("[Boss2] Missing Label node named 'bossdialog2'.")

	# --- สร้าง Quiz Overlay ---
	_quiz = QuizOverlayLite.new()
	var layer := get_tree().current_scene.get_node_or_null("CanvasLayer")
	if layer:
		layer.add_child(_quiz)
	else:
		get_tree().current_scene.add_child(_quiz)
	_quiz.z_index = 9999
	_quiz.answered.connect(_on_quiz_answered)

	# --- ตั้งค่า InteractArea ---
	_area = $InteractArea as InteractArea
	if _area == null:
		push_error("[Boss2] Missing InteractArea with InteractArea.gd attached.")
		return
	_area.action_name = "talk"
	_area.interact = Callable(self, "_do_open_quiz")
	_area.body_entered.connect(_on_enter)
	_area.body_exited.connect(_on_exit)

func _physics_process(_dt: float) -> void:
	# Fallback: อยู่ในระยะแล้วกด E เพื่อเปิดกล่องคำถาม
	if _in_range and not _quiz.visible and Input.is_action_just_pressed("interact"):
		_do_open_quiz()

# === Label helpers ============================================================
func _boss_say(text: String, auto_hide_sec: float = -1.0) -> void:
	if boss_label == null:
		return
	boss_label.text = text
	boss_label.visible = true
	if auto_hide_sec > 0.0:
		_hide_label_later(auto_hide_sec)

func _boss_clear() -> void:
	if boss_label:
		boss_label.text = ""
		boss_label.visible = false

func _hide_label_later(sec: float) -> void:
	await get_tree().create_timer(sec).timeout
	_boss_clear()

# === Triggers ================================================================
func _on_enter(body: Node) -> void:
	if body.is_in_group("player"):
		_player = body
		_in_range = true
		if show_hint_text:
			if _done:
				_boss_say("ไปต่อได้แล้ว...", 2.0)
			else:
				_boss_say("ทดสอบง่าย ๆ หน่อยสิ กด [E] เพื่อเริ่มนับ 0-9 ...")

func _on_exit(body: Node) -> void:
	if body == _player:
		_in_range = false
		_player = null
		_boss_clear()

# === Quiz events =============================================================
func _do_open_quiz() -> void:
	if _done or not _in_range or _player == null or _quiz.visible:
		return
	_boss_clear()
	if _player.has_method("set_movement_locked"):
		_player.set_movement_locked(true)
	# เปิดคำถาม
	_quiz.ask(quiz_question, quiz_answer)

func _on_quiz_answered(correct: bool, _given: String) -> void:
	# ปลดล็อกการเดิน
	if _player and _player.has_method("set_movement_locked"):
		_player.set_movement_locked(false)

	if correct:
		_done = true

		# ---- เปิดทาง: ลบ Wall2 หากมีในฉากหลัก ----
		var wall2 := get_tree().current_scene.get_node_or_null("Wall2")
		if wall2:
			wall2.queue_free()
		else:
			# เผื่อกรณีโอ๊ตตั้ง blocker_path ไว้ใน Inspector
			if blocker_path != NodePath():
				var wall := get_node_or_null(blocker_path)
				if wall:
					wall.queue_free()

		_boss_say("ดีมาก! ผ่านไปได้เลย...", 2.0)
	else:
		_boss_say("ยังไม่ใช่นะ ลองนับ 0 ถึง 9 ให้ถูกวิธีอีกครั้ง...", 2.0)

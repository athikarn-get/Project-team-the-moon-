extends Node2D

# Quiz config (Boss1)
@export var quiz_question := "🧠 ข้อที่ 1 — พื้นฐาน Python (if-else + loop)\n\nnums = [1, 2, 3, 4, 5]\ntotal = 0\nfor n in nums:\n    if n % 2 == 0:\n        total += n\nprint(total)"
@export var quiz_answer := "6"
@export var blocker_path: NodePath
@export var show_hint_text := true

var _player: Node = null
var _in_range := false
var _done := false
var _quiz: QuizOverlayLite = null
var _area: InteractArea

@onready var boss_label: Label = $bossdialog 

func _ready() -> void:
	#  ซ่อน Label 
	if boss_label:
		boss_label.visible = false
	else:
		push_error("[Boss1] Missing Label node named 'bossdialog'.")

	# เซ็ทค่า InteractArea
	_area = $InteractArea as InteractArea
	if _area == null:
		push_error("[Boss1] Missing InteractArea with InteractArea.gd attached.")
		return
	_area.action_name = "talk"
	_area.interact = Callable(self, "_do_open_quiz")
	_area.body_entered.connect(_on_enter)
	_area.body_exited.connect(_on_exit)

	_ensure_quiz()

func _ensure_quiz() -> void:
	if not is_instance_valid(_quiz):
		_quiz = QuizOverlayLite.new()
		var layer := get_tree().current_scene.get_node_or_null("CanvasLayer")
		if layer == null:
			layer = CanvasLayer.new()
			layer.name = "CanvasLayer"
			layer.layer = 100
			get_tree().current_scene.add_child(layer)
		layer.add_child(_quiz)
		_quiz.z_index = 9999
		if not _quiz.answered.is_connected(_on_quiz_answered):
			_quiz.answered.connect(_on_quiz_answered)

func _physics_process(_dt: float) -> void:
	var quiz_visible := is_instance_valid(_quiz) and _quiz.visible
	if _in_range and (not quiz_visible) and Input.is_action_just_pressed("interact"):
		_do_open_quiz()

# Label helpers
func _boss_say(text: String, auto_hide_sec: float = -1.0) -> void:
	if boss_label == null:
		return
	boss_label.text = text
	boss_label.visible = true
	if auto_hide_sec > 0.0:
		await get_tree().create_timer(auto_hide_sec).timeout
		_boss_clear()

func _boss_clear() -> void:
	if boss_label:
		boss_label.text = ""
		boss_label.visible = false

# Triggers 
func _on_enter(body: Node) -> void:
	if body.is_in_group("player"):
		_player = body
		_in_range = true
		if show_hint_text:
			if _done:
				_boss_say("ไปต่อได้แล้ว...", 2.0)
			else:
				_boss_say("กด [E] เพื่อคุยกับบอส...")

func _on_exit(body: Node) -> void:
	if body == _player:
		_in_range = false
		_player = null
		_boss_clear()

# Quiz flow
func _do_open_quiz() -> void:
	if _done or not _in_range or _player == null:
		return
	_ensure_quiz()
	if _quiz.visible:
		return
	_boss_clear()
	if _player.has_method("set_movement_locked"):
		_player.set_movement_locked(true)
	_quiz.ask(quiz_question, quiz_answer)

func _on_quiz_answered(correct: bool, _given: String) -> void:
	# ปลดการเดิน
	if _player and _player.has_method("set_movement_locked"):
		_player.set_movement_locked(false)

	# ไม่ free ทันที
	if is_instance_valid(_quiz):
		_quiz.hide()

	if correct:
		_done = true
		
		if blocker_path != NodePath():
			var wall := get_node_or_null(blocker_path)
			if wall:
				wall.queue_free()
		else:
			
			var wall_auto := get_tree().current_scene.get_node_or_null("Wall")
			if wall_auto:
				wall_auto.queue_free()

		_boss_say("ถูกต้อง! ทางข้างหน้าถูกเปิดแล้ว...", 2.0)
	else:
		_boss_say("ยังไม่ถูก ลองใหม่นะ...", 2.0)

extends Node2D

@export var quiz_question := "พิมพ์ฟังก์ชันที่ใช้แสดงผลข้อความใน Python"
@export var quiz_answer := "print()"
@export var blocker_path: NodePath
@export var show_hint_text := true

var _player: Node = null
var _in_range := false
var _done := false
var _quiz: QuizOverlay
var _area: InteractArea

func _ready() -> void:
	_quiz = QuizOverlay.new()

	# ถ้ามี CanvasLayer ให้แปะไว้บน Canvas เลย
	var layer := get_tree().current_scene.get_node_or_null("CanvasLayer")
	if layer:
		layer.add_child(_quiz)
	else:
		get_tree().current_scene.add_child(_quiz)
	_quiz.z_index = 9999

	_quiz.answered.connect(_on_quiz_answered)

	_area = $InteractArea as InteractArea
	if _area == null:
		push_error("[Boss] Missing InteractArea with InteractArea.gd attached.")
		return

	_area.action_name = "talk"
	_area.interact = Callable(self, "_do_open_quiz")

	_area.body_entered.connect(_on_enter)
	_area.body_exited.connect(_on_exit)

func _physics_process(_dt: float) -> void:
	# --- Fallback: ถ้าอยู่ในระยะและกด E แต่ Manager ไม่เรียก ก็เปิดเอง ---
	if _in_range and not _quiz.visible and Input.is_action_just_pressed("interact"):
		_do_open_quiz()

func _on_enter(body: Node) -> void:
	if body.is_in_group("player"):
		_player = body
		_in_range = true
		if show_hint_text and _player.has_method("speak_line"):
			_player.speak_line("กด [E] เพื่อคุยกับบอส...", 0.03)

func _on_exit(body: Node) -> void:
	if body == _player:
		_in_range = false
		_player = null

func _do_open_quiz() -> void:
	if _done or not _in_range or _player == null or _quiz.visible:
		return
	if _player.has_method("set_movement_locked"):
		_player.set_movement_locked(true)
	_quiz.ask(quiz_question, quiz_answer)

func _on_quiz_answered(correct: bool, _given: String) -> void:
	if _player and _player.has_method("set_movement_locked"):
		_player.set_movement_locked(false)

	if correct:
		_done = true
		if blocker_path != NodePath():
			var wall := get_node_or_null(blocker_path)
			if wall:
				wall.queue_free()
		if _player and _player.has_method("speak_line"):
			_player.speak_line("ถูกต้อง! ทางข้างหน้าถูกเปิดแล้ว...", 0.03)
	else:
		if _player and _player.has_method("speak_line"):
			_player.speak_line("ยังไม่ถูก ลองใหม่นะ...", 0.03)

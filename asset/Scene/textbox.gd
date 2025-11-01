extends CanvasLayer
signal finished

const CHAR_READ_RATE := 0.03

@onready var textbox_container: Control = $TextboxContainer
@onready var start_symbol: Label = $TextboxContainer/MarginContainer/HBoxContainer/Start
@onready var end_symbol: Label = $TextboxContainer/MarginContainer/HBoxContainer/End
@onready var label: Label = $TextboxContainer/MarginContainer/HBoxContainer/Control/Label

enum State { READY, READING, FINISHED }
var current_state: State = State.READY          # <-- typed

var reveal_tween: Tween = null                  # <-- typed (SceneTreeTween is a Tween in 4.x)
var text_queue: Array[String] = []              # <-- typed
var anchor_world_pos: Vector2 = Vector2.ZERO    # <-- typed

func _ready() -> void:
	hide_textbox()
	label.autowrap_mode = TextServer.AUTOWRAP_WORD

func _process(_delta: float) -> void:
	match current_state:
		State.READY:
			if not text_queue.is_empty():
				display_text()
		State.READING:
			if Input.is_action_just_pressed("ui_accept"):
				if reveal_tween:
					reveal_tween.kill()
					reveal_tween = null
				label.visible_characters = label.text.length()
				end_symbol.text = "v"
				change_state(State.FINISHED)
		State.FINISHED:
			if Input.is_action_just_pressed("ui_accept"):
				if not text_queue.is_empty():
					display_text()
				else:
					change_state(State.READY)
					hide_textbox()
					emit_signal("finished")

# ---- Public API ----
func queue_text(t: String) -> void:
	text_queue.push_back(t)

func display_text() -> void:
	var t: String = text_queue.pop_front() as String      # <-- typed + cast
	if reveal_tween:
		reveal_tween.kill()
		reveal_tween = null

	start_symbol.text = ""
	end_symbol.text = ""
	label.text = t
	label.visible_characters = 0

	_set_popup_screen_pos(anchor_world_pos)
	change_state(State.READING)
	show_textbox()

	var duration: float = float(t.length()) * CHAR_READ_RATE   # <-- typed
	reveal_tween = create_tween()                               # <-- reveal_tween already typed
	reveal_tween.tween_method(
		func(v): label.visible_characters = int(v),
		0, t.length(), duration
	).set_trans(Tween.TRANS_LINEAR).set_ease(Tween.EASE_IN_OUT)

	reveal_tween.finished.connect(func():
		end_symbol.text = "v"
		change_state(State.FINISHED)
		reveal_tween = null
	)

func hide_textbox() -> void:
	start_symbol.text = ""
	end_symbol.text = ""
	label.text = ""
	textbox_container.hide()

func show_textbox() -> void:
	textbox_container.show()

func _set_popup_screen_pos(world_pos: Vector2) -> void:
	var xform: Transform2D = get_viewport().get_canvas_transform()   # <-- typed
	var screen_pos: Vector2 = xform * world_pos                      # <-- typed

	var box: Control = textbox_container                              # <-- typed
	var box_size: Vector2 = box.size                                   # <-- typed
	if box_size == Vector2.ZERO:
		box_size = Vector2(360, 120)

	var margin: float = 40.0                                           # <-- typed
	box.global_position = screen_pos - Vector2(box_size.x * 0.5, box_size.y + margin)

	var vp: Vector2 = get_viewport().get_visible_rect().size          # <-- typed
	box.global_position.x = clampf(box.global_position.x, 8.0, vp.x - box_size.x - 8.0)
	box.global_position.y = clampf(box.global_position.y, 8.0, vp.y - box_size.y - 8.0)

func change_state(s: State) -> void:                                  # <-- typed
	current_state = s

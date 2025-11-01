extends Node2D

@onready var area: Area2D = $InteractionArea
@export var textbox_scene: PackedScene   # drag textbox.tscn here

var in_range := false
var player: Node = null

func _ready() -> void:
	area.body_entered.connect(_on_enter)
	area.body_exited.connect(_on_exit)

func _on_enter(body: Node) -> void:
	if body.is_in_group("player"):
		in_range = true
		player = body

func _on_exit(body: Node) -> void:
	if body == player:
		in_range = false
		player = null

func _unhandled_input(event: InputEvent) -> void:
	if in_range and player and event.is_action_pressed("interact"):
		_run_textbox()

func _run_textbox() -> void:
	if not textbox_scene:
		push_error("Assign the textbox_scene in the Inspector.")
		return

	var textbox := textbox_scene.instantiate()
	get_tree().root.add_child(textbox)

	# lock player while dialog is open
	if player and player.has_method("set_movement_locked"):
		player.set_movement_locked(true)

	# unlock when finished
	if textbox.has_signal("finished"):
		textbox.finished.connect(func():
			if player and player.has_method("set_movement_locked"):
				player.set_movement_locked(false)
			textbox.queue_free()
		)

	# queue dialogue using your queue system
	textbox.queue_text("You found a chest!")
	textbox.queue_text("It creaks open slowly...")
	textbox.queue_text("Inside... just dust.")

	# start showing text
	textbox.display_text()

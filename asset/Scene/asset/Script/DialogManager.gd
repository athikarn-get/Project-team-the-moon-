extends Node2D

@onready var area: Area2D = $CollisionShape2D
@onready var interact_label: Label = $Label
@export var textbox_scene: PackedScene

var in_range := false
var player: Node = null
var textbox_instance: Node = null

func _ready() -> void:
	if not area:
		push_error("No Area2D found (parent of CollisionShape2D). Make sure CollisionShape2D is under an Area2D.")
		return

	interact_label.visible = false

	if not area.is_connected("body_entered", Callable(self, "_on_enter")):
		area.body_entered.connect(_on_enter)
	if not area.is_connected("body_exited", Callable(self, "_on_exit")):
		area.body_exited.connect(_on_exit)

func _on_enter(body: Node) -> void:
	if _is_player(body):
		in_range = true
		player = body
		interact_label.text = "Press [E]"
		interact_label.visible = true

func _on_exit(body: Node) -> void:
	if body == player:
		in_range = false
		player = null
		interact_label.visible = false

func _unhandled_input(event: InputEvent) -> void:
	if in_range and player and event.is_action_pressed("interact"):
		_run_textbox()

func _run_textbox() -> void:
	if not textbox_scene:
		push_error("Assign the textbox_scene in the Inspector.")
		return

	textbox_instance = textbox_scene.instantiate()
	get_tree().root.add_child(textbox_instance)

	if textbox_instance.has_method("set_anchor_world_pos"):
		textbox_instance.set_anchor_world_pos(player.global_position)

	if player and player.has_method("set_movement_locked"):
		player.set_movement_locked(true)

	interact_label.visible = false

	if textbox_instance.has_signal("finished"):
		textbox_instance.finished.connect(func ():
			if player and player.has_method("set_movement_locked"):
				player.set_movement_locked(false)
			if is_instance_valid(textbox_instance):
				textbox_instance.queue_free()
			textbox_instance = null
			if in_range:
				interact_label.visible = true
		)

	if textbox_instance.has_method("queue_text"):
		textbox_instance.queue_text("You found a chest!")
		textbox_instance.queue_text("It creaks open slowly...")
		textbox_instance.queue_text("Inside... just dust.")
	if textbox_instance.has_method("display_text"):
		textbox_instance.display_text()

func _is_player(body: Node) -> bool:
	return body != null and (body.is_in_group("player") or body.name == "Player")

extends Node

var current_checkpoint_position: Vector2 = Vector2.ZERO

func _ready() -> void:
	var player = get_parent().get_node("Player")
	if player:
		current_checkpoint_position = player.global_position
	for checkpoint in get_children():
		if checkpoint is Area2D:
			checkpoint.connect("checkpoint_reached", Callable(self, "_on_checkpoint_reached"))

func _on_checkpoint_reached(position: Vector2) -> void:
	set_checkpoint(position)



func set_checkpoint(position: Vector2) -> void:
	current_checkpoint_position = position
	print("Checkpoint updated to: ", position)

func get_checkpoint() -> Vector2:
	return current_checkpoint_position

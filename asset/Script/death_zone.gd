extends Area2D

var player: Node
var checkpoint_manager: Node

func _ready() -> void:
	await get_tree().process_frame
	player = get_parent().get_node("Player")
	checkpoint_manager = get_parent().get_node("CheckpointManager")
	connect("body_entered", Callable(self, "_on_body_entered"))

func _on_body_entered(body):
	if body == player and checkpoint_manager:
		var respawn_pos = checkpoint_manager.get_checkpoint()
		player.global_position = respawn_pos
		print("Player respawned at checkpoint: ", respawn_pos)

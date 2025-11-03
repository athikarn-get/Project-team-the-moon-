extends Area2D

signal checkpoint_reached(position: Vector2)

func _ready() -> void:
	connect("body_entered", Callable(self, "_on_body_entered"))

func _on_body_entered(body):
	if body.name == "Player":
		emit_signal("checkpoint_reached", global_position)

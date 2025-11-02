extends Area2D

@export var object_name = "chest"
@export var description = "hint"
var player_in_range = false

func _ready():
	connect("body_entered", Callable(self, "_on_body_entered"))
	connect("body_exited", Callable(self, "_on_body_exited"))
	
func _on_body_entered(body):
	if body.name == "Player":
		player_in_range = true

func _on_body_exited(body):
	if body.name == "Player":
		player_in_range = false
	
#func _process(delta):
	#if player_in_range and Input.is_action_just_pressed("interact"):
		#get_tree().call_group("ui", "show_popup", object_name, description)

func _process(_delta):
	if player_in_range and Input.is_action_just_pressed("interact"):
		get_tree().call_group("ui", "show_popup", object_name, description)

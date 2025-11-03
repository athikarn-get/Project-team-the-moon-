extends Node2D

@onready var player = get_tree().get_first_node_in_group("player")
@onready var label: Label = $Label

const base_text = "[E] to "

var active_areas: Array = []
var can_interact: bool = true

func _process(_delta: float) -> void:
	if active_areas.size() > 0 and can_interact:
		active_areas.sort_custom(_sort_by_distance_to_player)
		var a = active_areas[0]
		label.text = base_text + a.action_name
		label.global_position = a.global_position
		label.global_position.y -= 36
		label.global_position.x -= label.size.x / 2
		label.show()
	else:
		label.hide()

func _sort_by_distance_to_player(a1, a2) -> bool:
	var d1 = player.global_position.distance_to(a1.global_position)
	var d2 = player.global_position.distance_to(a2.global_position)
	return d1 < d2

func _input(event: InputEvent) -> void:
	if event.is_action_pressed("interact") and can_interact:
		if active_areas.size() > 0:
			can_interact = false
			label.hide()
			var target = active_areas[0]
			if target.interact.is_valid():
				await target.interact.call()
			can_interact = true

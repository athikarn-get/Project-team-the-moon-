extends PopupPanel

@onready var label = $Label
@onready var close_button = $Button
@onready var color_rect = get_node_or_null("../ColorRect")  # now linked to ColorRect

func _ready():
	add_to_group("ui")
	close_button.pressed.connect(_on_close_pressed)
	hide()
	if color_rect:
		color_rect.visible = false

func show_popup(popup_title: String, desc: String):
	label.bbcode_enabled = true
	label.text = "[b]" + popup_title + "[/b]\n" + desc
	popup_centered()
	show()
	if color_rect:
		color_rect.visible = true


func _on_close_pressed():
	hide()
	if color_rect:
		color_rect.visible = false

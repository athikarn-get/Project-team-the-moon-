@onready var label: Label = $Label

func _ready():
	var f := FontFile.new()
	f.load("res://fonts/Kanit-Regular.ttf") # ใส่พาธฟอนต์ของมีน
	label.add_theme_font_override("font", f)
	label.add_theme_color_override("font_outline_color", Color.BLACK)
	label.add_theme_constant_override("outline_size", 3)
	label.add_theme_font_size_override("font_size", 32) # Godot 4.x

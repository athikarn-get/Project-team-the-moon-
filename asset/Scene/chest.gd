extends Node2D
#----------------------------------------------------------------------------------------------------------------------------------
@onready var area: Area2D = $InteractionArea
@onready var interact_label: Label = $Label
@export var textbox_scene: PackedScene

@onready var sprite_closed: Sprite2D = $Sprite2D     # หีบปิด
@onready var sprite_opened: Sprite2D = $Sprite2D2    # หีบเปิด

var in_range := false
var player: Node = null
var textbox_instance: Node = null
var chest_opened: bool = false

func _ready() -> void:
	# ซ่อน Sprite2D2 (หีบเปิด) ตอนเริ่ม
	if sprite_opened:
		sprite_opened.visible = false
	if sprite_closed:
		sprite_closed.visible = true

	if interact_label:
		interact_label.visible = false

	if area == null:
		push_error("Chest.gd: ต้องมี Area2D ชื่อ 'InteractionArea' ใต้ Chest")
		return

	if not area.is_connected("body_entered", Callable(self, "_on_enter")):
		area.body_entered.connect(_on_enter)
	if not area.is_connected("body_exited", Callable(self, "_on_exit")):
		area.body_exited.connect(_on_exit)

func _on_enter(body: Node) -> void:
	if _is_player(body):
		in_range = true
		player = body
		if interact_label:
			interact_label.text = "You already open..." if chest_opened else "Press [E]"
			interact_label.visible = true

func _on_exit(body: Node) -> void:
	if body == player:
		in_range = false
		player = null
		if interact_label:
			interact_label.visible = false

func _unhandled_input(event: InputEvent) -> void:
	if chest_opened:
		return
	if in_range and player and event.is_action_pressed("interact"):
		_run_textbox()

func _run_textbox() -> void:
	if not textbox_scene:
		push_error("Assign the textbox_scene in the Inspector.")
		return

	textbox_instance = textbox_scene.instantiate()
	get_tree().root.add_child(textbox_instance)

	if textbox_instance.has_method("set_anchor_world_pos") and player:
		textbox_instance.set_anchor_world_pos(player.global_position)

	if player and player.has_method("set_movement_locked"):
		player.set_movement_locked(true)

	if interact_label:
		interact_label.visible = false

	if textbox_instance.has_signal("finished"):
		textbox_instance.finished.connect(func ():
			if player and player.has_method("set_movement_locked"):
				player.set_movement_locked(false)
			if is_instance_valid(textbox_instance):
				textbox_instance.queue_free()
			textbox_instance = null
			_on_chest_opened_final()
		)

	if textbox_instance.has_method("queue_text"):
		textbox_instance.queue_text("You found a chest!")
		textbox_instance.queue_text("It creaks open slowly...")
		textbox_instance.queue_text("You got a hint!")

	if textbox_instance.has_method("display_text"):
		textbox_instance.display_text()

func _on_chest_opened_final() -> void:
	chest_opened = true

	# ✅ ซ่อนหีบปิด / โชว์หีบเปิด
	if sprite_closed:
		sprite_closed.visible = false
	if sprite_opened:
		sprite_opened.visible = true

	# ✅ อัปเดตข้อความ
	if interact_label and in_range:
		interact_label.text = "You already open..."
		interact_label.visible = true

	# ✅ แจ้ง Main เพื่อเพิ่ม Hint ข้อที่ 1
	_notify_main_chest_opened()

func _is_player(body: Node) -> bool:
	return body != null and (body.is_in_group("player") or body.name == "Player")

func _notify_main_chest_opened() -> void:
	var main := get_tree().get_first_node_in_group("Main")
	if main and main.has_method("on_chest_opened_with_hint"):
		main.on_chest_opened_with_hint("""💡 คำใบ้ข้อที่ 1
1) ลูปจะเช็กทุกค่าทีละตัวใน nums
2) เงื่อนไข % 2 == 0 ผ่านเฉพาะบางค่า (เลขคู่เท่านั้น)
3) total จะเพิ่มขึ้นเรื่อย ๆ ตามค่าที่ผ่านเงื่อนไข
4) คำตอบออกมาเป็นเลขคู่บวก ที่ไม่ได้ใหญ่มาก
5) ถ้าอยากรู้คำตอบไว ลองพิมพ์ค่าที่เข้า if ดูก่อนสิ
""")
#----------------------------------------------------------------------------------------------------------------------------------

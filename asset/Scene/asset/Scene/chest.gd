extends Node2D
#----------------------------------------------------------------------------------------------------------------------------------
@onready var area: Area2D = $InteractionArea
@onready var interact_label: Label = $Label          # ชื่อ Label ต้องตรงกับใน Scene
@export var textbox_scene: PackedScene               # ลาก textbox.tscn มาใส่ใน Inspector

var in_range := false
var player: Node = null
var textbox_instance: Node = null
var chest_opened: bool = false   # ✅ เปิดแล้วหรือยัง (ไว้แจ้ง Main ให้เปลี่ยน Hint)

func _ready() -> void:
	# ซ่อน "Press [E]" ไว้ก่อน
	if interact_label:
		interact_label.visible = false

	# กันพลาด: ถ้าหา Area2D ไม่เจอ ให้ฟ้อง และหยุดต่อสัญญาณ
	if area == null:
		push_error("Chest.gd: Node 'InteractionArea' not found under this Chest. Please add Area2D named 'InteractionArea'.")
		return

	# ต่อสัญญาณ (กันพลาดแม้ยังไม่ได้ connect ใน Editor)
	if not area.is_connected("body_entered", Callable(self, "_on_enter")):
		area.body_entered.connect(_on_enter)
	if not area.is_connected("body_exited", Callable(self, "_on_exit")):
		area.body_exited.connect(_on_exit)

func _on_enter(body: Node) -> void:
	if _is_player(body):
		in_range = true
		player = body
		if interact_label:
			interact_label.visible = true

func _on_exit(body: Node) -> void:
	if body == player:
		in_range = false
		player = null
		if interact_label:
			interact_label.visible = false

func _unhandled_input(event: InputEvent) -> void:
	if in_range and player and event.is_action_pressed("interact"):
		_run_textbox()

func _run_textbox() -> void:
	if not textbox_scene:
		push_error("Assign the textbox_scene in the Inspector.")
		return

	# สร้าง textbox ครั้งใหม่ทุกครั้งที่คุย (หรือจะรีใช้ instance เดิมก็ได้)
	textbox_instance = textbox_scene.instantiate()
	get_tree().root.add_child(textbox_instance)

	# ชี้ให้ textbox ไปโผล่ 'ใต้ player'
	if textbox_instance.has_method("set_anchor_world_pos") and player:
		# ใน textbox.gd มี offset +Vector2(0, 64) แล้ว ส่งตำแหน่ง player ตรง ๆ ได้เลย
		textbox_instance.set_anchor_world_pos(player.global_position)

	# ระหว่างคุย: ล็อกการเคลื่อนที่ถ้า player มีเมธอดนี้
	if player and player.has_method("set_movement_locked"):
		player.set_movement_locked(true)

	# ให้ "Press [E]" หายไประหว่างแสดงกล่องข้อความ
	if interact_label:
		interact_label.visible = false

	# ต่อสัญญาณเสร็จสิ้นจาก textbox แล้วปลดล็อก player + แจ้ง Main ว่าเปิดหีบแล้ว
	if textbox_instance.has_signal("finished"):
		textbox_instance.finished.connect(func ():
			if player and player.has_method("set_movement_locked"):
				player.set_movement_locked(false)
			# ลบกล่องข้อความทิ้งเมื่อคุยจบ
			if is_instance_valid(textbox_instance):
				textbox_instance.queue_free()
			textbox_instance = null
			# โชว์ "Press [E]" อีกครั้งถ้ายังยืนอยู่ในระยะ
			if in_range and interact_label:
				interact_label.visible = true
			# ✅ แจ้ง Main ครั้งเดียวว่าหีบเปิดแล้ว เพื่อให้ Hint เปลี่ยนเป็น "print() ?"
			if not chest_opened:
				_notify_main_chest_opened()
				chest_opened = true
		)

	# คิวข้อความตัวอย่าง (ลบ/แก้ได้ตามต้องการ)
	if textbox_instance.has_method("queue_text"):
		textbox_instance.queue_text("You found a chest!")
		textbox_instance.queue_text("It creaks open slowly...")
		textbox_instance.queue_text("You got a hint!")

	# สั่งเริ่มแสดงข้อความ
	if textbox_instance.has_method("display_text"):
		textbox_instance.display_text()

func _is_player(body: Node) -> bool:
	return body != null and (body.is_in_group("player") or body.name == "Player")

func _notify_main_chest_opened() -> void:
	var main := get_tree().get_first_node_in_group("Main")
	if main and main.has_method("on_chest_opened"):
		main.on_chest_opened()
#----------------------------------------------------------------------------------------------------------

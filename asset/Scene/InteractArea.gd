extends Area2D
class_name InteractArea

@export var action_name: String = "interact"
var interact: Callable = Callable()

@onready var _manager: Node = get_tree().current_scene.get_node_or_null("InteractionManager")

func _ready() -> void:
	# เปิดการตรวจจับชน
	monitoring = true
	monitorable = true

	# เชื่อมสัญญาณเข้าฟังก์ชัน
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)

func _on_body_entered(body: Node) -> void:
	# เมื่อ Player เดินเข้ามาในพื้นที่ Interact
	if body.is_in_group("player") and _manager:
		if not _manager.active_areas.has(self):
			_manager.active_areas.append(self)

func _on_body_exited(body: Node) -> void:
	# เมื่อ Player เดินออกจากพื้นที่ Interact
	if body.is_in_group("player") and _manager:
		var idx: int = _manager.active_areas.find(self)  # ✅ ระบุชนิด int ให้ชัดเจน
		if idx != -1:
			_manager.active_areas.remove_at(idx)

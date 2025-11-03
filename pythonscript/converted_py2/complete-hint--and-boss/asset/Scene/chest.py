# --- Godot Python bridge imports (py4godot primary) ---
from typing import Optional, Any

try:
    # py4godot (Godot 4.x Pluginscript)
    from py4godot import gdclass, signal
    from py4godot.core import *  # import all core Godot classes (Node2D, AcceptDialog, Area2D, Label, Button, etc.)
except Exception:
    # Fallback: godot-python (experimental for Godot 4, signatures may differ)
    from godot import exposed as gdclass, signal
    from godot import *  # type: ignore

@gdclass
class Chest(Node2D):
    def __init__(self):
        super().__init__()
        self.area: Any = None  # onready; set in _ready
        self.interact_label: Any = None  # onready; set in _ready
        self.textbox_scene = None  # @export
        self.sprite_closed: Any = None  # onready; set in _ready
        self.sprite_opened: Any = None  # onready; set in _ready
        self.in_range = None
        self.player =  None
        self.textbox_instance =  None
        self.chest_opened =  False
        self.main = None

    def _ready(self) -> None:
        self.area = self.get_node(\"\1\")
        self.interact_label = self.get_node(\"\1\")
        self.sprite_closed = self.get_node(\"\1\")     # หีบปิด
        self.sprite_opened = self.get_node(\"\1\")    # หีบเปิด
    #----------------------------------------------------------------------------------------------------------------------------------




    def _ready(self):
    	# ซ่อน Sprite2D2 (หีบเปิด) ตอนเริ่ม
    	if sprite_opened:
    		sprite_opened.visible = False
    	if sprite_closed:
    		sprite_closed.visible = True

    	if interact_label:
    		interact_label.visible = False

    	if area == None:
    		push_error("Chest.gd: ต้องมี Area2D ชื่อ 'InteractionArea' ใต้ Chest")
    		return

    	if not area.is_connected("body_entered", Callable(self, "_on_enter")):
    		area.body_entered.connect(_on_enter)
    	if not area.is_connected("body_exited", Callable(self, "_on_exit")):
    		area.body_exited.connect(_on_exit)


    def _on_enter(self, body):
    	if _is_player(body):
    		in_range = True
    		player = body
    		if interact_label:
    			interact_label.text = "You already open..." if chest_opened else "Press [E]"
    			interact_label.visible = True


    def _on_exit(self, body):
    	if body == player:
    		in_range = False
    		player = None
    		if interact_label:
    			interact_label.visible = False


    def _unhandled_input(self, event):
    	if chest_opened:
    		return
    	if in_range and player and event.is_action_pressed("interact"):
    		_run_textbox()


    def _run_textbox(self):
    	if not textbox_scene:
    		push_error("Assign the textbox_scene in the Inspector.")
    		return

    	textbox_instance = textbox_scene.instantiate()
    	get_tree().root.add_child(textbox_instance)

    	if textbox_instance.has_method("set_anchor_world_pos") and player:
    		textbox_instance.set_anchor_world_pos(player.global_position)

    	if player and player.has_method("set_movement_locked"):
    		player.set_movement_locked(True)

    	if interact_label:
    		interact_label.visible = False

    	if textbox_instance.has_signal("finished"):
    		textbox_instance.finished.connect(func ():
    			if player and player.has_method("set_movement_locked"):
    				player.set_movement_locked(False)
    			if is_instance_valid(textbox_instance):
    				textbox_instance.queue_free()
    			textbox_instance = None
    			_on_chest_opened_final()
    		)

    	if textbox_instance.has_method("queue_text"):
    		textbox_instance.queue_text("You found a chest!")
    		textbox_instance.queue_text("It creaks open slowly...")
    		textbox_instance.queue_text("You got a hint!")

    	if textbox_instance.has_method("display_text"):
    		textbox_instance.display_text()


    def _on_chest_opened_final(self):
    	chest_opened = True

    	# ✅ ซ่อนหีบปิด / โชว์หีบเปิด
    	if sprite_closed:
    		sprite_closed.visible = False
    	if sprite_opened:
    		sprite_opened.visible = True

    	# ✅ อัปเดตข้อความ
    	if interact_label and in_range:
    		interact_label.text = "You already open..."
    		interact_label.visible = True

    	# ✅ แจ้ง Main เพื่อเพิ่ม Hint ข้อที่ 1
    	_notify_main_chest_opened()


    def _is_player(self, body):
    	return body != None and (body.is_in_group("player") or body.name == "Player")


    def _notify_main_chest_opened(self):
    	if main and main.has_method("on_chest_opened_with_hint"):
    		main.on_chest_opened_with_hint("""💡 คำใบ้ข้อที่ 1
    1) ลูปจะเช็กทุกค่าทีละตัวใน nums
    2) เงื่อนไข % 2 == 0 ผ่านเฉพาะบางค่า (เลขคู่เท่านั้น)
    3) total จะเพิ่มขึ้นเรื่อย ๆ ตามค่าที่ผ่านเงื่อนไข
    4) คำตอบออกมาเป็นเลขคู่บวก ที่ไม่ได้ใหญ่มาก
    5) ถ้าอยากรู้คำตอบไว ลองพิมพ์ค่าที่เข้า if ดูก่อนสิ
    """)
    #----------------------------------------------------------------------------------------------------------------------------------

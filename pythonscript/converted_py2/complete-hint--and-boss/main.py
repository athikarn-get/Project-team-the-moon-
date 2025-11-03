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
class Main(Node2D):
    def __init__(self):
        super().__init__()
        self.chest_opened =  False
        self.GLOW_SCALE = 1.25
        self.GLOW_OFFSET = Vector2(-6.9, -18)
        self.new_hint_available =  False
        self.hint_button: Any = None  # onready; set in _ready
        self.glow_rect = None
        self.glow_tween = None
        self.pulse_tween = None
        self.hint_root = None
        self.hint_panel = None
        self.hint_label = None
        self.hint_close = None
        self.hint_open = None
        self.nav_box = None
        self.btn_prev = None
        self.btn_next = None
        self.page_label = None
        self._page = None
        self.hints = []           # เก็บทีละหน้า (หนึ่งหน้าหนึ่งข้อความ)
        self.ui_parent = None
        self.empty = None
        self.layer = None
        self.dimmer = None
        self.paper = None
        self.vbox = None
        self.font = None
        self.close_style = None
        self.tw = None
        self.tw = None
        self.t = None
        self.shader = None
        self.mat = None

    def _ready(self) -> None:
        self.hint_button = self.get_node(\"\1\")
    #---------------------------------------------------------------------------------------------------------------
    # ===== ปรับได้เล็กน้อย =====


    # ---------- Glow ----------

    # ---------- Hint UI ----------

    # ---------- Page Nav ----------

    # ---------- เก็บ Hint หลายอัน ----------
    const HINT_SEPARATOR := "\n\n"

    # ---------- Hints ตามภาพ (ไม่ใส่คำตอบ) ----------
    const H_HINT1 := """💡 คำใบ้ข้อที่ 1
    1) ลูปจะเช็กทุกค่าทีละตัวใน nums
    2) เงื่อนไข % 2 == 0 ผ่านเฉพาะบางค่า (เลขคู่เท่านั้น)
    3) total จะเพิ่มขึ้นเรื่อย ๆ ตามค่าที่ผ่านเงื่อนไข
    4) คำตอบออกมาเป็นเลขคู่บวก ที่ไม่ได้ใหญ่มาก
    5) ถ้าอยากรู้คำตอบไว ลองพิมพ์ค่าที่เข้า if ดูก่อนสิ
    """

    const H_HINT2 := """💡 คำใบ้ข้อที่ 2
    1) ช่วงยาว “คี่” ใช้ ซ้าย - ขวา, ช่วงยาว “คู่” ใช้ ซ้าย + ขวา
    2) [2, -3, 4] คือฝั่งซ้ายของการแบ่งใหญ่
    3) [1, 5] คือฝั่งขวา และจะถูกรวมแบบบวก
    4) ผลรวมสุดท้ายได้จาก “ฝั่งซ้ายลบฝั่งขวา”
    5) ค่าที่ได้เป็นจำนวนติดลบเล็ก ๆ
    """

    const H_HINT3 := """💡 คำใบ้ข้อที่ 3
    1) ลองมองแต่ละคำแล้วนับตัวที่ซ้ำ เช่น p, r, o, g...
    2) “programming” มีตัวซ้ำหลายตัว โดยเฉพาะ m กับ g
    3) “very” มีตัวซ้ำบ้างแต่ไม่มาก
    4) “Python” ไม่มีตัวซ้ำเลย
    5) ถ้ามีหลายคำซ้ำเท่ากัน ให้เลือกคำที่ “อยู่ก่อน” ในข้อความ
    """




    def _ready(self):
    	# --- ตำแหน่งปุ่มหลอดไฟ ---
    	if ui_parent and ui_parent is Control:
    		ui_parent.anchor_left = 1.0
    		ui_parent.anchor_top = 0.0
    		ui_parent.anchor_right = 1.0
    		ui_parent.anchor_bottom = 0.0
    		ui_parent.offset_left = -84.0
    		ui_parent.offset_top = 20.0
    		ui_parent.offset_right = -20.0
    		ui_parent.offset_bottom = 84.0

    	hint_button.text = "💡"
    	hint_button.custom_minimum_size = Vector2(64, 64)
    	hint_button.add_theme_font_size_override("font_size", 36)
    	for s in ["normal","hover","pressed","focus"]:
    		hint_button.add_theme_stylebox_override(s, empty)
    	for m in ["left","right","top","bottom"]:
    		hint_button.add_theme_constant_override("content_margin_%s" % m, 0)
    	hint_button.add_theme_color_override("font_color", Color(1,1,1))
    	hint_button.focus_mode = Control.FOCUS_NONE
    	get_viewport().gui_release_focus()

    	hint_button.pressed.connect(_on_hint_button_pressed)

    	_build_parchment_hint()

    	_create_glow_centered()
    	hint_button.resized.connect(_update_glow_size)
    	hint_button.minimum_size_changed.connect(_update_glow_size)
    	_update_glow_size()
    	hint_button.mouse_entered.connect(func():
    		if not new_hint_available: _animate_glow(0.95, 1.15)
    	)
    	hint_button.mouse_exited.connect(func():
    		if not new_hint_available: _animate_glow(0.0, 1.0)
    	)

    # ---------- UI ----------

    def _build_parchment_hint(self):
    	if layer == None:
    		layer = CanvasLayer.new()
    		layer.layer = 100
    		add_child(layer)

    	hint_root = Control.new()
    	hint_root.name = "ParchmentHint"
    	hint_root.visible = False
    	hint_root.mouse_filter = Control.MOUSE_FILTER_STOP
    	hint_root.set_anchors_preset(Control.PRESET_FULL_RECT)
    	layer.add_child(hint_root)

    	dimmer.color = Color(0, 0, 0, 0.5)
    	dimmer.set_anchors_preset(Control.PRESET_FULL_RECT)
    	dimmer.mouse_filter = Control.MOUSE_FILTER_STOP
    	dimmer.gui_input.connect(func(ev):
    		if ev is InputEventMouseButton and ev.pressed:
    			_close_hint()
    	)
    	hint_root.add_child(dimmer)

    	hint_panel = Panel.new()
    	hint_panel.mouse_filter = Control.MOUSE_FILTER_STOP
    	hint_panel.anchor_left = 0.5
    	hint_panel.anchor_top = 0.5
    	hint_panel.anchor_right = 0.5
    	hint_panel.anchor_bottom = 0.5
    	hint_panel.offset_left = -280
    	hint_panel.offset_top = -180
    	hint_panel.offset_right = 280
    	hint_panel.offset_bottom = 180
    	hint_panel.pivot_offset = Vector2(280, 180)
    	hint_root.add_child(hint_panel)

    	paper.bg_color = Color(0.96, 0.92, 0.78, 1.0)
    	paper.set_corner_radius_all(18)
    	paper.border_color = Color(0.55, 0.4, 0.2, 0.9)
    	paper.set_border_width_all(2)
    	paper.set_expand_margin_all(8)
    	hint_panel.add_theme_stylebox_override("panel", paper)

    	# เนื้อหา
    	vbox.anchor_left = 0.0
    	vbox.anchor_top = 0.0
    	vbox.anchor_right = 1.0
    	vbox.anchor_bottom = 1.0
    	vbox.offset_left = 24
    	vbox.offset_top = 28
    	vbox.offset_right = -24
    	vbox.offset_bottom = -24
    	vbox.add_theme_constant_override("separation", 12)
    	hint_panel.add_child(vbox)

    	hint_label = RichTextLabel.new()
    	hint_label.bbcode_enabled = False
    	hint_label.fit_content = True
    	hint_label.autowrap_mode = TextServer.AUTOWRAP_WORD
    	if font: hint_label.add_theme_font_override("normal_font", font)
    	hint_label.add_theme_font_size_override("normal_font_size", 22)
    	hint_label.add_theme_constant_override("outline_size", 6)
    	hint_label.add_theme_color_override("font_outline_color", Color(0.0, 0.0, 0.0, 0.85))
    	vbox.add_child(hint_label)

    	# แถบนำทาง (Prev / Page / Next)
    	nav_box = HBoxContainer.new()
    	nav_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    	nav_box.add_theme_constant_override("separation", 10)
    	vbox.add_child(nav_box)

    	btn_prev = Button.new()
    	btn_prev.text = "◀"
    	btn_prev.custom_minimum_size = Vector2(48, 32)
    	btn_prev.pressed.connect(func(): _goto_page(_page - 1))
    	nav_box.add_child(btn_prev)

    	page_label = Label.new()
    	page_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    	page_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    	page_label.text = "0/0"
    	nav_box.add_child(page_label)

    	btn_next = Button.new()
    	btn_next.text = "▶"
    	btn_next.custom_minimum_size = Vector2(48, 32)
    	btn_next.pressed.connect(func(): _goto_page(_page + 1))
    	nav_box.add_child(btn_next)

    	# ปุ่มปิด
    	hint_close = Button.new()
    	hint_close.text = "✕"
    	hint_close.focus_mode = Control.FOCUS_NONE
    	hint_close.anchor_left = 1.0
    	hint_close.anchor_top = 0.0
    	hint_close.anchor_right = 1.0
    	hint_close.anchor_bottom = 0.0
    	hint_close.offset_left = -40
    	hint_close.offset_top = 8
    	hint_close.offset_right = -8
    	hint_close.offset_bottom = 38
    	hint_close.pressed.connect(_close_hint)
    	for s in ["normal","hover","pressed","focus"]:
    		hint_close.add_theme_stylebox_override(s, close_style)
    	hint_close.add_theme_font_size_override("font_size", 22)
    	hint_panel.add_child(hint_close)

    # ---------- เปิด/ปิด ----------

    def _on_hint_button_pressed(self):
    	if new_hint_available:
    		new_hint_available = False
    		_stop_hint_pulse()

    	if hint_open:
    		_close_hint()
    	else:
    		_open_hint()


    def _open_hint(self):
    	_refresh_hint_view()
    	hint_root.visible = True
    	hint_open = True

    	hint_panel.modulate.a = 0.0
    	hint_panel.scale = Vector2(0.85, 0.85)
    	hint_panel.rotation_degrees = -4.0

    	tw.set_parallel(True)
    	tw.tween_property(hint_panel, "modulate:a", 1.0, 0.18)\
    		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
    	tw.tween_property(hint_panel, "scale", Vector2.ONE, 0.22)\
    		.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
    	tw.tween_property(hint_panel, "rotation_degrees", 0.0, 0.22)\
    		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)


    def _close_hint(self):
    	if not hint_open: return
    	hint_open = False
    	tw.set_parallel(True)
    	tw.tween_property(hint_panel, "modulate:a", 0.0, 0.16)\
    		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
    	tw.tween_property(hint_panel, "scale", Vector2(0.9, 0.9), 0.16)\
    		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
    	tw.tween_property(hint_panel, "rotation_degrees", 3.0, 0.16)\
    		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
    # TODO: convert awaiting: 	await tw.finished
    	hint_root.visible = False

    # ---------- View/Page helpers ----------

    def _refresh_hint_view(self):
    	if hints.size() == 0:
    		hint_label.text = "i have no idea right now"
    		page_label.text = "0/0"
    		btn_prev.disabled = True
    		btn_next.disabled = True
    		return

    	_page = clampi(_page, 0, hints.size() - 1)
    	hint_label.text = hints[_page]
    	page_label.text = str(_page + 1) + "/" + str(hints.size())
    	btn_prev.disabled = (hints.size() <= 1)
    	btn_next.disabled = (hints.size() <= 1)


    def _goto_page(self, p):
    	if hints.size() == 0:
    		return
    	# เลื่อนแบบวนรอบ
    	_page = (p % hints.size() + hints.size()) % hints.size()
    	_refresh_hint_view()

    # ---------- API เรียกจากหีบ ----------

    def on_chest_opened(self):
    	# หีบ 1 → Hint1 (ตามภาพ, ไม่รวมคำตอบ)
    	_add_hint_unique(H_HINT1)
    	new_hint_available = True
    	_start_hint_pulse()


    def on_chest2_opened(self):
    	# หีบ 2 → Hint2
    	_add_hint_unique(H_HINT2)
    	new_hint_available = True
    	_start_hint_pulse()


    def on_chest3_opened(self):
    	# หีบ 3 → Hint3
    	_add_hint_unique(H_HINT3)
    	new_hint_available = True
    	_start_hint_pulse()

    # ทางเลือก: ยังรองรับส่งข้อความเอง

    def on_chest_opened_with_hint(self, hint_text):
    	_add_hint_unique(hint_text)
    	new_hint_available = True
    	_start_hint_pulse()

    # ---------- จัดการ Hint ----------

    def _add_hint_unique(self, text):
    	if t == "":
    		return
    	for h in hints:
    		if h == t:
    			# ซ้ำ ไม่เพิ่ม แต่เลื่อนไปหน้าที่มีอยู่
    			_page = hints.find(h)
    			_refresh_hint_view()
    			return
    	hints.append(t)
    	_page = hints.size() - 1
    	_refresh_hint_view()
    	chest_opened = True

    # ---------- Glow ----------

    def _create_glow_centered(self):
    	glow_rect = ColorRect.new()
    	glow_rect.color = Color.TRANSPARENT
    	glow_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
    	glow_rect.z_index = -1
    	hint_button.add_child(glow_rect)
    	hint_button.move_child(glow_rect, 0)

    	glow_rect.anchor_left = 0.5
    	glow_rect.anchor_top = 0.5
    	glow_rect.anchor_right = 0.5
    	glow_rect.anchor_bottom = 0.5

    	shader.code = """
    		shader_type canvas_item;
    		uniform vec4 glow_color : source_color = vec4(1.0, 1.0, 0.4, 1.0);
    		uniform float glow_alpha : hint_range(0.0,1.0) = 0.0;
    		uniform float radius = 0.25;
    		uniform float softness = 0.55;
    		uniform float rim_thickness = 0.10;
    		uniform vec4 rim_color : source_color = vec4(1.0, 0.88, 0.35, 1.0);
    		void fragment() {
    			vec2 uv = UV * 2.0 - 1.0;
    			float d = length(uv);
    			float glow = 1.0 - smoothstep(radius, radius + softness, d);
    			float rim_in  = smoothstep(radius - rim_thickness, radius, d);
    			float rim_out = 1.0 - smoothstep(radius, radius + rim_thickness, d);
    			float rim = rim_in * rim_out;
    			vec3 col = glow_color.rgb * glow + rim_color.rgb * rim;
    			float a = glow_alpha * max(glow, rim);
    			COLOR = vec4(col, a);
    		}
    	"""
    	mat.shader = shader
    	mat.set_shader_parameter("glow_color", Color(1.0, 0.95, 0.4, 1.0))
    	mat.set_shader_parameter("glow_alpha", 0.0)
    	mat.set_shader_parameter("radius", 0.22)
    	mat.set_shader_parameter("softness", 0.65)
    	mat.set_shader_parameter("rim_thickness", 0.10)
    	mat.set_shader_parameter("rim_color", Color(1.0, 0.88, 0.35, 1.0))
    	glow_rect.material = mat
    	glow_rect.scale = Vector2.ONE


    def _update_glow_size(self):
    	if not is_instance_valid(glow_rect) or not is_instance_valid(hint_button):
    		return
    	glow_rect.size = hint_button.size * GLOW_SCALE
    	glow_rect.offset_left   = -glow_rect.size.x * 0.5 + GLOW_OFFSET.x
    	glow_rect.offset_top    = -glow_rect.size.y * 0.5 + GLOW_OFFSET.y
    	glow_rect.offset_right  =  glow_rect.size.x * 0.5 + GLOW_OFFSET.x
    	glow_rect.offset_bottom =  glow_rect.size.y * 0.5 + GLOW_OFFSET.y


    def _animate_glow(self, to_alpha, to_scale):
    	if glow_tween and glow_tween.is_running():
    		glow_tween.kill()
    	glow_tween = create_tween()
    	glow_tween.tween_property(
    		glow_rect.material, "shader_parameter/glow_alpha", to_alpha, 0.15
    	).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
    	glow_tween.parallel().tween_property(
    		glow_rect, "scale", Vector2(to_scale, to_scale), 0.15
    	).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)

    # ---------- Pulse ----------

    def _start_hint_pulse(self):
    	_stop_hint_pulse()
    	pulse_tween = create_tween().set_loops()
    	pulse_tween.tween_property(glow_rect.material, "shader_parameter/glow_alpha", 0.95, 0.35)\
    		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
    	pulse_tween.parallel().tween_property(glow_rect, "scale", Vector2(1.15, 1.15), 0.35)\
    		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
    	pulse_tween.tween_property(glow_rect.material, "shader_parameter/glow_alpha", 0.0, 0.35)\
    		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
    	pulse_tween.parallel().tween_property(glow_rect, "scale", Vector2(1.0, 1.0), 0.35)\
    		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)


    def _stop_hint_pulse(self):
    	if pulse_tween and pulse_tween.is_running():
    		pulse_tween.kill()
    	if is_instance_valid(glow_rect) and is_instance_valid(glow_rect.material):
    		glow_rect.material.set_shader_parameter("glow_alpha", 0.0)
    	glow_rect.scale = Vector2.ONE
    #---------------------------------------------------------------------------------------------------------------

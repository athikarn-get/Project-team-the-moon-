extends Node2D
#---------------------------------------------------------------------------------------------------------------หีบแรก
# ===== ปรับได้เล็กน้อย =====
var chest_opened: bool = false                 # เรียก on_chest_opened() จาก chest.gd
var GLOW_SCALE: float = 1.25                   # ขนาดวงแสงเทียบกับปุ่ม
var GLOW_OFFSET: Vector2 = Vector2(-6.9, -18)     # ชดเชยตำแหน่ง (emoji มักเอียงบน-ล่างไม่เท่ากัน)
# ============================
var new_hint_available: bool = false           # ✅ มี hint ใหม่แล้วยังไม่ได้อ่าน?

@onready var hint_button: Button = $CanvasLayer/UI/HintButton
var hint_window: AcceptDialog

# โหนดเอฟเฟกต์
var glow_rect: ColorRect
var glow_tween: Tween
var pulse_tween: Tween                         # ✅ ทวีนที่ทำให้กระพริบเอง

func _ready() -> void:
	# --- วางพาเรนต์ของปุ่มไว้ขวาบน ---
	var ui_parent := hint_button.get_parent()
	if ui_parent and ui_parent is Control:
		ui_parent.anchor_left = 1.0
		ui_parent.anchor_top = 0.0
		ui_parent.anchor_right = 1.0
		ui_parent.anchor_bottom = 0.0
		ui_parent.offset_left = -84.0   # 64px ปุ่ม + 20px margin
		ui_parent.offset_top = 20.0
		ui_parent.offset_right = -20.0
		ui_parent.offset_bottom = 84.0

	# --- ปุ่มเป็นไอคอนหลอดไฟล้วน + โปร่งใส ---
	hint_button.text = "💡"
	hint_button.custom_minimum_size = Vector2(64, 64)
	hint_button.add_theme_font_size_override("font_size", 36)

	var empty := StyleBoxEmpty.new()
	for s in ["normal","hover","pressed","focus"]:
		hint_button.add_theme_stylebox_override(s, empty)
	# เอา padding ภายในออก เพื่อให้ไอคอนอยู่กลางจริง ๆ
	for m in ["left","right","top","bottom"]:
		hint_button.add_theme_constant_override("content_margin_%s" % m, 0)
	hint_button.add_theme_color_override("font_color", Color(1,1,1))

	# ไม่ให้ Spacebar ไปกดปุ่ม
	hint_button.focus_mode = Control.FOCUS_NONE
	get_viewport().gui_release_focus()

	# --- หน้าต่าง Hint (toggle ด้วยปุ่ม) ---
	hint_button.pressed.connect(_on_hint_button_pressed)
	hint_window = AcceptDialog.new()
	hint_window.title = "Hint"
	hint_window.dialog_text = get_hint_text()
	add_child(hint_window)
	if hint_window.get_ok_button():
		hint_window.get_ok_button().visible = false

	# --- วงแสง + ขอบ (rim) เป็น "ลูกของปุ่ม" และยึดกึ่งกลาง ---
	_create_glow_centered()

	# อัปเดตตำแหน่ง/ขนาดเมื่อเลย์เอาต์เปลี่ยน
	hint_button.resized.connect(_update_glow_size)
	hint_button.minimum_size_changed.connect(_update_glow_size)
	_update_glow_size()

	# Hover = สว่างขึ้น + ขยายเล็กน้อย (ปิดถ้ากำลังกระพริบเอง)
	hint_button.mouse_entered.connect(func():
		if not new_hint_available: _animate_glow(0.95, 1.15)
	)
	hint_button.mouse_exited.connect(func():
		if not new_hint_available: _animate_glow(0.0, 1.0)
	)

# ---------- Glow (รัศมี + ขอบ) ----------
func _create_glow_centered() -> void:
	glow_rect = ColorRect.new()
	glow_rect.color = Color.TRANSPARENT
	glow_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	glow_rect.z_index = -1  # ให้อยู่ใต้ตัวอักษรของปุ่ม
	hint_button.add_child(glow_rect)
	hint_button.move_child(glow_rect, 0)

	# ยึดกึ่งกลางปุ่ม (anchors = 0.5)
	glow_rect.anchor_left = 0.5
	glow_rect.anchor_top = 0.5
	glow_rect.anchor_right = 0.5
	glow_rect.anchor_bottom = 0.5

	# Shader วงแสง + ขอบ (rim)
	var shader := Shader.new()
	shader.code = """
		shader_type canvas_item;

		uniform vec4 glow_color : source_color = vec4(1.0, 1.0, 0.4, 1.0);
		uniform float glow_alpha : hint_range(0.0,1.0) = 0.0; // tween ค่านี้
		uniform float radius = 0.25;     // รัศมีแสงหลัก
		uniform float softness = 0.55;   // ความนุ่มของขอบแสง

		uniform float rim_thickness = 0.10;                 // ความหนาขอบ
		uniform vec4 rim_color : source_color = vec4(1.0, 0.88, 0.35, 1.0); // สีขอบ

		void fragment() {
			vec2 uv = UV * 2.0 - 1.0;  // center (0,0)
			float d = length(uv);

			// glow นุ่ม ๆ
			float glow = 1.0 - smoothstep(radius, radius + softness, d);

			// rim = วงขอบบาง ๆ รอบรัศมี
			float rim_in  = smoothstep(radius - rim_thickness, radius, d);
			float rim_out = 1.0 - smoothstep(radius, radius + rim_thickness, d);
			float rim = rim_in * rim_out;

			vec3 col = glow_color.rgb * glow + rim_color.rgb * rim;
			float a = glow_alpha * max(glow, rim);
			COLOR = vec4(col, a);
		}
	"""
	var mat := ShaderMaterial.new()
	mat.shader = shader
	mat.set_shader_parameter("glow_color", Color(1.0, 0.95, 0.4, 1.0))
	mat.set_shader_parameter("glow_alpha", 0.0)
	mat.set_shader_parameter("radius", 0.22)
	mat.set_shader_parameter("softness", 0.65)
	mat.set_shader_parameter("rim_thickness", 0.10)
	mat.set_shader_parameter("rim_color", Color(1.0, 0.88, 0.35, 1.0))
	glow_rect.material = mat
	glow_rect.scale = Vector2.ONE

func _update_glow_size() -> void:
	if not is_instance_valid(glow_rect) or not is_instance_valid(hint_button):
		return
	# ขนาดวงแสง (ใหญ่กว่าปุ่มเล็กน้อย)
	glow_rect.size = hint_button.size * GLOW_SCALE
	# จัดกึ่งกลาง + ชดเชย offset เผื่อ emoji ไม่สมมาตร
	glow_rect.offset_left   = -glow_rect.size.x * 0.5 + GLOW_OFFSET.x
	glow_rect.offset_top    = -glow_rect.size.y * 0.5 + GLOW_OFFSET.y
	glow_rect.offset_right  =  glow_rect.size.x * 0.5 + GLOW_OFFSET.x
	glow_rect.offset_bottom =  glow_rect.size.y * 0.5 + GLOW_OFFSET.y

func _animate_glow(to_alpha: float, to_scale: float) -> void:
	if glow_tween and glow_tween.is_running():
		glow_tween.kill()
	glow_tween = create_tween()
	glow_tween.tween_property(
		glow_rect.material, "shader_parameter/glow_alpha", to_alpha, 0.15
	).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	glow_tween.parallel().tween_property(
		glow_rect, "scale", Vector2(to_scale, to_scale), 0.15
	).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)

# ---------- กระพริบอัตโนมัติเมื่อมี Hint ใหม่ ----------
func _start_hint_pulse() -> void:
	# ให้แสง “เต้นไป-มา” เหมือน hover แต่ลูปเอง
	_stop_hint_pulse()
	pulse_tween = create_tween().set_loops()   # ลูปไม่สิ้นสุดจนกว่าจะหยุด
	pulse_tween.tween_property(glow_rect.material, "shader_parameter/glow_alpha", 0.95, 0.35)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	pulse_tween.parallel().tween_property(glow_rect, "scale", Vector2(1.15, 1.15), 0.35)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	pulse_tween.tween_property(glow_rect.material, "shader_parameter/glow_alpha", 0.0, 0.35)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	pulse_tween.parallel().tween_property(glow_rect, "scale", Vector2(1.0, 1.0), 0.35)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)

func _stop_hint_pulse() -> void:
	if pulse_tween and pulse_tween.is_running():
		pulse_tween.kill()
	# รีเซ็ตกลับเหมือนยังไม่ hover
	if is_instance_valid(glow_rect) and is_instance_valid(glow_rect.material):
		glow_rect.material.set_shader_parameter("glow_alpha", 0.0)
	glow_rect.scale = Vector2.ONE

# ---------- Hint Window ----------
func _on_hint_button_pressed() -> void:
	# ถ้ามี hint ใหม่ → ถือว่าอ่านแล้ว และหยุดกระพริบทันที
	if new_hint_available:
		new_hint_available = false
		_stop_hint_pulse()

	if hint_window.visible:
		hint_window.hide()
	else:
		hint_window.dialog_text = get_hint_text()
		hint_window.popup_centered()

func get_hint_text() -> String:
	return "print()\nwhy PSCP SO HARD BRO ?" if chest_opened else "I have no idea right now."

# เรียกจาก chest.gd เมื่อเปิดหีบ
func on_chest_opened() -> void:
	chest_opened = true
	new_hint_available = true
	_start_hint_pulse()   # ✅ เริ่มกระพริบทันทีที่ได้ hint ใหม่
#---------------------------------------------------------------------------------------------------------------

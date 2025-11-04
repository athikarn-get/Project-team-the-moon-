from typing import Optional, Any
try:
	from py4godot import gdclass, signal
	from py4godot.core import *
except Exception:
	from godot import exposed as gdclass, signal
	from godot import *  # type: ignore


@gdclass
class QuizOverlayLite(Control):
	answered = signal()

	def __init__(self):
		super().__init__()
		self._expected: str = ""
		self._open: bool = False
		self._font: Optional[Font] = None
		self._dimmer: Optional[ColorRect] = None
		self._panel: Optional[Panel] = None
		self._margin: Optional[MarginContainer] = None
		self._vbox: Optional[VBoxContainer] = None
		self._question: Optional[RichTextLabel] = None
		self._scroll: Optional[ScrollContainer] = None
		self._qwrap: Optional[VBoxContainer] = None
		self._answer: Optional[TextEdit] = None
		self._btn_ok: Optional[Button] = None
		self._btn_cancel: Optional[Button] = None
		self._dragging: bool = False
		self._drag_offset: Vector2 = Vector2.ZERO

	def _ready(self) -> None:
		self._font = load("res://asset/font/2005_iannnnnCPU.ttf")
		self.visible = False
		self.mouse_filter = Control.MOUSE_FILTER_STOP
		self.set_anchors_preset(Control.PRESET_FULL_RECT)
		self.z_index = 9999

		self._dimmer = ColorRect.new()
		self._dimmer.color = Color(0, 0, 0, 0.55)
		self._dimmer.set_anchors_preset(Control.PRESET_FULL_RECT)
		self._dimmer.mouse_filter = Control.MOUSE_FILTER_STOP
		self._dimmer.gui_input.connect(self._on_dimmer_input)
		self.add_child(self._dimmer)

		self._panel = Panel.new()
		self._panel.set_anchors_preset(Control.PRESET_CENTER)
		vp = self.get_viewport_rect().size
		target = vp * 0.75
		max_size = Vector2(900, 620)
		size = Vector2(min(target.x, max_size.x), min(target.y, max_size.y))
		self._panel.size = size
		self._panel.pivot_offset = size / 2
		self._panel.mouse_filter = Control.MOUSE_FILTER_STOP
		self.add_child(self._panel)

		panel_box = StyleBoxFlat.new()
		panel_box.bg_color = Color(0.09, 0.09, 0.10, 0.96)
		panel_box.set_corner_radius_all(16)
		panel_box.set_border_width_all(2)
		panel_box.border_color = Color(1, 1, 1, 0.12)
		panel_box.shadow_size = 20
		panel_box.shadow_color = Color(0, 0, 0, 0.45)
		panel_box.shadow_offset = Vector2(0, 6)
		self._panel.add_theme_stylebox_override("panel", panel_box)

		self._panel.gui_input.connect(self._on_panel_gui_input)

		self._margin = MarginContainer.new()
		self._margin.anchor_left = 0
		self._margin.anchor_top = 0
		self._margin.anchor_right = 1
		self._margin.anchor_bottom = 1
		self._margin.offset_left = 20
		self._margin.offset_top = 20
		self._margin.offset_right = -20
		self._margin.offset_bottom = -20
		self._panel.add_child(self._margin)

		self._vbox = VBoxContainer.new()
		self._vbox.size_flags_vertical = Control.SIZE_EXPAND_FILL
		self._vbox.add_theme_constant_override("separation", 12)
		self._margin.add_child(self._vbox)

		self._scroll = ScrollContainer.new()
		self._scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		self._scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
		self._scroll.custom_minimum_size = Vector2(0, 140)
		self._scroll.size_flags_stretch_ratio = 1.0
		self._vbox.add_child(self._scroll)

		self._qwrap = VBoxContainer.new()
		self._qwrap.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		self._scroll.add_child(self._qwrap)

		self._question = RichTextLabel.new()
		self._question.bbcode_enabled = False
		self._question.fit_content = True
		self._question.autowrap_mode = TextServer.AUTOWRAP_WORD
		self._question.add_theme_color_override("default_color", Color(1, 1, 1, 0.96))
		self._question.add_theme_font_size_override("normal_font_size", 26)
		if self._font:
			self._question.add_theme_font_override("normal_font", self._font)
		self._qwrap.add_child(self._question)

		self._vbox.add_child(HSeparator.new())

		self._answer = TextEdit.new()
		self._answer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		self._answer.size_flags_vertical = Control.SIZE_EXPAND_FILL
		self._answer.size_flags_stretch_ratio = 1.2
		self._answer.custom_minimum_size = Vector2(0, 140)
		if self._font:
			self._answer.add_theme_font_override("font", self._font)
			self._answer.add_theme_font_size_override("font_size", 22)

		te_normal = StyleBoxFlat.new()
		te_normal.bg_color = Color(0.07, 0.07, 0.08, 1.0)
		te_normal.set_corner_radius_all(10)
		te_normal.set_border_width_all(1)
		te_normal.border_color = Color(1, 1, 1, 0.12)
		te_normal.shadow_size = 12
		te_normal.shadow_color = Color(0, 0, 0, 0.25)
		te_normal.shadow_offset = Vector2(0, 3)

		te_focus = StyleBoxFlat.new()
		te_focus.copy_from(te_normal)
		te_focus.border_color = Color(0.55, 0.8, 1.0, 0.75)

		self._answer.add_theme_stylebox_override("normal", te_normal)
		self._answer.add_theme_stylebox_override("focus", te_focus)
		self._answer.add_theme_color_override("font_color", Color(1, 1, 1, 0.98))
		self._answer.add_theme_color_override("caret_color", Color(1, 1, 1, 1))
		self._answer.add_theme_color_override("selection_color", Color(0.35, 0.65, 1.0, 0.35))
		if typeof(self._answer.get("insert_text_on_tab")) != TYPE_NIL:
			self._answer.set("insert_text_on_tab", True)
		elif typeof(self._answer.get("accepts_tab")) != TYPE_NIL:
			self._answer.set("accepts_tab", True)
		self._answer.gui_input.connect(self._on_answer_gui_input)
		self.set_process_unhandled_key_input(True)
		self._vbox.add_child(self._answer)

		buttons = HBoxContainer.new()
		buttons.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		buttons.add_theme_constant_override("separation", 10)
		spacer = Control.new()
		spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		buttons.add_child(spacer)

		self._btn_cancel = Button.new()
		self._btn_cancel.text = "Cancel"
		self._btn_ok = Button.new()
		self._btn_ok.text = "Submit"

		for b in [self._btn_cancel, self._btn_ok]:
			b.custom_minimum_size = Vector2(120, 38)
			if self._font:
				b.add_theme_font_override("font", self._font)
				b.add_theme_font_size_override("font_size", 22)
			sb_normal = StyleBoxFlat.new()
			sb_normal.bg_color = Color(0.18, 0.18, 0.2, 1)
			sb_normal.set_corner_radius_all(10)
			sb_normal.set_border_width_all(1)
			sb_normal.border_color = Color(1, 1, 1, 0.12)
			sb_hover = StyleBoxFlat.new()
			sb_hover.copy_from(sb_normal)
			sb_hover.bg_color = Color(0.24, 0.24, 0.28, 1)
			sb_pressed = StyleBoxFlat.new()
			sb_pressed.copy_from(sb_normal)
			sb_pressed.bg_color = Color(0.12, 0.12, 0.14, 1)
			b.add_theme_stylebox_override("normal", sb_normal)
			b.add_theme_stylebox_override("hover", sb_hover)
			b.add_theme_stylebox_override("pressed", sb_pressed)
			b.add_theme_color_override("font_color", Color(1, 1, 1))
			b.add_theme_color_override("font_focus_color", Color(1, 1, 1))

		self._btn_cancel.pressed.connect(self._cancel)
		self._btn_ok.pressed.connect(self._submit)
		buttons.add_child(self._btn_cancel)
		buttons.add_child(self._btn_ok)
		self._vbox.add_child(buttons)

	def _on_dimmer_input(self, e: InputEvent) -> None:
		if isinstance(e, InputEventMouseButton) and e.pressed:
			self._cancel()

	def _on_answer_gui_input(self, e: InputEvent) -> None:
		if isinstance(e, InputEventKey) and e.pressed and e.keycode == KEY_ENTER:
			if e.shift_pressed:
				self._answer.insert_text_at_caret("\n")
				self._answer.accept_event()
			else:
				self._submit()
				self._answer.accept_event()

	def _unhandled_key_input(self, e: InputEvent) -> None:
		if not self._open:
			return
		if isinstance(e, InputEventKey) and e.pressed and e.keycode == KEY_ESCAPE:
			self._cancel()

	def _on_panel_gui_input(self, e: InputEvent) -> None:
		if isinstance(e, InputEventMouseButton) and e.button_index == MOUSE_BUTTON_LEFT:
			if e.pressed:
				if self._answer and self._answer.get_global_rect().has_point(self.get_global_mouse_position()):
					return
				self._dragging = True
				self._drag_offset = self._panel.global_position - self.get_global_mouse_position()
				self._panel.grab_focus()
				self._panel.accept_event()
			else:
				self._dragging = False
		elif isinstance(e, InputEventMouseMotion) and self._dragging:
			vp = self.get_viewport_rect().size
			pos = self.get_global_mouse_position() + self._drag_offset
			pos.x = clamp(pos.x, 0.0, vp.x - self._panel.size.x)
			pos.y = clamp(pos.y, 0.0, vp.y - self._panel.size.y)
			self._panel.global_position = pos
			self._panel.accept_event()

	def _center_panel(self) -> None:
		vp = self.get_viewport_rect().size
		self._panel.global_position = (vp - self._panel.size) * 0.5

	def ask(self, question: str, expected_answer: str) -> None:
		if not self._panel or not self._question or not self._answer:
			return
		self._question.text = question or ""
		self._expected = expected_answer or ""
		self.visible = True
		self._open = True
		self._answer.text = ""
		self._center_panel()
		self._answer.grab_focus()
		self._panel.modulate = Color(1, 1, 1, 0)
		self._panel.scale = Vector2(0.9, 0.9)
		tw = self.create_tween().set_parallel(True)
		tw.tween_property(self._panel, "modulate:a", 1.0, 0.15)
		tw.tween_property(self._panel, "scale", Vector2.ONE, 0.18)

	def _submit(self) -> None:
		given = self._answer.text if self._answer else ""
		ok = self._compare_answer(given, self._expected)
		self._close()
		self.emit_signal("answered", ok, given)

	def _cancel(self) -> None:
		given = self._answer.text if self._answer else ""
		self._close()
		self.emit_signal("answered", False, given)

	def _close(self) -> None:
		if not self._open:
			return
		self._open = False
		self._dragging = False
		tw = self.create_tween().set_parallel(True)
		tw.tween_property(self._panel, "modulate:a", 0.0, 0.12)
		tw.tween_property(self._panel, "scale", Vector2(0.95, 0.95), 0.12)
		self.call_deferred("set_visible", False)

	def _normalize(self, s: str) -> str:
		t = (s or "").replace("\r\n", "\n").replace("\r", "\n").replace("\t", "    ")
		lines = t.split("\n")
		lines = [ln.rstrip(" ") for ln in lines]
		return "\n".join(lines)

	def _compare_answer(self, given: str, expected: str) -> bool:
		return self._normalize(given) == self._normalize(expected)

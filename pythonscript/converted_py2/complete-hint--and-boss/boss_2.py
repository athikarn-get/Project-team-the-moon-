from typing import Any, Optional
try:
	from py4godot import gdclass, signal
	from py4godot.core import *
except Exception:
	from godot import exposed as gdclass, signal
	from godot import *  # type: ignore


@gdclass
class Boss_2(Node2D):
	def __init__(self):
		super().__init__()
		self.quiz_question: str = "ฟังก์ชันที่ใช้แสดงข้อความใน Python คืออะไร"
		self.quiz_answer: str = "print()"
		self.blocker_path: str = "../Wall2"
		self.show_hint_text: bool = True

		self._player: Optional[Node] = None
		self._in_range: bool = False
		self._done: bool = False

		self.boss_label: Optional[Label] = None
		self._area: Optional[Area2D] = None
		self._dialog: Optional[AcceptDialog] = None
		self._line: Optional[LineEdit] = None

	def _ready(self) -> None:
		self.boss_label = self.get_node_or_null("bossdialog2")
		if self.boss_label:
			self.boss_label.visible = False

		self._area = self.get_node_or_null("InteractArea")
		if self._area:
			self._area.body_entered.connect(self._on_enter)
			self._area.body_exited.connect(self._on_exit)

		self._build_popup()

	def _build_popup(self) -> None:
		d = AcceptDialog.new()
		d.title = "ตอบคำถาม"
		d.ok_button_text = "ยืนยัน"
		d.visible = False
		self.add_child(d)

		v = VBoxContainer.new()
		v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		v.size_flags_vertical = Control.SIZE_EXPAND_FILL
		v.custom_minimum_size = Vector2(420, 0)
		d.add_child(v)

		q = Label.new()
		q.autowrap_mode = TextServer.AUTOWRAP_WORD
		q.text = self.quiz_question
		v.add_child(q)

		self._line = LineEdit.new()
		self._line.placeholder_text = "พิมพ์คำตอบ แล้วกด Enter หรือปุ่มยืนยัน"
		self._line.text_submitted.connect(self._on_submit_text)
		v.add_child(self._line)

		d.confirmed.connect(self._check_answer)
		self._dialog = d

	def _physics_process(self, _dt: float) -> None:
		if self._done:
			return
		if self._in_range and Input.is_action_just_pressed("interact"):
			if self._dialog and not self._dialog.visible:
				self._dialog.popup_centered()
				if self._line:
					self._line.grab_focus()

	def _on_enter(self, body: Node) -> None:
		if hasattr(body, "is_in_group") and body.is_in_group("player"):
			self._player = body
			self._in_range = True
			if self.show_hint_text and not self._done:
				self._say("กด [E] เพื่อตอบคำถาม")

	def _on_exit(self, body: Node) -> None:
		if body == self._player:
			self._in_range = False
			self._player = None
			self._clear_say()
			if self._dialog and self._dialog.visible:
				self._dialog.hide()

	def _say(self, text: str) -> None:
		if self.boss_label:
			self.boss_label.text = text
			self.boss_label.visible = True

	def _clear_say(self) -> None:
		if self.boss_label:
			self.boss_label.text = ""
			self.boss_label.visible = False

	def _on_submit_text(self, _text: str) -> None:
		self._check_answer()

	def _normalize_answer(self, s: str) -> str:
		t = s.strip().lower()
		if t.endswith("()"):
			t = t[:-2]
		return t

	def _check_answer(self) -> None:
		if not self._line:
			return
		if self._done:
			return
		given_raw = self._line.text
		ok = self
from py4godot import gdclass, signal
from py4godot.core import PopupPanel

@gdclass
class Popupui(PopupPanel):
    def __init__(self):
        super().__init__()
        self.label = None
        self.close_button = None
        self.color_rect = None

    def _ready(self):
        self.label = self.get_node("Label")
        self.close_button = self.get_node("CloseButton")
        self.color_rect = self.get_node_or_null("../ColorRect")

        self.add_to_group("ui")

        # connect button
        self.close_button.pressed.connect(self._on_close_pressed)

        self.hide()
        if self.color_rect:
            self.color_rect.visible = False

    def show_popup(self, title: str, desc: str):
        self.label.text = f"[b]{title}[/b]\n{desc}"
        self.label.bbcode_enabled = True
        
        self.popup_centered()
        self.show()

        if self.color_rect:
            self.color_rect.visible = True

    def _on_close_pressed(self):
        self.hide()
        if self.color_rect:
            self.color_rect.visible = False

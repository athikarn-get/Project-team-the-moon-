from typing import Optional, Any
try:
    from py4godot import gdclass, signal
    from py4godot.core import *
except Exception:
    from godot import exposed as gdclass, signal
    from godot import *  # type: ignore

@gdclass
class LabelStyler(Node):
    def __init__(self):
        super().__init__()
        self.target_path: Optional[NodePath] = None
        self._label: Optional[Label] = None
        self._font: Optional[Font] = None

    def _ready(self) -> None:
        self._label = self if isinstance(self, Label) else self.get_node_or_null("Label")
        self._font = load("res://fonts/Kanit-Regular.ttf")
        if not self._label or not self._font:
            return
        self._label.add_theme_font_override("font", self._font)
        self._label.add_theme_color_override("font_outline_color", Color.BLACK)
        self._label.add_theme_constant_override("outline_size", 3)
        self._label.add_theme_font_size_override("font_size", 32)

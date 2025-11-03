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
class Text_Box(MarginContainer):
    def __init__(self):
        super().__init__()
        self.label: Any = None  # onready; set in _ready
        self.timer: Any = None  # onready; set in _ready
        self.text = ""
        self.letter_index = 0
        self.letter_time = 0.03
        self.space_time = 0.06
        self.punctuation_time = 0.2

    def _ready(self) -> None:
        self.label = self.get_node(\"\1\")
        self.timer = self.get_node(\"\1\")



    const MAX_WIDTH = 200


    signal finished_displaying()



    def display_text(self, text_to_display):
    	text = text_to_display
    	label.text = text_to_display

    # TODO: convert awaiting: 	await resized
    	custom_minimum_size.x = min(size.x, MAX_WIDTH)

    	if size.x > MAX_WIDTH:
    		label.autowrap_mode = TextServer.AUTOWRAP_WORD
    # TODO: convert awaiting: 		await resized
    # TODO: convert awaiting: 		await resized

    	global_position.x -= size.x / 2
    	global_position.y -= size.y + 24

    	label.text = ""
    	_display_letter()


    def _display_letter(self):
    	label.text += text[letter_index]

    	letter_index += 1
    	if letter_index >= text.length():
    		finished_displaying.emit()
    		return

    	match text[letter_index]:
    		"!", ".", ",", "?":
    			timer.start(punctuation_time)
    		" ":
    			timer.start(space_time)
    		_:
    			timer.start(letter_time)



    def _on_letterdisplaytimer_timeout(self):
    	_display_letter()

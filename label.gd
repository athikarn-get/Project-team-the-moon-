extends Node

@export var delay_min := 10.0    # เวลาเวลาที่มันจะพูด น้อยสุด
@export var delay_max := 20.0    # เวลาที่มันจะพูด สูงสุด
@export var text_speed := 0.04   # ความเร็วในการพิม
@export var stay_time := 1.8     # เวลาที่ text อยู่บนหน้าจอ

var speech_label: Label
var random_talk_timer: Timer
var is_intro_finished := false

# ประโยคสงสัย
var random_lines := [
	"นั่นเสียงอะไรน่ะ...",
	"ฉันเห็นอะไรอยู่ตรงนั้นหรือเปล่า...",
	"ที่นี่มันเงียบเกินไปไหม...",
	"เรามาอยู่ที่นี่ได้ยังไงกัน...",
	"หรือว่าฉันแค่จินตนาการไปเอง...",
	"มีบางอย่าง...ไม่ถูกต้อง",
	"เธอได้ยินเหมือนฉันไหม...",
	"นี่เราควรไปทางนั้นจริง ๆ เหรอ...",
	"แปลกจัง...",
	"ทำไมรู้สึกว่าดวงจันทร์มันใกล้เกินไป...",
	"เสียงเมื่อกี้... มาจากไหนกันแน่...",
	"ฉันรู้สึกเหมือนมีบางอย่างอยู่ข้างหลัง...",
	"จะได้เกรดเื่าไหร่นะ",
	"ทำไมอากาศถึงเย็นขึ้นกะทันหัน...",
	"แสงนั่น... มันกำลังขยับอยู่หรือเปล่า...",
	"เหมือนจะได้ยินเสียงใครเรียกชื่อฉัน...",
	"มีบางอย่างไม่ถูกต้องกับที่แห่งนี้...",
	"ดวงจันทร์นั่น... ทำไมมันดูใกล้ขนาดนั้น...",
	"ที่นี่เคยมีคนอยู่มาก่อนจริง ๆ เหรอ...",
	"ถ้าออกไปจากที่นี่ไม่ได้... จะเกิดอะไรขึ้นนะ..."

]

# เริ่มต้น
func _ready() -> void:
	randomize()
	_create_label()
	_create_timer()

# เรียกจาก Player เมื่อ intro พูดจบ
func start_random_talks() -> void:
	is_intro_finished = true
	_restart_timer()


# สร้าง Label สำหรับแสดงข้อความ
func _create_label() -> void:
	speech_label = Label.new()
	speech_label.visible = false
	speech_label.autowrap_mode = TextServer.AUTOWRAP_WORD
	speech_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	speech_label.add_theme_font_size_override("font_size", 18)
	speech_label.size = Vector2(220, 0)
	speech_label.position = Vector2(-110, -70)
	add_child(speech_label)

# สร้าง Timer สำหรับสุ่มบทพูด
func _create_timer() -> void:
	random_talk_timer = Timer.new()
	random_talk_timer.one_shot = true
	random_talk_timer.timeout.connect(_on_random_talk_timeout)
	add_child(random_talk_timer)


# เมื่อถึงเวลาพูดสุ่ม
func _on_random_talk_timeout() -> void:
	if not is_intro_finished:
		return  # ❌ ยังอยู่ในฉากเปิดเกม
	var line = random_lines[randi() % random_lines.size()]
	await _speak_line(line)
	_restart_timer()

# พิมพ์ข้อความ
func _speak_line(line: String) -> void:
	speech_label.visible = true
	speech_label.text = ""
	for c in line:
		speech_label.text += c
		await get_tree().create_timer(text_speed).timeout
	await get_tree().create_timer(stay_time).timeout
	speech_label.visible = false

# ตั้งเวลาใหม่แบบสุ่ม
func _restart_timer() -> void:
	var wait := randf_range(delay_min, delay_max)
	random_talk_timer.start(wait)

extends CharacterBody2D

const SPEED := 200.0
const JUMP_VELOCITY := -400.0

@onready var animated_sprite: AnimatedSprite2D = $AnimatedSprite2D

var can_move: bool = true

func set_movement_locked(locked: bool) -> void:
	can_move = not locked
	velocity = Vector2.ZERO
	if locked and animated_sprite:
		animated_sprite.play("idle")

func _ready() -> void:
	add_to_group("player")

func _physics_process(delta: float) -> void:
	# Stop all movement if locked
	if not can_move:
		velocity = Vector2.ZERO
		move_and_slide()
		return

	# Gravity
	if not is_on_floor():
		velocity += get_gravity() * delta

	# Jump
	if Input.is_action_just_pressed("jump") and is_on_floor():
		velocity.y = JUMP_VELOCITY

	# Horizontal input
	var dir := Input.get_axis("walk_l", "walk_r")

	# Flip sprite
	if dir > 0:
		animated_sprite.flip_h = false
	elif dir < 0:
		animated_sprite.flip_h = true

	# Animations
	if is_on_floor():
		if dir == 0:
			animated_sprite.play("idle")
		else:
			animated_sprite.play("run")
	else:
		animated_sprite.play("jump")

	# Velocity X
	if dir != 0:
		velocity.x = dir * SPEED
	else:
		velocity.x = move_toward(velocity.x, 0, SPEED)

	move_and_slide()

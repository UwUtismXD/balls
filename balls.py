import pygame
import sys
import math
import random
import json

# Initialize Pygame and the mixer
pygame.init()
pygame.mixer.init()

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

# Constants
WIDTH, HEIGHT = 1920, 1080
BALL_RADIUS = 20
INITIAL_CIRCLE_RADIUS = 450
GRAVITY = 8
BOUNCE_DELAY = 50  # Delay in milliseconds
CIRCLE_THICKNESS = 5  # Increased thickness of the circle
FIXED_TIME_STEP = 1 / 240  # Fixed time step for physics calculations
TRAIL_LENGTH = 20  # Number of trail segments
BALL_GROWTH_RATE = 1  # Amount by which the ball increases in size
FREEZE_TIME = 10000  # Time in milliseconds after which the ball freezes
SPEED_INCREASE_RATE = 1.005  # Speed increase rate per bounce

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball in a Circle")

# Font setup
font = pygame.font.SysFont(None, 36)

# Load the bounce sound if enabled in config
if config.get('sound', False):
    bounce_sound = pygame.mixer.Sound('bounce.wav')

def reset_game():
    global balls, start_time
    # Ball setup with random variance
    spawn_variance = 100
    ball_pos = [
        WIDTH // 2 + random.randint(-spawn_variance, spawn_variance),
        HEIGHT // 2 - INITIAL_CIRCLE_RADIUS // 4 + random.randint(-spawn_variance, spawn_variance)
    ]
    ball_speed = [2, 2]
    balls = [{'pos': ball_pos, 'speed': ball_speed, 'trail': [], 'last_bounce_time': pygame.time.get_ticks(), 'frozen': False}]
    start_time = pygame.time.get_ticks()

def spawn_ball():
    spawn_variance = 100
    ball_pos = [
        WIDTH // 2 + random.randint(-spawn_variance, spawn_variance),
        HEIGHT // 2 - INITIAL_CIRCLE_RADIUS // 4 + random.randint(-spawn_variance, spawn_variance)
    ]
    ball_speed = [2, 2]
    balls.append({'pos': ball_pos, 'speed': ball_speed, 'trail': [], 'last_bounce_time': pygame.time.get_ticks(), 'frozen': False})
    print("Ball spawned:", ball_pos)

def handle_ball_collision(ball1, ball2):
    if ball1['frozen'] or ball2['frozen']:
        return

    dx = ball1['pos'][0] - ball2['pos'][0]
    dy = ball1['pos'][1] - ball2['pos'][1]
    distance = math.sqrt(dx**2 + dy**2)
    if distance < 2 * BALL_RADIUS:
        angle = math.atan2(dy, dx)
        speed1 = math.sqrt(ball1['speed'][0]**2 + ball1['speed'][1]**2)
        speed2 = math.sqrt(ball2['speed'][0]**2 + ball2['speed'][1]**2)
        direction1 = math.atan2(ball1['speed'][1], ball1['speed'][0])
        direction2 = math.atan2(ball2['speed'][1], ball2['speed'][0])
        
        # Calculate new speeds along the collision axis
        new_speed1 = speed2 * math.cos(direction2 - angle)
        new_speed2 = speed1 * math.cos(direction1 - angle)
        
        # Update velocities
        ball1['speed'][0] = new_speed1 * math.cos(angle) + speed1 * math.sin(direction1 - angle) * math.cos(angle + math.pi / 2)
        ball1['speed'][1] = new_speed1 * math.sin(angle) + speed1 * math.sin(direction1 - angle) * math.sin(angle + math.pi / 2)
        ball2['speed'][0] = new_speed2 * math.cos(angle) + speed2 * math.sin(direction2 - angle) * math.cos(angle + math.pi / 2)
        ball2['speed'][1] = new_speed2 * math.sin(angle) + speed2 * math.sin(direction2 - angle) * math.sin(angle + math.pi / 2)
        
        # Separate the balls to avoid overlap
        overlap = 2 * BALL_RADIUS - distance
        ball1['pos'][0] += overlap * math.cos(angle) / 2
        ball1['pos'][1] += overlap * math.sin(angle) / 2
        ball2['pos'][0] -= overlap * math.cos(angle) / 2
        ball2['pos'][1] -= overlap * math.sin(angle) / 2

# Initialize game state
reset_game()

# Timer setup
clock = pygame.time.Clock()

# Main loop
running = True
color_change = 0
accumulator = 0.0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Calculate the elapsed time
    delta_time = clock.tick(120) / 1000.0
    accumulator += delta_time

    while accumulator >= FIXED_TIME_STEP:
        for ball in balls:
            if not ball['frozen']:
                ball_pos = ball['pos']
                ball_speed = ball['speed']
                ball_trail = ball['trail']
                last_bounce_time = ball['last_bounce_time']

                # Apply gravity
                ball_speed[1] += GRAVITY

                # Move the ball
                ball_pos[0] += ball_speed[0] * FIXED_TIME_STEP
                ball_pos[1] += ball_speed[1] * FIXED_TIME_STEP

                # Check for collision with the circle boundary
                distance_from_center = math.sqrt((ball_pos[0] - WIDTH // 2) ** 2 + (ball_pos[1] - HEIGHT // 2) ** 2)
                if distance_from_center + BALL_RADIUS >= INITIAL_CIRCLE_RADIUS:
                    # Reflect the ball
                    angle = math.atan2(ball_pos[1] - HEIGHT // 2, ball_pos[0] - WIDTH // 2)
                    normal = [math.cos(angle), math.sin(angle)]
                    dot_product = ball_speed[0] * normal[0] + ball_speed[1] * normal[1]
                    ball_speed[0] -= 2 * dot_product * normal[0]
                    ball_speed[1] -= 2 * dot_product * normal[1]

                    # Adjust ball position to be inside the circle
                    overlap = (distance_from_center + BALL_RADIUS) - INITIAL_CIRCLE_RADIUS
                    ball_pos[0] -= overlap * normal[0]
                    ball_pos[1] -= overlap * normal[1]

                    # Play the bounce sound if enabled in config
                    if config.get('sound', False):
                        bounce_sound.play()

                    # Increase the ball radius gradually if the growing mode is enabled
                    if config['growing']:
                        current_time = pygame.time.get_ticks()
                        if current_time - last_bounce_time >= BOUNCE_DELAY:
                            BALL_RADIUS += BALL_GROWTH_RATE
                            ball['last_bounce_time'] = current_time

                    # Increase the ball speed gradually if the speed mode is enabled
                    if config['speed']:
                        ball_speed[0] *= SPEED_INCREASE_RATE
                        ball_speed[1] *= SPEED_INCREASE_RATE

                # Add the current ball position to the trail
                ball_trail.append((int(ball_pos[0]), int(ball_pos[1])))
                if len(ball_trail) > TRAIL_LENGTH:
                    ball_trail.pop(0)

        # Handle collisions between balls
        for i in range(len(balls)):
            for j in range(i + 1, len(balls)):
                handle_ball_collision(balls[i], balls[j])

        accumulator -= FIXED_TIME_STEP

    # Freeze the ball if the timer mode is enabled and 10 seconds have passed
    if config['timer']:
        current_time = pygame.time.get_ticks()
        elapsed_time = (FREEZE_TIME - (current_time - start_time)) // 1000
        if elapsed_time <= 0:
            for ball in balls:
                ball['speed'] = [0, 0]
                ball['frozen'] = True
            spawn_ball()
            start_time = pygame.time.get_ticks()
        else:
            # Render the timer text in the middle of the circle
            timer_text = font.render(f'{elapsed_time}', True, WHITE)
            text_rect = timer_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(timer_text, text_rect)

    # Clear the screen
    screen.fill(BLACK)

    # Change the circle color over time
    color_change = (color_change + 1) % 360
    circle_color = pygame.Color(0)
    circle_color.hsva = (color_change, 100, 100)

    # Draw the circle with increased thickness
    pygame.draw.circle(screen, circle_color, (WIDTH // 2, HEIGHT // 2), INITIAL_CIRCLE_RADIUS, CIRCLE_THICKNESS)

    # Draw the ball trails
    for ball in balls:
        for i, pos in enumerate(ball['trail']):
            alpha = int(255 * (i + 1) / TRAIL_LENGTH)
            trail_color = (GRAY[0], GRAY[1], GRAY[2], alpha)
            s = pygame.Surface((BALL_RADIUS * 2, BALL_RADIUS * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, trail_color, (BALL_RADIUS, BALL_RADIUS), BALL_RADIUS)
            screen.blit(s, (pos[0] - BALL_RADIUS, pos[1] - BALL_RADIUS))

    # Draw the balls
    for ball in balls:
        ball_pos = ball['pos']
        pygame.draw.circle(screen, GREEN, (int(ball_pos[0]), int(ball_pos[1])), BALL_RADIUS)

    # Render the FPS text
    fps = clock.get_fps()
    fps_text = font.render(f'FPS: {fps:.2f}', True, WHITE)
    screen.blit(fps_text, (10, 10))

    # Update the display
    pygame.display.flip()

pygame.quit()
sys.exit()
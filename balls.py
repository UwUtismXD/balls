import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1920, 1080
BALL_RADIUS = 20
INITIAL_CIRCLE_RADIUS = 450
CIRCLE_RADIUS_DECREMENT = 1
GRAVITY = 8
BOUNCE_DELAY = 50  # Delay in milliseconds
CIRCLE_THICKNESS = 5  # Increased thickness of the circle
FIXED_TIME_STEP = 1 / 240  # Fixed time step for physics calculations
TRAIL_LENGTH = 5  # Number of trail segments

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

def reset_game():
    global balls, CIRCLE_RADIUS, last_bounce_time
    # Ball setup with random variance
    spawn_variance = 10
    ball_pos = [
        WIDTH // 2 + random.randint(-spawn_variance, spawn_variance),
        HEIGHT // 2 - INITIAL_CIRCLE_RADIUS // 4 + random.randint(-spawn_variance, spawn_variance)
    ]
    ball_speed = [2, 2]
    balls = [{'pos': ball_pos, 'speed': ball_speed, 'trail': [], 'last_bounce_time': pygame.time.get_ticks()}]
    CIRCLE_RADIUS = INITIAL_CIRCLE_RADIUS
    last_bounce_time = pygame.time.get_ticks()

def spawn_ball():
    spawn_variance = 10
    ball_pos = [
        WIDTH // 2 + random.randint(-spawn_variance, spawn_variance),
        HEIGHT // 2 - INITIAL_CIRCLE_RADIUS // 4 + random.randint(-spawn_variance, spawn_variance)
    ]
    ball_speed = [2, 2]
    balls.append({'pos': ball_pos, 'speed': ball_speed, 'trail': [], 'last_bounce_time': pygame.time.get_ticks()})
    print("Ball spawned:", ball_pos)

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
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if 10 <= mouse_x <= 110 and 90 <= mouse_y <= 140:
                print("Button clicked")
                spawn_ball()

    # Calculate the elapsed time
    delta_time = clock.tick(120) / 1000.0
    accumulator += delta_time

    while accumulator >= FIXED_TIME_STEP:
        for ball in balls:
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
            if distance_from_center + BALL_RADIUS >= CIRCLE_RADIUS:
                # Reflect the ball
                angle = math.atan2(ball_pos[1] - HEIGHT // 2, ball_pos[0] - WIDTH // 2)
                normal = [math.cos(angle), math.sin(angle)]
                dot_product = ball_speed[0] * normal[0] + ball_speed[1] * normal[1]
                ball_speed[0] -= 2 * dot_product * normal[0]
                ball_speed[1] -= 2 * dot_product * normal[1]

                # Adjust ball position to be inside the circle
                overlap = (distance_from_center + BALL_RADIUS) - CIRCLE_RADIUS
                ball_pos[0] -= overlap * normal[0]
                ball_pos[1] -= overlap * normal[1]

                # Decrease the circle radius if enough time has passed
                current_time = pygame.time.get_ticks()
                if current_time - last_bounce_time >= BOUNCE_DELAY:
                    CIRCLE_RADIUS -= CIRCLE_RADIUS_DECREMENT
                    last_bounce_time = current_time

            # Add the current ball position to the trail
            ball_trail.append((int(ball_pos[0]), int(ball_pos[1])))
            if len(ball_trail) > TRAIL_LENGTH:
                ball_trail.pop(0)

        accumulator -= FIXED_TIME_STEP

    # Check if the circle radius has reached -50
    if CIRCLE_RADIUS <= -50:
        reset_game()

    # Clear the screen
    screen.fill(BLACK)

    # Change the circle color over time
    color_change = (color_change + 1) % 360
    circle_color = pygame.Color(0)
    circle_color.hsva = (color_change, 100, 100)

    # Draw the circle with increased thickness
    pygame.draw.circle(screen, circle_color, (WIDTH // 2, HEIGHT // 2), CIRCLE_RADIUS, CIRCLE_THICKNESS)

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

    # Draw the spawn button
    pygame.draw.rect(screen, RED, (10, 90, 100, 50))
    button_text = font.render('Spawn Ball', True, WHITE)
    screen.blit(button_text, (15, 100))

    # Update the display
    pygame.display.flip()

pygame.quit()
sys.exit()
import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1600, 900
BALL_RADIUS = 20
CIRCLE_RADIUS = 450
CIRCLE_RADIUS_DECREMENT = 5
GRAVITY = 7
BOUNCE_DELAY = 50  # Delay in milliseconds
CIRCLE_THICKNESS = 5  # Increased thickness of the circle
FIXED_TIME_STEP = 1 / 240  # Fixed time step for physics calculations

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Free Views")

# Font setup
font = pygame.font.SysFont(None, 36)

# Ball setup with random variance
spawn_variance = 250
ball_pos = [
    WIDTH // 2 + random.randint(-spawn_variance, spawn_variance),
    HEIGHT // 2 + random.randint(-spawn_variance, spawn_variance)
]
ball_speed = [2, 2]

# Timer setup
last_bounce_time = pygame.time.get_ticks()
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

        accumulator -= FIXED_TIME_STEP

    # Calculate the ball's velocity
    velocity = math.sqrt(ball_speed[0] ** 2 + ball_speed[1] ** 2)

    # Clear the screen
    screen.fill(BLACK)

    # Change the circle color over time
    color_change = (color_change + 1) % 360
    circle_color = pygame.Color(0)
    circle_color.hsva = (color_change, 100, 100)

    # Draw the circle with increased thickness
    pygame.draw.circle(screen, circle_color, (WIDTH // 2, HEIGHT // 2), CIRCLE_RADIUS, CIRCLE_THICKNESS)

    # Draw the ball
    pygame.draw.circle(screen, GREEN, (int(ball_pos[0]), int(ball_pos[1])), BALL_RADIUS)

    # Render the velocity text
    velocity_text = font.render(f'Velocity: {velocity:.2f}', True, WHITE)
    screen.blit(velocity_text, (10, 10))

    # Render the FPS text
    fps = clock.get_fps()
    fps_text = font.render(f'FPS: {fps:.2f}', True, WHITE)
    screen.blit(fps_text, (10, 50))

    # Render the circle radius text
    radius_text = font.render(f'Radius: {CIRCLE_RADIUS}', True, WHITE)
    screen.blit(radius_text, (10, 90))

    # Update the display
    pygame.display.flip()

pygame.quit()
sys.exit()
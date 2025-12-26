import pygame
import socket
import time

# UDP configuration
UDP_IP = "10.134.123.122"  # Replace with your ESP32's IP address
UDP_PORT = 12345

# Initialize pygame
pygame.init()

# Canvas dimensions (should match OLED dimensions)
WIDTH, HEIGHT = 128, 64
canvas = pygame.display.set_mode((WIDTH * 4, HEIGHT * 4))  # Scaled up for visibility
pygame.display.set_caption("OLED Drawing Tool - Left: Draw | Right: Erase | C: Clear")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Initialize canvas
canvas.fill(BLACK)
pygame.display.flip()

# Drawing variables
drawing = False
erasing = False
last_pos = None
pixel_size = 4  # Scaling factor for display

def send_pixel(x, y, state):
    """Send pixel data to ESP32 over UDP"""
    message = f"{x},{y},{state}"
    sock.sendto(message.encode(), (UDP_IP, UDP_PORT))

def clear_screen():
    """Clear both local canvas and OLED display"""
    # Clear local canvas
    canvas.fill(BLACK)
    pygame.display.flip()
    
    # Send clear command to ESP32 (special message)
    sock.sendto(b"clear", (UDP_IP, UDP_PORT))

def draw_pixel(pos, state):
    """Draw/erase pixel on canvas and send to ESP32"""
    x, y = pos[0] // pixel_size, pos[1] // pixel_size
    
    # Ensure coordinates are within bounds
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        # Draw on local canvas
        color = WHITE if state else BLACK
        pygame.draw.rect(canvas, color, (x * pixel_size, y * pixel_size, pixel_size, pixel_size))
        
        # Send to ESP32
        send_pixel(x, y, state)
        
        pygame.display.flip()
        return (x, y)
    return None

def draw_line(start, end, state):
    """Draw/erase line between two points using Bresenham's algorithm"""
    x0, y0 = start
    x1, y1 = end
    
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    
    while True:
        draw_pixel((x0 * pixel_size, y0 * pixel_size), state)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button - draw
                drawing = True
                erasing = False
                pos = (event.pos[0], event.pos[1])
                last_pos = draw_pixel(pos, 1)
            elif event.button == 3:  # Right mouse button - erase
                erasing = True
                drawing = False
                pos = (event.pos[0], event.pos[1])
                last_pos = draw_pixel(pos, 0)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                drawing = False
                last_pos = None
            elif event.button == 3:  # Right mouse button
                erasing = False
                last_pos = None
        
        elif event.type == pygame.MOUSEMOTION:
            if drawing:
                pos = (event.pos[0], event.pos[1])
                current_pos = draw_pixel(pos, 1)
                if last_pos and current_pos:
                    draw_line(last_pos, current_pos, 1)
                last_pos = current_pos
            elif erasing:
                pos = (event.pos[0], event.pos[1])
                current_pos = draw_pixel(pos, 0)
                if last_pos and current_pos:
                    draw_line(last_pos, current_pos, 0)
                last_pos = current_pos
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:  # Clear screen
                clear_screen()
    
    pygame.display.flip()
    time.sleep(0.01)  # Small delay to prevent high CPU usage

pygame.quit()
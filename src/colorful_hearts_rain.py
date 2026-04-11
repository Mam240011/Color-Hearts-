# colorful_hearts_rain.py
# Requires: pygame (pip install pygame)
# Run: python colorful_hearts_rain.py

import pygame, random, sys, math

# Configuration
WIDTH, HEIGHT = 800, 600
FPS = 60
NUM_HEARTS = 120
MIN_SPEED, MAX_SPEED = 60, 360    # pixels per second
MIN_SIZE, MAX_SIZE = 16, 64

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Colorful Hearts Rain")
clock = pygame.time.Clock()

def hsv_to_rgb(h, s, v):
    h = float(h) % 360
    s = float(s)
    v = float(v)
    c = v * s
    x = c * (1 - abs(((h / 60.0) % 2) - 1))
    m = v - c
    if h < 60:
        r1, g1, b1 = c, x, 0
    elif h < 120:
        r1, g1, b1 = x, c, 0
    elif h < 180:
        r1, g1, b1 = 0, c, x
    elif h < 240:
        r1, g1, b1 = 0, x, c
    elif h < 300:
        r1, g1, b1 = x, 0, c
    else:
        r1, g1, b1 = c, 0, x
    return int((r1 + m) * 255), int((g1 + m) * 255), int((b1 + m) * 255)

def random_color():
    palette_choice = random.choices(["warm", "blue", "green"], weights=[0.5, 0.25, 0.25])[0]
    if palette_choice == "warm":
        h = random.uniform(330, 360) if random.random() < 0.6 else random.uniform(0, 20)
        s = random.uniform(0.6, 1.0); v = random.uniform(0.8, 1.0)
    elif palette_choice == "blue":
        h = random.uniform(190, 250); s = random.uniform(0.5, 1.0); v = random.uniform(0.7, 1.0)
    else:
        h = random.uniform(100, 170); s = random.uniform(0.5, 1.0); v = random.uniform(0.7, 1.0)
    return hsv_to_rgb(h, s, v)

def make_vector_heart(size, color, alpha):
    # Draw heart shape into a Surface sized (size,size) using two circles + bottom triangle.
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    surf = surf.convert_alpha()
    r = size * 0.25
    cx1 = size * 0.35
    cx2 = size * 0.65
    cy = size * 0.30
    # circles (left, right)
    pygame.draw.circle(surf, color + (alpha,), (int(cx1), int(cy)), int(r))
    pygame.draw.circle(surf, color + (alpha,), (int(cx2), int(cy)), int(r))
    # bottom triangle
    p1 = (int(size * 0.15), int(size * 0.45))
    p2 = (int(size * 0.85), int(size * 0.45))
    p3 = (int(size * 0.5), int(size * 0.95))
    pygame.draw.polygon(surf, color + (alpha,), (p1, p2, p3))
    # optional small smoothing: draw a slightly smaller overlay to fix seam
    return surf

class Heart:
    def __init__(self):
        self.reset(initial=True)

    def reset(self, initial=False):
        self.size = random.randint(MIN_SIZE, MAX_SIZE)
        self.x = random.uniform(0, max(1, screen.get_width() - self.size))
        self.y = random.uniform(-screen.get_height(), -self.size) if initial else random.uniform(-self.size*8, -self.size)
        speed_factor = (self.size / MAX_SIZE) * 0.8 + 0.6
        self.speed = random.uniform(MIN_SPEED, MAX_SPEED) * speed_factor
        self.color = random_color()
        self.alpha = random.randint(180, 255)
        self._render_image()

    def _render_image(self):
        self.image = make_vector_heart(self.size, self.color, self.alpha)

    def update(self, dt):
        self.y += self.speed * dt
        self.x += math.sin(self.y * 0.02 + self.size) * 20 * dt
        if self.y - self.size > screen.get_height():
            self.reset()

    def draw(self, surf):
        surf.blit(self.image, (int(self.x), int(self.y)))

hearts = [Heart() for _ in range(NUM_HEARTS)]

paused = False

def make_gradient(w, h, top=(10,10,20), bottom=(40,10,30)):
    grad = pygame.Surface((w, h))
    for y in range(h):
        t = y / (h - 1) if h > 1 else 0
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        pygame.draw.line(grad, (r, g, b), (0, y), (w, y))
    return grad

gradient = make_gradient(WIDTH, HEIGHT)

while True:
    dt = clock.tick(FPS) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            gradient = make_gradient(WIDTH, HEIGHT)
            for h in hearts:
                h._render_image()
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_q, pygame.K_ESCAPE):
                pygame.quit(); sys.exit()
            elif event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                for h in hearts: h.speed *= 1.15
            elif event.key in (pygame.K_MINUS, pygame.K_UNDERSCORE):
                for h in hearts: h.speed *= 0.85
            elif event.key == pygame.K_r:
                for h in hearts: h.reset()

    if not paused:
        for h in hearts: h.update(dt)

    screen.blit(gradient, (0,0))
    for h in hearts: h.draw(screen)

    hud_font = pygame.font.SysFont(None, 18)
    hud = hud_font.render("Space: pause  +/-: speed  R: reset  Q/Esc: quit", True, (220,220,220))
    screen.blit(hud, (8, screen.get_height() - 24))
    pygame.display.flip()



import pygame
import random
import sys
import math
import time
import numpy as np

# =========================================================
# CONFIG
# =========================================================

WIDTH, HEIGHT = 1000, 700
FPS = 60

NUM_HEARTS = 140

MIN_SPEED, MAX_SPEED = 60, 360
MIN_SIZE, MAX_SIZE = 16, 64

TRAIL_ALPHA_DECAY = 55

BLOOM_INTENSITY = 1.4
BLOOM_DOWNSAMPLE = 0.22

BACKGROUND_TOP = (10, 10, 25)
BACKGROUND_BOTTOM = (50, 10, 40)

screen_flash = 0

# =========================================================
# COLOR UTILITIES
# =========================================================

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

    return (
        int((r1 + m) * 255),
        int((g1 + m) * 255),
        int((b1 + m) * 255)
    )

def random_color():

    palette = random.choices(
        ["warm", "blue", "green"],
        weights=[0.5, 0.25, 0.25]
    )[0]

    if palette == "warm":
        h = random.uniform(330, 360) if random.random() < 0.6 else random.uniform(0, 20)
    elif palette == "blue":
        h = random.uniform(190, 250)
    else:
        h = random.uniform(100, 170)

    s = random.uniform(0.6, 1.0)
    v = random.uniform(0.8, 1.0)

    return hsv_to_rgb(h, s, v)

# =========================================================
# HEART DRAWING
# =========================================================

def make_vector_heart(size, color, alpha):

    surf = pygame.Surface((size, size), pygame.SRCALPHA)

    r = size * 0.25

    cx1 = size * 0.35
    cx2 = size * 0.65
    cy = size * 0.30

    pygame.draw.circle(
        surf,
        color + (alpha,),
        (int(cx1), int(cy)),
        int(r)
    )

    pygame.draw.circle(
        surf,
        color + (alpha,),
        (int(cx2), int(cy)),
        int(r)
    )

    p1 = (int(size * 0.15), int(size * 0.45))
    p2 = (int(size * 0.85), int(size * 0.45))
    p3 = (int(size * 0.50), int(size * 0.95))

    pygame.draw.polygon(
        surf,
        color + (alpha,),
        (p1, p2, p3)
    )

    return surf

# =========================================================
# HEART CLASS
# =========================================================

class Heart:

    def __init__(self, screen):
        self.screen = screen
        self.reset(initial=True)

    def reset(self, initial=False):

        self.size = random.randint(MIN_SIZE, MAX_SIZE)

        self.x = random.uniform(
            0,
            self.screen.get_width() - self.size
        )

        self.y = (
            random.uniform(-HEIGHT, -self.size)
            if initial else
            random.uniform(-self.size * 10, -self.size)
        )

        self.vx = random.uniform(-30, 30)
        self.vy = random.uniform(MIN_SPEED, MAX_SPEED)

        self.color = random_color()

        self.alpha = random.randint(180, 255)

        self.phase = random.uniform(0, math.pi * 2)

        self.twinkle_speed = random.uniform(1.5, 4)

        self.rotation = random.uniform(-15, 15)

        self._render_image()

    def _render_image(self):

        self.image = make_vector_heart(
            self.size,
            self.color,
            self.alpha
        )

        glow_size = int(self.size * 1.8)

        self.glow = make_vector_heart(
            glow_size,
            self.color,
            int(self.alpha * 0.25)
        )

    # =====================================================
    # EXPLOSION EFFECT
    # =====================================================

    def explode(self, mx, my):

        dx = self.x - mx
        dy = self.y - my

        dist = max(1, math.hypot(dx, dy))

        power = 450 / dist

        self.vx += (dx / dist) * power * 120
        self.vy += (dy / dist) * power * 120

    # =====================================================
    # UPDATE
    # =====================================================

    def update(self, dt):

        # Floating sway
        self.x += math.sin(
            self.y * 0.015 + self.phase
        ) * 25 * dt

        # Velocity damping
        self.vx *= 0.985
        self.vy *= 0.998

        # Movement
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Extra drift
        self.x += math.sin(
            time.time() + self.phase
        ) * 12 * dt

        # Respawn
        if self.y > self.screen.get_height() + 120:
            self.reset()

        if self.x < -120 or self.x > self.screen.get_width() + 120:
            self.reset()

    # =====================================================
    # DRAW
    # =====================================================

    def draw(self, surf):

        pulse = math.sin(
            time.time() * self.twinkle_speed + self.phase
        ) * 25

        img = self.image.copy()

        img.set_alpha(
            max(80, min(255, self.alpha + int(pulse)))
        )

        rotated = pygame.transform.rotate(
            img,
            self.rotation
        )

        surf.blit(
            rotated,
            (int(self.x), int(self.y))
        )

# =========================================================
# BACKGROUND
# =========================================================

def make_gradient(w, h):

    grad = pygame.Surface((w, h))

    for y in range(h):

        t = y / h

        r = int(BACKGROUND_TOP[0] * (1 - t) + BACKGROUND_BOTTOM[0] * t)
        g = int(BACKGROUND_TOP[1] * (1 - t) + BACKGROUND_BOTTOM[1] * t)
        b = int(BACKGROUND_TOP[2] * (1 - t) + BACKGROUND_BOTTOM[2] * t)

        pygame.draw.line(grad, (r, g, b), (0, y), (w, y))

    return grad

# =========================================================
# BLOOM EFFECT
# =========================================================

def apply_bloom(source):

    w, h = source.get_size()

    small = pygame.transform.smoothscale(
        source,
        (
            int(w * BLOOM_DOWNSAMPLE),
            int(h * BLOOM_DOWNSAMPLE)
        )
    )

    blurred = pygame.transform.smoothscale(
        small,
        (w, h)
    )

    result = blurred.copy()

    alpha = pygame.surfarray.pixels_alpha(result)

    alpha[:] = np.clip(
        alpha * BLOOM_INTENSITY,
        0,
        255
    )

    del alpha

    return result

# =========================================================
# MAIN
# =========================================================

def main():

    global screen_flash

    pygame.init()

    screen = pygame.display.set_mode(
        (WIDTH, HEIGHT),
        pygame.RESIZABLE
    )

    pygame.display.set_caption(
        "Interactive Neon Hearts"
    )

    clock = pygame.time.Clock()

    hearts = [Heart(screen) for _ in range(NUM_HEARTS)]

    gradient = make_gradient(WIDTH, HEIGHT)

    trail_surf = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    paused = False

    while True:

        dt = clock.tick(FPS) / 1000.0

        # =================================================
        # EVENTS
        # =================================================

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:

                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.quit()
                    sys.exit()

                elif event.key == pygame.K_SPACE:
                    paused = not paused

            elif event.type == pygame.MOUSEBUTTONDOWN:

                mx, my = event.pos

                # Trigger screen flash
                screen_flash = 220

                for hrt in hearts:

                    dx = hrt.x - mx
                    dy = hrt.y - my

                    dist = math.hypot(dx, dy)

                    if dist < 180:
                        hrt.explode(mx, my)

            elif event.type == pygame.VIDEORESIZE:

                screen = pygame.display.set_mode(
                    (event.w, event.h),
                    pygame.RESIZABLE
                )

                gradient = make_gradient(
                    event.w,
                    event.h
                )

                trail_surf = pygame.Surface(
                    (event.w, event.h),
                    pygame.SRCALPHA
                )

        # =================================================
        # UPDATE
        # =================================================

        if not paused:
            for hrt in hearts:
                hrt.update(dt)

        # =================================================
        # DRAW BACKGROUND
        # =================================================

        screen.blit(gradient, (0, 0))

        # =================================================
        # HEART LAYER
        # =================================================

        fg = pygame.Surface(
            screen.get_size(),
            pygame.SRCALPHA
        )

        for hrt in hearts:
            hrt.draw(fg)

        # =================================================
        # TRAILS
        # =================================================

        fade = pygame.Surface(
            screen.get_size(),
            pygame.SRCALPHA
        )

        fade.fill((0, 0, 0, TRAIL_ALPHA_DECAY))

        trail_surf.blit(
            fade,
            (0, 0),
            special_flags=pygame.BLEND_RGBA_SUB
        )

        trail_surf.blit(fg, (0, 0))

        screen.blit(trail_surf, (0, 0))

        # =================================================
        # BLOOM
        # =================================================

        glow_surf = pygame.Surface(
            screen.get_size(),
            pygame.SRCALPHA
        )

        for hrt in hearts:

            gx = int(
                hrt.x
                + hrt.size * 0.5
                - hrt.glow.get_width() * 0.5
            )

            gy = int(
                hrt.y
                + hrt.size * 0.5
                - hrt.glow.get_height() * 0.5
            )

            glow_surf.blit(
                hrt.glow,
                (gx, gy)
            )

        bloom = apply_bloom(glow_surf)

        screen.blit(
            bloom,
            (0, 0),
            special_flags=pygame.BLEND_ADD
        )

        # =================================================
        # SCREEN FLASH EFFECT
        # =================================================

        if screen_flash > 0:

            flash = pygame.Surface(screen.get_size())

            flash.fill((255, 255, 255))

            flash.set_alpha(int(screen_flash))

            screen.blit(flash, (0, 0))

            screen_flash -= 500 * dt

            if screen_flash < 0:
                screen_flash = 0

        # =================================================
        # HUD
        # =================================================

        font = pygame.font.SysFont(None, 22)

        hud = font.render(
            "CLICK = heart explosion + flash   SPACE = pause   ESC = quit",
            True,
            (240, 240, 240)
        )

        screen.blit(
            hud,
            (10, screen.get_height() - 30)
        )

        pygame.display.flip()

# =========================================================
# START
# =========================================================

if __name__ == "__main__":
    main()

# Requires: pygame, python
# Run: python colorful_hearts_rain.py



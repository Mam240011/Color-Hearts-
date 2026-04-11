import pygame, random, sys, math, time

# Configuration
WIDTH, HEIGHT = 800, 600
FPS = 60
NUM_HEARTS = 120
MIN_SPEED, MAX_SPEED = 60, 360    # pixels per second
MIN_SIZE, MAX_SIZE = 16, 64

# Trail / bloom parameters
TRAIL_ALPHA_DECAY = 40     # per second, higher = faster fade
BLOOM_INTENSITY = 0.8      # additive intensity for bloom layer
BLOOM_DOWNSAMPLE = 0.25    # fraction size for blur pass (0.1 - 0.5)

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
    surf = pygame.Surface((size, size), pygame.SRCALPHA).convert_alpha()
    r = size * 0.25
    cx1 = size * 0.35
    cx2 = size * 0.65
    cy = size * 0.30
    pygame.draw.circle(surf, color + (alpha,), (int(cx1), int(cy)), int(r))
    pygame.draw.circle(surf, color + (alpha,), (int(cx2), int(cy)), int(r))
    p1 = (int(size * 0.15), int(size * 0.45))
    p2 = (int(size * 0.85), int(size * 0.45))
    p3 = (int(size * 0.5), int(size * 0.95))
    pygame.draw.polygon(surf, color + (alpha,), (p1, p2, p3))
    return surf

class Heart:
    def __init__(self, screen):
        self.screen = screen
        self.reset(initial=True)

    def reset(self, initial=False):
        self.size = random.randint(MIN_SIZE, MAX_SIZE)
        self.x = random.uniform(0, max(1, self.screen.get_width() - self.size))
        self.y = random.uniform(-self.screen.get_height(), -self.size) if initial else random.uniform(-self.size*8, -self.size)
        speed_factor = (self.size / MAX_SIZE) * 0.8 + 0.6
        self.speed = random.uniform(MIN_SPEED, MAX_SPEED) * speed_factor
        self.color = random_color()
        self.alpha = random.randint(200, 255)
        self._render_image()

    def _render_image(self):
        self.image = make_vector_heart(self.size, self.color, self.alpha)
        # precompute glow image (slightly larger, softer alpha) for bloom pass
        glow_size = int(self.size * 1.6)
        glow = make_vector_heart(glow_size, self.color, int(self.alpha * 0.25))
        self.glow = pygame.transform.smoothscale(glow, (glow_size, glow_size)).convert_alpha()

    def update(self, dt):
        self.y += self.speed * dt
        self.x += math.sin(self.y * 0.02 + self.size) * 20 * dt
        if self.y - self.size > self.screen.get_height():
            self.reset()

    def draw(self, surf):
        surf.blit(self.image, (int(self.x), int(self.y)))

def make_gradient(w, h, top=(10,10,20), bottom=(40,10,30)):
    grad = pygame.Surface((w, h))
    for y in range(h):
        t = y / (h - 1) if h > 1 else 0
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        pygame.draw.line(grad, (r, g, b), (0, y), (w, y))
    return grad

def apply_bloom(source_surf, downscale=BLOOM_DOWNSAMPLE, intensity=BLOOM_INTENSITY):
    # downsample -> blur via smoothscale -> upsample -> return additive surface
    w, h = source_surf.get_size()
    small_w = max(2, int(w * downscale))
    small_h = max(2, int(h * downscale))
    small = pygame.transform.smoothscale(source_surf, (small_w, small_h))
    # repeated blur passes (down/up) to soften
    small = pygame.transform.smoothscale(small, (max(2, int(small_w*0.8)), max(2, int(small_h*0.8))))
    blurred = pygame.transform.smoothscale(small, (w, h))
    # multiply alpha by intensity by converting to additive-like surface
    result = blurred.copy().convert_alpha()
    arr = pygame.surfarray.pixels_alpha(result)
    # scale alpha safely
    arr[:] = numpy_clip_mult(arr, intensity)
    del arr
    return result

def numpy_clip_mult(alpha_array, intensity):
    # helper: use numpy if available, else fallback
    try:
        import numpy as np
        a = np.array(alpha_array, copy=False)
        a = (a.astype(np.float32) * intensity).clip(0, 255).astype(np.uint8)
        return a
    except Exception:
        # fallback: manual iteration (slower), but we returned the alpha array object originally
        h, w = alpha_array.shape
        for y in range(h):
            for x in range(w):
                v = alpha_array[y][x]
                nv = int(v * intensity)
                alpha_array[y][x] = 255 if nv > 255 else nv
        return alpha_array

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Colorful Hearts Rain (T: trails, B: bloom)")
    clock = pygame.time.Clock()

    hearts = [Heart(screen) for _ in range(NUM_HEARTS)]
    paused = False
    trails_enabled = True
    bloom_enabled = True

    gradient = make_gradient(WIDTH, HEIGHT)
    # trail surface accumulates previous frames; keep alpha channel
    trail_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA).convert_alpha()
    last_time = time.time()

    while True:
        now = time.time()
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                w, h = event.w, event.h
                screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
                gradient = make_gradient(w, h)
                trail_surf = pygame.Surface((w, h), pygame.SRCALPHA).convert_alpha()
                for hrt in hearts:
                    hrt.screen = screen
                    hrt._render_image()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit(); sys.exit()
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                    for hrt in hearts: hrt.speed *= 1.15
                elif event.key in (pygame.K_MINUS, pygame.K_UNDERSCORE):
                    for hrt in hearts: hrt.speed *= 0.85
                elif event.key == pygame.K_r:
                    for hrt in hearts: hrt.reset()
                elif event.key == pygame.K_t:
                    trails_enabled = not trails_enabled
                elif event.key == pygame.K_b:
                    bloom_enabled = not bloom_enabled

        if not paused:
            for hrt in hearts: hrt.update(dt)

        # draw base gradient background
        screen.blit(gradient, (0,0))

        # draw hearts onto a foreground surface
        fg = pygame.Surface(screen.get_size(), pygame.SRCALPHA).convert_alpha()
        for hrt in hearts:
            hrt.draw(fg)

        # Trails: accumulate fg on trail_surf and fade trail_surf slightly each frame
        if trails_enabled:
            # fade existing trail surface by drawing a translucent rectangle
            fade_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            # alpha decay scaled by dt
            decay = int(TRAIL_ALPHA_DECAY * dt)
            fade_surf.fill((0,0,0, decay))
            trail_surf.blit(fade_surf, (0,0), special_flags=pygame.BLEND_RGBA_SUB)
            # add current fg to trails (lighter alpha to avoid instant opacity)
            trail_surf.blit(fg, (0,0))
            screen.blit(trail_surf, (0,0))
        else:
            screen.blit(fg, (0,0))

        # Bloom: create additive blurred glow from heart glows and composite
        if bloom_enabled:
            # render glows to a separate surface
            glow_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA).convert_alpha()
            for hrt in hearts:
                # position glow slightly centered relative to heart
                gx = int(hrt.x + hrt.size * 0.5 - hrt.glow.get_width() * 0.5)
                gy = int(hrt.y + hrt.size * 0.5 - hrt.glow.get_height() * 0.5)
                glow_surf.blit(hrt.glow, (gx, gy))
            try:
                # if numpy available, use apply_bloom which uses numpy for alpha scaling
                bloom_layer = apply_bloom(glow_surf, downscale=BLOOM_DOWNSAMPLE, intensity=BLOOM_INTENSITY)
            except Exception:
                # simple fallback blur by multiple smoothscales
                small = pygame.transform.smoothscale(glow_surf, (max(2,int(screen.get_width()*BLOOM_DOWNSAMPLE)), max(2,int(screen.get_height()*BLOOM_DOWNSAMPLE))))
                blurred = pygame.transform.smoothscale(small, screen.get_size())
                bloom_layer = blurred
            # additive composite: BLEND_ADD
            screen.blit(bloom_layer, (0,0), special_flags=pygame.BLEND_ADD)

        # HUD
        hud_font = pygame.font.SysFont(None, 18)
        hud = hud_font.render(f"Space: pause  T: trails({ 'on' if trails_enabled else 'off'})  B: bloom({ 'on' if bloom_enabled else 'off'})  +/-: speed  R: reset  Q/Esc: quit", True, (220,220,220))
        screen.blit(hud, (8, screen.get_height() - 24))

        pygame.display.flip()

if __name__ == "__main__":
    main()

# Requires: pygame 
# Run: python colorful_hearts_rain.py



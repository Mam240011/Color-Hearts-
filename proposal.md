Colorful Hearts Rain
Repository
https://github.com/Mam240011/Color-Hearts-

Description
A Pygame-based generative visual that renders falling, colorful vector hearts with fading trails and a bloom/glow effect. It is designed for use in live visuals and media-art experiments.

Features
Falling colorful hearts

Hearts made with randomized size, speed, color (warm/blue/green) and opacity rendered each frame. Fading trails
Trails that continues and disappears over time to make motion blur-like trails. Bloom / glow effect
Blurred glow layer made from per-heart glow, downsampled/upsampled to simulate bloom. Interactive controls
Keyboard controls: Space (pause), +/- (speed), R (reset), T (toggle trails), B (toggle bloom), Q/Esc (quit). Responsive window
Resizable window with gradient background and automatic re-render of assets on resize.
Challenges
Alpha/blend handling for trails and blooming without dropping FPS.
Implementing pleasant bloom using downsample/blur passes and handling optional numpy speed up.
Designing vector hearts that scale cleanly and look good across many sizes/resolutions.
Outcomes
Ideal Outcome:

A polished generative-visual application with smooth 60fps performance on typical hardware, good visually trails and bloom, multiple presets and easy export of frames/video for use in installations.
Minimal Viable Outcome:

A stable Pygame script that shows falling colored hearts with working trails and bloom toggles, resizing, and keyboard controls.
Milestones
Week 1

Set up repository, project layout, README, and basic requirements.
Put in core heart system: vector heart rendering, randomized properties, falling motion, and gradient background.
Week 2

Add trails system: decay/fade, and T toggle.
Add bloom: per-heart glow, downsample/upsample blur pass, and B toggle.
Week N (Final)

Improve performance
Make a simple demo video.
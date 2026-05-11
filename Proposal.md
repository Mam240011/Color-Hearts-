# Colorful Hearts Rain

## Repository
https://github.com/Mam240011/Color-Hearts-

## Description:
A Pygame-based generative visual that renders falling, Animated floating hearts, Smooth bloom lighting effect. Motion trails, Interactive click explosions and Dynamic screen flash effect. Designed as a real-time animated visualizer

Features:
Falling colorful hearts
Hearts made with randomized size, speed, color (warm/blue/green) and opacity rendered each frame. Fading trails
Trails that disappears over time to make motion blur-like trails. Bloom / glow effect
Blurred glow layer made from per-heart glow, downsampled/upsampled to simulate bloom. Interactive Effects
Mouse clicks trigger explosions
Nearby hearts burst outward
Entire screen flashes white for impact Interactive controls
Keyboard controls: Space (pause), click (Mouse)
Resizable window with gradient background and automatic re-render of assets on resize.

Challenges:
Alpha/blend handling for trails and blooming without dropping FPS.
Implementing pleasant bloom using downsample/blur passes and handling optional numpy speed up.
Designing vector hearts that scale cleanly and look good across many sizes/resolutions.
Making the explosions have the white impact.
Outcomes

Ideal Outcome:
A polished generative-visual application with smooth 60fps performance on typical hardware, good visually trails and bloom, multiple presets and easy export of frames/video for use in installations.
Minimal Viable Outcome:
A stable Pygame script that shows falling colored hearts with working trails and bloom toggles, resizing, explosions and keyboard controls.
Milestones

Week 1
Set up repository, project layout, README, and basic requirements.
Put in core heart system: vector heart rendering, randomized properties, falling motion, and gradient background.

Week 2
Add trails system: decay/fade, and T toggle.
Add bloom: per-heart glow, downsample/upsample blur pass, and B toggle.
Add explosions that pushes nearby hearts outward with the mouse.

Week N (Final)
Improve performance
Make a simple demo video.



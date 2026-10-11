import os
import glob
from moviepy.editor import (
    ImageClip,
    TextClip,
    CompositeVideoClip,
    ColorClip,
    concatenate_videoclips,
    vfx,
    AudioFileClip,
)
from moviepy.video.VideoClip import VideoClip
import numpy as np

# Configuration
WIDTH, HEIGHT = 1080, 1920
FPS = 30
OUTPUT_FOLDER = "output"
PHOTO_FOLDER = "photos"
MUSIC_FILE = "music.mp3"  # ajoute ta musique ici

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(PHOTO_FOLDER, exist_ok=True)

# Palettes couleur premium
GOLD = "#FFD700"
WHITE = "#FFFFFF"
BLACK = "#000000"
DARK_BG = "#0A0A0A"
ROSE_GOLD = "#F7E6B3"

def get_photos():
    patterns = ["*.jpg", "*.jpeg", "*.png", "*.webp"]
    files = []
    for p in patterns:
        files.extend(glob.glob(os.path.join(PHOTO_FOLDER, p)))
    return sorted(files)[:6]  # max 6 images pour TikTok

def ken_burns_zoom(clip, zoom_start=1.0, zoom_end=1.2, direction="in"):
    """Effet Ken Burns : zoom lent et élégant"""
    w, h = clip.w, clip.h
    
    def make_frame(get_frame, t):
        frame = get_frame(t)
        progress = t / clip.duration
        
        if direction == "in":
            zoom = zoom_start + (zoom_end - zoom_start) * progress
        else:
            zoom = zoom_end - (zoom_end - zoom_start) * progress
        
        new_w = int(w * zoom)
        new_h = int(h * zoom)
        
        x_crop = (new_w - w) // 2
        y_crop = (new_h - h) // 2
        
        resized = clip.resize(width=new_w)
        return resized.get_frame(t)[y_crop:y_crop+h, x_crop:x_crop+w]
    
    return VideoClip(make_frame, duration=clip.duration).set_size((w, h))

def make_premium_image_clip(path, duration, index):
    """Image avec effet Ken Burns"""
    clip = ImageClip(path).set_duration(duration)
    
    # Resize avec ratio
    clip = clip.resize(height=HEIGHT)
    
    # Applique le Ken Burns effect
    if index % 2 == 0:
        clip = clip.resize(lambda t: 1.0 + 0.15 * (t / duration))  # zoom in
    else:
        clip = clip.resize(lambda t: 1.15 - 0.15 * (t / duration))  # zoom out
    
    clip = clip.set_position(("center", "center"))
    clip = clip.crossfadein(0.3).crossfadeout(0.3)
    
    return clip

def make_animated_text(text, fontsize, color, y_pos, duration, delay=0):
    """Texte avec animation d'entrée"""
    txt_clip = TextClip(
        text,
        fontsize=fontsize,
        font="DejaVu-Sans-Bold",
        color=color,
        stroke_color="#000000",
        stroke_width=2,
        method="caption",
        size=(950, None),
    ).set_duration(duration)
    
    txt_clip = txt_clip.set_position(("center", y_pos))
    
    # Animation : fade in + scale
    if delay > 0:
        txt_clip = txt_clip.set_start(delay)
    
    return txt_clip

def create_hook_frame(duration=0.8):
    """Frame d'accroche ultra percutante"""
    bg = ColorClip(size=(WIDTH, HEIGHT), color=(20, 20, 20), duration=duration)
    
    hook_text = TextClip(
        "✨ BIJOUX PREMIUM ✨",
        fontsize=96,
        font="DejaVu-Sans-Bold",
        color=GOLD,
        stroke_color=BLACK,
        stroke_width=3,
        method="caption",
    ).set_duration(duration).set_position(("center", "center"))
    
    return CompositeVideoClip([bg, hook_text], size=(WIDTH, HEIGHT)).set_duration(duration)

def create_transition_flash(duration=0.2):
    """Flash blanc pour transition"""
    return ColorClip(size=(WIDTH, HEIGHT), color=WHITE, duration=duration)

# Main
photos = get_photos()

if not photos:
    raise FileNotFoundError("Aucune photo dans photos/")

clips = []

# === HOOK ULTRA FORT ===
print("📹 Création du hook...")
hook = create_hook_frame(duration=0.7)
clips.append(hook)

# Flash transition
flash = create_transition_flash(duration=0.15)
clips.append(flash)

# === IMAGES AVEC EFFETS ===
print("📹 Ajout des images avec effets...")
for idx, photo in enumerate(photos):
    duration = 2.2 if idx == 0 else 1.8  # première image plus longue
    
    bg = ColorClip(size=(WIDTH, HEIGHT), color=DARK_BG, duration=duration)
    image_clip = make_premium_image_clip(photo, duration, idx)
    
    # Texte principal
    title = make_animated_text(
        "Yline Bijoux",
        fontsize=68,
        color=GOLD,
        y_pos=150,
        duration=duration,
        delay=0.2
    )
    
    # Sous-titre
    subtitle = make_animated_text(
        "Élégance & Luxe",
        fontsize=52,
        color=WHITE,
        y_pos=HEIGHT - 300,
        duration=duration,
        delay=0.4
    )
    
    # CTA animée
    cta = make_animated_text(
        "👉 Shop Now 👈",
        fontsize=56,
        color=ROSE_GOLD,
        y_pos=HEIGHT - 150,
        duration=duration,
        delay=0.5
    )
    
    composite = CompositeVideoClip(
        [bg, image_clip, title, subtitle, cta],
        size=(WIDTH, HEIGHT)
    ).set_duration(duration)
    
    clips.append(composite)
    
    # Flash entre les images
    if idx < len(photos) - 1:
        clips.append(create_transition_flash(duration=0.12))

# === FRAME FINALE CTA ===
print("📹 Création de la frame finale...")
final_bg = ColorClip(size=(WIDTH, HEIGHT), color=(15, 15, 15), duration=1.2)

final_text1 = TextClip(
    "⭐ Collection Exclusive ⭐",
    fontsize=64,
    font="DejaVu-Sans-Bold",
    color=GOLD,
    stroke_color=BLACK,
    stroke_width=2,
    method="caption",
).set_duration(1.2).set_position(("center", 300))

final_text2 = TextClip(
    "Découvre nos bijoux premium",
    fontsize=48,
    font="DejaVu-Sans",
    color=WHITE,
    method="caption",
    size=(900, None),
).set_duration(1.2).set_position(("center", 800))

final_text3 = TextClip(
    "➜ www.ylinebijoux.com ➜",
    fontsize=56,
    font="DejaVu-Sans-Bold",
    color=ROSE_GOLD,
    stroke_color=BLACK,
    stroke_width=2,
).set_duration(1.2).set_position(("center", HEIGHT - 200))

final_frame = CompositeVideoClip(
    [final_bg, final_text1, final_text2, final_text3],
    size=(WIDTH, HEIGHT)
).set_duration(1.2)

clips.append(final_frame)

# === MONTAGE FINAL ===
print("📹 Montage du projet complet...")
final_video = concatenate_videoclips(clips, method="compose")

# Ajoute la musique si elle existe
if os.path.exists(MUSIC_FILE):
    print(f"📹 Ajout de la musique...")
    audio = AudioFileClip(MUSIC_FILE)
    # Coupe ou boucle l'audio pour qu'il corresponde à la durée vidéo
    if audio.duration < final_video.duration:
        # Boucle l'audio
        n_loops = int(final_video.duration / audio.duration) + 1
        audio = concatenate_videoclips([audio] * n_loops).set_duration(final_video.duration)
    else:
        audio = audio.set_duration(final_video.duration)
    
    final_video = final_video.set_audio(audio)

# Export
output_path = os.path.join(OUTPUT_FOLDER, "tiktok_bijoux_pro.mp4")
print(f"📹 Export en cours... {output_path}")
final_video.write_videofile(
    output_path,
    fps=FPS,
    codec="libx264",
    preset="fast",
    bitrate="12000k",
    threads=4,
    audio=True if os.path.exists(MUSIC_FILE) else False,
    verbose=False,
    logger=None
)

print(f"✅ Vidéo créée : {output_path}")
print(f"⏱️ Durée : {final_video.duration:.1f}s")

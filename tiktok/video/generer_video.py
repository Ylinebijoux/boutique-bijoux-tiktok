"""
Génère la vidéo TikTok « Golden Hour » (Yline Bijoux) à partir de tes photos.

    pip install -r requirements.txt
    python generer_video.py

Les photos sont lues dans photos/ par ordre alphabétique : nomme-les
01-....jpg à 08-....jpg pour qu'elles suivent les 8 plans du script.
S'il y en a moins de 8, elles sont réutilisées dans l'ordre.
"""
import argparse
import glob
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
from moviepy import (
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    afx,
    vfx,
)

# --------------------------------------
# Configuration
# --------------------------------------
WIDTH, HEIGHT = 1080, 1920
FPS = 30
DUREE = 23
FONDU = 0.3                      # fondu enchaîné entre deux plans (s)
ZONE_TEXTE_HAUT = int(HEIGHT * 0.15)
MARGE = int(WIDTH * 0.09)

ICI = os.path.dirname(os.path.abspath(__file__))
PHOTO_FOLDER = os.path.join(ICI, "photos")
OUTPUT_FOLDER = os.path.join(ICI, "output")
VOIX_OFF = os.path.join(ICI, "..", "audio", "voix-off-calee-23s.mp3")
FONTS_FOLDER = os.path.join(ICI, "fonts")

IVOIRE = (248, 243, 234)
OR = (227, 194, 127)
ENCRE = (30, 22, 17)             # texte sur fond clair (satin, flat lay)

# Les 8 plans du script (tiktok/01-golden-hour.md).
# style : "titre" (serif, centré), "phrase" (sans-serif, centré), "etiquette" (petites capitales, à gauche)
PLANS = [
    dict(debut=0,  fin=2,  texte="On dirait de l'or fin… non\u00a0?",               style="titre",     zoom=(1.04, 1.12)),
    dict(debut=2,  fin=4,  texte="Acier inoxydable doré",                           style="titre",     zoom=(1.00, 1.05)),
    dict(debut=4,  fin=7,  texte="Hypoallergénique · Sans\u00a0nickel · Ne\u00a0s'oxyde\u00a0pas", style="phrase", zoom=(1.06, 1.00)),
    dict(debut=7,  fin=10, texte="Boucles «\u00a0Ayana\u00a0»",                     style="etiquette", zoom=(1.00, 1.08)),
    dict(debut=10, fin=13, texte="Collier «\u00a0Giulia\u00a0»",                    style="etiquette", zoom=(1.00, 1.12)),
    dict(debut=13, fin=16, texte="Bracelet «\u00a0Lunéa\u00a0»",                    style="etiquette", zoom=(1.00, 1.06)),
    dict(debut=16, fin=19, texte="Le look complet\u00a0: 48,50\u00a0€",             style="titre",     zoom=(1.08, 1.00)),
    dict(debut=19, fin=23, texte="Compose ton look doré",                           style="titre",     zoom=(1.00, 1.03),
         cta="yline.fr · lien en bio"),
]

# Polices : Bodoni Moda et Jost sont fournies dans fonts/ (licence libre OFL).
# Pour en changer, dépose fonts/titre.ttf et/ou fonts/texte.ttf. Sinon, une police système proche est utilisée.
POLICES_TITRE = [
    "fonts/titre.ttf", "fonts/BodoniModa.ttf",
    "/System/Library/Fonts/Supplemental/Didot.ttc",
    "/System/Library/Fonts/Supplemental/Georgia.ttf",
    "C:/Windows/Fonts/georgia.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
]
POLICES_TEXTE = [
    "fonts/texte.ttf", "fonts/Jost.ttf",
    "/System/Library/Fonts/Avenir Next.ttc",
    "/System/Library/Fonts/Supplemental/Futura.ttc",
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


# --------------------------------------
# Helpers
# --------------------------------------
def trouver_police(candidates, taille, axes=None):
    """axes : réglages d'une police variable, ex. [graisse, taille optique] pour Bodoni Moda."""
    for chemin in candidates:
        if not os.path.isabs(chemin):
            chemin = os.path.join(ICI, chemin)
        if os.path.exists(chemin):
            police = ImageFont.truetype(chemin, taille)
            if axes:
                try:
                    police.set_variation_by_axes(axes[:len(police.get_variation_axes())])
                except OSError:
                    pass                             # police non variable : on la garde telle quelle
            return police
    return ImageFont.load_default(taille)


def fond_clair(img):
    """True si la zone où s'écrit le texte (haut du cadre) est claire."""
    zone = img.convert("L").crop((MARGE, int(HEIGHT * 0.12), WIDTH - MARGE, int(HEIGHT * 0.36)))
    return np.asarray(zone).mean() > 150


def get_photos(dossier):
    patterns = ["*.jpg", "*.jpeg", "*.png", "*.webp"]
    files = []
    for p in patterns:
        files.extend(glob.glob(os.path.join(dossier, p)))
        files.extend(glob.glob(os.path.join(dossier, p.upper())))
    return sorted(set(files))


def recadrer(img, largeur, hauteur):
    """Remplit largeur x hauteur en recadrant au centre (sans déformer)."""
    ratio = max(largeur / img.width, hauteur / img.height)
    img = img.resize((round(img.width * ratio), round(img.height * ratio)), Image.LANCZOS)
    x = (img.width - largeur) // 2
    y = (img.height - hauteur) // 2
    return img.crop((x, y, x + largeur, y + hauteur))


def etalonner(img):
    """Étalonnage chaud et léger vignettage : l'or reste doré, pas orange."""
    arr = np.asarray(img).astype(np.float32)
    arr[..., 0] *= 1.04
    arr[..., 2] *= 0.94
    yy, xx = np.mgrid[0:img.height, 0:img.width]
    d = np.sqrt(((xx - img.width / 2) / (img.width / 2)) ** 2 + ((yy - img.height / 2) / (img.height / 2)) ** 2)
    arr *= (1 - 0.22 * np.clip(d - 0.55, 0, 1))[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def preparer_photo(path):
    """
    Photo verticale (ta vidéo/ton tournage) : plein cadre.
    Photo carrée ou horizontale (photo produit) : posée au centre sur un fond flou
    de la même photo, pour ne pas couper le bijou.
    """
    img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")   # remet droites les photos de téléphone
    if img.height / img.width >= 1.4:
        return etalonner(recadrer(img, WIDTH, HEIGHT))

    fond = recadrer(img, WIDTH, HEIGHT).filter(ImageFilter.GaussianBlur(45))
    fond = Image.fromarray((np.asarray(fond).astype(np.float32) * 0.45).astype(np.uint8))
    largeur = int(WIDTH * 0.9)
    photo = img.resize((largeur, round(img.height * largeur / img.width)), Image.LANCZOS)
    hauteur = min(photo.height, int(HEIGHT * 0.6))
    haut = (photo.height - hauteur) // 2
    photo = photo.crop((0, haut, largeur, haut + hauteur))
    masque = Image.new("L", photo.size, 0)
    ImageDraw.Draw(masque).rounded_rectangle((0, 0, *photo.size), radius=28, fill=255)
    ombre = Image.new("L", (WIDTH, HEIGHT), 0)
    x = (WIDTH - photo.width) // 2
    y = int(HEIGHT * 0.47) - photo.height // 2       # un peu au-dessus du centre : le bas est caché par TikTok
    ImageDraw.Draw(ombre).rounded_rectangle((x, y + 18, x + photo.width, y + photo.height + 18), radius=28, fill=150)
    fond.paste(Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0)), (0, 0), ombre.filter(ImageFilter.GaussianBlur(30)))
    fond.paste(photo, (x, y), masque)
    return etalonner(fond)


def couper_lignes(draw, texte, police, largeur_max, espacement=0):
    mots, lignes, ligne = texte.split(" "), [], ""
    for mot in mots:
        essai = (ligne + " " + mot).strip()
        if mesurer(draw, essai, police, espacement) <= largeur_max or not ligne:
            ligne = essai
        else:
            lignes.append(ligne)
            ligne = mot
    lignes.append(ligne)
    return lignes


def mesurer(draw, texte, police, espacement=0):
    return draw.textlength(texte, font=police) + espacement * max(len(texte) - 1, 0)


def ecrire(draw, xy, texte, police, couleur, espacement=0):
    if not espacement:
        draw.text(xy, texte, font=police, fill=couleur)
        return
    x, y = xy
    for lettre in texte:
        draw.text((x, y), lettre, font=police, fill=couleur)
        x += draw.textlength(lettre, font=police) + espacement


def calque_texte(plan, clair=False):
    """Calque transparent plein cadre avec le texte du plan, ombre douce comprise."""
    calque = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(calque)
    couleur = ENCRE if clair else IVOIRE
    blocs = []                                       # (lignes, police, couleur, espacement, alignement, y)

    if plan["style"] == "titre":
        police = trouver_police(POLICES_TITRE, 88, axes=[560, 24])   # taille optique 24 : déliés assez épais pour la compression TikTok
        blocs.append((couper_lignes(draw, plan["texte"], police, WIDTH - 2 * MARGE), police, couleur, 0, "centre", ZONE_TEXTE_HAUT))
    elif plan["style"] == "phrase":
        police = trouver_police(POLICES_TEXTE, 54, axes=[450])
        blocs.append((couper_lignes(draw, plan["texte"], police, WIDTH - 2 * MARGE), police, couleur, 0, "centre", ZONE_TEXTE_HAUT))
    else:
        police = trouver_police(POLICES_TEXTE, 44, axes=[500])
        blocs.append(([plan["texte"].upper()], police, couleur, 7, "gauche", ZONE_TEXTE_HAUT))

    if plan.get("cta"):
        police = trouver_police(POLICES_TEXTE, 46, axes=[500])
        blocs.append(([plan["cta"].upper()], police, ENCRE if clair else OR, 6, "centre", int(HEIGHT * 0.30)))

    texte = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    dt = ImageDraw.Draw(texte)
    for lignes, police, couleur, espacement, alignement, y in blocs:
        hauteur_ligne = int(police.size * 1.18)
        for ligne in lignes:
            largeur = mesurer(dt, ligne, police, espacement)
            x = MARGE if alignement == "gauche" else (WIDTH - largeur) / 2
            ecrire(dt, (x, y), ligne, police, couleur + (255,), espacement)
            y += hauteur_ligne

    alpha = texte.getchannel("A")
    ombre = Image.new("RGBA", (WIDTH, HEIGHT), (255, 248, 236, 0) if clair else (0, 0, 0, 0))
    ombre.putalpha(alpha.filter(ImageFilter.GaussianBlur(10)).point(lambda a: int(a * 0.55)))
    calque = Image.alpha_composite(calque, ombre)
    calque = Image.alpha_composite(calque, texte)
    return np.asarray(calque)


def make_plan_clip(plan, photo_path, index):
    duree = plan["fin"] - plan["debut"]
    if index < len(PLANS) - 1:
        duree += FONDU                               # chevauche le plan suivant pour le fondu
    z0, z1 = plan["zoom"]
    image = preparer_photo(photo_path)
    clip = (
        ImageClip(np.asarray(image))
        .with_duration(duree)
        .resized(lambda t: z0 + (z1 - z0) * min(t / duree, 1))
        .with_position(("center", "center"))
        .with_start(plan["debut"])
    )
    if index > 0:
        clip = clip.with_effects([vfx.CrossFadeIn(FONDU)])

    texte = (
        ImageClip(calque_texte(plan, clair=fond_clair(image)))
        .with_duration(plan["fin"] - plan["debut"])
        .with_start(plan["debut"])
        .with_effects([vfx.CrossFadeIn(0.35)])
    )
    return clip, texte


# --------------------------------------
# Main
# --------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Vidéo TikTok « Golden Hour » - Yline Bijoux")
    parser.add_argument("--photos", default=PHOTO_FOLDER, help="dossier des photos (défaut : photos/)")
    parser.add_argument("--voix", default=VOIX_OFF, help="voix off calée sur 23 s (défaut : ../audio/voix-off-calee-23s.mp3)")
    parser.add_argument("--musique", help="musique de fond, mise à ~22 %% sous la voix")
    parser.add_argument("--sortie", default=os.path.join(OUTPUT_FOLDER, "golden-hour.mp4"))
    args = parser.parse_args()

    photos = get_photos(args.photos)
    if not photos:
        raise FileNotFoundError(
            f"Aucune photo trouvée dans {args.photos}. "
            "Ajoute tes photos de bijoux (01-bague.jpg, 02-...) dans ce dossier."
        )
    print(f"{len(photos)} photo(s) pour {len(PLANS)} plans")

    couches = []
    textes = []
    for i, plan in enumerate(PLANS):
        photo = photos[i % len(photos)]
        print(f"  plan {i + 1} ({plan['debut']}-{plan['fin']} s) : {os.path.basename(photo)}")
        clip, texte = make_plan_clip(plan, photo, i)
        couches.append(clip)
        textes.append(texte)

    video = CompositeVideoClip(couches + textes, size=(WIDTH, HEIGHT), bg_color=(10, 8, 6)).with_duration(DUREE)

    pistes = []
    if args.voix and os.path.exists(args.voix):
        voix = AudioFileClip(args.voix)
        pistes.append(voix.subclipped(0, min(DUREE, voix.duration)))
    else:
        print("Pas de voix off trouvée : vidéo exportée sans voix.")
    if args.musique:
        musique = AudioFileClip(args.musique)
        musique = musique.subclipped(0, min(DUREE, musique.duration))
        pistes.append(musique.with_volume_scaled(0.22).with_effects([afx.AudioFadeOut(1.5)]))
    if pistes:
        video = video.with_audio(CompositeAudioClip(pistes).with_duration(DUREE))

    os.makedirs(os.path.dirname(os.path.abspath(args.sortie)), exist_ok=True)
    video.write_videofile(
        args.sortie,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        bitrate="8000k",
        threads=4,
        audio=bool(pistes),
    )
    print(f"Vidéo créée : {args.sortie}")


if __name__ == "__main__":
    main()

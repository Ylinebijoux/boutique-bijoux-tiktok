"""
Compose l'image du plan 7 « Le look complet » : les 5 pièces en vitrine, avec nom et prix.

    python composer_look.py        ->  photos/07-look-complet.png

Les photos produits sont lues dans photos/look/. Change la liste PIECES si tu changes de pièces ou de prix.
"""
import os

from PIL import Image, ImageDraw, ImageFilter, ImageOps

import generer_video as gv

PIECES = [
    ("look/1-angelica.jpg", "Angelica", "9,90 €"),
    ("look/2-bedra.webp",   "Bedra",    "8,90 €"),
    ("look/3-ayana.jpg",    "Ayana",    "8,90 €"),
    ("look/4-giulia.jpg",   "Giulia",   "8,90 €"),
    ("look/5-lunea.jpg",    "Lunéa",    "11,90 €"),
]
TUILE = 300
ECART = 36
HAUT = 580                        # sous le titre « Le look complet : 48,50 € »
LEGENDE = 118                     # place pour le nom et le prix sous chaque tuile


def tuile(chemin):
    img = ImageOps.exif_transpose(Image.open(os.path.join(gv.PHOTO_FOLDER, chemin))).convert("RGB")
    img = ImageOps.pad(img, (TUILE, TUILE), color=(255, 255, 255), method=Image.LANCZOS)
    masque = Image.new("L", (TUILE, TUILE), 0)
    ImageDraw.Draw(masque).rounded_rectangle((0, 0, TUILE, TUILE), radius=22, fill=255)
    return img, masque


def main():
    fond = gv.fond_ecrin()
    draw = ImageDraw.Draw(fond)
    nom_police = gv.trouver_police(gv.POLICES_TITRE, 40, axes=[520, 24])
    prix_police = gv.trouver_police(gv.POLICES_TEXTE, 30, axes=[500])

    rangees = [PIECES[:3], PIECES[3:]]
    positions = []
    for r, rangee in enumerate(rangees):
        largeur = len(rangee) * TUILE + (len(rangee) - 1) * ECART
        x0 = (gv.WIDTH - largeur) // 2
        y = HAUT + r * (TUILE + LEGENDE)
        positions += [(x0 + i * (TUILE + ECART), y) for i in range(len(rangee))]

    ombre = Image.new("L", fond.size, 0)
    for x, y in positions:
        ImageDraw.Draw(ombre).rounded_rectangle((x, y + 16, x + TUILE, y + TUILE + 16), radius=22, fill=160)
    fond.paste(Image.new("RGB", fond.size, (0, 0, 0)), (0, 0), ombre.filter(ImageFilter.GaussianBlur(24)))

    for (chemin, nom, prix), (x, y) in zip(PIECES, positions):
        img, masque = tuile(chemin)
        fond.paste(img, (x, y), masque)
        cx = x + TUILE / 2
        draw.text((cx, y + TUILE + 22), nom, font=nom_police, fill=gv.IVOIRE, anchor="mt")
        draw.text((cx, y + TUILE + 72), prix, font=prix_police, fill=gv.OR, anchor="mt")

    sortie = os.path.join(gv.PHOTO_FOLDER, "07-look-complet.png")
    fond.save(sortie)
    print(f"Image créée : {sortie}")


if __name__ == "__main__":
    main()

# Générer la vidéo « Golden Hour » automatiquement

Ce script monte la vidéo TikTok de 23 s à partir de tes photos. Il reprend les 8 plans, les textes à l'écran et la voix off du script [`../01-golden-hour.md`](../01-golden-hour.md).

## 1. Installer (une seule fois)

Il faut Python 3.9 ou plus récent.

```bash
cd tiktok/video
pip install -r requirements.txt
```

## 2. Les photos

Les photos de la vidéo actuelle sont déjà dans `photos/`. Ce sont les photos produits du site yline.fr :

| Fichier | Plan | Photo |
|---|---|---|
| `01-angelica-portee.jpg` | Hook | Bague Angelica portée |
| `02-bedra-lumiere.webp` | Acier inoxydable doré | Bague Bedra posée, lumière rasante |
| `03-bedra-portee.webp` | Hypoallergénique | Bague Bedra portée |
| `04-ayana-portees.webp` | Boucles | Boucle Ayana portée, de profil |
| `05-giulia-porte.jpg` | Collier | Collier Giulia porté |
| `06-lunea.jpg` | Bracelet | Bracelet Lunéa sur fond doré |
| `07-look-complet.png` | Look complet | Vitrine des 5 pièces avec nom et prix, créée par `composer_look.py` |
| `08-ayana-lumiere.webp` | CTA | Boucles Ayana dans la lumière |

Pour changer une photo, remplace le fichier en gardant le numéro au début du nom : les photos sont prises dans l'ordre alphabétique. S'il y en a moins de 8, elles sont réutilisées dans l'ordre.

La vitrine du plan 7 se refait avec `python composer_look.py`, à partir des photos produits de `photos/look/`. Les noms et les prix sont dans la liste `PIECES` en haut du fichier : pense à les mettre à jour si un prix change.

Deux cadrages possibles, réglables pour chaque plan dans la liste `PLANS` de `generer_video.py` :
- **`"plein"`** : la photo remplit l'écran. Idéal pour une photo portée en haute définition ou une photo verticale prise au téléphone. `focus=(x, y)` choisit le point à garder au centre (0 à 1). `echelle` permet de recadrer plus serré.
- **`"carte"`** : la photo entière est posée au centre sur un fond sombre façon écrin. Idéal pour une photo produit carrée. C'est le cadrage par défaut des photos qui ne sont pas verticales.

Garde le haut du cadre dégagé : c'est là que s'affichent les textes.

## 3. Lancer

```bash
python generer_video.py
```

La vidéo sort dans `output/golden-hour.mp4` (1080×1920, 30 i/s, avec la voix off).

Il existe deux versions :

| Commande | Vidéo | Durée | Son |
|---|---|---|---|
| `python generer_video.py` | **Golden Hour** : posée, élégante, avec la voix off calée | 23 s | voix off |
| `python generer_video.py --version dynamique` | **Dynamique** : hook « Ce look a l'air de coûter 300 €… », coupes rapides avec un éclat doré, réponse « 48,50 € » à la fin | 15 s | aucun : ajoute un son tendance dans TikTok |

La version dynamique sort dans `output/golden-hour-dynamique.mp4`. Ses plans sont dans la liste `PLANS_DYNAMIQUE`. Chaque plan y désigne sa photo avec la clé `photo`.

Options :

```bash
python generer_video.py --musique ma-musique.mp3      # ajoute une musique à ~22 % sous la voix
python generer_video.py --voix ../audio/autre.mp3     # change la voix off
python generer_video.py --photos ~/Desktop/shooting   # autre dossier de photos
```

Pour TikTok, il est souvent plus simple de ne pas mettre de musique ici et de l'ajouter dans l'app au moment de publier. Sur un compte pro, prends-la dans la Commercial Music Library.

## Ce que fait le script

- **Timing :** suit le script à la seconde (0–2 s, 2–4 s, 4–7 s…), avec un fondu enchaîné de 0,3 s entre les plans.
- **Mouvement :** chaque photo a un léger zoom avant ou arrière, pour qu'aucun plan ne reste figé.
- **Étalonnage :** chaud et léger, avec un petit vignettage. En plein écran, un léger voile sombre en haut garde les textes lisibles.
- **Textes :** toujours dans le tiers supérieur, jamais dans le bas de l'écran que l'interface TikTok cache. Ils sont ivoire sur fond sombre et passent automatiquement en noir chaud sur fond clair (satin).
- **Polices :** Bodoni Moda pour les titres, Jost pour le reste. Elles sont fournies dans `fonts/` sous licence libre OFL. Pour en changer, ajoute `fonts/titre.ttf` et/ou `fonts/texte.ttf`.
- **Voix off :** `../audio/voix-off-calee-23s.mp3`, la prise 1 d'ElevenLabs découpée pour que chaque phrase tombe sur son plan.

Pour modifier un texte, une durée ou un zoom, change la liste `PLANS` en haut de `generer_video.py`.

## Les fichiers audio

| Fichier | Contenu |
|---|---|
| `../audio/voix-off-prise-1.mp3`, `-2`, `-3` | Les 3 prises brutes (~17 s), voix « LyLyPodcast » (ElevenLabs) |
| `../audio/voix-off-calee-23s.mp3` | Prise 1, chaque phrase placée sur son plan. C'est celle qu'utilise le script |

Les prises 2 et 3 ne sont pas calées sur les plans. Si tu en préfères une, demande à Claude de la caler de la même façon.

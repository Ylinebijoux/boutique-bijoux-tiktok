# Générer la vidéo « Golden Hour » automatiquement

Ce script monte la vidéo TikTok de 23 s à partir de tes photos. Il reprend les 8 plans, les textes à l'écran et la voix off du script [`../01-golden-hour.md`](../01-golden-hour.md).

## 1. Installer (une seule fois)

Il faut Python 3.9 ou plus récent.

```bash
cd tiktok/video
pip install -r requirements.txt
```

## 2. Mettre les photos

Dépose 8 photos dans `photos/`, nommées dans l'ordre des plans :

| Fichier | Plan | Ce qu'on doit voir |
|---|---|---|
| `01-....jpg` | Hook | Bague Angelica en très gros plan, dans la lumière |
| `02-....jpg` | Superposition | Bagues Angelica et Bedra sur le doigt |
| `03-....jpg` | Matière | Main baguée sur du satin |
| `04-....jpg` | Boucles | Boucle Ayana portée, de profil |
| `05-....jpg` | Collier | Collier Giulia sur la clavicule |
| `06-....jpg` | Bracelet | Bracelet Lunéa au poignet |
| `07-....jpg` | Look complet | Le look entier, face caméra ou dans un miroir |
| `08-....jpg` | CTA | Les 5 pièces posées à plat avec le packaging |

- **Photos verticales** (prises au téléphone) : affichées en plein écran. C'est le meilleur rendu.
- **Photos carrées** (photos produits du site) : posées au centre sur un fond flou de la même photo, pour ne pas couper le bijou.
- **Moins de 8 photos** : elles sont réutilisées dans l'ordre.
- **Haut du cadre** : garde-le dégagé, c'est là que s'affichent les textes.

## 3. Lancer

```bash
python generer_video.py
```

La vidéo sort dans `output/golden-hour.mp4` (1080×1920, 30 i/s, avec la voix off).

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
- **Étalonnage :** chaud et léger, avec un petit vignettage.
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

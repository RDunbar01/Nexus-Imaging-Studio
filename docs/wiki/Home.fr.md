# Nexus Imaging Studio

**Édition navigateur 1.0 · Application Windows 3.2.13**

**[Ouvrir l’essai dans le navigateur](https://rdunbar01.github.io/Nexus-Imaging-Studio/Nexus_Imaging_Studio_Browser_v1.html)** · [Télécharger l’application Windows](https://github.com/RDunbar01/Nexus-Imaging-Studio/tree/main/releases/3.2.13) · [README actuel](https://github.com/RDunbar01/Nexus-Imaging-Studio/blob/main/README.md)

## Outils du navigateur

Choisissez une image locale non compressée ou **Try synthetic image** pour un exemple synthétique. Le navigateur examine les limites et chevauchements des partitions MBR, les CRC et la géométrie de l’en-tête et de la table GPT primaire, ainsi que les signatures ISO 9660. Il calcule SHA-256 dans un worker par blocs de 4 Mio, compare une empreinte fournie et exporte un rapport JSON, un journal et une liste de préparation non exécutable. Aucun fichier n’est envoyé. Python et PyTorch ne sont pas nécessaires.

Le fichier HTML unique contient l’interface, les algorithmes et le worker pour faciliter l’essai en ligne et l’utilisation hors ligne après téléchargement. Il ne donne pas accès aux disques bruts Windows. **Le navigateur ne peut pas flasher, formater, effacer, sauvegarder, réparer ou récupérer des disques physiques.** La capacité est saisie manuellement, non détectée. Les tables GPT sont limitées à 4 Mio. Le GPT de secours, les systèmes de fichiers, les chargeurs de démarrage et les supports physiques ne sont pas validés. Une signature ou une empreinte identique ne prouve ni l’amorçabilité ni l’identité de l’éditeur.

## Application Windows et contribution technique

L’application distincte propose l’écriture et la relecture d’images, la sauvegarde brute, la gestion des partitions et volumes et certains traitements de récupération depuis des images en lecture seule. AEGIS associe réponses déterministes aux erreurs, contrôle de l’identité du disque, protection des disques système, vérification des limites, journaux et indication explicite des vérifications partielles. L’édition navigateur rend accessible la préparation en lecture seule sans installer ces fonctions privilégiées.

Le paquet natif exige **CPython 3.12 64 bits avec Tkinter/Tcl-Tk**, sans PyTorch. Téléchargez tout le répertoire de la version et suivez les [instructions](https://github.com/RDunbar01/Nexus-Imaging-Studio/blob/main/releases/3.2.13/INSTALL.txt). Le mode local `--preview` n’énumère pas les disques physiques. Une écriture peut détruire définitivement des données : sauvegardez sur un autre appareil et vérifiez indépendamment la cible. Les tests synthétiques et navigateur ne qualifient pas Windows, l’UAC, les écritures physiques ou le backend exFAT expérimental. Le paquet natif 3.2.13 reste inchangé.

## Utilisation et crédits

Rich Dunbar / Nexus Emerging Technology, avec assistance au codage par IA. L’usage personnel et les tests et évaluations commerciaux internes sont autorisés pour les éléments appartenant à Nexus. La distribution, la modification, le déploiement en production et les autres usages commerciaux nécessitent un consentement écrit explicite. Les licences tierces et les droits déjà accordés restent inchangés. [Autorisation et portée](https://github.com/RDunbar01/Nexus-Imaging-Studio/blob/main/COMMERCIAL_EVALUATION_PERMISSION.md) · [Licence](https://github.com/RDunbar01/Nexus-Imaging-Studio/blob/main/LICENSE).

[English](https://github.com/RDunbar01/Nexus-Imaging-Studio/wiki/NEXUS-Imaging-Studio-(English)) · [Français](https://github.com/RDunbar01/Nexus-Imaging-Studio/wiki/NEXUS-Imaging-Studio-(French)) · [日本語](https://github.com/RDunbar01/Nexus-Imaging-Studio/wiki/%23-NEXUS-Imaging-Studio-(Japanese)) · [한국어](https://github.com/RDunbar01/Nexus-Imaging-Studio/wiki/NEXUS-Imaging-Studio-(Korean))

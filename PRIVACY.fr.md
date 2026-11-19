# Politique de confidentialité — StreamRemaster

*Dernière mise à jour : 19 novembre 2026*

*[English](PRIVACY.md) · [Español](PRIVACY.es.md) · [Deutsch](PRIVACY.de.md) · [Français](PRIVACY.fr.md) · [Italiano](PRIVACY.it.md) · [Nederlands](PRIVACY.nl.md) · [Polski](PRIVACY.pl.md) · [Português](PRIVACY.pt.md) · [Русский](PRIVACY.ru.md) · [Українська](PRIVACY.uk.md) · [简体中文](PRIVACY.zh-CN.md) · [日本語](PRIVACY.ja.md) · [한국어](PRIVACY.ko.md) · [ไทย](PRIVACY.th.md) · [हिन्दी](PRIVACY.hi.md) · [Català](PRIVACY.ca.md) · [Galego](PRIVACY.gl.md) · [Euskara](PRIVACY.eu.md)*

## 1. Responsable du traitement

L'extension de navigateur StreamRemaster, anciennement dénommée Stream Transcription (l'« Extension »), est publiée sur addons.mozilla.org et sur https://github.com/javimentallab/StreamRemaster par Javier Comyn Pérez, domicilié à calle Olivos, número 36, 28670 Villaviciosa de Odón, Madrid, España (le « Fournisseur »), sous le nom de développeur javimentallab. Le Fournisseur est le responsable du traitement des données à caractère personnel visées dans la présente politique, laquelle est régie par le règlement (UE) 2016/679, règlement général sur la protection des données (le « RGPD »), et par la loi organique espagnole 3/2018 du 5 décembre relative à la protection des données à caractère personnel et à la garantie des droits numériques (Ley Orgánica 3/2018, de 5 de diciembre, de Protección de Datos Personales y garantía de los derechos digitales). L'utilisateur de l'Extension (l'« Utilisateur ») peut contacter le Fournisseur à l'adresse jotacomyn@gmail.com.

## 2. Absence de traitement de données à caractère personnel dans l'Extension

L'Extension ne collecte ni ne traite aucune donnée à caractère personnel de l'Utilisateur pour le compte du Fournisseur. L'Extension ne comporte ni comptes d'utilisateur, ni publicité, ni outils d'analyse, ni systèmes de rapport de plantage, et elle ne communique avec aucun serveur du Fournisseur ; elle ne comporte et ne comportera aucun de ces éléments. Ni les données de l'Utilisateur, ni l'audio, ni les images traités par l'Extension ne parviennent au Fournisseur. Les seules données à caractère personnel que le Fournisseur est susceptible de traiter sont celles que l'Utilisateur lui communique de sa propre initiative lorsqu'il le contacte, conformément à la section 7.

## 3. Fonctionnement de l'Extension

**3.1. Sous-titres avec un serveur de l'Utilisateur.** Lorsque l'Utilisateur active les sous-titres en mode serveur, l'Extension envoie l'audio de l'onglet à l'adresse de serveur que l'Utilisateur a lui-même saisie dans l'Extension, généralement un serveur WhisperLive installé sur l'ordinateur ou sur le réseau local de l'Utilisateur, et en reçoit les sous-titres. Ce serveur est installé et contrôlé par l'Utilisateur, qui est seul responsable de sa configuration et de sa sécurité ; le Fournisseur n'a accès ni à ce serveur ni à l'audio.

**3.2. Sous-titres sur l'ordinateur de l'Utilisateur.** Lorsque l'Utilisateur choisit de transcrire sur l'ordinateur, l'audio est traité dans le navigateur, sur la carte graphique de l'Utilisateur, et ne quitte pas l'ordinateur.

**3.3. Vidéo fluide.** La fonction de vidéo fluide traite les images de la vidéo de la page dans le navigateur, sur la carte graphique de l'Utilisateur. Les images ne quittent pas l'ordinateur et ne sont pas conservées.

## 4. Communications avec des tiers

L'Extension ne se connecte à des sites autres que le serveur de l'Utilisateur que lorsque l'Utilisateur le demande expressément, et uniquement dans les cas suivants :

- **GitHub (api.github.com).** Uniquement lorsque l'Utilisateur clique sur « Rechercher des mises à jour », l'Extension demande à GitHub le numéro de la dernière version publiée. La requête ne contient aucune donnée relative à l'Utilisateur ni à son utilisation de l'Extension.
- **Hugging Face (huggingface.co).** Uniquement lorsque l'Utilisateur télécharge un modèle de transcription pour l'utiliser sur l'ordinateur, l'Extension le télécharge depuis Hugging Face.
- **Adresses saisies par l'Utilisateur.** Lorsque l'Utilisateur ajoute un modèle de vidéo fluide en indiquant son adresse, l'Extension le télécharge depuis cette adresse.

Comme pour toute connexion à Internet, le site auquel l'Extension se connecte reçoit l'adresse IP de l'Utilisateur et l'identification de son navigateur. Chacun de ces sites traite ces données en qualité de responsable du traitement, conformément à sa propre politique de confidentialité, dont le Fournisseur ne répond pas.

## 5. Autorisations

- **Stockage (storage) :** conserver les réglages de l'Extension dans le navigateur.
- **Capture de l'onglet (tabCapture et offscreen), uniquement dans les navigateurs basés sur Chromium :** obtenir l'audio de l'onglet dans lequel l'Utilisateur active les sous-titres, uniquement après que l'Utilisateur a cliqué sur le bouton de l'Extension dans cet onglet.
- **Onglet actif et exécution de scripts (activeTab et scripting), uniquement dans les navigateurs basés sur Chromium :** afficher les sous-titres et appliquer la vidéo fluide dans l'onglet dans lequel l'Utilisateur a cliqué sur le bouton de l'Extension.
- **Accès aux sites web (<all_urls>) :** dans Firefox, lire l'audio et la vidéo de la page pour les sous-titres et la vidéo fluide. Dans les navigateurs basés sur Chromium, il s'agit d'une autorisation facultative, que l'Extension ne demande que si l'Utilisateur coche la case qui active automatiquement la vidéo fluide sur n'importe quel site web.

## 6. Données stockées dans le navigateur

L'Extension conserve dans le stockage du navigateur de l'Utilisateur ses réglages (adresse du serveur, modèle, langues, taille et position des sous-titres et options de la vidéo fluide), les modèles de vidéo fluide que l'Utilisateur ajoute et les modèles de transcription que l'Utilisateur télécharge pour les utiliser sur l'ordinateur. Ces données demeurent dans le navigateur de l'Utilisateur, ne sont pas envoyées au Fournisseur et sont supprimées lors de la désinstallation de l'Extension ; les modèles peuvent également être supprimés depuis les réglages de l'Extension. Si l'Utilisateur active l'option d'enregistrement des sous-titres, un fichier `.srt` est téléchargé sur l'ordinateur de l'Utilisateur lorsque les sous-titres sont arrêtés, et reste à la disposition de l'Utilisateur.

## 7. Données issues des communications de l'Utilisateur

Lorsque l'Utilisateur contacte le Fournisseur par courrier électronique, le Fournisseur traite l'adresse électronique de l'Utilisateur, son nom, s'il le communique, et le contenu du message. Lorsque l'Utilisateur ouvre un ticket sur GitHub, ce ticket est public et soumis aux conditions et à la politique de confidentialité de GitHub.

Conformément à l'article 13 du RGPD, les informations suivantes sont fournies :

- **Finalité :** traiter la question, le ticket ou la demande de l'Utilisateur.
- **Base juridique :** le consentement de l'Utilisateur, exprimé en contactant le Fournisseur (article 6, paragraphe 1, point a), du RGPD), et, lorsque les droits visés à la section 8 sont exercés, le respect d'une obligation légale à laquelle le Fournisseur est soumis (article 6, paragraphe 1, point c), du RGPD).
- **Durée de conservation :** le temps nécessaire au traitement de la communication puis le délai de prescription des actions susceptibles d'en découler. À l'issue de ce délai, les données sont supprimées.
- **Destinataires :** les données ne sont pas communiquées à des tiers, sauf obligation légale. La messagerie électronique du Fournisseur est fournie par Google, en qualité de prestataire de services.

## 8. Droits de l'Utilisateur

L'Utilisateur peut exercer les droits d'accès, de rectification, d'effacement, de limitation du traitement, d'opposition et de portabilité, prévus aux articles 15 à 22 du RGPD, et retirer son consentement à tout moment, sans que cela compromette la licéité du traitement effectué avant ce retrait, en contactant le Fournisseur à l'adresse jotacomyn@gmail.com. L'Utilisateur peut également introduire une réclamation auprès de l'Agencia Española de Protección de Datos (Agence espagnole de protection des données, www.aepd.es).

## 9. Modifications

Le Fournisseur peut modifier la présente politique ; la date de la dernière mise à jour figure en tête du présent document.

## 10. Contact

Toute question relative à la présente politique peut être adressée au Fournisseur à l'adresse jotacomyn@gmail.com ou en ouvrant un ticket sur https://github.com/javimentallab/StreamRemaster/issues.

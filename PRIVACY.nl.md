# Privacybeleid — StreamRemaster

*Laatst bijgewerkt: 19 november 2026*

*[English](PRIVACY.md) · [Español](PRIVACY.es.md) · [Deutsch](PRIVACY.de.md) · [Français](PRIVACY.fr.md) · [Italiano](PRIVACY.it.md) · [Nederlands](PRIVACY.nl.md) · [Polski](PRIVACY.pl.md) · [Português](PRIVACY.pt.md) · [Русский](PRIVACY.ru.md) · [Українська](PRIVACY.uk.md) · [简体中文](PRIVACY.zh-CN.md) · [日本語](PRIVACY.ja.md) · [한국어](PRIVACY.ko.md) · [ไทย](PRIVACY.th.md) · [हिन्दी](PRIVACY.hi.md) · [Català](PRIVACY.ca.md) · [Galego](PRIVACY.gl.md) · [Euskara](PRIVACY.eu.md)*

## 1. Verwerkingsverantwoordelijke

De browserextensie StreamRemaster, voorheen Stream Transcription genaamd (de “Extensie”), wordt op addons.mozilla.org en op https://github.com/javimentallab/StreamRemaster gepubliceerd door Javier Comyn Pérez, met adres te calle Olivos, número 36, 28670 Villaviciosa de Odón, Madrid, España (de “Aanbieder”), onder de ontwikkelaarsnaam javimentallab. De Aanbieder is de verwerkingsverantwoordelijke voor de in dit privacybeleid bedoelde persoonsgegevens; dit privacybeleid wordt beheerst door Verordening (EU) 2016/679, de algemene verordening gegevensbescherming (de “AVG”), en door de Spaanse organieke wet 3/2018 van 5 december inzake de bescherming van persoonsgegevens en de waarborging van digitale rechten (Ley Orgánica 3/2018, de 5 de diciembre, de Protección de Datos Personales y garantía de los derechos digitales). De gebruiker van de Extensie (de “Gebruiker”) kan contact opnemen met de Aanbieder via jotacomyn@gmail.com.

## 2. Geen verwerking van persoonsgegevens in de Extensie

De Extensie verzamelt noch verwerkt persoonsgegevens van de Gebruiker namens de Aanbieder. De Extensie heeft geen gebruikersaccounts, advertenties, analysetools of systemen voor crashrapportage en communiceert met geen enkele server van de Aanbieder; zij bevat geen van deze elementen en zal er ook in de toekomst geen bevatten. Noch gegevens van de Gebruiker, noch de audio of de beelden die de Extensie verwerkt, bereiken de Aanbieder. De enige persoonsgegevens die de Aanbieder kan verwerken, zijn die welke de Gebruiker uit eigen beweging verstrekt wanneer hij contact opneemt met de Aanbieder, zoals uiteengezet in paragraaf 7.

## 3. Werking van de Extensie

**3.1. Ondertitels met een server van de Gebruiker.** Wanneer de Gebruiker de ondertitels in de servermodus inschakelt, verzendt de Extensie de audio van het tabblad naar het serveradres dat de Gebruiker zelf in de Extensie heeft ingevoerd, doorgaans een WhisperLive-server die op de computer of in het lokale netwerk van de Gebruiker is geïnstalleerd, en ontvangt zij daarvan de ondertitels. Die server wordt geïnstalleerd en beheerd door de Gebruiker, die als enige verantwoordelijk is voor de configuratie en de beveiliging ervan; de Aanbieder heeft geen toegang tot de server of tot de audio.

**3.2. Ondertitels op de computer van de Gebruiker.** Wanneer de Gebruiker ervoor kiest op de computer te transcriberen, wordt de audio in de browser verwerkt, op de videokaart van de Gebruiker, en verlaat deze de computer niet.

**3.3. Vloeiende video.** De functie voor vloeiende video verwerkt de beelden van de video op de pagina in de browser, op de videokaart van de Gebruiker. De beelden verlaten de computer niet en worden niet opgeslagen.

## 4. Communicatie met derden

De Extensie maakt alleen verbinding met andere sites dan de server van de Gebruiker wanneer de Gebruiker daar uitdrukkelijk om verzoekt, en uitsluitend in de volgende gevallen:

- **GitHub (api.github.com).** Alleen wanneer de Gebruiker op “Controleren op updates” klikt, vraagt de Extensie bij GitHub het nummer van de laatst gepubliceerde versie op. Het verzoek bevat geen gegevens over de Gebruiker of over diens gebruik van de Extensie.
- **Hugging Face (huggingface.co).** Alleen wanneer de Gebruiker een transcriptiemodel downloadt om het op de computer te gebruiken, downloadt de Extensie het van Hugging Face.
- **Door de Gebruiker ingevoerde adressen.** Wanneer de Gebruiker een model voor vloeiende video toevoegt door het adres ervan op te geven, downloadt de Extensie het van dat adres.

Zoals bij elke verbinding via internet ontvangt de site waarmee de Extensie verbinding maakt het IP-adres van de Gebruiker en de identificatie van diens browser. Elk van die sites verwerkt die gegevens als verwerkingsverantwoordelijke, overeenkomstig zijn eigen privacybeleid, waarvoor de Aanbieder niet aansprakelijk is.

## 5. Machtigingen

- **Opslag (storage):** het bewaren van de instellingen van de Extensie in de browser.
- **Vastleggen van het tabblad (tabCapture en offscreen), alleen in browsers op basis van Chromium:** het verkrijgen van de audio van het tabblad waarin de Gebruiker de ondertitels inschakelt, uitsluitend nadat de Gebruiker in dat tabblad op de knop van de Extensie heeft geklikt.
- **Actief tabblad en uitvoering van scripts (activeTab en scripting), alleen in browsers op basis van Chromium:** het tonen van de ondertitels en het toepassen van de vloeiende video in het tabblad waarin de Gebruiker op de knop van de Extensie heeft geklikt.
- **Toegang tot websites (<all_urls>):** in Firefox, het lezen van de audio en de video van de pagina voor de ondertitels en de vloeiende video. In browsers op basis van Chromium is dit een optionele machtiging, die de Extensie alleen aanvraagt als de Gebruiker het vakje aanvinkt waarmee de vloeiende video automatisch op elke website wordt ingeschakeld.

## 6. In de browser opgeslagen gegevens

De Extensie bewaart in de browseropslag van de Gebruiker haar instellingen (serveradres, model, talen, grootte en positie van de ondertitels en opties voor de vloeiende video), de modellen voor vloeiende video die de Gebruiker toevoegt en de transcriptiemodellen die de Gebruiker downloadt om ze op de computer te gebruiken. Deze gegevens blijven in de browser van de Gebruiker, worden niet naar de Aanbieder verzonden en worden gewist wanneer de Extensie wordt verwijderd; de modellen kunnen ook via de instellingen van de Extensie worden gewist. Indien de Gebruiker de optie om de ondertitels op te slaan inschakelt, wordt bij het stoppen ervan een `.srt`-bestand naar de computer van de Gebruiker gedownload, dat ter beschikking van de Gebruiker blijft.

## 7. Gegevens uit de communicatie van de Gebruiker

Wanneer de Gebruiker per e-mail contact opneemt met de Aanbieder, verwerkt de Aanbieder het e-mailadres van de Gebruiker, diens naam, indien opgegeven, en de inhoud van het bericht. Wanneer de Gebruiker een issue op GitHub opent, is dat issue openbaar en valt het onder de voorwaarden en het privacybeleid van GitHub.

Overeenkomstig artikel 13 van de AVG wordt de volgende informatie verstrekt:

- **Doel:** het behandelen van de vraag, het issue of het verzoek van de Gebruiker.
- **Rechtsgrond:** de toestemming van de Gebruiker, gegeven door contact op te nemen met de Aanbieder (artikel 6, lid 1, punt a), van de AVG), en, wanneer de rechten uit paragraaf 8 worden uitgeoefend, het voldoen aan een wettelijke verplichting van de Aanbieder (artikel 6, lid 1, punt c), van de AVG).
- **Bewaartermijn:** de tijd die nodig is om de communicatie te behandelen en vervolgens de verjaringstermijn van eventuele vorderingen die daaruit kunnen voortvloeien. Na afloop van die termijn worden de gegevens gewist.
- **Ontvangers:** de gegevens worden niet aan derden verstrekt, behalve indien de wet dit vereist. De e-maildienst van de Aanbieder wordt geleverd door Google, als dienstverlener.

## 8. Rechten van de Gebruiker

De Gebruiker kan de rechten op inzage, rectificatie, wissing, beperking van de verwerking, bezwaar en overdraagbaarheid uitoefenen, op grond van de artikelen 15 tot en met 22 van de AVG, en kan zijn toestemming te allen tijde intrekken, zonder dat dit afbreuk doet aan de rechtmatigheid van de verwerking vóór de intrekking daarvan, door contact op te nemen met de Aanbieder via jotacomyn@gmail.com. De Gebruiker kan ook een klacht indienen bij de Agencia Española de Protección de Datos (Spaanse gegevensbeschermingsautoriteit, www.aepd.es).

## 9. Wijzigingen

De Aanbieder kan dit privacybeleid wijzigen; de datum van de laatste bijwerking wordt bovenaan dit document vermeld.

## 10. Contact

Vragen over dit privacybeleid kunnen aan de Aanbieder worden gericht via jotacomyn@gmail.com of door een issue te openen op https://github.com/javimentallab/StreamRemaster/issues.

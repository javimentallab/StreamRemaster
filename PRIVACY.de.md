# Datenschutzerklärung — StreamRemaster

*Letzte Aktualisierung: 19. November 2026*

*[English](PRIVACY.md) · [Español](PRIVACY.es.md) · [Deutsch](PRIVACY.de.md) · [Français](PRIVACY.fr.md) · [Italiano](PRIVACY.it.md) · [Nederlands](PRIVACY.nl.md) · [Polski](PRIVACY.pl.md) · [Português](PRIVACY.pt.md) · [Русский](PRIVACY.ru.md) · [Українська](PRIVACY.uk.md) · [简体中文](PRIVACY.zh-CN.md) · [日本語](PRIVACY.ja.md) · [한국어](PRIVACY.ko.md) · [ไทย](PRIVACY.th.md) · [हिन्दी](PRIVACY.hi.md) · [Català](PRIVACY.ca.md) · [Galego](PRIVACY.gl.md) · [Euskara](PRIVACY.eu.md)*

## 1. Verantwortlicher

Die Browsererweiterung StreamRemaster, früher Stream Transcription genannt (die „Erweiterung“), wird auf addons.mozilla.org und unter https://github.com/javimentallab/StreamRemaster von Javier Comyn Pérez, mit Anschrift calle Olivos, número 36, 28670 Villaviciosa de Odón, Madrid, España (der „Anbieter“), unter dem Entwicklernamen javimentallab veröffentlicht. Der Anbieter ist der Verantwortliche für die in dieser Datenschutzerklärung genannten personenbezogenen Daten; diese Datenschutzerklärung unterliegt der Verordnung (EU) 2016/679, der Datenschutz-Grundverordnung (die „DSGVO“), sowie dem spanischen Organgesetz 3/2018 vom 5. Dezember über den Schutz personenbezogener Daten und die Gewährleistung digitaler Rechte (Ley Orgánica 3/2018, de 5 de diciembre, de Protección de Datos Personales y garantía de los derechos digitales). Der Nutzer der Erweiterung (der „Nutzer“) kann den Anbieter unter jotacomyn@gmail.com kontaktieren.

## 2. Keine Verarbeitung personenbezogener Daten in der Erweiterung

Die Erweiterung erhebt und verarbeitet keine personenbezogenen Daten des Nutzers im Auftrag des Anbieters. Die Erweiterung verfügt weder über Nutzerkonten noch über Werbung, Analysewerkzeuge oder Systeme zur Absturzberichterstattung und kommuniziert mit keinem Server des Anbieters; sie enthält keines dieser Elemente und wird auch künftig keines davon enthalten. Weder Daten des Nutzers noch das Audio oder die Bilder, die die Erweiterung verarbeitet, gelangen zum Anbieter. Die einzigen personenbezogenen Daten, die der Anbieter verarbeiten kann, sind diejenigen, die der Nutzer ihm aus eigener Initiative bei einer Kontaktaufnahme mitteilt, wie in Abschnitt 7 dargelegt.

## 3. Funktionsweise der Erweiterung

**3.1. Untertitel mit einem Server des Nutzers.** Aktiviert der Nutzer die Untertitel im Servermodus, sendet die Erweiterung das Audio des Tabs an die Serveradresse, die der Nutzer selbst in der Erweiterung eingegeben hat, in der Regel ein WhisperLive-Server, der auf dem Computer oder im lokalen Netzwerk des Nutzers installiert ist, und empfängt von diesem die Untertitel. Dieser Server wird vom Nutzer installiert und kontrolliert, der allein für dessen Konfiguration und Sicherheit verantwortlich ist; der Anbieter hat weder auf den Server noch auf das Audio Zugriff.

**3.2. Untertitel auf dem Computer des Nutzers.** Entscheidet sich der Nutzer für die Transkription auf dem Computer, wird das Audio im Browser auf der Grafikkarte des Nutzers verarbeitet und verlässt den Computer nicht.

**3.3. Flüssiges Video.** Die Funktion für flüssiges Video verarbeitet die Bilder des Videos auf der Seite im Browser auf der Grafikkarte des Nutzers. Die Bilder verlassen den Computer nicht und werden nicht gespeichert.

## 4. Kommunikation mit Dritten

Die Erweiterung verbindet sich mit anderen Websites als dem Server des Nutzers nur, wenn der Nutzer dies ausdrücklich verlangt, und ausschließlich in den folgenden Fällen:

- **GitHub (api.github.com).** Nur wenn der Nutzer auf „Nach Updates suchen“ klickt, fragt die Erweiterung bei GitHub die Nummer der neuesten veröffentlichten Version ab. Die Anfrage enthält keine Daten über den Nutzer oder dessen Nutzung der Erweiterung.
- **Hugging Face (huggingface.co).** Nur wenn der Nutzer ein Transkriptionsmodell herunterlädt, um es auf dem Computer zu verwenden, lädt die Erweiterung es von Hugging Face herunter.
- **Vom Nutzer eingegebene Adressen.** Fügt der Nutzer ein Modell für flüssiges Video unter Angabe seiner Adresse hinzu, lädt die Erweiterung es von dieser Adresse herunter.

Wie bei jeder Verbindung über das Internet erhält die Website, mit der sich die Erweiterung verbindet, die IP-Adresse des Nutzers und die Kennung seines Browsers. Jede dieser Websites verarbeitet diese Daten als Verantwortlicher nach ihrer eigenen Datenschutzerklärung, für die der Anbieter nicht haftet.

## 5. Berechtigungen

- **Speicher (storage):** um die Einstellungen der Erweiterung im Browser zu speichern.
- **Tab-Erfassung (tabCapture und offscreen), nur in Chromium-basierten Browsern:** um das Audio des Tabs zu erhalten, in dem der Nutzer die Untertitel aktiviert, und zwar erst, nachdem der Nutzer in diesem Tab auf die Schaltfläche der Erweiterung geklickt hat.
- **Aktiver Tab und Ausführung von Skripten (activeTab und scripting), nur in Chromium-basierten Browsern:** um die Untertitel anzuzeigen und das flüssige Video in dem Tab anzuwenden, in dem der Nutzer auf die Schaltfläche der Erweiterung geklickt hat.
- **Zugriff auf Websites (<all_urls>):** in Firefox, um das Audio und das Video der Seite für die Untertitel und das flüssige Video auszulesen. In Chromium-basierten Browsern handelt es sich um eine optionale Berechtigung, die die Erweiterung nur anfordert, wenn der Nutzer das Kästchen aktiviert, mit dem das flüssige Video auf jeder Website automatisch eingeschaltet wird.

## 6. Im Browser gespeicherte Daten

Die Erweiterung speichert im Browserspeicher des Nutzers ihre Einstellungen (Serveradresse, Modell, Sprachen, Größe und Position der Untertitel sowie Optionen für das flüssige Video), die vom Nutzer hinzugefügten Modelle für flüssiges Video und die Transkriptionsmodelle, die der Nutzer herunterlädt, um sie auf dem Computer zu verwenden. Diese Daten verbleiben im Browser des Nutzers, werden nicht an den Anbieter übermittelt und bei der Deinstallation der Erweiterung gelöscht; die Modelle können auch in den Einstellungen der Erweiterung gelöscht werden. Aktiviert der Nutzer die Option zum Speichern der Untertitel, wird beim Beenden der Untertitel eine `.srt`-Datei auf den Computer des Nutzers heruntergeladen, die dem Nutzer zur Verfügung steht.

## 7. Daten aus der Kommunikation des Nutzers

Wendet sich der Nutzer per E-Mail an den Anbieter, verarbeitet der Anbieter die E-Mail-Adresse des Nutzers, seinen Namen, sofern er ihn angibt, und den Inhalt der Nachricht. Eröffnet der Nutzer ein Issue auf GitHub, ist dieses öffentlich und unterliegt den Bedingungen und der Datenschutzerklärung von GitHub.

Gemäß Art. 13 DSGVO werden folgende Informationen bereitgestellt:

- **Zweck:** Bearbeitung der Anfrage, des Issues oder des Anliegens des Nutzers.
- **Rechtsgrundlage:** die Einwilligung des Nutzers, die er durch die Kontaktaufnahme mit dem Anbieter erteilt (Art. 6 Abs. 1 lit. a DSGVO), sowie, wenn die Rechte nach Abschnitt 8 ausgeübt werden, die Erfüllung einer rechtlichen Verpflichtung des Anbieters (Art. 6 Abs. 1 lit. c DSGVO).
- **Speicherdauer:** die für die Bearbeitung der Kommunikation erforderliche Zeit und anschließend die Verjährungsfrist etwaiger sich daraus ergebender Ansprüche. Nach Ablauf dieser Frist werden die Daten gelöscht.
- **Empfänger:** Die Daten werden nicht an Dritte weitergegeben, sofern dies nicht gesetzlich vorgeschrieben ist. Der E-Mail-Dienst des Anbieters wird von Google als Dienstleister bereitgestellt.

## 8. Rechte des Nutzers

Der Nutzer kann die Rechte auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Widerspruch und Datenübertragbarkeit gemäß Art. 15 bis 22 DSGVO ausüben und seine Einwilligung jederzeit widerrufen, ohne dass die Rechtmäßigkeit der bis zum Widerruf erfolgten Verarbeitung berührt wird, indem er sich unter jotacomyn@gmail.com an den Anbieter wendet. Der Nutzer kann außerdem eine Beschwerde bei der Agencia Española de Protección de Datos (spanische Datenschutzbehörde, www.aepd.es) einreichen.

## 9. Änderungen

Der Anbieter kann diese Datenschutzerklärung ändern; das Datum der letzten Aktualisierung ist am Anfang dieses Dokuments angegeben.

## 10. Kontakt

Anfragen zu dieser Datenschutzerklärung können unter jotacomyn@gmail.com an den Anbieter gerichtet oder durch Eröffnen eines Issues unter https://github.com/javimentallab/StreamRemaster/issues gestellt werden.

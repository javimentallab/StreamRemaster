# Privacy policy — StreamRemaster

*Last updated: 19 November 2026*

*[English](PRIVACY.md) · [Español](PRIVACY.es.md) · [Deutsch](PRIVACY.de.md) · [Français](PRIVACY.fr.md) · [Italiano](PRIVACY.it.md) · [Nederlands](PRIVACY.nl.md) · [Polski](PRIVACY.pl.md) · [Português](PRIVACY.pt.md) · [Русский](PRIVACY.ru.md) · [Українська](PRIVACY.uk.md) · [简体中文](PRIVACY.zh-CN.md) · [日本語](PRIVACY.ja.md) · [한국어](PRIVACY.ko.md) · [ไทย](PRIVACY.th.md) · [हिन्दी](PRIVACY.hi.md) · [Català](PRIVACY.ca.md) · [Galego](PRIVACY.gl.md) · [Euskara](PRIVACY.eu.md)*

## 1. Data controller

The StreamRemaster browser extension, formerly called Stream Transcription (the "Extension"), is published on addons.mozilla.org and at https://github.com/javimentallab/StreamRemaster by Javier Comyn Pérez, with address at calle Olivos, número 36, 28670 Villaviciosa de Odón, Madrid, España (the "Provider"), under the developer name javimentallab. The Provider is the controller of the personal data referred to in this policy, which is governed by Regulation (EU) 2016/679, the General Data Protection Regulation (the "GDPR"), and by Spanish Organic Law 3/2018 of 5 December on the Protection of Personal Data and the Guarantee of Digital Rights. The user of the Extension (the "User") may contact the Provider at jotacomyn@gmail.com.

## 2. No processing of personal data in the Extension

The Extension does not collect or process any personal data of the User on behalf of the Provider. The Extension has no user accounts, advertising, analytics tools or crash reporting systems, and it does not communicate with any server of the Provider; it does not and will not include any of these. No data of the User, and none of the audio or images processed by the Extension, reach the Provider. The only personal data the Provider may process are those the User provides of his or her own accord when contacting the Provider, as set out in section 7.

## 3. How the Extension works

**3.1. Subtitles with a server of the User.** When the User turns on the subtitles in server mode, the Extension sends the audio of the tab to the server address that the User has entered in the Extension, usually a WhisperLive server installed on the User's computer or local network, and receives the subtitles from it. That server is installed and controlled by the User, who is solely responsible for its configuration and security; the Provider has no access to it or to the audio.

**3.2. Subtitles on the User's computer.** When the User chooses to transcribe on the computer, the audio is processed in the browser, on the User's graphics card, and does not leave the computer.

**3.3. Smooth video.** The smooth video feature processes the images of the video on the page in the browser, on the User's graphics card. The images do not leave the computer and are not stored.

## 4. Communications with third parties

The Extension connects to sites other than the User's server only when the User expressly asks for it, and only in the following cases:

- **GitHub (api.github.com).** Only when the User presses "Check for updates", the Extension asks GitHub for the number of the latest release. The request contains no data about the User or the User's use of the Extension.
- **Hugging Face (huggingface.co).** Only when the User downloads a transcription model to use it on the computer, the Extension downloads it from Hugging Face.
- **Addresses entered by the User.** When the User adds a smooth video model by giving its address, the Extension downloads it from that address.

As with any connection over the Internet, the site the Extension connects to receives the User's IP address and the identification of the User's browser. Each of those sites processes those data as controller, under its own privacy policy, for which the Provider is not liable.

## 5. Permissions

- **Storage (storage):** to keep the Extension's settings in the browser.
- **Tab capture (tabCapture and offscreen), only in Chromium-based browsers:** to obtain the audio of the tab in which the User turns on the subtitles, only after the User presses the Extension's button on that tab.
- **Active tab and script execution (activeTab and scripting), only in Chromium-based browsers:** to show the subtitles and apply the smooth video on the tab in which the User has pressed the Extension's button.
- **Access to websites (<all_urls>):** in Firefox, to read the audio and video of the page for the subtitles and the smooth video. In Chromium-based browsers it is an optional permission, which the Extension only requests if the User ticks the box that turns on the smooth video automatically on any website.

## 6. Data stored in the browser

The Extension keeps in the User's browser storage its settings (server address, model, languages, size and position of the subtitles, and smooth video options), the smooth video models the User adds and the transcription models the User downloads to use them on the computer. These data remain in the User's browser, are not sent to the Provider and are deleted when the Extension is uninstalled; the models can also be deleted from the Extension's settings. If the User turns on the option to save the subtitles, an `.srt` file is downloaded to the User's computer when they are stopped, and remains at the User's disposal.

## 7. Data from the User's communications

When the User contacts the Provider by email, the Provider processes the User's email address, name, if given, and the content of the message. When the User opens an issue on GitHub, the issue is public and subject to GitHub's terms and privacy policy.

As required by Article 13 of the GDPR, the following information is provided:

- **Purpose:** to deal with the User's enquiry, issue or request.
- **Legal basis:** the User's consent, given by contacting the Provider (Article 6(1)(a) of the GDPR), and, when the rights under section 8 are exercised, compliance with a legal obligation of the Provider (Article 6(1)(c) of the GDPR).
- **Retention period:** the time needed to deal with the communication and, afterwards, the limitation period of any claims that may arise from it. After that period, the data are deleted.
- **Recipients:** the data are not disclosed to third parties, except where required by law. The Provider's email is provided by Google, acting as service provider.

## 8. Rights of the User

The User may exercise the rights of access, rectification, erasure, restriction of processing, objection and portability, under Articles 15 to 22 of the GDPR, and may withdraw consent at any time, without affecting the lawfulness of processing carried out before its withdrawal, by contacting the Provider at jotacomyn@gmail.com. The User may also lodge a complaint with the Spanish Data Protection Agency (www.aepd.es).

## 9. Amendments

The Provider may amend this policy; the date of the latest update will appear at the top of this document.

## 10. Contact

Enquiries about this policy may be addressed to the Provider at jotacomyn@gmail.com or by opening an issue at https://github.com/javimentallab/StreamRemaster/issues.

# Privacy policy — StreamRemaster

*Last updated: <DATE>*

*Versión en español: [PRIVACY.es.md](PRIVACY.es.md)*

## 1. Data controller

The StreamRemaster browser extension, formerly called Stream Transcription (the "Extension"), is published on addons.mozilla.org and at https://github.com/javimentallab/StreamRemaster by <NOMBRE>, with address at <DIRECCIÓN> (the "Provider"), under the developer name javimentallab. The Provider is the controller of the personal data referred to in this policy, and the User may contact the Provider at <CORREO>.

## 2. No processing of personal data by the Provider

The Provider does not collect or process any personal data of the User. The Extension has no user accounts, advertising, analytics tools or crash reporting systems, and it does not communicate with any server of the Provider. No data of the User, and none of the audio or images processed by the Extension, reach the Provider.

## 3. How the Extension works

**3.1. Subtitles with a server of the User.** When the User turns on the subtitles in server mode, the Extension sends the audio of the tab to the server address that the User has typed into the Extension, usually a WhisperLive server installed on the User's computer or local network, and receives the subtitles from it. That server is installed and controlled by the User; the Provider has no access to it or to the audio.

**3.2. Subtitles on the User's computer.** When the User chooses to transcribe on the computer, the audio is processed in the browser, on the User's graphics card, and does not leave the computer.

**3.3. Smooth video.** The smooth video feature processes the images of the video on the page in the browser, on the User's graphics card. The images do not leave the computer and are not stored.

## 4. Communications with third parties

The Extension connects to sites other than the User's server only when the User expressly asks for it, and in the following cases:

- **GitHub (api.github.com).** Only when the User presses "Check for updates", the Extension asks GitHub for the number of the latest release. The request carries no data about the User or the User's use of the Extension.
- **Hugging Face (huggingface.co).** Only when the User downloads a transcription model to use it on the computer, the Extension downloads it from Hugging Face.
- **Addresses typed by the User.** When the User adds a smooth video model by giving its address, the Extension downloads it from that address.

As with any connection over the Internet, the site the Extension connects to receives the User's IP address and the name of the User's browser. Each of those sites processes those data under its own privacy policy, for which the Provider is not responsible.

## 5. Permissions

- **Storage (storage):** to keep the Extension's settings in the browser.
- **Tab capture (tabCapture, offscreen), only in Chromium-based browsers:** to obtain the audio of the tab in which the User turns on the subtitles, only after the User presses the Extension's button on that tab.
- **Access to websites (<all_urls>):** in Firefox, to read the audio and video of the page for the subtitles and the smooth video. In Chromium-based browsers it is an optional permission, which the Extension only requests if the User ticks the box that turns on the smooth video automatically on any website.

## 6. Data stored in the browser

The Extension keeps in the User's browser storage its settings (server address, model, languages, size and position of the subtitles, and smooth video options), the smooth video models the User adds and the transcription models the User downloads to use them on the computer. These data stay in the User's browser, are not sent to the Provider and are deleted when the Extension is uninstalled; the models can also be deleted from the Extension's settings. If the User turns on the option to save the subtitles, an `.srt` file is downloaded to the User's computer when they are stopped.

## 7. Rights of the User

As the Provider does not process personal data of the User, the Provider holds no data in respect of which the rights of access, rectification, erasure, restriction of processing, objection and portability under articles 15 to 22 of the General Data Protection Regulation could be exercised. Nevertheless, the User may contact the Provider at <CORREO> about any matter relating to them, and may lodge a complaint with the Spanish Data Protection Agency (www.aepd.es).

## 8. Amendments

The Provider may amend this policy; the date of the latest update will appear at the top of this document.

## 9. Contact

Questions about this policy may be addressed to the Provider at <CORREO> or by opening an issue at https://github.com/javimentallab/StreamRemaster/issues.

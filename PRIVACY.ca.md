# Política de privadesa — StreamRemaster

*Última actualització: 19 de novembre de 2026*

*[English](PRIVACY.md) · [Español](PRIVACY.es.md) · [Deutsch](PRIVACY.de.md) · [Français](PRIVACY.fr.md) · [Italiano](PRIVACY.it.md) · [Nederlands](PRIVACY.nl.md) · [Polski](PRIVACY.pl.md) · [Português](PRIVACY.pt.md) · [Русский](PRIVACY.ru.md) · [Українська](PRIVACY.uk.md) · [简体中文](PRIVACY.zh-CN.md) · [日本語](PRIVACY.ja.md) · [한국어](PRIVACY.ko.md) · [ไทย](PRIVACY.th.md) · [हिन्दी](PRIVACY.hi.md) · [Català](PRIVACY.ca.md) · [Galego](PRIVACY.gl.md) · [Euskara](PRIVACY.eu.md)*

## 1. Responsable del tractament

L'extensió de navegador StreamRemaster, anteriorment denominada Stream Transcription (d'ara endavant, l'«Extensió»), és publicada a addons.mozilla.org i a https://github.com/javimentallab/StreamRemaster per Javier Comyn Pérez, amb domicili a calle Olivos, número 36, 28670 Villaviciosa de Odón, Madrid, España (d'ara endavant, el «Titular»), amb el nom de desenvolupador javimentallab. El Titular és el responsable del tractament de les dades personals a què es refereix aquesta política, que es regeix pel Reglament (UE) 2016/679, general de protecció de dades (d'ara endavant, l'«RGPD»), i per la Llei orgànica 3/2018, de 5 de desembre, de protecció de dades personals i garantia dels drets digitals. L'usuari de l'Extensió (d'ara endavant, l'«Usuari») pot adreçar-se al Titular a jotacomyn@gmail.com.

## 2. Absència de tractament de dades personals a l'Extensió

L'Extensió no recull ni tracta dades personals de l'Usuari per compte del Titular. L'Extensió no disposa de comptes d'usuari, publicitat, eines d'analítica ni sistemes d'informe d'errors, i no es comunica amb cap servidor del Titular; no incorpora ni incorporarà cap d'aquests elements. Cap dada de l'Usuari, ni l'àudio ni les imatges que processa l'Extensió, no arriba al Titular. Les úniques dades personals que pot arribar a tractar el Titular són les que l'Usuari li faciliti per iniciativa pròpia en adreçar-s'hi, d'acord amb la clàusula 7.

## 3. Funcionament de l'Extensió

**3.1. Subtítols amb un servidor de l'Usuari.** Quan l'Usuari activa els subtítols en el mode de servidor, l'Extensió envia l'àudio de la pestanya a l'adreça de servidor que el mateix Usuari ha introduït a l'Extensió, normalment un servidor WhisperLive instal·lat al seu ordinador o a la seva xarxa local, i en rep els subtítols. Aquest servidor l'instal·la i el controla l'Usuari, que és l'únic responsable de la seva configuració i de la seva seguretat; el Titular no té accés ni al servidor ni a l'àudio.

**3.2. Subtítols a l'ordinador de l'Usuari.** Quan l'Usuari tria transcriure al seu ordinador, l'àudio es processa al navegador, mitjançant la targeta gràfica de l'Usuari, i no surt de l'ordinador.

**3.3. Vídeo fluid.** La funció de vídeo fluid processa les imatges del vídeo de la pàgina al navegador, mitjançant la targeta gràfica de l'Usuari. Les imatges no surten de l'ordinador ni s'emmagatzemen.

## 4. Comunicacions amb tercers

L'Extensió només es connecta amb llocs diferents del servidor de l'Usuari quan aquest ho sol·licita de manera expressa, i únicament en els supòsits següents:

- **GitHub (api.github.com).** Només quan l'Usuari prem «Cerca actualitzacions», l'Extensió consulta a GitHub el número de la darrera versió publicada. La consulta no conté dades de l'Usuari ni de l'ús que fa de l'Extensió.
- **Hugging Face (huggingface.co).** Només quan l'Usuari descarrega un model de transcripció per utilitzar-lo al seu ordinador, l'Extensió el descarrega de Hugging Face.
- **Adreces introduïdes per l'Usuari.** Quan l'Usuari afegeix un model de vídeo fluid indicant-ne l'adreça, l'Extensió el descarrega d'aquesta adreça.

Com en tota connexió a Internet, el lloc amb què es connecta l'Extensió rep l'adreça IP de l'Usuari i la identificació del seu navegador. Cadascun d'aquests llocs tracta aquestes dades com a responsable, d'acord amb la seva pròpia política de privadesa, de la qual el Titular no respon.

## 5. Permisos

- **Emmagatzematge (storage):** conservar la configuració de l'Extensió al navegador.
- **Captura de la pestanya (tabCapture i offscreen), només als navegadors basats en Chromium:** obtenir l'àudio de la pestanya en què l'Usuari activa els subtítols, únicament després que premi el botó de l'Extensió en aquesta pestanya.
- **Pestanya activa i execució de scripts (activeTab i scripting), només als navegadors basats en Chromium:** mostrar els subtítols i aplicar el vídeo fluid a la pestanya en què l'Usuari ha premut el botó de l'Extensió.
- **Accés als llocs web (<all_urls>):** al Firefox, llegir l'àudio i el vídeo de la pàgina per als subtítols i el vídeo fluid. Als navegadors basats en Chromium és un permís opcional, que l'Extensió només sol·licita si l'Usuari marca la casella que activa el vídeo fluid de manera automàtica a qualsevol lloc web.

## 6. Dades emmagatzemades al navegador

L'Extensió conserva a l'emmagatzematge del navegador de l'Usuari la seva configuració (adreça del servidor, model, idiomes, mida i posició dels subtítols i opcions del vídeo fluid), els models de vídeo fluid que l'Usuari afegeixi i els models de transcripció que descarregui per utilitzar-los al seu ordinador. Aquestes dades romanen al navegador de l'Usuari, no s'envien al Titular i se suprimeixen en desinstal·lar l'Extensió; els models també es poden suprimir des de la configuració de l'Extensió. Si l'Usuari activa l'opció de desar els subtítols, en aturar-los es descarrega un fitxer `.srt` al seu ordinador, del qual disposa l'Usuari.

## 7. Dades de les comunicacions de l'Usuari

Quan l'Usuari s'adreça al Titular per correu electrònic, el Titular tracta la seva adreça de correu, el seu nom, si el facilita, i el contingut del missatge. Quan l'Usuari obre una incidència a GitHub, la incidència és pública i queda subjecta a les condicions i a la política de privadesa de GitHub.

Per exigència de l'article 13 de l'RGPD, s'indica el següent:

- **Finalitat:** atendre la consulta, la incidència o la sol·licitud de l'Usuari.
- **Base jurídica:** el consentiment de l'Usuari, manifestat en adreçar-se al Titular (article 6.1.a de l'RGPD), i, en l'exercici dels drets de la clàusula 8, el compliment d'una obligació legal del Titular (article 6.1.c de l'RGPD).
- **Termini de conservació:** el temps necessari per atendre la comunicació i, després, el termini de prescripció de les accions que se'n puguin derivar. Transcorregut aquest termini, les dades se suprimeixen.
- **Destinataris:** les dades no es cedeixen a tercers, llevat d'obligació legal. El correu electrònic del Titular el presta Google, que actua com a proveïdor del servei.

## 8. Drets de l'Usuari

L'Usuari pot exercir els drets d'accés, rectificació, supressió, limitació del tractament, oposició i portabilitat, en els termes dels articles 15 a 22 de l'RGPD, així com retirar en qualsevol moment el consentiment prestat, sense que això afecti la licitud del tractament anterior, adreçant-se al Titular a jotacomyn@gmail.com. Així mateix, pot presentar una reclamació davant l'Agència Espanyola de Protecció de Dades (www.aepd.es).

## 9. Modificacions

El Titular podrà modificar aquesta política; la data de la darrera actualització figurarà a l'inici del document.

## 10. Contacte

Les consultes relatives a aquesta política es podran adreçar al Titular a jotacomyn@gmail.com o mitjançant una incidència a https://github.com/javimentallab/StreamRemaster/issues.

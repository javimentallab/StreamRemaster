# Informativa sulla privacy — StreamRemaster

*Ultimo aggiornamento: 19 novembre 2026*

*[English](PRIVACY.md) · [Español](PRIVACY.es.md) · [Deutsch](PRIVACY.de.md) · [Français](PRIVACY.fr.md) · [Italiano](PRIVACY.it.md) · [Nederlands](PRIVACY.nl.md) · [Polski](PRIVACY.pl.md) · [Português](PRIVACY.pt.md) · [Русский](PRIVACY.ru.md) · [Українська](PRIVACY.uk.md) · [简体中文](PRIVACY.zh-CN.md) · [日本語](PRIVACY.ja.md) · [한국어](PRIVACY.ko.md) · [ไทย](PRIVACY.th.md) · [हिन्दी](PRIVACY.hi.md) · [Català](PRIVACY.ca.md) · [Galego](PRIVACY.gl.md) · [Euskara](PRIVACY.eu.md)*

## 1. Titolare del trattamento

L'estensione per browser StreamRemaster, precedentemente denominata Stream Transcription (l'«Estensione»), è pubblicata su addons.mozilla.org e su https://github.com/javimentallab/StreamRemaster da Javier Comyn Pérez, con indirizzo in calle Olivos, número 36, 28670 Villaviciosa de Odón, Madrid, España (il «Fornitore»), con il nome di sviluppatore javimentallab. Il Fornitore è il titolare del trattamento dei dati personali di cui alla presente informativa, che è disciplinata dal regolamento (UE) 2016/679, regolamento generale sulla protezione dei dati (il «GDPR»), e dalla legge organica spagnola 3/2018, del 5 dicembre, sulla protezione dei dati personali e la garanzia dei diritti digitali (Ley Orgánica 3/2018, de 5 de diciembre, de Protección de Datos Personales y garantía de los derechos digitales). L'utente dell'Estensione (l'«Utente») può contattare il Fornitore all'indirizzo jotacomyn@gmail.com.

## 2. Assenza di trattamento di dati personali nell'Estensione

L'Estensione non raccoglie né tratta alcun dato personale dell'Utente per conto del Fornitore. L'Estensione non dispone di account utente, pubblicità, strumenti di analisi o sistemi di segnalazione degli arresti anomali e non comunica con alcun server del Fornitore; non include né includerà alcuno di tali elementi. Né i dati dell'Utente né l'audio o le immagini elaborati dall'Estensione giungono al Fornitore. Gli unici dati personali che il Fornitore può trattare sono quelli che l'Utente gli fornisce di propria iniziativa quando lo contatta, secondo quanto previsto dalla sezione 7.

## 3. Funzionamento dell'Estensione

**3.1. Sottotitoli con un server dell'Utente.** Quando l'Utente attiva i sottotitoli in modalità server, l'Estensione invia l'audio della scheda all'indirizzo del server che l'Utente stesso ha inserito nell'Estensione, di norma un server WhisperLive installato sul computer o sulla rete locale dell'Utente, e ne riceve i sottotitoli. Tale server è installato e controllato dall'Utente, che è l'unico responsabile della sua configurazione e della sua sicurezza; il Fornitore non ha accesso né al server né all'audio.

**3.2. Sottotitoli sul computer dell'Utente.** Quando l'Utente sceglie di trascrivere sul computer, l'audio è elaborato nel browser, sulla scheda video dell'Utente, e non lascia il computer.

**3.3. Video fluido.** La funzione di video fluido elabora le immagini del video della pagina nel browser, sulla scheda video dell'Utente. Le immagini non lasciano il computer e non sono conservate.

## 4. Comunicazioni con terzi

L'Estensione si collega a siti diversi dal server dell'Utente solo quando l'Utente lo richiede espressamente, e unicamente nei casi seguenti:

- **GitHub (api.github.com).** Solo quando l'Utente preme «Cerca aggiornamenti», l'Estensione chiede a GitHub il numero dell'ultima versione pubblicata. La richiesta non contiene dati relativi all'Utente né al suo utilizzo dell'Estensione.
- **Hugging Face (huggingface.co).** Solo quando l'Utente scarica un modello di trascrizione per utilizzarlo sul computer, l'Estensione lo scarica da Hugging Face.
- **Indirizzi inseriti dall'Utente.** Quando l'Utente aggiunge un modello di video fluido indicandone l'indirizzo, l'Estensione lo scarica da tale indirizzo.

Come per qualsiasi connessione a Internet, il sito al quale l'Estensione si collega riceve l'indirizzo IP dell'Utente e l'identificazione del suo browser. Ciascuno di tali siti tratta tali dati in qualità di titolare del trattamento, secondo la propria informativa sulla privacy, della quale il Fornitore non risponde.

## 5. Autorizzazioni

- **Archiviazione (storage):** conservare le impostazioni dell'Estensione nel browser.
- **Acquisizione della scheda (tabCapture e offscreen), solo nei browser basati su Chromium:** ottenere l'audio della scheda in cui l'Utente attiva i sottotitoli, solo dopo che l'Utente ha premuto il pulsante dell'Estensione in tale scheda.
- **Scheda attiva ed esecuzione di script (activeTab e scripting), solo nei browser basati su Chromium:** mostrare i sottotitoli e applicare il video fluido nella scheda in cui l'Utente ha premuto il pulsante dell'Estensione.
- **Accesso ai siti web (<all_urls>):** in Firefox, leggere l'audio e il video della pagina per i sottotitoli e il video fluido. Nei browser basati su Chromium è un'autorizzazione facoltativa, che l'Estensione richiede solo se l'Utente seleziona la casella che attiva automaticamente il video fluido su qualsiasi sito web.

## 6. Dati conservati nel browser

L'Estensione conserva nella memoria del browser dell'Utente le proprie impostazioni (indirizzo del server, modello, lingue, dimensione e posizione dei sottotitoli e opzioni del video fluido), i modelli di video fluido aggiunti dall'Utente e i modelli di trascrizione che l'Utente scarica per utilizzarli sul computer. Tali dati restano nel browser dell'Utente, non sono inviati al Fornitore e sono cancellati alla disinstallazione dell'Estensione; i modelli possono inoltre essere cancellati dalle impostazioni dell'Estensione. Se l'Utente attiva l'opzione di salvataggio dei sottotitoli, quando questi vengono interrotti viene scaricato sul computer dell'Utente un file `.srt`, che resta a disposizione dell'Utente.

## 7. Dati delle comunicazioni dell'Utente

Quando l'Utente contatta il Fornitore via e-mail, il Fornitore tratta l'indirizzo e-mail dell'Utente, il suo nome, se fornito, e il contenuto del messaggio. Quando l'Utente apre una segnalazione su GitHub, la segnalazione è pubblica ed è soggetta ai termini e all'informativa sulla privacy di GitHub.

Ai sensi dell'articolo 13 del GDPR, si forniscono le seguenti informazioni:

- **Finalità:** gestire la richiesta di informazioni, la segnalazione o la domanda dell'Utente.
- **Base giuridica:** il consenso dell'Utente, espresso contattando il Fornitore (articolo 6, paragrafo 1, lettera a), del GDPR), e, in caso di esercizio dei diritti di cui alla sezione 8, l'adempimento di un obbligo legale del Fornitore (articolo 6, paragrafo 1, lettera c), del GDPR).
- **Periodo di conservazione:** il tempo necessario per gestire la comunicazione e, successivamente, il termine di prescrizione delle azioni che possano derivarne. Decorso tale termine, i dati sono cancellati.
- **Destinatari:** i dati non sono comunicati a terzi, salvo ove richiesto dalla legge. Il servizio di posta elettronica del Fornitore è fornito da Google, in qualità di prestatore di servizi.

## 8. Diritti dell'Utente

L'Utente può esercitare i diritti di accesso, rettifica, cancellazione, limitazione del trattamento, opposizione e portabilità, ai sensi degli articoli da 15 a 22 del GDPR, e revocare in qualsiasi momento il consenso prestato, senza pregiudicare la liceità del trattamento effettuato prima della revoca, contattando il Fornitore all'indirizzo jotacomyn@gmail.com. L'Utente può inoltre proporre reclamo all'Agencia Española de Protección de Datos (Agenzia spagnola per la protezione dei dati, www.aepd.es).

## 9. Modifiche

Il Fornitore può modificare la presente informativa; la data dell'ultimo aggiornamento è indicata all'inizio del presente documento.

## 10. Contatti

Le richieste relative alla presente informativa possono essere indirizzate al Fornitore all'indirizzo jotacomyn@gmail.com o aprendo una segnalazione su https://github.com/javimentallab/StreamRemaster/issues.

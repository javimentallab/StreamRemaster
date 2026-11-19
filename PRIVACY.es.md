# Política de privacidad — StreamRemaster

*Última actualización: 19 de noviembre de 2026*

*[English](PRIVACY.md) · [Español](PRIVACY.es.md) · [Deutsch](PRIVACY.de.md) · [Français](PRIVACY.fr.md) · [Italiano](PRIVACY.it.md) · [Nederlands](PRIVACY.nl.md) · [Polski](PRIVACY.pl.md) · [Português](PRIVACY.pt.md) · [Русский](PRIVACY.ru.md) · [Українська](PRIVACY.uk.md) · [简体中文](PRIVACY.zh-CN.md) · [日本語](PRIVACY.ja.md) · [한국어](PRIVACY.ko.md) · [ไทย](PRIVACY.th.md) · [हिन्दी](PRIVACY.hi.md) · [Català](PRIVACY.ca.md) · [Galego](PRIVACY.gl.md) · [Euskara](PRIVACY.eu.md)*

## 1. Responsable del tratamiento

La extensión de navegador StreamRemaster, antes denominada Stream Transcription (en adelante, «la Extensión»), se publica en addons.mozilla.org y en https://github.com/javimentallab/StreamRemaster por Javier Comyn Pérez, con domicilio en calle Olivos, número 36, 28670 Villaviciosa de Odón, Madrid, España (en adelante, «el Titular»), con el nombre de desarrollador javimentallab. El Titular es el responsable del tratamiento de los datos personales a que se refiere esta política, que se rige por el Reglamento (UE) 2016/679, General de Protección de Datos (en adelante, «el RGPD»), y por la Ley Orgánica 3/2018, de 5 de diciembre, de Protección de Datos Personales y garantía de los derechos digitales. El usuario de la Extensión (en adelante, «el Usuario») puede dirigirse al Titular en jotacomyn@gmail.com.

## 2. Ausencia de tratamiento de datos personales en la Extensión

La Extensión no recoge ni trata datos personales del Usuario por cuenta del Titular. La Extensión no dispone de cuentas de usuario, publicidad, herramientas de analítica ni sistemas de informe de fallos, y no se comunica con ningún servidor del Titular; no incorpora ni incorporará ninguno de esos elementos. Ningún dato del Usuario, ni el audio ni las imágenes que procesa la Extensión, llega al Titular. Los únicos datos personales que puede llegar a tratar el Titular son los que el Usuario le facilite por iniciativa propia al dirigirse a él, conforme a la cláusula 7.

## 3. Funcionamiento de la Extensión

**3.1. Subtítulos con un servidor del Usuario.** Cuando el Usuario activa los subtítulos en el modo de servidor, la Extensión envía el audio de la pestaña a la dirección de servidor que el propio Usuario ha introducido en la Extensión, normalmente un servidor WhisperLive instalado en su ordenador o en su red local, y recibe de él los subtítulos. Dicho servidor lo instala y controla el Usuario, que es el único responsable de su configuración y de su seguridad; el Titular no tiene acceso a él ni al audio.

**3.2. Subtítulos en el ordenador del Usuario.** Cuando el Usuario elige transcribir en su ordenador, el audio se procesa en el navegador, mediante la tarjeta gráfica del Usuario, y no sale del ordenador.

**3.3. Vídeo fluido.** La función de vídeo fluido procesa las imágenes del vídeo de la página en el navegador, mediante la tarjeta gráfica del Usuario. Las imágenes no salen del ordenador ni se almacenan.

## 4. Comunicaciones con terceros

La Extensión solo se conecta con sitios distintos del servidor del Usuario cuando este lo solicita de forma expresa, y únicamente en los supuestos siguientes:

- **GitHub (api.github.com).** Solo cuando el Usuario pulsa «Buscar actualizaciones», la Extensión consulta a GitHub el número de la última versión publicada. La consulta no contiene datos del Usuario ni de su uso de la Extensión.
- **Hugging Face (huggingface.co).** Solo cuando el Usuario descarga un modelo de transcripción para utilizarlo en su ordenador, la Extensión lo descarga de Hugging Face.
- **Direcciones introducidas por el Usuario.** Cuando el Usuario añade un modelo de vídeo fluido indicando su dirección, la Extensión lo descarga de esa dirección.

Como en toda conexión a Internet, el sitio con el que se conecta la Extensión recibe la dirección IP del Usuario y la identificación de su navegador. Cada uno de esos sitios trata dichos datos como responsable, conforme a su propia política de privacidad, de la que el Titular no responde.

## 5. Permisos

- **Almacenamiento (storage):** conservar los ajustes de la Extensión en el navegador.
- **Captura de la pestaña (tabCapture y offscreen), solo en los navegadores basados en Chromium:** obtener el audio de la pestaña en la que el Usuario activa los subtítulos, únicamente después de que pulse el botón de la Extensión en esa pestaña.
- **Pestaña activa y ejecución de scripts (activeTab y scripting), solo en los navegadores basados en Chromium:** mostrar los subtítulos y aplicar el vídeo fluido en la pestaña en la que el Usuario ha pulsado el botón de la Extensión.
- **Acceso a los sitios web (<all_urls>):** en Firefox, leer el audio y el vídeo de la página para los subtítulos y el vídeo fluido. En los navegadores basados en Chromium es un permiso opcional, que la Extensión solo solicita si el Usuario marca la casilla que activa el vídeo fluido de forma automática en cualquier sitio web.

## 6. Datos almacenados en el navegador

La Extensión conserva en el almacenamiento del navegador del Usuario sus ajustes (dirección del servidor, modelo, idiomas, tamaño y posición de los subtítulos y opciones del vídeo fluido), los modelos de vídeo fluido que el Usuario añada y los modelos de transcripción que descargue para utilizarlos en su ordenador. Estos datos permanecen en el navegador del Usuario, no se envían al Titular y se suprimen al desinstalar la Extensión; los modelos pueden suprimirse también desde los ajustes de la Extensión. Si el Usuario activa la opción de guardar los subtítulos, al detenerlos se descarga un fichero `.srt` en su ordenador, del que dispone el Usuario.

## 7. Datos de las comunicaciones del Usuario

Cuando el Usuario se dirige al Titular por correo electrónico, el Titular trata su dirección de correo, su nombre, si lo facilita, y el contenido del mensaje. Cuando el Usuario abre una incidencia en GitHub, la incidencia es pública y queda sujeta a las condiciones y a la política de privacidad de GitHub.

Por exigencia del artículo 13 del RGPD, se señala lo siguiente:

- **Finalidad:** atender la consulta, la incidencia o la solicitud del Usuario.
- **Base jurídica:** el consentimiento del Usuario, manifestado al dirigirse al Titular (artículo 6.1.a del RGPD), y, en el ejercicio de los derechos de la cláusula 8, el cumplimiento de una obligación legal del Titular (artículo 6.1.c del RGPD).
- **Plazo de conservación:** el tiempo necesario para atender la comunicación y, después, el plazo de prescripción de las acciones que pudieran derivarse de ella. Transcurrido dicho plazo, los datos se suprimen.
- **Destinatarios:** los datos no se ceden a terceros, salvo obligación legal. El correo electrónico del Titular se presta por Google, que actúa como proveedor del servicio.

## 8. Derechos del Usuario

El Usuario puede ejercer los derechos de acceso, rectificación, supresión, limitación del tratamiento, oposición y portabilidad, en los términos de los artículos 15 a 22 del RGPD, así como retirar en cualquier momento el consentimiento prestado, sin que ello afecte a la licitud del tratamiento anterior, dirigiéndose al Titular en jotacomyn@gmail.com. Asimismo, puede presentar una reclamación ante la Agencia Española de Protección de Datos (www.aepd.es).

## 9. Modificaciones

El Titular podrá modificar esta política; la fecha de la última actualización figurará al inicio del documento.

## 10. Contacto

Las consultas relativas a esta política podrán dirigirse al Titular en jotacomyn@gmail.com o mediante una incidencia en https://github.com/javimentallab/StreamRemaster/issues.

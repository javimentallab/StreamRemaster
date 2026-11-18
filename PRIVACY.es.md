# Política de privacidad — StreamRemaster

*Última actualización: 18 de noviembre de 2026*

*English version: [PRIVACY.md](PRIVACY.md)*

## 1. Responsable del tratamiento

La extensión de navegador StreamRemaster, antes llamada Stream Transcription (en adelante, «la Extensión»), se publica en addons.mozilla.org y en https://github.com/javimentallab/StreamRemaster por Javier Comyn Pérez, con domicilio en calle Olivos, número 36, 28670 Villaviciosa de Odón, Madrid, España (en adelante, «el Titular»), con el nombre de desarrollador javimentallab. El Titular es el responsable del tratamiento de los datos personales a que se refiere esta política, y el Usuario puede dirigirse a él en jotacomyn@gmail.com.

## 2. Ausencia de tratamiento de datos personales por el Titular

El Titular no recoge ni trata datos personales del Usuario. La Extensión no dispone de cuentas de usuario, publicidad, herramientas de analítica ni sistemas de informe de fallos, y no se comunica con ningún servidor del Titular. Ningún dato del Usuario, del audio ni de las imágenes que procesa la Extensión llega al Titular.

## 3. Funcionamiento de la Extensión

**3.1. Subtítulos con un servidor del Usuario.** Cuando el Usuario activa los subtítulos en el modo de servidor, la Extensión envía el audio de la pestaña a la dirección de servidor que el propio Usuario ha escrito en la Extensión, normalmente un servidor WhisperLive instalado en su ordenador o en su red local, y recibe de él los subtítulos. Ese servidor lo instala y controla el Usuario; el Titular no tiene acceso a él ni al audio.

**3.2. Subtítulos en el propio ordenador.** Cuando el Usuario elige transcribir en su ordenador, el audio se procesa en el navegador, con la tarjeta gráfica del Usuario, y no sale del ordenador.

**3.3. Vídeo fluido.** La función de vídeo fluido procesa las imágenes del vídeo de la página en el navegador, con la tarjeta gráfica del Usuario. Las imágenes no salen del ordenador ni se guardan.

## 4. Comunicaciones con terceros

La Extensión solo se conecta a sitios distintos del servidor del Usuario cuando el Usuario lo pide de forma expresa, y en los casos siguientes:

- **GitHub (api.github.com).** Solo cuando el Usuario pulsa «Buscar actualizaciones», la Extensión pregunta a GitHub el número de la última versión publicada. La consulta no lleva datos del Usuario ni de su uso de la Extensión.
- **Hugging Face (huggingface.co).** Solo cuando el Usuario descarga un modelo de transcripción para usarlo en su ordenador, la Extensión lo descarga de Hugging Face.
- **Direcciones que escriba el Usuario.** Cuando el Usuario añade un modelo de vídeo fluido indicando su dirección, la Extensión lo descarga de esa dirección.

Como en toda conexión a Internet, el sitio al que se conecta la Extensión recibe la dirección IP del Usuario y el nombre de su navegador. Cada uno de esos sitios trata esos datos conforme a su propia política de privacidad, de la que el Titular no es responsable.

## 5. Permisos

- **Almacenamiento (storage):** guardar los ajustes de la Extensión en el navegador.
- **Captura de la pestaña (tabCapture, offscreen), solo en los navegadores basados en Chromium:** obtener el audio de la pestaña en la que el Usuario activa los subtítulos, únicamente después de que pulse el botón de la Extensión en esa pestaña.
- **Acceso a los sitios web (<all_urls>):** en Firefox, leer el audio y el vídeo de la página para los subtítulos y el vídeo fluido. En los navegadores basados en Chromium es un permiso opcional, que la Extensión solo pide si el Usuario marca la casilla que activa el vídeo fluido de forma automática en cualquier sitio web.

## 6. Datos almacenados en el navegador

La Extensión guarda en el almacenamiento del navegador del Usuario sus ajustes (dirección del servidor, modelo, idiomas, tamaño y posición de los subtítulos y opciones del vídeo fluido), los modelos de vídeo fluido que el Usuario añada y los modelos de transcripción que descargue para usarlos en su ordenador. Estos datos permanecen en el navegador del Usuario, no se envían al Titular y se borran al desinstalar la Extensión; los modelos pueden borrarse también desde los ajustes de la Extensión. Si el Usuario activa la opción de guardar los subtítulos, al detenerlos se descarga un fichero `.srt` en su ordenador.

## 7. Derechos del Usuario

Dado que el Titular no trata datos personales del Usuario, no conserva datos sobre los que puedan ejercerse los derechos de acceso, rectificación, supresión, limitación del tratamiento, oposición y portabilidad de los artículos 15 a 22 del Reglamento General de Protección de Datos. No obstante, el Usuario puede dirigirse al Titular en jotacomyn@gmail.com para cualquier cuestión relativa a ellos, y presentar una reclamación ante la Agencia Española de Protección de Datos (www.aepd.es).

## 8. Modificaciones

El Titular podrá modificar esta política; la fecha de la última actualización figurará al inicio del documento.

## 9. Contacto

Las consultas relativas a esta política podrán dirigirse al Titular en jotacomyn@gmail.com o mediante una incidencia en https://github.com/javimentallab/StreamRemaster/issues.

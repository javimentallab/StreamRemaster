#!/usr/bin/env python3
"""Writes extension/shared/_locales/<lang>/messages.json from the table below (en, es) and tools/i18n-more.py.

Keeping both languages side by side makes a missing translation impossible.
Placeholders are {0}, {1}... (replaced by shared/i18n.js, not by chrome.i18n).
Run:  python tools/i18n-messages.py
"""
import json
import re
import os

M = {
    "error_local_lost": ("The graphics card stopped the transcription model several times in a row.", "La tarjeta gráfica ha parado el modelo de transcripción varias veces seguidas."),
    "fg_hq_badge": ("For powerful graphics cards", "Para gráficas potentes"),
    "where_fg_models": ("Where the models are", "Dónde están los modelos"),
    "fg_local_title": ("Smooth video models on this computer", "Modelos de vídeo fluido en este ordenador"),
    "fg_server_title": ("Smooth video models on the server", "Modelos de vídeo fluido en el servidor"),
    "fg_server_intro": ("The server only keeps them: the chosen model is downloaded from it and runs on this computer's graphics card.", "El servidor solo los guarda: el modelo elegido se baja de él y funciona en la tarjeta gráfica de este ordenador."),
    "fg_server_none": ("The server has no smooth video models yet.", "El servidor todavía no tiene modelos de vídeo fluido."),
    "fg_server_old": ("This server doesn't keep smooth video models: update it to the latest version.", "Este servidor no guarda modelos de vídeo fluido: actualízalo a la última versión."),
    "fg_add_server_title": ("Add to the server", "Añadir al servidor"),
    "fg_server_loading": ("Downloading the model from the server…", "Bajando el modelo del servidor…"),
    "section_transcription": ("Transcription models", "Modelos de transcripción"),
    "transcription_intro": ("Choose where speech is turned into text: on a WhisperLive server or on this computer's graphics card.", "Elige dónde se pasa la voz a texto: en un servidor WhisperLive o en la tarjeta gráfica de este ordenador."),
    "where_transcribe": ("Where to transcribe", "Dónde transcribir"),
    "engine_server": ("On the server", "En el servidor"),
    "engine_local": ("On this computer", "En este ordenador"),
    "trans_server_title": ("Transcription models on the server", "Modelos de transcripción en el servidor"),
    "trans_local_title": ("Transcription models on this computer", "Modelos de transcripción en este ordenador"),
    "badge_in_use": ("In use", "En uso"),
    "fg_downloaded_title": ("Downloaded", "Descargados"),
    "fg_add_title": ("Add a model", "Añadir un modelo"),
    "fg_add_url_placeholder": ("Address of a model file (.stmodel)", "Dirección de un archivo de modelo (.stmodel)"),
    "fg_download_failed": ("It could not be downloaded ({0}). Download the file with the browser and choose it from this computer.", "No se ha podido descargar ({0}). Descarga el archivo con el navegador y elígelo desde este ordenador."),
    "fg_memory": ("Graphics memory: about {0} with a 1080p video", "Memoria gráfica: unos {0} con un vídeo de 1080p"),
    "fg_memory_4k": ("about {0} upscaling 1080p to 4K", "unos {0} reescalando de 1080p a 4K"),
    "fg_memory_now": ("Graphics memory in use: about {0}", "Memoria gráfica en uso: unos {0}"),
    "fg_file_size": ("File: {0}", "Archivo: {0}"),
    "fg_options": ("Options", "Opciones"),
    # --- frame generation tab ---------------------------------------------------------
    'fg_resolution': ('Upscaling target resolution', 'Resolución objetivo del reescalado'),
    'fg_res_original': ('Original (no upscaling)', 'Original (sin reescalar)'),
    "fg_model": ("Smooth video model", "Modelo de vídeo fluido"),
    "fg_kind_sr": ("Upscaling only", "Solo reescalado"),
    "fg_kind_fi": ("In-between frames only", "Solo fotogramas intermedios"),
    'fg_builtin': ('Built-in', 'Incluido'),
    'fg_model_none': ('None (no AI)', 'Ninguno (sin IA)'),
    'fg_sharpen': ('Sharpness', 'Nitidez'),
    'fg_sharpen_off': ('Off', 'Desactivada'),
    'fg_sharpen_soft': ('Soft', 'Suave'),
    'fg_sharpen_medium': ('Medium', 'Media'),
    'fg_sharpen_strong': ('Strong', 'Fuerte'),
    'section_fgmodels': ('Smooth video models', 'Modelos de vídeo fluido'),
    "fg_models_hint": ("Smooth video always runs on this computer's graphics card. StreamRemaster comes with the extension; other models can be on this computer or on your server.", "El vídeo fluido funciona siempre en la tarjeta gráfica de este ordenador. StreamRemaster viene con la extensión; otros modelos pueden estar en este ordenador o en tu servidor."),
    "fg_add_model": ("Choose a file on this computer", "Elegir un archivo de este ordenador"),
    "fg_no_models": ("No downloaded models yet.", "Todavía no has descargado ningún modelo."),
    'fg_model_bad': ('That file is not a valid model.', 'Ese archivo no es un modelo válido.'),
    "tab_subs": ("Subtitles", "Subtítulos"),
    "tab_fg": ("Smooth video", "Vídeo fluido"),
    "fg_start": ("Turn on smooth video", "Activar vídeo fluido"),
    "fg_stop": ("Turn off smooth video", "Quitar vídeo fluido"),
    "fg_target": ("Target frame rate", "FPS objetivo"),
    "fg_target_display": ("Match the screen", "Igual que la pantalla"),
    "fg_state_off": ("Off", "Apagado"),
    "fg_state_measuring": ("Measuring the video…", "Midiendo el vídeo…"),
    "fg_state_on": ("{0} fps (video at {1} fps)", "{0} fps (vídeo a {1} fps)"),
    "fg_no_video": ("There is no video playing on this page.", "No hay ningún vídeo reproduciéndose en esta página."),
    "fg_no_webgpu": ("This browser cannot use the GPU for this (WebGPU is not available).", "Este navegador no puede usar la GPU para esto (no tiene WebGPU)."),
    "fg_cannot_read": ("This video cannot be read: it is protected or comes from another site.", "Este vídeo no se puede leer: está protegido o viene de otro sitio."),
    "fg_unavailable": ("This page does not allow extensions.", "Esta página no admite extensiones."),
    "fg_meter": ("Show the frame rate over the video", "Mostrar los fps sobre el vídeo"),
    "fg_auto_start": ("Turn on smooth video when a video plays", "Activar el vídeo fluido al reproducirse un vídeo"),
    "subs_auto_start": ("Start the subtitles when a video plays", "Iniciar los subtítulos al reproducirse un vídeo"),
    "auto_start_hint": ("In this browser it only works on tabs where you have clicked the extension's button, until they go to another site.", "En este navegador solo funciona en las pestañas en las que hayas pulsado el botón de la extensión, hasta que pasen a otro sitio web."),
    "fg_allow_all_sites": ("Allow on all sites", "Permitir en todos los sitios web"),

    # --- manifest --------------------------------------------------------------------
    "extName": ("StreamRemaster", "StreamRemaster"),
    "extDescription": (
        "Live subtitles for any tab, transcribed and translated by your own Whisper server.",
        "Subtítulos en directo para cualquier pestaña, transcritos y traducidos por tu propio servidor Whisper."),

    # --- popup -----------------------------------------------------------------------
    "start": ("Start subtitles", "Activar subtítulos"),
    "stop": ("Stop subtitles", "Quitar subtítulos"),
    "status_idle": ("Ready", "Listo"),
    "status_connecting": ("Connecting…", "Conectando…"),
    "status_loading": ("Loading model…", "Cargando el modelo…"),
    "status_listening": ("Listening…", "Escuchando…"),
    "status_live": ("Live", "En directo"),
    "status_stalled": ("Audio stopped", "Audio parado"),
    "status_error": ("Error", "Error"),
    "status_noresponse": ("No response", "Sin respuesta"),
    "model": ("Transcription model", "Modelo de transcripción"),
    "model_server_default": ("Server default", "El del servidor"),
    "model_default_tag": ("{0} · default", "{0} · por defecto"),
    "manage_models": ("Manage models", "Gestionar modelos"),
    "spoken_lang": ("Spoken language", "Idioma del audio"),
    "auto_detect": ("Auto-detect", "Automático"),
    "detected": ("Detected: {0}", "Detectado: {0}"),
    "subs_lang": ("Subtitles in", "Subtítulos en"),
    "original_lang": ("No translation", "Sin traducir"),
    "lines": ("Lines", "Líneas"),
    "text_size": ("Text size", "Tamaño del texto"),
    "save_srt": ("Save subtitles (.srt) when stopping", "Guardar los subtítulos (.srt) al parar"),
    "advanced": ("Advanced", "Avanzado"),
    "use_vad": ("Skip silences (voice detection)", "Saltar silencios (detección de voz)"),
    "settings": ("Settings", "Ajustes"),
    "first_load_hint": (
        "The first time a model loads it can take up to a minute.",
        "La primera vez que se carga un modelo puede tardar hasta un minuto."),
    "options_locked": ("Stop the subtitles to change these options.", "Quita los subtítulos para cambiar estas opciones."),

    # --- server ----------------------------------------------------------------------
    "server_setup_title": ("Connect your server", "Conecta tu servidor"),
    "server_setup_hint": (
        "StreamRemaster transcribes with a WhisperLive server on your computer or your network, or with this computer's graphics card.",
        "StreamRemaster transcribe con un servidor WhisperLive en tu ordenador o en tu red, o con la tarjeta gráfica de este ordenador."),
    "server_address": ("Server address", "Dirección del servidor"),
    "server_placeholder": ("e.g. localhost:9090 or 192.168.1.10:9090", "p. ej. localhost:9090 o 192.168.1.10:9090"),
    "connect": ("Connect", "Conectar"),
    "server_ok_models": ("Connected · {0} models", "Conectado · {0} modelos"),
    "server_ok_one_model": ("Connected · 1 model", "Conectado · 1 modelo"),
    "server_plain": (
        "Connected · standard WhisperLive (no model management)",
        "Conectado · WhisperLive estándar (sin gestión de modelos)"),
    "server_checking": ("Checking…", "Comprobando…"),
    "server_unreachable": (
        "Can't reach the server. Is it running? Check the address and the firewall.",
        "No se puede conectar con el servidor. ¿Está encendido? Revisa la dirección y el cortafuegos."),
    "server_timeout": ("The server didn't answer in time.", "El servidor no ha respondido a tiempo."),
    "server_bad_url": ("That address isn't valid.", "Esa dirección no es válida."),
    "server_change": ("Change", "Cambiar"),
    "server_help": ("How do I set up a server?", "¿Cómo monto un servidor?"),
    "server_help_1": (
        "You need a WhisperLive server (free and open source) running on a computer, ideally one with an NVIDIA "
        "graphics card. Small models also run on the processor alone.",
        "Necesitas un servidor WhisperLive (libre y gratuito) en un ordenador, mejor si tiene una tarjeta gráfica "
        "NVIDIA. Los modelos pequeños también funcionan solo con el procesador."),
    "server_help_2": (
        "Then type its address here: the computer's IP and the port, e.g. 192.168.1.10:9090. If it runs on this "
        "same computer, localhost:9090.",
        "Luego escribe aquí su dirección: la IP del ordenador y el puerto, p. ej. 192.168.1.10:9090. Si está en "
        "este mismo ordenador, localhost:9090."),
    "server_help_3": (
        "To download and manage models from this page, add the StreamRemaster add-on to the server.",
        "Para descargar y gestionar modelos desde esta página, añade al servidor el complemento de StreamRemaster."),
    "server_help_guide": ("Step-by-step guide", "Guía paso a paso"),

    # --- capture errors --------------------------------------------------------------
    "error_capture": (
        "This tab can't be captured (browser pages, extension stores and PDFs are off limits).",
        "No se puede capturar esta pestaña (las páginas del navegador, las tiendas de extensiones y los PDF no se dejan)."),
    "error_no_media": ("There's no video or audio on this page.", "No hay vídeo ni audio en esta página."),
    "error_server_full": ("The server is busy. Estimated wait: {0} min.", "El servidor está ocupado. Espera estimada: {0} min."),
    "error_disconnected": ("The server closed the connection.", "El servidor ha cerrado la conexión."),
    "error_model_load": (
        "⚠ Not enough graphics memory (VRAM) on the server for this model. Pick a smaller model, or turn on "
        "“Save memory (int8)” in Advanced.",
        "⚠ No hay memoria gráfica (VRAM) suficiente en el servidor para este modelo. Elige un modelo más pequeño "
        "o activa «Ahorrar memoria (int8)» en Avanzado."),
    "warn_no_response": (
        "⚠ Subtitles have stopped although there is sound. The model probably doesn't fit in the server's "
        "graphics memory (VRAM): pick a smaller model or turn on “Save memory (int8)” in Advanced.",
        "⚠ Han dejado de llegar subtítulos aunque hay sonido. Seguramente el modelo no cabe en la memoria gráfica "
        "(VRAM) del servidor: elige un modelo más pequeño o activa «Ahorrar memoria (int8)» en Avanzado."),
    "warn_slow_load": (
        "⚠ The model is taking too long to load. It may not fit in the server's graphics memory (VRAM): "
        "pick a smaller model or turn on “Save memory (int8)” in Advanced.",
        "⚠ El modelo está tardando demasiado en cargar. Puede que no quepa en la memoria gráfica (VRAM) del "
        "servidor: elige un modelo más pequeño o activa «Ahorrar memoria (int8)» en Avanzado."),
    "error_reload": ("Reload the page (F5) and start again.", "Recarga la página (F5) y vuelve a empezar."),
    "error_no_server": ("Set up the server first.", "Primero configura el servidor."),

    # --- settings page ---------------------------------------------------------------
    "settings_title": ("StreamRemaster · Settings", "StreamRemaster · Ajustes"),
    "section_subtitles": ("Subtitles", "Subtítulos"),
    "section_interface": ("Interface", "Interfaz"),
    "section_about": ("About", "Acerca de"),
    "installed_models": ("Installed on the server", "Instalados en el servidor"),
    "no_models": ("No models installed yet.", "Aún no hay modelos instalados."),
    "badge_default": ("Default", "Por defecto"),
    "badge_loaded": ("In memory", "En memoria"),
    "badge_selected": ("Selected", "Elegido"),
    "use_model": ("Use", "Usar"),
    "delete_model": ("Delete", "Borrar"),
    "confirm_delete": ("Delete {0} from the server? It frees {1}.", "¿Borrar {0} del servidor? Libera {1}."),
    "add_model": ("Add a model", "Añadir un modelo"),
    "add_model_hint": (
        "Paste the name or the link of a model on Hugging Face. Any Whisper model works: faster-whisper "
        "(CTranslate2) models are used as they are, and normal ones (transformers) are converted automatically. "
        "A direct link to a .zip or .tar.gz with a model also works.",
        "Pega el nombre o el enlace de un modelo de Hugging Face. Vale cualquier modelo Whisper: los de "
        "faster-whisper (CTranslate2) se usan tal cual y los normales (transformers) se convierten solos. "
        "También vale un enlace directo a un .zip o .tar.gz con un modelo."),
    "add_model_placeholder": ("e.g. Systran/faster-whisper-large-v3", "p. ej. Systran/faster-whisper-large-v3"),
    "download": ("Download", "Descargar"),
    "suggestions": ("Suggestions:", "Sugerencias:"),
    "browse_hf": ("Browse Whisper models on Hugging Face", "Ver modelos Whisper en Hugging Face"),
    "vram_hint": (
        "Bigger models are more accurate but need more GPU memory: small ≈ 1 GB, medium ≈ 2 GB, large ≈ 4 GB.",
        "Los modelos grandes aciertan más pero piden más memoria de la tarjeta gráfica: small ≈ 1 GB, medium ≈ 2 GB, large ≈ 4 GB."),
    "keep_open": (
        "Keep this page open until the download finishes.",
        "Deja esta página abierta hasta que termine la descarga."),
    "job_downloading": ("Downloading… {0} of {1}", "Descargando… {0} de {1}"),
    "job_downloading_nosize": ("Downloading… {0}", "Descargando… {0}"),
    "job_converting": ("Converting to faster-whisper format…", "Convirtiendo al formato de faster-whisper…"),
    "job_extracting": ("Extracting…", "Descomprimiendo…"),
    "job_ready": ("Installed", "Instalado"),
    "job_error": ("Failed: {0}", "Ha fallado: {0}"),
    "retry": ("Retry", "Reintentar"),
    "plain_server_hint": (
        "This is a standard WhisperLive server: type a model size (tiny, base, small, medium, large-v3, "
        "large-v3-turbo) and the server downloads it the first time. To download any model from here, install "
        "the StreamRemaster add-on on the server.",
        "Es un servidor WhisperLive estándar: escribe un tamaño de modelo (tiny, base, small, medium, large-v3, "
        "large-v3-turbo) y el servidor lo descarga la primera vez. Para descargar cualquier modelo desde aquí, "
        "instala el complemento de StreamRemaster en el servidor."),
    "model_name": ("Model name", "Nombre del modelo"),
    "save": ("Save", "Guardar"),
    "saved": ("Saved", "Guardado"),
    "reset_position": ("Reset subtitle position", "Recolocar los subtítulos"),
    "position_reset_done": ("Done: they'll go back to the bottom.", "Hecho: volverán abajo."),
    "section_performance": ("Performance", "Rendimiento"),
    "performance_hint": (
        "If the server's graphics card runs out of memory (subtitles that never arrive, or a memory warning), "
        "these two options free a lot of it. They only work with the StreamRemaster server.",
        "Si la tarjeta gráfica del servidor se queda sin memoria (los subtítulos no llegan o sale un aviso de "
        "memoria), estas dos opciones liberan bastante. Solo funcionan con el servidor de StreamRemaster."),
    "precision": ("Model precision", "Precisión del modelo"),
    "precision_auto": ("Automatic", "Automática"),
    "precision_int8": ("Save memory (int8)", "Ahorrar memoria (int8)"),
    "precision_hint": (
        "int8 uses about half the graphics memory and, in practice, writes the same text.",
        "int8 gasta más o menos la mitad de memoria gráfica y, en la práctica, escribe el mismo texto."),
    "translator_device": ("Translator runs on", "El traductor va en"),
    "device_gpu": ("Graphics card", "La tarjeta gráfica"),
    "device_cpu": ("Processor (CPU)", "El procesador (CPU)"),
    "translator_device_hint": (
        "On the processor it frees graphics memory, but translated subtitles arrive a little later.",
        "En el procesador libera memoria gráfica, pero los subtítulos traducidos llegan algo más tarde."),
    "interface_lang": ("Interface language", "Idioma de la interfaz"),
    "lang_auto": ("Same as the browser", "El del navegador"),
    "about_text": (
        "Source code available (PolyForm Noncommercial license). The audio only goes to the server you set up here; nothing is sent anywhere else.",
        "Código fuente disponible (licencia PolyForm Noncommercial). El audio solo va al servidor que configures aquí; no se envía nada a ningún otro sitio."),
    "about_based": ("Based on WhisperLive by Collabora.", "Basado en WhisperLive, de Collabora."),
    "source_code": ("Source code", "Código fuente"),
    "subtitle_preview": ("This is how your subtitles will look.", "Así se verán tus subtítulos."),

    # --- updates (only checked when the user asks) -----------------------------------
    "updates": ("Updates", "Actualizaciones"),
    "check_updates": ("Check for updates", "Buscar actualizaciones"),
    "check_again": ("Check again", "Volver a buscar"),
    "update_now": ("Update", "Actualizar"),
    "update_available": ("Version {0} is available (you have {1}).", "Ya está la versión {0} (tienes la {1})."),
    "update_latest": ("You have the latest version ({0}).", "Tienes la última versión ({0})."),
    "update_rate_limited": (
        "GitHub is limiting checks for a while. Try again later.",
        "GitHub está limitando las consultas durante un rato. Vuelve a intentarlo más tarde."),
    "update_failed": (
        "Could not check for updates. Check your connection and try again.",
        "No se han podido buscar actualizaciones. Revisa la conexión y vuelve a intentarlo."),
    "update_how_firefox": (
        "Firefox installs new versions by itself. To get it now, open about:addons, click the gear icon and "
        "choose ‘Check for Updates’. A version that has just come out can take a few days to reach the add-ons site.",
        "Firefox instala solo las versiones nuevas. Para tenerla ya, abre about:addons, pulsa el icono del engranaje "
        "y elige «Buscar actualizaciones». Una versión recién salida puede tardar unos días en llegar a la web de complementos."),
    "update_how_chromium": (
        "To update, download the Chromium zip from the release page, unzip it over the old folder and press the "
        "reload icon on the StreamRemaster card in chrome://extensions. Your settings are kept.",
        "Para actualizar, descarga el zip de Chromium de la página de la versión, descomprímelo encima de la carpeta "
        "antigua y pulsa el icono de recargar en la tarjeta de StreamRemaster de chrome://extensions. Los ajustes se conservan."),
    "update_privacy": (
        "Checking only asks GitHub for the number of the latest version; nothing else is sent.",
        "Al buscar, solo se pregunta a GitHub el número de la última versión; no se envía nada más."),
    "server_update_available": (
        "Your server has version {0} and {1} is available. To update it, run this on the computer that hosts it:",
        "Tu servidor tiene la versión {0} y ya está la {1}. Para actualizarlo, ejecuta esto en el ordenador donde está:"),
    "server_version_unknown": (
        "Your server does not say which version it has, so it is older than this check. To update it, run this "
        "on the computer that hosts it:",
        "Tu servidor no dice qué versión tiene, así que es anterior a esta comprobación. Para actualizarlo, ejecuta "
        "esto en el ordenador donde está:"),
    "server_update_latest": ("Your server is up to date ({0}).", "Tu servidor está al día ({0})."),
    "server_update_note": (
        "The models stay in the Docker volume and are not downloaded again. If you edited docker-compose.yml and "
        "git pull complains, run git stash before it and git stash pop after it.",
        "Los modelos se quedan en el volumen de Docker y no se vuelven a descargar. Si has cambiado "
        "docker-compose.yml y git pull se queja, ejecuta git stash antes y git stash pop después."),

    # --- model errors (codes sent by the server) -------------------------------------
    "err_invalid_source": ("That isn't a Hugging Face model name or a link.", "Eso no es un nombre de modelo de Hugging Face ni un enlace."),
    "err_unsupported_url": (
        "Only Hugging Face links or direct links to .zip / .tar.gz files.",
        "Solo enlaces de Hugging Face o enlaces directos a ficheros .zip / .tar.gz."),
    "err_repo_not_found": ("That model doesn't exist on Hugging Face (check the name).", "Ese modelo no existe en Hugging Face (revisa el nombre)."),
    "err_gated_repo": (
        "That model asks you to accept its terms on Hugging Face; the server needs an HF_TOKEN.",
        "Ese modelo pide aceptar sus condiciones en Hugging Face; el servidor necesita un HF_TOKEN."),
    "err_not_whisper": ("That isn't a Whisper model.", "Eso no es un modelo Whisper."),
    "err_no_weights": ("That repository has no model weights.", "Ese repositorio no tiene los pesos del modelo."),
    "err_network_error": ("Network error. Try again: it resumes where it stopped.", "Error de red. Vuelve a intentarlo: sigue por donde iba."),
    "err_download_failed": ("The download failed.", "La descarga ha fallado."),
    "setup_or": ("or", "o"),
    "use_local": ("Use this computer", "Usar este ordenador"),
    "use_local_hint": ("Whisper runs on this computer's graphics card, with no server. You download the model once, in Settings.", "Whisper funciona con la tarjeta gráfica de este ordenador, sin servidor. El modelo se descarga una vez, en Ajustes."),
    "local_footer": ("This computer", "Este ordenador"),
    "local_none": ("No model yet: download one", "Ningún modelo: descarga uno"),
    "local_intro": ("Whisper runs in the browser, on your graphics card (WebGPU). Each model is downloaded once from Hugging Face and stays in the browser. The bigger ones write better and need more graphics memory.", "Whisper funciona en el navegador, con tu tarjeta gráfica (WebGPU). Cada modelo se descarga una vez de Hugging Face y se queda en el navegador. Los más grandes escriben mejor y necesitan más memoria gráfica."),
    "local_sizes": ("Download {0} · takes {1} · about {2} of graphics memory", "Descarga {0} · ocupa {1} · unos {2} de memoria gráfica"),
    "local_progress": ("Downloading… {0} of {1}", "Descargando… {0} de {1}"),
    "local_cancel": ("Cancel", "Cancelar"),
    "local_gpu": ("Graphics card: {0}", "Tarjeta gráfica: {0}"),
    "badge_downloaded": ("Downloaded", "Descargado"),
    "error_no_webgpu": ("This browser can't use the graphics card (WebGPU), so it can't transcribe on this computer.", "Este navegador no puede usar la tarjeta gráfica (WebGPU), así que no puede transcribir en este ordenador."),
    "error_local_missing": ("Download a model first, in Settings → Models on this computer.", "Primero descarga un modelo, en Ajustes → Modelos en este ordenador."),
    "error_local_failed": ("Transcription on this computer stopped because of an error.", "La transcripción en este ordenador se ha parado por un error."),
    "error_local_vram": ("⚠ Not enough graphics memory on this computer for this model. Pick a smaller one.", "⚠ No hay memoria gráfica suficiente en este ordenador para este modelo. Elige uno más pequeño."),
    "local_download_failed": ("The download failed ({0}).", "La descarga ha fallado ({0})."),
    "local_confirm_delete": ("Delete the {0} model from this computer? It frees {1}.", "¿Borrar el modelo {0} de este ordenador? Libera {1}."),
    "local_only_english": ("On this computer the subtitles can only be translated into English.", "En este ordenador los subtítulos solo se pueden traducir al inglés."),
    "err_convert_failed": ("The model couldn't be converted.", "No se ha podido convertir el modelo."),
    "err_bad_archive": ("The archive is damaged or unsafe.", "El fichero comprimido está dañado o no es seguro."),
    "err_already_downloading": ("It's already downloading.", "Ya se está descargando."),
    "err_already_installed": ("It's already installed.", "Ya está instalado."),
    "err_management_disabled": ("Model management is turned off on this server.", "La gestión de modelos está desactivada en este servidor."),
    "err_is_default": (
        "That's the server's default model; it can't be deleted from here.",
        "Es el modelo por defecto del servidor; no se puede borrar desde aquí."),
    "err_in_use": ("A running transcription is using it.", "Lo está usando una transcripción en marcha."),
    "err_not_found": ("That model is no longer on the server.", "Ese modelo ya no está en el servidor."),
    "err_server_error": ("Server error.", "Error del servidor."),
    "err_unreachable": ("Can't reach the server.", "No se puede conectar con el servidor."),
    "err_timeout": ("The server didn't answer in time.", "El servidor no ha respondido a tiempo."),
    "err_unknown": ("Unexpected error ({0}).", "Error inesperado ({0})."),
}


def tables():
    """English and Spanish from M; the other languages from tools/i18n-more.py ("key|text" lines),
    checked against English: same keys, same {n} placeholders."""
    here = os.path.dirname(os.path.abspath(__file__))
    out = {"en": {k: v[0] for k, v in M.items()}, "es": {k: v[1] for k, v in M.items()}}
    more = {}
    with open(os.path.join(here, "i18n-more.py"), encoding="utf-8") as fh:
        exec(fh.read(), more)
    for lang, block in more["LANGS"].items():
        t = {}
        for line in block.split("\n"):
            if line.strip():
                k, v = line.split("|", 1)
                t[k] = v
        missing, extra = set(M) - set(t), set(t) - set(M)
        assert not missing and not extra, (lang, sorted(missing), sorted(extra))
        for k in M:
            assert set(re.findall(r"\{\d\}", t[k])) == set(re.findall(r"\{\d\}", M[k][0])), (lang, k)
        assert len(t["extDescription"]) <= 132, (lang, "extDescription")  # Chrome's limit
        out[lang] = t
    return out


def main():
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "extension", "shared", "_locales")
    all_tables = tables()
    for lang, table in all_tables.items():
        out = {k: {"message": v} for k, v in table.items()}
        d = os.path.join(root, lang)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "messages.json"), "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
    print(f"{len(M)} messages x {len(all_tables)} languages")


if __name__ == "__main__":
    main()

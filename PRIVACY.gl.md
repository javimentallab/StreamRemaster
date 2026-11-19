# Política de privacidade — StreamRemaster

*Última actualización: 19 de novembro de 2026*

*[English](PRIVACY.md) · [Español](PRIVACY.es.md) · [Deutsch](PRIVACY.de.md) · [Français](PRIVACY.fr.md) · [Italiano](PRIVACY.it.md) · [Nederlands](PRIVACY.nl.md) · [Polski](PRIVACY.pl.md) · [Português](PRIVACY.pt.md) · [Русский](PRIVACY.ru.md) · [Українська](PRIVACY.uk.md) · [简体中文](PRIVACY.zh-CN.md) · [日本語](PRIVACY.ja.md) · [한국어](PRIVACY.ko.md) · [ไทย](PRIVACY.th.md) · [हिन्दी](PRIVACY.hi.md) · [Català](PRIVACY.ca.md) · [Galego](PRIVACY.gl.md) · [Euskara](PRIVACY.eu.md)*

## 1. Responsable do tratamento

A extensión de navegador StreamRemaster, antes denominada Stream Transcription (en diante, a «Extensión»), é publicada en addons.mozilla.org e en https://github.com/javimentallab/StreamRemaster por Javier Comyn Pérez, con domicilio en calle Olivos, número 36, 28670 Villaviciosa de Odón, Madrid, España (en diante, o «Titular»), co nome de desenvolvedor javimentallab. O Titular é o responsable do tratamento dos datos persoais a que se refire esta política, que se rexe polo Regulamento (UE) 2016/679, xeral de protección de datos (en diante, o «RXPD»), e pola Lei orgánica 3/2018, do 5 de decembro, de protección de datos persoais e garantía dos dereitos dixitais. O usuario da Extensión (en diante, o «Usuario») pode dirixirse ao Titular en jotacomyn@gmail.com.

## 2. Ausencia de tratamento de datos persoais na Extensión

A Extensión non recolle nin trata datos persoais do Usuario por conta do Titular. A Extensión non dispón de contas de usuario, publicidade, ferramentas de analítica nin sistemas de informes de erros, e non se comunica con ningún servidor do Titular; non incorpora nin incorporará ningún destes elementos. Ningún dato do Usuario, nin o audio nin as imaxes que procesa a Extensión, chega ao Titular. Os únicos datos persoais que pode chegar a tratar o Titular son os que o Usuario lle facilite por iniciativa propia ao dirixirse a el, conforme á cláusula 7.

## 3. Funcionamento da Extensión

**3.1. Subtítulos cun servidor do Usuario.** Cando o Usuario activa os subtítulos no modo de servidor, a Extensión envía o audio da lapela ao enderezo de servidor que o propio Usuario introduciu na Extensión, normalmente un servidor WhisperLive instalado no seu ordenador ou na súa rede local, e recibe del os subtítulos. Ese servidor instálao e contrólao o Usuario, que é o único responsable da súa configuración e da súa seguridade; o Titular non ten acceso a el nin ao audio.

**3.2. Subtítulos no ordenador do Usuario.** Cando o Usuario escolle transcribir no seu ordenador, o audio procésase no navegador, mediante a tarxeta gráfica do Usuario, e non sae do ordenador.

**3.3. Vídeo fluído.** A función de vídeo fluído procesa as imaxes do vídeo da páxina no navegador, mediante a tarxeta gráfica do Usuario. As imaxes non saen do ordenador nin se almacenan.

## 4. Comunicacións con terceiros

A Extensión só se conecta con sitios distintos do servidor do Usuario cando este o solicita de forma expresa, e unicamente nos supostos seguintes:

- **GitHub (api.github.com).** Só cando o Usuario preme «Buscar actualizacións», a Extensión consulta a GitHub o número da última versión publicada. A consulta non contén datos do Usuario nin do seu uso da Extensión.
- **Hugging Face (huggingface.co).** Só cando o Usuario descarga un modelo de transcrición para utilizalo no seu ordenador, a Extensión descárgao de Hugging Face.
- **Enderezos introducidos polo Usuario.** Cando o Usuario engade un modelo de vídeo fluído indicando o seu enderezo, a Extensión descárgao dese enderezo.

Como en toda conexión a Internet, o sitio co que se conecta a Extensión recibe o enderezo IP do Usuario e a identificación do seu navegador. Cada un deses sitios trata os ditos datos como responsable, conforme á súa propia política de privacidade, da que o Titular non responde.

## 5. Permisos

- **Almacenamento (storage):** conservar os axustes da Extensión no navegador.
- **Captura da lapela (tabCapture e offscreen), só nos navegadores baseados en Chromium:** obter o audio da lapela na que o Usuario activa os subtítulos, unicamente despois de que prema o botón da Extensión nesa lapela.
- **Lapela activa e execución de scripts (activeTab e scripting), só nos navegadores baseados en Chromium:** mostrar os subtítulos e aplicar o vídeo fluído na lapela na que o Usuario premeu o botón da Extensión.
- **Acceso aos sitios web (<all_urls>):** en Firefox, ler o audio e o vídeo da páxina para os subtítulos e o vídeo fluído. Nos navegadores baseados en Chromium é un permiso opcional, que a Extensión só solicita se o Usuario marca a caixa que activa o vídeo fluído de forma automática en calquera sitio web.

## 6. Datos almacenados no navegador

A Extensión conserva no almacenamento do navegador do Usuario os seus axustes (enderezo do servidor, modelo, idiomas, tamaño e posición dos subtítulos e opcións do vídeo fluído), os modelos de vídeo fluído que o Usuario engada e os modelos de transcrición que descargue para utilizalos no seu ordenador. Estes datos permanecen no navegador do Usuario, non se envían ao Titular e suprímense ao desinstalar a Extensión; os modelos tamén poden suprimirse desde os axustes da Extensión. Se o Usuario activa a opción de gardar os subtítulos, ao detelos descárgase un ficheiro `.srt` no seu ordenador, do que dispón o Usuario.

## 7. Datos das comunicacións do Usuario

Cando o Usuario se dirixe ao Titular por correo electrónico, o Titular trata o seu enderezo de correo, o seu nome, se o facilita, e o contido da mensaxe. Cando o Usuario abre unha incidencia en GitHub, a incidencia é pública e queda suxeita ás condicións e á política de privacidade de GitHub.

Por exixencia do artigo 13 do RXPD, indícase o seguinte:

- **Finalidade:** atender a consulta, a incidencia ou a solicitude do Usuario.
- **Base xurídica:** o consentimento do Usuario, manifestado ao dirixirse ao Titular (artigo 6.1.a do RXPD), e, no exercicio dos dereitos da cláusula 8, o cumprimento dunha obriga legal do Titular (artigo 6.1.c do RXPD).
- **Prazo de conservación:** o tempo necesario para atender a comunicación e, despois, o prazo de prescrición das accións que puidesen derivar dela. Transcorrido o dito prazo, os datos suprímense.
- **Destinatarios:** os datos non se ceden a terceiros, agás obriga legal. O correo electrónico do Titular é prestado por Google, que actúa como provedor do servizo.

## 8. Dereitos do Usuario

O Usuario pode exercer os dereitos de acceso, rectificación, supresión, limitación do tratamento, oposición e portabilidade, nos termos dos artigos 15 a 22 do RXPD, así como retirar en calquera momento o consentimento prestado, sen que isto afecte á licitude do tratamento anterior, dirixíndose ao Titular en jotacomyn@gmail.com. Así mesmo, pode presentar unha reclamación ante a Axencia Española de Protección de Datos (www.aepd.es).

## 9. Modificacións

O Titular poderá modificar esta política; a data da última actualización figurará ao inicio do documento.

## 10. Contacto

As consultas relativas a esta política poderán dirixirse ao Titular en jotacomyn@gmail.com ou mediante unha incidencia en https://github.com/javimentallab/StreamRemaster/issues.

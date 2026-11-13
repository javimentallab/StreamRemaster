# Pendiente antes de publicar StreamRemaster 1.0.0

Lo que solo puedes decidir o hacer tú. Los borradores de esta carpeta están hechos sobre el texto actual
de `main` (ya con PolyForm Noncommercial 1.0.0). El producto pasa a llamarse StreamRemaster y esta es su
versión 1.0.0.

## Decidir

- [ ] **Fecha de la 1.0.0.** En `CHANGELOG.md` queda como `1.0.0 — date to be decided`. Los manifiestos
  siguen en 2.2.0.
- [ ] **AMO y el número de versión.** En addons.mozilla.org el complemento ya tiene versiones hasta la 2.x
  con el ID `stream-transcription@javimentallab`. Una 1.0.0 con el mismo ID sería más baja que la que
  tienen instalada los usuarios. Hay dos salidas: una ficha y un ID nuevos para StreamRemaster, o una
  versión por encima de la 2.2.0.
- [ ] **Venta en Chromium.** En los navegadores Chromium se venderá y en Firefox será gratis. La Chrome
  Web Store no tiene sistema de pago propio, así que hace falta uno externo de pago y licencias. Los README
  ya dicen que en Firefox es gratis; lo de Chromium queda como TODO hasta que se decida, y los textos de
  las tiendas también tendrán que decirlo.
- [ ] **Qué modelo se publica.** El encargo dice que la red de reescalado tiene 32 canales y 4 bloques,
  pero el `streamremaster.stmodel` que hay ahora lleva «StreamRemaster SR 24x4 (prueba)» (24 canales) y
  «FI 32x64 sync». En `docs/MODEL*.md` el número de canales está como `<…>`.
- [ ] **Seguridad en el CHANGELOG.** Decir si se corrige alguna vulnerabilidad (en la 2.2.0 se puso «No
  vulnerabilities fixed in this release»).

## Hacer

- [ ] **Revisión del jurista** de la licencia de los modelos entrenados con REDS (CC BY 4.0) y con
  partidas de Xonotic (juego GPL, con recursos bajo varias licencias). Afecta a `NOTICE` y al apartado de
  licencia de `docs/MODEL*.md`.
- [ ] **Capturas** de la pestaña Vídeo fluido para los README (hueco marcado con
  `<!-- TODO: captura de la pestaña Vídeo fluido -->`).
- [ ] **Comprobar que todo cabe** en la pestaña nueva y en el apartado de modelos de los ajustes, en los
  18 idiomas.
- [ ] **Instalación desde cero y prueba real**, en Firefox y en un Chromium, con el `.zip` que salga de
  `tools/build.py`.
- [ ] **Textos de AMO** (`store/amo-metadata.json`, 13 idiomas): no están redactados.

## Para saber

- El repositorio, la carpeta del `git clone` y los `.zip` de `tools/build.py` siguen llamándose
  `stream-transcription`; los README no los cambian.
- Los README de `main` aún enumeran 15 idiomas; los borradores ya añaden el catalán, el gallego y el
  euskera.
- En el worktree `framegen`, `LICENSE` sigue siendo la MIT hasta que se rebase sobre `main`.

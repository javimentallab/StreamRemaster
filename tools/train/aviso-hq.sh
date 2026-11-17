#!/bin/sh
# Vigilante del entrenamiento hq64x4-real (mint-run-hq-real.sh): avisa al móvil por ntfy (~/scripts/notify.sh)
#  - al saber la velocidad (pasada la iteración 1.000), con la hora a la que acabará;
#  - cuando termina o falla, con el mejor punto y lo que gana en reescalado e intermedios frente a rife32x4;
#  - si el proceso desaparece sin terminar (reinicio, corte) o lleva 30 min sin escribir nada.
# Uso: nohup ./aviso-hq.sh > aviso-hq.log 2>&1 &
cd "$(dirname "$0")" || exit 1
RUN=runs/hq64x4-real
OUT=runs/hq64x4-real.out
LOG=run-hq-real.log
TOTAL=60000
avisa() { ~/scripts/notify.sh "StreamRemaster" "$1"; echo "$(date '+%d %H:%M') $1"; }

resumen() {
  .venv/bin/python - "$RUN/best.json" <<'EOF' 2>/dev/null
import json, sys
b = json.load(open(sys.argv[1]))
g = lambda k, r: b.get(k, 0) - b.get(k + r, 0)
print(f"mejor en la it. {b['iteration']}; reescalado sobre bicúbico: REDS real {g('fps60_reds_real_key', '_bicubic'):+.2f} dB, "
      f"juegos real {g('fps60_games_ss_real_key', '_bicubic'):+.2f} (rife32x4: +0,74 y +0,32); "
      f"intermedios sobre el fundido: REDS real {g('fps60_reds_real_mid', '_fade'):+.2f}, "
      f"juegos real {g('fps60_games_ss_real_mid', '_fade'):+.2f} (rife32x4: +1,55 y +0,69)")
EOF
}

eta_dicha=0
colgado_dicho=0
while :; do
  sleep 120
  if grep -qE "ESTADO: (terminado|fallo)" $LOG 2>/dev/null; then
    avisa "Entrenamiento HQ: $(grep ESTADO $LOG | tail -1 | sed 's/^ESTADO: //') (Mint). $(resumen)"
    exit 0
  fi
  if ! pgrep -f "run $RUN" > /dev/null; then
    avisa "Entrenamiento HQ PARADO sin terminar (Mint), última línea: $(grep -o '"iteration": [0-9]*' $OUT | tail -1). Se reanuda con nohup ./mint-run-hq-real.sh"
    exit 1
  fi
  if [ "$eta_dicha" = 0 ]; then
    line=$(grep per_second $OUT | tail -1)
    it=$(echo "$line" | sed -n 's/.*"iteration": \([0-9]*\).*/\1/p')
    if [ -n "$it" ] && [ "$it" -ge 1000 ]; then
      # media de las últimas 10 medidas: una sola baila mucho
      rate=$(grep per_second $OUT | tail -10 | sed 's/.*"per_second": \([0-9.]*\).*/\1/' | awk '{ s += $1 } END { printf "%.2f", s / NR }')
      # validaciones de ~1 min además de los pasos
      fin=$(awk -v it="$it" -v r="$rate" -v t="$TOTAL" 'BEGIN { printf "%d", (t - it) / r + 30 * 60 }')
      avisa "Entrenamiento HQ en marcha a $rate it/s: acabará hacia las $(date -d "+$fin seconds" '+%H:%M del %d'). Te aviso al terminar."
      eta_dicha=1
    fi
  fi
  if [ -n "$(find $OUT -mmin +30 2>/dev/null)" ]; then
    [ "$colgado_dicho" = 0 ] && avisa "Entrenamiento HQ: 30 min sin escribir nada, puede estar colgado (Mint)."
    colgado_dicho=1
  else
    colgado_dicho=0
  fi
done

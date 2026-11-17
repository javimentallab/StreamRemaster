#!/bin/sh
# Vigilante del entrenamiento rife32x4 (mint-run-rife.sh): avisa al móvil por ntfy (~/scripts/notify.sh)
#  - al saber la velocidad, con la hora a la que acabará;
#  - cuando termina o falla, con el mejor punto y lo que gana en fotogramas intermedios;
#  - si el proceso desaparece sin terminar (reinicio, corte) o lleva 30 min sin escribir nada.
# Uso: nohup ./aviso-rife.sh > aviso-rife.log 2>&1 &
cd "$(dirname "$0")" || exit 1
RUN=runs/rife32x4
OUT=runs/rife32x4.out
TOTAL=60000
avisa() { ~/scripts/notify.sh "StreamRemaster" "$1"; echo "$(date '+%d %H:%M') $1"; }

resumen() {
  .venv/bin/python - "$RUN/best.json" <<'EOF' 2>/dev/null
import json, sys
b = json.load(open(sys.argv[1]))
g = lambda k: b.get(k, 0) - b.get(k + "_fade", 0)
print(f"mejor en la it. {b['iteration']}; intermedios sobre el fundido: REDS real {g('fps60_reds_real_mid'):+.2f} dB, "
      f"juegos real {g('fps60_games_ss_real_mid'):+.2f}, lluvia {g('fps60_rain_mid'):+.2f} "
      f"(antes, real32x4: +1,45, +0,50 y +0,44)")
EOF
}

eta_dicha=0
colgado_dicho=0
while :; do
  sleep 120
  if grep -qE "ESTADO: (terminado|fallo)" run-rife.log 2>/dev/null; then
    avisa "Entrenamiento con RIFE: $(grep ESTADO run-rife.log | tail -1 | sed 's/^ESTADO: //') (Mint). $(resumen)"
    exit 0
  fi
  if ! pgrep -f "$RUN" > /dev/null; then
    avisa "Entrenamiento con RIFE PARADO sin terminar (Mint), última línea: $(grep -o '"iteration": [0-9]*' $OUT | tail -1). Se reanuda con nohup ./mint-run-rife.sh"
    exit 1
  fi
  if [ "$eta_dicha" = 0 ]; then
    line=$(grep per_second $OUT | tail -1)
    if [ -n "$line" ]; then
      it=$(echo "$line" | sed 's/.*"iteration": \([0-9]*\).*/\1/')
      rate=$(echo "$line" | sed 's/.*"per_second": \([0-9.]*\).*/\1/')
      # 30 validaciones de ~1 min además de los pasos
      fin=$(awk -v it="$it" -v r="$rate" -v t="$TOTAL" 'BEGIN { printf "%d", (t - it) / r + 30 * 60 }')
      avisa "Entrenamiento con RIFE en marcha a $rate it/s: acabará hacia las $(date -d "+$fin seconds" '+%H:%M del %d'). Te aviso al terminar."
      eta_dicha=1
    fi
  fi
  if [ -n "$(find $OUT -mmin +30 2>/dev/null)" ]; then
    [ "$colgado_dicho" = 0 ] && avisa "Entrenamiento con RIFE: 30 min sin escribir nada, puede estar colgado (Mint)."
    colgado_dicho=1
  else
    colgado_dicho=0
  fi
done

#!/bin/bash
# ============================================================
# FIX: iso-zeit PDF Export — 2 undefinierte Variablen
# ============================================================
# Problem: "Lohnzettel PDF" Button crasht mit ReferenceError
#   1) Zeile ~1959: atStr ist undefiniert (muss ma.arbeitstage sein)
#   2) Zeile ~2030: atGes ist undefiniert (muss berechnet werden)
#
# Ausfuehren auf dem Server (46.225.166.62):
#   bash fix-iso-zeit-pdf-export.sh
# ============================================================

set -euo pipefail

# --- Dateipfad anpassen falls noetig ---
FILE="/var/www/dashboard/iso-zeit/index.html"

# Alternativen pruefen
for candidate in \
  "/var/www/dashboard/iso-zeit/index.html" \
  "/var/www/html/iso-zeit/index.html" \
  "/opt/dashboard/iso-zeit/index.html" \
  "/srv/www/iso-zeit/index.html" \
  "/root/dashboard/iso-zeit/index.html"; do
  if [ -f "$candidate" ]; then
    FILE="$candidate"
    break
  fi
done

if [ ! -f "$FILE" ]; then
  echo "FEHLER: Datei nicht gefunden. Bitte Pfad manuell setzen."
  echo "Suche nach der Datei..."
  find / -path '*/iso-zeit/index.html' -type f 2>/dev/null
  exit 1
fi

echo "Datei gefunden: $FILE"

# Backup erstellen
BACKUP="${FILE}.bak.$(date +%Y%m%d_%H%M%S)"
cp "$FILE" "$BACKUP"
echo "Backup erstellt: $BACKUP"

# FIX 1: atStr → ma.arbeitstage (Zeile mit "const atSet3 = atSet2(atStr)")
sed -i 's/const atSet3 = atSet2(atStr);/const atSet3 = atSet2(ma.arbeitstage);/' "$FILE"

# FIX 2: atGes → maArbeitstage(ma.arbeitstage, false) (Zeile mit "atGes + ' Tage'")
sed -i "s/\['Arbeitstage (Soll)', atGes + ' Tage'\]/['Arbeitstage (Soll)', maArbeitstage(ma.arbeitstage, false) + ' Tage']/" "$FILE"

# Verifizieren
echo ""
echo "=== Verifizierung ==="
if grep -n "atSet2(ma.arbeitstage)" "$FILE" > /dev/null; then
  echo "FIX 1 OK: atStr → ma.arbeitstage"
else
  echo "FIX 1 FEHLER: Patch nicht angewendet!"
fi

if grep -n "maArbeitstage(ma.arbeitstage, false)" "$FILE" > /dev/null; then
  echo "FIX 2 OK: atGes → maArbeitstage(ma.arbeitstage, false)"
else
  echo "FIX 2 FEHLER: Patch nicht angewendet!"
fi

# Pruefen ob keine atStr/atGes Referenzen mehr existieren (ausser in Funktionsdefinitionen)
echo ""
echo "=== Restliche Referenzen pruefen ==="
REMAINING=$(grep -n 'atStr\|atGes' "$FILE" | grep -v 'function.*atStr' | grep -v 'atSet2(atStr)' | grep -v '// ' || true)
if [ -z "$REMAINING" ]; then
  echo "SAUBER: Keine problematischen Referenzen mehr."
else
  echo "WARNUNG: Noch vorhandene Referenzen:"
  echo "$REMAINING"
fi

echo ""
echo "=== FERTIG ==="
echo "PDF-Export sollte jetzt funktionieren."
echo "Teste: https://dashboard.isotec-kiel.eu/iso-zeit/ → Lohnzettel PDF"
echo "Bei Problemen Backup wiederherstellen: cp $BACKUP $FILE"

# MASTER-PROMPT: Viterma BLS → ISOTEC-Kiel Dashboard Migration

> **Lade diesen Prompt in eine lokale Claude-Instanz mit SSH-Zugang zum Server.**
> Alle Analyse-Ergebnisse sind eingebettet. Claude fuehrt den gesamten Plan autonom aus.

---

## ROLLE

Du bist ein Senior Full-Stack Engineer mit Spezialisierung auf Badsanierungs-Vertriebssoftware. Du hast Zugriff auf den Produktivserver via SSH und fuehrst alle Arbeitspakete eigenstaendig aus. Du arbeitest praezise, testest jeden Schritt, und dokumentierst deine Aenderungen.

## KONTEXT

### Zwei Systeme

**Original — Viterma BLS**
- URL: https://bls.viterma.com/dashboard
- Login: Benutzer `lasse.ottsen` / Passwort `LAS526#777OTT`
- Bereich: "Angebote" → Workflows → Schritte
- Technologie: Angular 17+, Material Design 3, NgRx, PDF.js, Web Worker
- Beschreibung: "Viterma - Better Life System for sales administration"
- Regionen: AT (20% MwSt), DE (19% MwSt), CH (8.1% MwSt)
- Theme: Orange #ed6b06, Dunkelblau #004766

**Kopie — ISOTEC-Kiel Dashboard**
- URL: https://dashboard.isotec-kiel.eu/dashboard/vit-Angebote/
- Server: 46.225.166.62 (SSH als root, Key auf diesem Mac)
- Technologie: Vanilla JS, HTML, CSS, eigene Auth-API
- Status: Workflow-Grundstruktur vorhanden, Rest fehlt

### Was bereits funktioniert
- Login/Authentifizierung (`/auth-api/login`)
- Workflow-Navigation mit Schritten
- Grundlegendes Dashboard-Layout (Dark Theme)

### Was komplett fehlt
- Produktdatenbank mit korrekten Zuordnungen
- Produktvarianten (Farbe, Material, Groesse)
- Kalkulationsengine (Preisberechnung)
- 200-500+ Abhaengigkeitsregeln zwischen Produkten
- Automatische Mengenberechnung aus Raumdaten
- Dynamische Formulare (bedingte Felder)
- Interaktive PDF-Kataloge (PDF.js)
- Live-Preisvorschau
- Rabatt-/Margen-System
- MwSt-/Laenderlogik
- Angebots-PDF-Generierung
- Shower-Tray-Designer

---

## ANALYSE-ERGEBNISSE (bereits durchgefuehrt)

### Perspektive 1: Solution Architect

Das BLS nutzt:
- Angular 17+ mit Standalone Components
- NgRx fuer State Management (@ngrx/router-store bestaetigt)
- Dedizierten Web Worker (`worker-FM6BN62R.js`) fuer Kalkulationen
- PDF.js mit vollstaendigem Locale- und CMAP-Support
- Service Worker mit differenzierten Cache-Strategien:
  - `/privatemedia/*` → Freshness, 60 Tage Cache
  - `/media/*` → Freshness, 1 Jahr Cache
- ~92 Lazy-Loaded Chunks (grosse Applikation)
- PWA: manifest.webmanifest, Icons 72-512px, Offline-faehig

**Datenmodell des BLS (rekonstruiert):**

```
Angebot (Offer)
├── Kundendaten (Customer)
├── Aufmass/Raumdaten (Room Measurements)
│   ├── Raumtyp, L x B x H
│   ├── Tueren/Fenster-Positionen
│   └── Bestandsaufnahme
├── Angebotspositionen (Line Items)
│   ├── Produkt → Kategorie → Varianten
│   ├── Abhaengigkeiten (Pflicht/Ausschluss/Mengenformel/Varianten-Kopplung)
│   ├── Menge (aus Raumdaten berechnet)
│   ├── Preis (Staffel, Aktion, Region)
│   └── Positionspreis
├── Pakete/Bundles
├── Arbeitsleistungen (Labor)
├── Kalkulation
│   ├── Material-Summe → Arbeitskosten → Aufschlaege → Rabatte → MwSt → Gesamt
│   └── Marge (pro Berater konfigurierbar)
└── PDF-Angebotsdokument
```

**Fuer die Kopie empfohlen:** Kein Angular-Nachbau. Stattdessen Vanilla-JS mit JSON-Schema-Formularen, serverseitiger Kalkulation, und PDF.js als Standalone-Library.

### Perspektive 2: Business Analyst — Kalkulationslogik

**10-Schritte-Workflow im BLS:**

1. **Kundenauswahl** — Bestandskunde suchen ODER Neukunde anlegen
2. **Raumaufnahme** — Raumtyp, Masse (L/B/H), Tueren, Fenster, Bestand dokumentieren
3. **Demontage** — Was wird entfernt (Checkboxen) → Automatisch: Entsorgungspositionen
4. **Bodengestaltung** — PDF-Katalog Bodenbelag, Dekor/Farbe → Auto: Menge aus Raumdaten + Zubehoer
5. **Wandgestaltung** — PDF-Katalog Wandpaneele, Bereiche (volle Hoehe/Spritzbereich) → Auto: Menge, Profile
6. **Dusche/Badewanne** — Typ, Modell aus Katalog, Groesse, Farbe → Auto: Armaturen, Ablauf, Dichtung
7. **Sanitaerobjekte** — WC, Waschtisch, Spiegel, Zubehoer → Abhaengigkeiten pro Objekt
8. **Heizung/Elektro** — Handtuchheizkoerper, Steckdosen, Beleuchtung
9. **Montage/Arbeitsleistung** — Auto-berechnet aus Produktauswahl + Sonderleistungen
10. **Zusammenfassung** — Alle Positionen, Rabatte, Marge, Netto/Brutto, PDF generieren

**6 Abhaengigkeits-Typen:**

| Typ | Beispiel | Logik |
|-----|---------|-------|
| REQUIRED | Dusche → Ablaufgarnitur | Wenn A gewaehlt → B automatisch hinzufuegen |
| QUANTITY_FORMULA | Wandpaneele → Fugenprofile | Menge B = f(Menge A, Raumgeometrie) |
| EXCLUDED | Badewanne ↔ Bodengleiche Dusche | Wenn A → B nicht moeglich |
| VARIANT_LINK | Paneelfarbe → Profilfarbe | Variante B folgt Variante A |
| SURCHARGE | Sondermass → Aufpreis | Wenn Wert ausserhalb Standard → Zuschlag |
| BUNDLE | Komfort-Paket | Paketpreis < Summe Einzelpreise |

**Kalkulationsformel:**
```
Fuer jede Position:
  qty = calculate_quantity(product, room_data)   # aus Raumdaten oder manuell
  unit_price = get_price(product, qty, region)    # inkl. Staffelpreise
  line_total = qty * unit_price + variant_surcharges

subtotal_material = SUM(alle line_totals)
subtotal_labor = calculate_labor(products, room_data)  # Stundensaetze * Aufwandsfaktoren
subtotal = subtotal_material + subtotal_labor

discount = apply_discounts(subtotal, rules)   # Aktion → Menge → Kunde (Reihenfolge!)
margin = (subtotal - discount) * margin_pct
net_total = subtotal - discount + margin
tax = net_total * tax_rate                     # AT:20%, DE:19%, CH:8.1%
gross_total = net_total + tax
```

### Perspektive 3: UX-Designer

**Dynamische Formulare:** Felder erscheinen/verschwinden basierend auf Auswahlen:
- "Bodengleich" gewaehlt → Duschtassen-Felder verschwinden
- "Badewanne" gewaehlt → Dusch-Optionen deaktiviert
- Produkt gewaehlt → Pflicht-Zubehoer-Felder erscheinen

**PDF-Katalog-Interaktion:** PDF.js rendert Katalogseiten im Browser. Berater blaettert mit Kunde. Hotspot-Bereiche auf Seiten sind mit Produkten verknuepft. Klick = Auswahl.

**Validierung:** Pflichtfelder pro Schritt. Vorwaerts nur wenn valide. Rueckwaerts immer moeglich.

### Perspektive 4: Frontend-Entwickler

**BLS-Tech-Stack (bestaetigt):**
- Angular 17+, Material Design 3, NgRx, PDF.js, Web Worker, Service Worker/PWA
- Fonts: Roboto (300/400/500), Material Icons
- 45+ SVG-Icons, Shower-Tray-Design-Bilder, Laender-Flaggen (AT/CH/DE)

**Kopie-Tech-Stack:**
- Vanilla JS, HTML, CSS, Fetch API
- Dark Theme (#0d1117), eigene Auth-API
- Kein Framework, kein State Management, kein PDF, kein Worker

### Perspektive 5: QA/Daten-Analyst

**Geschaetzter BLS-Datenbestand:**
- 15-25 Produktkategorien
- 500-2.000+ Artikel mit Varianten
- 200-500+ Abhaengigkeitsregeln
- 50-100+ Preisregeln
- 5-15 PDF-Kataloge
- 10-30+ Shower-Tray-Designs

**Kritische Testfaelle nach Umsetzung:**
1. Standard-Bad 6m² komplett → Preis = BLS-Referenzwert
2. Nur Duschumbau → Alle Pflichtartikel erscheinen automatisch
3. Sondermass → Aufpreise korrekt
4. Rabatt-Kombination → Reihenfolge und Ergebnis korrekt
5. Laenderwechsel AT↔DE → MwSt korrekt

---

## DELTA-MATRIX

| Nr | Komponente | BLS | Kopie | Gap | Prio |
|----|-----------|-----|-------|-----|------|
| 1 | Produktdatenbank | 500-2000+ Artikel | Falsch zugeordnet | UNVOLLSTAENDIG | P0 |
| 2 | Produktvarianten | Vollstaendig | Nicht vorhanden | FEHLEND | P0 |
| 3 | Kalkulationsengine | Web Worker, Echtzeit | Nicht vorhanden | FEHLEND | P0 |
| 4 | Abhaengigkeitsregeln | 200-500+ Regeln | 0 Regeln | FEHLEND | P0 |
| 5 | Mengenberechnung aus Raumdaten | Automatisch | Nicht vorhanden | FEHLEND | P0 |
| 6 | Raumaufmass-Eingabe | Detailliert | Grundfelder | UNVOLLSTAENDIG | P1 |
| 7 | Dynamische Formulare | Vollstaendig | Nicht vorhanden | FEHLEND | P1 |
| 8 | Live-Preisvorschau | Echtzeit | Nicht vorhanden | FEHLEND | P1 |
| 9 | PDF-Kataloge | PDF.js + Hotspots | Nicht vorhanden | FEHLEND | P1 |
| 10 | Rabatt-/Margen-System | Mehrstufig | Nicht vorhanden | FEHLEND | P1 |
| 11 | MwSt/Laender-Logik | AT/DE/CH | Nicht vorhanden | FEHLEND | P1 |
| 12 | Angebots-PDF-Generierung | Vollstaendig | Nicht vorhanden | FEHLEND | P2 |
| 13 | Workflow-Validierung | Pflichtfelder pro Schritt | Nicht vorhanden | FEHLEND | P2 |
| 14 | Shower-Tray-Designer | Visueller Konfigurator | Nicht vorhanden | FEHLEND | P2 |
| 15 | Offline/PWA | Service Worker | Nicht vorhanden | FEHLEND | P3 |
| 16 | State Management | NgRx | Keines | ABWEICHEND | P2 |
| 17 | Workflow-Grundstruktur | Vollstaendig | Implementiert | IDENTISCH | — |

---

## AUFTRAG — SCHRITT FUER SCHRITT AUSFUEHREN

### SCHRITT 0: Server analysieren

Verbinde dich per SSH auf den Server und analysiere den aktuellen Stand:

```bash
SSH_SERVER="root@46.225.166.62"
```

Fuehre folgende Befehle aus und dokumentiere die Ergebnisse:

```bash
# 0.1 — Wo liegt der Code fuer das Dashboard?
ssh $SSH_SERVER "find / -path '*/vit-Angebote*' -type f 2>/dev/null | head -50"
ssh $SSH_SERVER "find / -path '*/dashboard*' -name '*.py' -o -name '*.js' -o -name '*.php' -o -name '*.html' 2>/dev/null | head -100"

# 0.2 — Webserver-Konfiguration
ssh $SSH_SERVER "cat /etc/nginx/sites-enabled/* 2>/dev/null; cat /etc/nginx/conf.d/*.conf 2>/dev/null"
ssh $SSH_SERVER "cat /etc/apache2/sites-enabled/* 2>/dev/null"

# 0.3 — Backend-Technologie identifizieren
ssh $SSH_SERVER "ps aux | grep -E 'python|node|php|gunicorn|uvicorn|pm2|django|flask|express'"

# 0.4 — Datenbank
ssh $SSH_SERVER "systemctl list-units --type=service | grep -E 'mysql|postgres|mongo|mariadb|sqlite'"

# 0.5 — Docker?
ssh $SSH_SERVER "docker ps 2>/dev/null; docker-compose ps 2>/dev/null"

# 0.6 — Aktueller Angebote-Code lesen
# (Pfade anpassen basierend auf 0.1 Ergebnis)
ssh $SSH_SERVER "cat /pfad/zu/vit-Angebote/index.html 2>/dev/null"
ssh $SSH_SERVER "ls -la /pfad/zu/vit-Angebote/"
```

**WICHTIG:** Passe alle nachfolgenden Pfade und Befehle an die tatsaechlichen Ergebnisse von Schritt 0 an.

---

### SCHRITT 1: BLS-Produktdaten erfassen (AP-01)

Logge dich im Viterma BLS ein und erfasse systematisch alle Produkte:

1. Oeffne https://bls.viterma.com/dashboard im Browser
2. Login: `lasse.ottsen` / `LAS526#777OTT`
3. Navigiere zu "Angebote" und starte einen neuen Angebots-Workflow
4. Gehe jeden Schritt durch und dokumentiere:
   - Alle verfuegbaren Produktkategorien
   - Alle Produkte pro Kategorie mit: Artikelnummer, Name, Preis, Einheit
   - Alle Varianten pro Produkt (Farbe, Material, Groesse) mit Preismodifikator
   - Alle automatisch erscheinenden Pflichtartikel
   - Alle PDF-Kataloge (welche Kataloge gibt es, wieviele Seiten)

**Alternativ** (wenn API zugaenglich): Nutze die Browser-DevTools (Network Tab) um die API-Endpunkte des BLS zu identifizieren und die Produktdaten als JSON zu extrahieren.

Erstelle aus den erfassten Daten folgende Dateien auf dem Server:

```bash
# Datenbank-Schema erstellen
ssh $SSH_SERVER "cat > /pfad/zum/projekt/migrations/001_products.sql << 'SQLEOF'
CREATE TABLE IF NOT EXISTS product_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    parent_id INTEGER REFERENCES product_categories(id),
    sort_order INTEGER DEFAULT 0,
    icon TEXT,
    active BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    category_id INTEGER REFERENCES product_categories(id),
    unit TEXT DEFAULT 'Stueck',  -- Stueck, m2, lfm, Pauschal
    base_price_net DECIMAL(10,2) NOT NULL,
    image_url TEXT,
    active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS variant_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL  -- 'Farbe', 'Material', 'Groesse'
);

CREATE TABLE IF NOT EXISTS product_variants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER REFERENCES products(id),
    variant_type_id INTEGER REFERENCES variant_types(id),
    value TEXT NOT NULL,           -- 'Marmor Weiss', 'Eiche Natur'
    price_modifier DECIMAL(10,2) DEFAULT 0,  -- Aufpreis/Abschlag
    sku_suffix TEXT,
    image_url TEXT,
    active BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS dependency_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_product_id INTEGER REFERENCES products(id),
    target_product_id INTEGER REFERENCES products(id),
    rule_type TEXT NOT NULL,       -- REQUIRED, EXCLUDED, QUANTITY_FORMULA, VARIANT_LINK, SURCHARGE, BUNDLE
    condition_json TEXT,           -- JSON mit Bedingungen
    formula TEXT,                  -- z.B. 'source_qty * 2.5 + 1' oder 'room_area * 0.1'
    description TEXT,
    active BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS price_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER REFERENCES products(id),
    rule_type TEXT NOT NULL,       -- STAFFEL, AKTION, REGIONAL
    min_qty DECIMAL(10,2),
    max_qty DECIMAL(10,2),
    price_net DECIMAL(10,2),
    discount_pct DECIMAL(5,2),
    region TEXT,                   -- AT, DE, CH oder NULL fuer alle
    valid_from DATE,
    valid_to DATE,
    active BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS tax_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_code TEXT NOT NULL,    -- AT, DE, CH
    rate_pct DECIMAL(5,2) NOT NULL,
    label TEXT
);

INSERT INTO tax_rates (country_code, rate_pct, label) VALUES
    ('AT', 20.00, 'USt Oesterreich'),
    ('DE', 19.00, 'MwSt Deutschland'),
    ('CH', 8.10, 'MWST Schweiz');

INSERT INTO variant_types (name) VALUES ('Farbe'), ('Material'), ('Groesse');

CREATE TABLE IF NOT EXISTS catalogs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category_id INTEGER REFERENCES product_categories(id),
    pdf_url TEXT NOT NULL,
    page_count INTEGER,
    active BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS catalog_hotspots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    catalog_id INTEGER REFERENCES catalogs(id),
    page_number INTEGER NOT NULL,
    x_pct DECIMAL(5,2),       -- Position in % der Seitenbreite
    y_pct DECIMAL(5,2),
    width_pct DECIMAL(5,2),
    height_pct DECIMAL(5,2),
    product_id INTEGER REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS offers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    customer_address TEXT,
    customer_email TEXT,
    customer_phone TEXT,
    region TEXT DEFAULT 'DE',
    status TEXT DEFAULT 'draft',  -- draft, calculated, sent, accepted, rejected
    current_step INTEGER DEFAULT 1,
    room_data_json TEXT,
    margin_pct DECIMAL(5,2) DEFAULT 15.00,
    discount_json TEXT,
    subtotal_material DECIMAL(10,2) DEFAULT 0,
    subtotal_labor DECIMAL(10,2) DEFAULT 0,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    margin_amount DECIMAL(10,2) DEFAULT 0,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    total_gross DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT
);

CREATE TABLE IF NOT EXISTS offer_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    offer_id INTEGER REFERENCES offers(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    variant_id INTEGER REFERENCES product_variants(id),
    quantity DECIMAL(10,3) NOT NULL,
    unit_price_net DECIMAL(10,2) NOT NULL,
    line_total_net DECIMAL(10,2) NOT NULL,
    is_auto_added BOOLEAN DEFAULT 0,  -- durch Abhaengigkeit hinzugefuegt
    added_by_rule_id INTEGER REFERENCES dependency_rules(id),
    sort_order INTEGER DEFAULT 0,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS workflow_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    step_number INTEGER NOT NULL,
    name TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    form_schema_json TEXT,        -- JSON-Schema fuer dynamische Formulare
    validation_rules_json TEXT,
    required BOOLEAN DEFAULT 1
);

INSERT INTO workflow_steps (step_number, name, title, description, required) VALUES
    (1, 'kunde', 'Kundendaten', 'Kunde auswaehlen oder neu anlegen', 1),
    (2, 'raumaufmass', 'Raumaufmass', 'Raumtyp und Masse erfassen', 1),
    (3, 'demontage', 'Demontage', 'Bestehende Ausstattung zur Demontage waehlen', 1),
    (4, 'boden', 'Bodengestaltung', 'Bodenbelag aus Katalog waehlen', 1),
    (5, 'wand', 'Wandgestaltung', 'Wandpaneele und Profile waehlen', 1),
    (6, 'dusche', 'Dusche / Badewanne', 'Dusch- oder Wannentyp konfigurieren', 1),
    (7, 'sanitaer', 'Sanitaerobjekte', 'WC, Waschtisch, Spiegel waehlen', 1),
    (8, 'heizung_elektro', 'Heizung & Elektro', 'Heizkoerper und Elektroinstallation', 0),
    (9, 'montage', 'Montage & Arbeitsleistung', 'Automatisch berechnet + Sonderleistungen', 1),
    (10, 'zusammenfassung', 'Zusammenfassung & Kalkulation', 'Uebersicht, Rabatte, PDF erstellen', 1);
SQLEOF"
```

---

### SCHRITT 2: Abhaengigkeits-Engine (AP-02)

Implementiere eine serverseitige Rule-Engine die bei jeder Produktaenderung aufgerufen wird:

**API-Endpunkt:** `POST /api/offers/{id}/evaluate-dependencies`

**Logik:**
```python
def evaluate_dependencies(offer_id):
    offer = get_offer(offer_id)
    room = json.loads(offer.room_data_json) if offer.room_data_json else {}
    items = get_offer_items(offer_id)
    result = {"add": [], "remove": [], "modify": []}

    for item in items:
        rules = get_active_rules(item.product_id)
        for rule in rules:
            if rule.rule_type == 'REQUIRED':
                if not item_exists(offer_id, rule.target_product_id):
                    target = get_product(rule.target_product_id)
                    qty = 1
                    if rule.formula:
                        qty = eval_formula(rule.formula, room, item.quantity)
                    result["add"].append({
                        "product_id": rule.target_product_id,
                        "quantity": qty,
                        "unit_price": target.base_price_net,
                        "is_auto_added": True,
                        "added_by_rule_id": rule.id
                    })

            elif rule.rule_type == 'EXCLUDED':
                if item_exists(offer_id, rule.target_product_id):
                    result["remove"].append(rule.target_product_id)

            elif rule.rule_type == 'QUANTITY_FORMULA':
                if item_exists(offer_id, rule.target_product_id):
                    new_qty = eval_formula(rule.formula, room, item.quantity)
                    result["modify"].append({
                        "product_id": rule.target_product_id,
                        "quantity": round(new_qty, 3)
                    })

            elif rule.rule_type == 'VARIANT_LINK':
                condition = json.loads(rule.condition_json) if rule.condition_json else {}
                if condition.get("variant_match") == "color" and item.variant_id:
                    variant = get_variant(item.variant_id)
                    matching = find_matching_variant(rule.target_product_id, variant.value)
                    if matching:
                        result["modify"].append({
                            "product_id": rule.target_product_id,
                            "variant_id": matching.id
                        })

            elif rule.rule_type == 'SURCHARGE':
                condition = json.loads(rule.condition_json) if rule.condition_json else {}
                if meets_surcharge_condition(item, condition):
                    surcharge = eval_formula(rule.formula, room, item.quantity)
                    result["modify"].append({
                        "product_id": item.product_id,
                        "surcharge": surcharge
                    })

    return result

def eval_formula(formula, room, source_qty):
    """Sichere Formel-Auswertung mit Raum- und Mengenvariablen"""
    variables = {
        "source_qty": source_qty,
        "room_length": room.get("length_cm", 0) / 100,
        "room_width": room.get("width_cm", 0) / 100,
        "room_height": room.get("height_cm", 0) / 100,
        "room_area": (room.get("length_cm", 0) * room.get("width_cm", 0)) / 10000,
        "wall_area": 2 * (room.get("length_cm", 0) + room.get("width_cm", 0)) * room.get("height_cm", 0) / 10000,
        "perimeter": 2 * (room.get("length_cm", 0) + room.get("width_cm", 0)) / 100,
        "door_count": room.get("door_count", 0),
        "window_count": room.get("window_count", 0),
    }
    # Nur erlaubte Variablen und Operatoren (kein eval()!)
    import ast
    tree = ast.parse(formula, mode='eval')
    # ... sichere Auswertung implementieren
```

---

### SCHRITT 3: Kalkulationsengine (AP-03)

**API-Endpunkt:** `GET /api/offers/{id}/calculate`

**Logik:**
```python
def calculate_offer(offer_id):
    offer = get_offer(offer_id)
    room = json.loads(offer.room_data_json) if offer.room_data_json else {}
    items = get_offer_items(offer_id)
    region = offer.region or 'DE'

    line_details = []
    subtotal_material = Decimal('0')

    for item in items:
        product = get_product(item.product_id)
        qty = item.quantity
        unit_price = get_effective_price(product, qty, region)

        # Varianten-Aufpreis
        if item.variant_id:
            variant = get_variant(item.variant_id)
            unit_price += variant.price_modifier

        line_total = qty * unit_price
        subtotal_material += line_total

        line_details.append({
            "product_name": product.name,
            "sku": product.sku,
            "quantity": float(qty),
            "unit": product.unit,
            "unit_price": float(unit_price),
            "line_total": float(line_total),
            "is_auto": item.is_auto_added
        })

    # Arbeitsleistung
    subtotal_labor = calculate_labor_costs(items, room, region)

    subtotal = subtotal_material + subtotal_labor

    # Rabatte (Reihenfolge: Aktion → Menge → Kunde)
    discount_details = []
    discount_total = Decimal('0')
    remaining = subtotal

    if offer.discount_json:
        discounts = json.loads(offer.discount_json)
        for d in sorted(discounts, key=lambda x: x.get("priority", 99)):
            if d["is_percentage"]:
                amount = remaining * Decimal(str(d["value"])) / 100
            else:
                amount = Decimal(str(d["value"]))
            discount_total += amount
            remaining -= amount
            discount_details.append({"name": d["name"], "amount": float(amount)})

    # Marge
    margin_pct = offer.margin_pct or Decimal('15')
    margin_base = subtotal - discount_total
    margin_amount = margin_base * margin_pct / 100

    net_total = margin_base + margin_amount

    # MwSt
    tax_rate = get_tax_rate(region)
    tax_amount = net_total * tax_rate / 100

    gross_total = net_total + tax_amount

    # Angebot aktualisieren
    update_offer_totals(offer_id,
        subtotal_material=subtotal_material,
        subtotal_labor=subtotal_labor,
        discount_amount=discount_total,
        margin_amount=margin_amount,
        tax_amount=tax_amount,
        total_gross=gross_total
    )

    return {
        "line_items": line_details,
        "subtotal_material": float(subtotal_material),
        "subtotal_labor": float(subtotal_labor),
        "subtotal": float(subtotal),
        "discounts": discount_details,
        "discount_total": float(discount_total),
        "margin_pct": float(margin_pct),
        "margin_amount": float(margin_amount),
        "net_total": float(net_total),
        "tax_rate": float(tax_rate),
        "tax_amount": float(tax_amount),
        "gross_total": float(gross_total),
        "region": region
    }

def get_effective_price(product, qty, region):
    """Staffelpreis und Regionalpreis pruefen"""
    rules = get_price_rules(product.id, region)
    for rule in rules:
        if rule.min_qty <= qty <= (rule.max_qty or Decimal('999999')):
            if rule.price_net:
                return rule.price_net
            if rule.discount_pct:
                return product.base_price_net * (1 - rule.discount_pct / 100)
    return product.base_price_net

def calculate_labor_costs(items, room, region):
    """Arbeitskosten basierend auf Produkten und Raum"""
    hours = Decimal('0')
    for item in items:
        product = get_product(item.product_id)
        # Aufwandsfaktor pro Produkt (in Produktdaten hinterlegt)
        labor_factor = get_labor_factor(product.id)
        hours += item.quantity * labor_factor

    hourly_rate = get_hourly_rate(region)  # Regionalabhaengig
    return hours * hourly_rate
```

---

### SCHRITT 4: Raumaufmass-Modul (AP-04)

Erweitere die bestehende Raumaufmass-Eingabe:

**Frontend-Formular (HTML/JS):**
```html
<div class="room-measurement-form" id="step-raumaufmass">
  <h3>Raumaufmass</h3>

  <select id="room-type" required>
    <option value="">Raumtyp waehlen...</option>
    <option value="bad">Badezimmer</option>
    <option value="gaeste-wc">Gaeste-WC</option>
    <option value="duschbad">Duschbad</option>
  </select>

  <div class="dimensions">
    <label>Laenge (cm) <input type="number" id="room-length" min="50" max="1000" required></label>
    <label>Breite (cm) <input type="number" id="room-width" min="50" max="1000" required></label>
    <label>Hoehe (cm) <input type="number" id="room-height" min="200" max="400" value="240" required></label>
  </div>

  <div class="openings">
    <label>Anzahl Tueren <input type="number" id="door-count" min="0" max="3" value="1"></label>
    <label>Anzahl Fenster <input type="number" id="window-count" min="0" max="3" value="0"></label>
  </div>

  <div class="existing-fixtures">
    <h4>Vorhandene Ausstattung</h4>
    <label><input type="checkbox" name="existing" value="bathtub"> Badewanne</label>
    <label><input type="checkbox" name="existing" value="shower"> Dusche</label>
    <label><input type="checkbox" name="existing" value="toilet"> WC</label>
    <label><input type="checkbox" name="existing" value="sink"> Waschbecken</label>
    <label><input type="checkbox" name="existing" value="radiator"> Heizkoerper</label>
  </div>

  <div class="calculated-values" id="room-calc">
    <!-- Automatisch berechnet und angezeigt -->
  </div>
</div>
```

**Auto-Berechnung (JS):**
```javascript
function calculateRoomValues() {
    const L = parseInt(document.getElementById('room-length').value) || 0;
    const B = parseInt(document.getElementById('room-width').value) || 0;
    const H = parseInt(document.getElementById('room-height').value) || 0;
    const doors = parseInt(document.getElementById('door-count').value) || 0;
    const windows = parseInt(document.getElementById('window-count').value) || 0;

    const doorArea = doors * 0.9 * 2.1;    // Standard-Tuer 90x210cm
    const windowArea = windows * 0.8 * 1.0; // Standard-Fenster 80x100cm

    const floorArea = (L * B) / 10000;                           // m²
    const wallAreaGross = 2 * (L + B) * H / 10000;               // m²
    const wallAreaNet = wallAreaGross - doorArea - windowArea;     // m²
    const perimeter = 2 * (L + B) / 100;                         // lfm
    const cornerCount = 4 + (doors * 2) + (windows * 2);

    document.getElementById('room-calc').innerHTML = `
        <p>Bodenflaeche: <strong>${floorArea.toFixed(2)} m²</strong></p>
        <p>Wandflaeche (brutto): <strong>${wallAreaGross.toFixed(2)} m²</strong></p>
        <p>Wandflaeche (netto): <strong>${wallAreaNet.toFixed(2)} m²</strong></p>
        <p>Umfang: <strong>${perimeter.toFixed(2)} lfm</strong></p>
        <p>Ecken/Kanten: <strong>${cornerCount}</strong></p>
    `;

    return {
        length_cm: L, width_cm: B, height_cm: H,
        door_count: doors, window_count: windows,
        floor_area_m2: floorArea,
        wall_area_gross_m2: wallAreaGross,
        wall_area_net_m2: wallAreaNet,
        perimeter_m: perimeter,
        corner_count: cornerCount
    };
}
```

---

### SCHRITT 5: Dynamische Formulare (AP-05)

**JSON-Schema pro Workflow-Schritt:**

```json
{
  "step": 6,
  "name": "dusche",
  "fields": [
    {
      "id": "dusch_typ",
      "label": "Typ waehlen",
      "type": "select",
      "required": true,
      "options": [
        {"value": "bodengleich", "label": "Bodengleiche Dusche"},
        {"value": "duschtasse", "label": "Duschtasse"},
        {"value": "badewanne", "label": "Badewanne"}
      ]
    },
    {
      "id": "tassen_modell",
      "label": "Duschtassen-Modell",
      "type": "product_select",
      "category": "duschtassen",
      "visible_when": {"field": "dusch_typ", "equals": "duschtasse"},
      "required_when_visible": true
    },
    {
      "id": "tassen_groesse",
      "label": "Groesse",
      "type": "variant_select",
      "variant_type": "Groesse",
      "depends_on_product": "tassen_modell",
      "visible_when": {"field": "dusch_typ", "equals": "duschtasse"}
    },
    {
      "id": "tassen_farbe",
      "label": "Farbe",
      "type": "variant_select",
      "variant_type": "Farbe",
      "depends_on_product": "tassen_modell",
      "visible_when": {"field": "dusch_typ", "equals": "duschtasse"}
    },
    {
      "id": "wannen_modell",
      "label": "Wannen-Modell",
      "type": "product_select",
      "category": "badewannen",
      "visible_when": {"field": "dusch_typ", "equals": "badewanne"},
      "required_when_visible": true
    },
    {
      "id": "wannen_groesse",
      "label": "Groesse",
      "type": "variant_select",
      "variant_type": "Groesse",
      "depends_on_product": "wannen_modell",
      "visible_when": {"field": "dusch_typ", "equals": "badewanne"}
    },
    {
      "id": "dusch_armatur",
      "label": "Armatur",
      "type": "product_select",
      "category": "armaturen_dusche",
      "visible_when": {"field": "dusch_typ", "in": ["bodengleich", "duschtasse"]},
      "required_when_visible": true
    }
  ]
}
```

**Form-Renderer (JS):**
```javascript
class DynamicFormRenderer {
    constructor(containerId, schema, offerState) {
        this.container = document.getElementById(containerId);
        this.schema = schema;
        this.state = offerState;
        this.values = {};
    }

    render() {
        this.container.innerHTML = '';
        for (const field of this.schema.fields) {
            if (this.isVisible(field)) {
                this.container.appendChild(this.createField(field));
            }
        }
    }

    isVisible(field) {
        if (!field.visible_when) return true;
        const cond = field.visible_when;
        const currentValue = this.values[cond.field];
        if (cond.equals) return currentValue === cond.equals;
        if (cond.in) return cond.in.includes(currentValue);
        if (cond.not_equals) return currentValue !== cond.not_equals;
        return true;
    }

    createField(field) {
        const wrapper = document.createElement('div');
        wrapper.className = 'form-field';
        wrapper.dataset.fieldId = field.id;

        const label = document.createElement('label');
        label.textContent = field.label;
        if (field.required || field.required_when_visible) {
            label.innerHTML += ' <span class="required">*</span>';
        }
        wrapper.appendChild(label);

        let input;
        switch (field.type) {
            case 'select':
                input = this.createSelect(field);
                break;
            case 'product_select':
                input = this.createProductSelect(field);
                break;
            case 'variant_select':
                input = this.createVariantSelect(field);
                break;
            case 'number':
                input = this.createNumberInput(field);
                break;
            case 'catalog_select':
                input = this.createCatalogButton(field);
                break;
            default:
                input = this.createTextInput(field);
        }

        input.addEventListener('change', (e) => {
            this.values[field.id] = e.target.value;
            this.onFieldChange(field, e.target.value);
            this.render();  // Re-render fuer bedingte Felder
        });

        wrapper.appendChild(input);
        return wrapper;
    }

    createProductSelect(field) {
        const select = document.createElement('select');
        select.id = field.id;
        select.innerHTML = '<option value="">Produkt waehlen...</option>';

        // Produkte aus API laden
        fetch(`/api/products?category=${field.category}`)
            .then(r => r.json())
            .then(products => {
                for (const p of products) {
                    const opt = document.createElement('option');
                    opt.value = p.id;
                    opt.textContent = `${p.name} — ${p.base_price_net.toFixed(2)} EUR`;
                    select.appendChild(opt);
                }
            });

        return select;
    }

    createVariantSelect(field) {
        const select = document.createElement('select');
        select.id = field.id;
        select.innerHTML = '<option value="">Variante waehlen...</option>';

        const productId = this.values[field.depends_on_product];
        if (productId) {
            fetch(`/api/products/${productId}/variants?type=${field.variant_type}`)
                .then(r => r.json())
                .then(variants => {
                    for (const v of variants) {
                        const opt = document.createElement('option');
                        opt.value = v.id;
                        const modifier = v.price_modifier > 0 ? ` (+${v.price_modifier.toFixed(2)} EUR)` : '';
                        opt.textContent = `${v.value}${modifier}`;
                        select.appendChild(opt);
                    }
                });
        }

        return select;
    }

    async onFieldChange(field, value) {
        // Produkt geaendert → Dependencies evaluieren
        if (field.type === 'product_select' || field.type === 'variant_select') {
            await this.evaluateDependencies();
            await this.recalculate();
        }
    }

    async evaluateDependencies() {
        const response = await fetch(`/api/offers/${this.state.offerId}/evaluate-dependencies`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({values: this.values})
        });
        const result = await response.json();
        // Auto-Artikel anzeigen, Ausschluesse deaktivieren
        this.state.autoItems = result.add;
        this.state.excludedProducts = result.remove;
        this.updateAutoItemsDisplay();
    }

    async recalculate() {
        const response = await fetch(`/api/offers/${this.state.offerId}/calculate`);
        const calc = await response.json();
        this.updatePriceDisplay(calc);
    }

    updatePriceDisplay(calc) {
        const priceEl = document.getElementById('live-price');
        if (priceEl) {
            priceEl.innerHTML = `
                <div class="price-summary">
                    <div class="price-row">Material: <strong>${calc.subtotal_material.toFixed(2)} EUR</strong></div>
                    <div class="price-row">Arbeitsleistung: <strong>${calc.subtotal_labor.toFixed(2)} EUR</strong></div>
                    <div class="price-row discount">Rabatte: <strong>-${calc.discount_total.toFixed(2)} EUR</strong></div>
                    <div class="price-row">Marge (${calc.margin_pct}%): <strong>${calc.margin_amount.toFixed(2)} EUR</strong></div>
                    <div class="price-row">Netto: <strong>${calc.net_total.toFixed(2)} EUR</strong></div>
                    <div class="price-row">MwSt (${calc.tax_rate}%): <strong>${calc.tax_amount.toFixed(2)} EUR</strong></div>
                    <hr>
                    <div class="price-row total">Gesamt (brutto): <strong>${calc.gross_total.toFixed(2)} EUR</strong></div>
                </div>
            `;
        }
    }

    validate() {
        const errors = [];
        for (const field of this.schema.fields) {
            if (!this.isVisible(field)) continue;
            const isRequired = field.required || field.required_when_visible;
            if (isRequired && !this.values[field.id]) {
                errors.push(`${field.label} ist ein Pflichtfeld`);
            }
        }
        return errors;
    }
}
```

---

### SCHRITT 6: PDF-Katalog-Integration (AP-07)

**PDF.js einbinden:**
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.min.mjs" type="module"></script>
```

**Katalog-Viewer (JS):**
```javascript
class CatalogViewer {
    constructor(containerId, onProductSelect) {
        this.container = document.getElementById(containerId);
        this.onProductSelect = onProductSelect;
        this.currentPage = 1;
        this.pdf = null;
        this.hotspots = [];
    }

    async open(catalogId) {
        // Katalog-Daten laden
        const response = await fetch(`/api/catalogs/${catalogId}`);
        const catalog = await response.json();

        // Hotspots laden
        const hsResponse = await fetch(`/api/catalogs/${catalogId}/hotspots`);
        this.hotspots = await hsResponse.json();

        // PDF laden
        const pdfjsLib = window['pdfjs-dist/build/pdf'];
        this.pdf = await pdfjsLib.getDocument(catalog.pdf_url).promise;

        this.showModal();
        this.renderPage(1);
    }

    async renderPage(pageNum) {
        this.currentPage = pageNum;
        const page = await this.pdf.getPage(pageNum);
        const viewport = page.getViewport({scale: 1.5});

        const canvas = this.container.querySelector('#catalog-canvas');
        canvas.width = viewport.width;
        canvas.height = viewport.height;

        const ctx = canvas.getContext('2d');
        await page.render({canvasContext: ctx, viewport}).promise;

        this.renderHotspots(pageNum, viewport);
        this.updateNavigation();
    }

    renderHotspots(pageNum, viewport) {
        const overlay = this.container.querySelector('#hotspot-overlay');
        overlay.innerHTML = '';
        overlay.style.width = viewport.width + 'px';
        overlay.style.height = viewport.height + 'px';

        const pageHotspots = this.hotspots.filter(h => h.page_number === pageNum);
        for (const hs of pageHotspots) {
            const div = document.createElement('div');
            div.className = 'hotspot';
            div.style.left = (hs.x_pct * viewport.width / 100) + 'px';
            div.style.top = (hs.y_pct * viewport.height / 100) + 'px';
            div.style.width = (hs.width_pct * viewport.width / 100) + 'px';
            div.style.height = (hs.height_pct * viewport.height / 100) + 'px';
            div.title = hs.product_name;
            div.addEventListener('click', () => {
                this.onProductSelect(hs.product_id, hs.product_name);
                div.classList.add('selected');
            });
            overlay.appendChild(div);
        }
    }

    showModal() {
        this.container.innerHTML = `
            <div class="catalog-modal">
                <div class="catalog-header">
                    <button id="catalog-prev">&#9664; Zurueck</button>
                    <span id="catalog-page-info">Seite 1 / ?</span>
                    <button id="catalog-next">Weiter &#9654;</button>
                    <button id="catalog-close">Schliessen</button>
                </div>
                <div class="catalog-body" style="position:relative">
                    <canvas id="catalog-canvas"></canvas>
                    <div id="hotspot-overlay" style="position:absolute;top:0;left:0"></div>
                </div>
            </div>
        `;
        this.container.querySelector('#catalog-prev').onclick = () => this.prevPage();
        this.container.querySelector('#catalog-next').onclick = () => this.nextPage();
        this.container.querySelector('#catalog-close').onclick = () => this.close();
        this.container.style.display = 'block';
    }

    prevPage() { if (this.currentPage > 1) this.renderPage(this.currentPage - 1); }
    nextPage() { if (this.currentPage < this.pdf.numPages) this.renderPage(this.currentPage + 1); }
    close() { this.container.style.display = 'none'; }

    updateNavigation() {
        const info = this.container.querySelector('#catalog-page-info');
        if (info) info.textContent = `Seite ${this.currentPage} / ${this.pdf.numPages}`;
    }
}
```

---

### SCHRITT 7: Rabatt-System & Live-Vorschau (AP-06, AP-08)

Die Kalkulationsengine aus Schritt 3 enthaelt bereits die Rabatt-Logik. Fuer das Frontend:

```javascript
// Rabatt-UI
function renderDiscountSection(offerId, currentDiscounts) {
    return `
        <div class="discount-section">
            <h4>Rabatte</h4>
            <div id="discount-list">
                ${currentDiscounts.map(d => `
                    <div class="discount-row">
                        <span>${d.name}</span>
                        <span>${d.is_percentage ? d.value + '%' : d.value.toFixed(2) + ' EUR'}</span>
                        <button onclick="removeDiscount(${offerId}, '${d.name}')">X</button>
                    </div>
                `).join('')}
            </div>
            <div class="add-discount">
                <input type="text" id="discount-name" placeholder="Rabattbezeichnung">
                <input type="number" id="discount-value" step="0.01" placeholder="Wert">
                <select id="discount-type">
                    <option value="percentage">Prozent (%)</option>
                    <option value="fixed">Festbetrag (EUR)</option>
                </select>
                <button onclick="addDiscount(${offerId})">Hinzufuegen</button>
            </div>
            <div class="margin-setting">
                <label>Marge: <input type="number" id="margin-pct" value="15" min="0" max="50" step="0.5"> %</label>
                <button onclick="updateMargin(${offerId})">Aktualisieren</button>
            </div>
        </div>
    `;
}

// Live-Vorschau: Debounced Recalculation
let recalcTimer = null;
function triggerRecalculation(offerId) {
    clearTimeout(recalcTimer);
    recalcTimer = setTimeout(async () => {
        const response = await fetch(`/api/offers/${offerId}/calculate`);
        const calc = await response.json();
        document.getElementById('live-price').innerHTML = formatPriceSummary(calc);
    }, 300);
}
```

---

### SCHRITT 8: Angebots-PDF-Generierung (AP-09)

**API-Endpunkt:** `POST /api/offers/{id}/generate-pdf`

Implementiere serverseitig mit der vorhandenen Backend-Technologie (nach Server-Analyse anpassen):

```python
# Beispiel mit WeasyPrint (Python)
from weasyprint import HTML

def generate_offer_pdf(offer_id):
    offer = get_offer(offer_id)
    calc = calculate_offer(offer_id)
    items = get_offer_items(offer_id)

    html_content = render_template('offer_pdf.html',
        offer=offer,
        calc=calc,
        items=items,
        company={
            "name": "ISOTEC Kiel",
            "address": "...",
            "logo_url": "/static/logo.png"
        }
    )

    pdf_bytes = HTML(string=html_content).write_pdf()

    filename = f"Angebot_{offer.id}_{offer.customer_name.replace(' ', '_')}.pdf"
    save_path = f"/media/offers/{filename}"

    with open(save_path, 'wb') as f:
        f.write(pdf_bytes)

    return {"pdf_url": f"/media/offers/{filename}"}
```

---

### SCHRITT 9: E2E-Validierung (AP-12)

Nach Implementierung aller Schritte:

1. Erstelle 10 Referenz-Angebote im Viterma BLS
2. Dokumentiere fuer jedes: Raumdaten, gewaehlte Produkte, Einzelpreise, Gesamtpreis
3. Stelle die gleichen Angebote in der Kopie nach
4. Vergleiche automatisiert:

```python
def validate_against_bls(reference_offers):
    results = []
    for ref in reference_offers:
        our_calc = calculate_offer(ref['offer_id_kopie'])
        bls_total = ref['bls_gross_total']
        our_total = our_calc['gross_total']
        diff = abs(bls_total - our_total)
        passed = diff <= 0.01

        results.append({
            "name": ref['name'],
            "bls_total": bls_total,
            "our_total": our_total,
            "diff": diff,
            "passed": passed
        })

    all_passed = all(r['passed'] for r in results)
    return {"results": results, "all_passed": all_passed}
```

---

### SCHRITT 10: Deployment

```bash
SSH_SERVER="root@46.225.166.62"

# 1. Backup
ssh $SSH_SERVER "mkdir -p /root/backups/$(date +%Y%m%d_%H%M%S) && cp -r /pfad/zum/projekt /root/backups/$(date +%Y%m%d_%H%M%S)/"

# 2. Code deployen (Pfade aus Schritt 0 anpassen!)
scp -r ./neue-dateien/* $SSH_SERVER:/pfad/zum/projekt/

# 3. Datenbank-Migration
ssh $SSH_SERVER "cd /pfad/zum/projekt && sqlite3 database.db < migrations/001_products.sql"
# ODER fuer PostgreSQL/MySQL:
ssh $SSH_SERVER "cd /pfad/zum/projekt && python manage.py migrate"

# 4. Produktdaten importieren
ssh $SSH_SERVER "cd /pfad/zum/projekt && python import_products.py"

# 5. Services neustarten
ssh $SSH_SERVER "systemctl restart nginx"
ssh $SSH_SERVER "systemctl restart gunicorn 2>/dev/null || pm2 restart all 2>/dev/null || systemctl restart php-fpm 2>/dev/null"

# 6. Smoke-Test
STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://dashboard.isotec-kiel.eu/dashboard/vit-Angebote/)
if [ "$STATUS" = "200" ] || [ "$STATUS" = "302" ]; then
    echo "DEPLOYMENT ERFOLGREICH (HTTP $STATUS)"
else
    echo "FEHLER HTTP $STATUS — Rollback wird ausgefuehrt..."
    ssh $SSH_SERVER "cp -r /root/backups/LETZTES_BACKUP/* /pfad/zum/projekt/ && systemctl restart nginx"
fi
```

---

## ARBEITSREIHENFOLGE (zusammengefasst)

```
SCHRITT 0  → Server analysieren, Pfade/Technologie identifizieren
SCHRITT 1  → Produktdaten aus BLS erfassen + DB-Schema anlegen
SCHRITT 2  → Abhaengigkeits-Engine implementieren
SCHRITT 3  → Kalkulationsengine implementieren
SCHRITT 4  → Raumaufmass-Modul erweitern
SCHRITT 5  → Dynamische Formulare mit JSON-Schema
SCHRITT 6  → PDF-Katalog-Integration (PDF.js)
SCHRITT 7  → Rabatt-System + Live-Preisvorschau
SCHRITT 8  → Angebots-PDF-Generierung
SCHRITT 9  → E2E-Validierung gegen BLS-Referenzwerte
SCHRITT 10 → Deployment mit Backup + Smoke-Test
```

## WICHTIGE REGELN

1. **Vor jeder Datei-Aenderung:** Backup des Originals erstellen
2. **Nach jedem Schritt:** Testen ob die Seite noch funktioniert
3. **Pfade anpassen:** Alle `/pfad/zum/projekt/` durch tatsaechliche Pfade aus Schritt 0 ersetzen
4. **Produktdaten:** Muessen exakt aus dem BLS kommen — keine Schaetzungen
5. **Kalkulation:** Max. 0.01 EUR Abweichung zum BLS toleriert
6. **Rollback:** Bei jedem Fehler sofort Backup wiederherstellen
7. **Kein Ueberschreiben:** Bestehende funktionierende Features nicht beschaedigen

---

*Master-Prompt Version 1.0 | 2026-03-13 | Projekt ISOTEC-Kiel / Viterma BLS Migration*

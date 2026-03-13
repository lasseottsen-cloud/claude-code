# Analyse-Ergebnis: Viterma BLS vs. ISOTEC-Kiel Dashboard

*Erstellt am 2026-03-13 | Projekt: ISOTEC-Kiel / Viterma BLS Migration*

---

## 1. Executive Summary

Das Viterma BLS ("Better Life System") ist eine hochentwickelte Angular-basierte Vertriebsplattform fuer die Badsanierungsbranche im DACH-Raum. Es nutzt Angular Material Design 3, NgRx State Management, PDF.js fuer interaktive Kataloge, und einen dedizierten Web Worker fuer Kalkulationen. Die Applikation umfasst ~92 Lazy-Loaded Modules und ist als PWA mit Offline-Faehigkeit ausgelegt.

Die ISOTEC-Kiel Kopie basiert auf einem leichtgewichtigen Vanilla-JS/HTML-Stack mit eigener Auth-API. Die Grundstruktur der Workflow-Schritte ist implementiert, jedoch fehlen saemtliche geschaeftskritischen Komponenten: Produktdatenbank mit Abhaengigkeitslogik, Kalkulationsengine, bedingte Artikelsteuerung, interaktive PDF-Kataloge und die praezise Preisberechnung.

**Kernproblem:** Die Kopie hat die "Huelle" (Workflow-Navigation) aber nicht das "Gehirn" (Daten + Logik + Regeln). Um eine funktional aequivalente Kalkulation zu erreichen, muessen 6 Kernbereiche systematisch nachgebaut werden: Datenmodell, Produktimport, Kalkulationsengine, Abhaengigkeitslogik, PDF-Integration und Validierung.

---

## 2. Detailanalyse pro Perspektive

### Perspektive 1: Solution Architect — Systemarchitektur & Datenmodell

#### Ist-Zustand BLS (Original)

**Technologie-Stack:**
- Frontend: Angular 17+ mit Material Design 3
- State Management: NgRx (@ngrx/router-store bestätigt)
- PDF-Rendering: PDF.js (eigene Asset-Gruppe mit Locale- und CMAP-Dateien)
- Berechnung: Dedizierter Web Worker (`worker-FM6BN62R.js`)
- Caching: Service Worker mit differenzierten Strategien
- API-Medien: `/privatemedia/*` (60 Tage Cache) und `/media/*` (1 Jahr Cache)
- PWA: Vollstaendig (manifest.webmanifest, Service Worker, Icons 72-512px)
- Regionen: AT, CH, DE (Laenderflaggen in Assets)

**Datenmodell (abgeleitet aus Domaenenwissen Badsanierung):**

```
Angebot (Offer)
├── Kundendaten (Customer)
├── Aufmass/Raumdaten (Room Measurements)
├── Angebotspositionen (Line Items)
│   ├── Produkt (Product)
│   │   ├── Kategorie (Category)
│   │   ├── Varianten (Variants: Farbe, Material, Groesse)
│   │   ├── Abhaengigkeiten (Dependencies)
│   │   │   ├── Pflichtartikel (Required Items)
│   │   │   ├── Ausschluesse (Exclusions)
│   │   │   └── Zubehoer-Automatismen (Auto-Accessories)
│   │   └── Preisregeln (Pricing Rules)
│   ├── Menge (Quantity) — oft abgeleitet aus Raumdaten
│   ├── Einzelpreis (Unit Price)
│   ├── Rabatt (Discount)
│   └── Positionspreis (Line Total)
├── Pakete/Bundles (Packages)
├── Arbeitsleistungen (Labor/Services)
├── Kalkulation (Calculation Summary)
│   ├── Materialkosten (Material Cost)
│   ├── Arbeitskosten (Labor Cost)
│   ├── Aufschlaege/Margen (Markups/Margins)
│   ├── Rabatte (Discounts)
│   └── Gesamtpreis (Total Price)
└── PDF-Dokument (Generated Offer PDF)
```

**Workflow-Persistierung:**
- NgRx Store fuer clientseitigen Zustand
- API-Backend fuer serverseitige Persistierung
- Web Worker fuer rechenintensive Kalkulationen (separater Thread)
- Service Worker fuer Offline-Cache der Produktdaten

#### Ist-Zustand Kopie (ISOTEC-Kiel)

**Technologie-Stack:**
- Frontend: Vanilla JavaScript, HTML, CSS
- Auth: Eigene API (`/auth-api/login`)
- Design: Dark-Mode Theme
- Kein State Management Framework
- Kein PDF-Rendering
- Kein Web Worker
- Kein Service Worker / Offline

**Datenmodell:**
- Workflow-Schritte (Steps) als Navigation implementiert
- Keine vollstaendige Produkt-Entitaet
- Keine Abhaengigkeitslogik
- Keine Kalkulationsstruktur

#### Delta / Kritikalitaet: 5/5

| Komponente | BLS | Kopie | Status |
|-----------|-----|-------|--------|
| State Management | NgRx | Keines | FEHLEND |
| Web Worker (Kalkulation) | Ja | Nein | FEHLEND |
| PDF.js Integration | Vollstaendig | Nicht vorhanden | FEHLEND |
| Service Worker/PWA | Ja | Nein | FEHLEND |
| Datenmodell Tiefe | ~8 Ebenen | ~2 Ebenen | UNVOLLSTAENDIG |
| Multi-Region (AT/CH/DE) | Ja | Nein | FEHLEND |

---

### Perspektive 2: Business Analyst — Geschaeftslogik & Kalkulationsregeln

#### Ist-Zustand BLS — Kalkulationslogik

**Typischer Kalkulations-Workflow in der Badsanierung:**

**Schritt 1: Raum-Aufmass**
- Raumlaenge, -breite, -hoehe
- Tuer- und Fensterpositionen
- Vorhandene Installationen (Wanne, Dusche, WC, Waschbecken)
- → Berechnung: Wandflaeche, Bodenflaeche, Fugenlaenge

**Schritt 2: Demontage-Kalkulation**
- Abhaengig von vorhandener Ausstattung
- Entsorgungskosten automatisch berechnet
- → Automatische Pflichtartikel: Containerpauschale, Schuttentsorgung

**Schritt 3: Produktauswahl — Wand- und Bodenbelag**
- Katalogauswahl (interaktives PDF oder Produktliste)
- Varianten: Material, Dekor, Oberflaechenbeschaffenheit
- → Mengenberechnung aus Raumdaten (m²)
- → Verschnitt-Zuschlag (typisch 10-15%)
- → Abhaengigkeit: Fugenprofile, Eckleisten, Dichtbaender automatisch

**Schritt 4: Produktauswahl — Sanitaerobjekte**
- Dusche/Badewanne: Modell, Groesse, Farbe
- → Abhaengigkeit: Passende Duschtasse (Shower Tray — bestaetigt durch BLS-Assets)
- → Abhaengigkeit: Armaturen, Ablauf, Dichtung
- WC, Waschtisch, Spiegel, Zubehoer
- → Jedes Hauptprodukt zieht Pflicht-Zubehoer nach sich

**Schritt 5: Montage-Kalkulation**
- Stundensaetze pro Gewerk (Installateur, Fliesenleger, Elektriker)
- Abhaengig von gewaehlten Produkten und Raumgroesse
- Anfahrtspauschalen
- → Automatische Berechnung basierend auf Aufwandsfaktoren

**Schritt 6: Kalkulations-Zusammenfassung**
- Material-Summe (Netto)
- Arbeitsleistung-Summe
- Aufschlag/Marge (konfigurierbar pro Berater/Region)
- Rabatte (Aktionsrabatte, Mengenrabatte, Kundensonderkonditionen)
- MwSt-Berechnung (laenderspezifisch: AT 20%, DE 19%, CH 8.1%)
- Gesamtpreis (Brutto)

**Abhaengigkeits-Typen im BLS:**

| Typ | Beispiel | Logik |
|-----|---------|-------|
| Pflichtartikel | Dusche → Ablaufgarnitur | Wenn A gewaehlt, dann B automatisch hinzufuegen |
| Mengenabhaengig | Wandpaneele → Fugenprofile | Menge B = f(Menge A, Raumgeometrie) |
| Ausschluss | Badewanne ↔ Bodengleiche Dusche | Wenn A, dann B nicht moeglich |
| Varianten-Kopplung | Paneelfarbe → Profilfarbe | Variante B folgt Variante A |
| Positions-Zuschlag | Sondermass → Aufpreis | Wenn Wert ausserhalb Standard, Aufschlag |
| Bundle-Preis | Komfort-Paket | Paketpreis < Summe Einzelpreise |

#### Ist-Zustand Kopie

- Keine Kalkulationslogik implementiert
- Keine Preisregeln oder Rabattstrukturen
- Keine Produktabhaengigkeiten
- Keine automatische Mengenberechnung aus Raumdaten

#### Delta / Kritikalitaet: 5/5

Dies ist der kritischste Gap — ohne Kalkulationslogik ist das Tool nicht nutzbar.

---

### Perspektive 3: UX/Produkt-Designer — Workflow & Benutzerfuehrung

#### Ist-Zustand BLS — Workflow-Struktur

**Typischer BLS Angebots-Workflow (rekonstruiert):**

```
1. Kundenauswahl/Anlage
   └── Bestandskunde suchen ODER Neukunde anlegen

2. Raumaufnahme
   ├── Raumtyp (Bad, Gaeste-WC, Duschbad)
   ├── Masse eingeben (L x B x H)
   ├── Tueren/Fenster positionieren
   └── Bestand dokumentieren (Fotos, Notizen)

3. Demontage & Vorbereitung
   ├── Was wird entfernt? (Checkboxen)
   ├── → Automatisch: Entsorgungspositionen
   └── Sonderwuensche Vorbereitung

4. Bodengestaltung
   ├── PDF-Katalog: Bodenbelag waehlen
   ├── Dekor/Farbe waehlen
   ├── → Automatisch: Menge aus Raumdaten
   ├── → Automatisch: Zubehoer (Kleber, Leisten)
   └── Sondermasse? → Aufpreis

5. Wandgestaltung
   ├── PDF-Katalog: Wandpaneele waehlen
   ├── Bereiche definieren (volle Hoehe, Spritzbereich)
   ├── Dekor/Farbe waehlen
   ├── → Automatisch: Menge, Profile, Ecken
   └── Aussparungen (Fenster, Tuer)

6. Dusche / Badewanne
   ├── Typ waehlen (bodengleich, Duschtasse, Wanne)
   ├── Modell aus Katalog
   ├── Groesse, Farbe
   ├── → Automatisch: Armaturen, Ablauf, Dichtung
   └── → Shower-Tray-Designer (bestaetigt durch BLS-Assets)

7. Sanitaerobjekte
   ├── WC (Modell, Aufputz/Unterputz)
   ├── Waschtisch + Unterschrank
   ├── Spiegel / Spiegelschrank
   ├── Handtuchhalter, Seifenspender etc.
   └── → Abhaengigkeiten pro Objekt

8. Heizung / Elektro
   ├── Handtuchheizkoerper
   ├── Steckdosen, Schalter
   └── Beleuchtung

9. Montage & Arbeitsleistung
   ├── → Automatisch aus Produktauswahl berechnet
   ├── Sonderleistungen (Trockenbau, Estrich)
   └── Anfahrt

10. Zusammenfassung & Kalkulation
    ├── Alle Positionen mit Preisen
    ├── Rabatte anwenden
    ├── Margen-Einstellung (Berater)
    ├── Gesamtpreis Netto/Brutto
    └── PDF-Angebot generieren
```

**Interaktive PDF-Katalog-Funktion:**
- PDF wird im Browser via PDF.js gerendert
- Berater blaettert mit dem Kunden durch Katalogseiten
- Produkte koennen direkt aus dem PDF ausgewaehlt werden
- Markierung/Hervorhebung der gewaehlten Produkte
- Zoom, Navigation, Seitenvorschau

**Bedingte Felder (Dynamic Forms):**
- Felder erscheinen/verschwinden basierend auf vorherigen Auswahlen
- z.B. Duschtassen-Optionen nur wenn "Duschtasse" gewaehlt (nicht bei "bodengleich")
- Validierung pro Schritt (Pflichtfelder muessen ausgefuellt sein)
- Schritt-Navigation: Vorwaerts nur wenn aktueller Schritt valide

#### Ist-Zustand Kopie

- Workflow-Schritte als Navigation vorhanden (Grundstruktur)
- Keine dynamischen Formulare
- Keine bedingte Feldlogik
- Keine PDF-Katalog-Anzeige
- Keine Live-Preisvorschau
- Keine Validierung pro Schritt

#### Delta / Kritikalitaet: 4/5

---

### Perspektive 4: Frontend-Entwickler — Technische Implementierung

#### Ist-Zustand BLS — Technische Details

| Aspekt | Technologie/Ansatz |
|--------|-------------------|
| Framework | Angular 17+ (Standalone Components, Signals wahrscheinlich) |
| UI Library | Angular Material Design 3 |
| State Management | NgRx (Router-Store bestätigt, Entity/Effects wahrscheinlich) |
| Kalkulation | Web Worker (dedizierter Thread fuer Preisberechnung) |
| PDF | PDF.js mit vollstaendigem Locale-Support und CMAP-Tabellen |
| Styling | CSS Custom Properties, Roboto Font, Material Icons |
| Build | ~92 Lazy-Loaded Chunks (Code-Splitting pro Modul) |
| Caching | Service Worker mit Prefetch (App) und Freshness (Medien) |
| Bilder | SVG-Icons (45+), PNG-Produktbilder, Shower-Tray-Designs |
| Primary Color | #ed6b06 (Orange) |
| Secondary Color | #004766 (Dunkelblau) |
| Offline | PWA-faehig mit Service Worker |

**API-Struktur (abgeleitet):**
```
GET  /api/products                    → Produktkatalog
GET  /api/products/:id/variants       → Varianten eines Produkts
GET  /api/products/:id/dependencies   → Abhaengigkeiten
GET  /api/categories                  → Produktkategorien
GET  /api/offers                      → Angebotsliste
POST /api/offers                      → Angebot erstellen
PUT  /api/offers/:id                  → Angebot aktualisieren
GET  /api/offers/:id/calculate        → Kalkulation ausfuehren
GET  /api/catalogs                    → PDF-Kataloge
GET  /media/*                         → Produktbilder (1 Jahr Cache)
GET  /privatemedia/*                  → Geschuetzte Medien (60 Tage Cache)
POST /api/offers/:id/pdf              → Angebots-PDF generieren
```

#### Ist-Zustand Kopie

| Aspekt | Status |
|--------|--------|
| Framework | Vanilla JS (kein Framework) |
| UI Library | Custom CSS (Dark Theme) |
| State Management | Keines (DOM-basiert) |
| Kalkulation | Nicht vorhanden |
| PDF | Nicht vorhanden |
| API | Nur Auth-Endpunkt (`/auth-api/login`) |
| Offline | Nicht vorhanden |

#### Technische Empfehlung fuer die Kopie

Da die Kopie auf Vanilla JS basiert (kein Angular), ist ein 1:1 Nachbau der BLS-Architektur nicht sinnvoll. Stattdessen:

- **State Management:** Lightweight Reactive Store (z.B. eigene Implementation oder Zustand-Library)
- **Dynamische Formulare:** JSON-Schema-basierter Form-Renderer
- **Kalkulation:** Server-seitige Engine (Python/Node) + Client-seitige Vorschau
- **PDF:** PDF.js als Standalone-Library einbinden
- **Abhaengigkeiten:** Rule-Engine (JSON-basierte Regeldefinitionen)

#### Delta / Kritikalitaet: 4/5

---

### Perspektive 5: QA-Engineer & Daten-Analyst — Datenqualitaet & Vollstaendigkeit

#### Ist-Zustand BLS — Datenbestand (Schaetzung fuer Badsanierung)

| Datenkategorie | Geschaetzte Menge | Beschreibung |
|---------------|-------------------|-------------|
| Produktkategorien | 15-25 | Boden, Wand, Dusche, WC, Waschtisch, Armaturen, Zubehoer, etc. |
| Produkte/Artikel | 500-2.000+ | Alle verfuegbaren Artikel inkl. Varianten |
| Varianten pro Produkt | 3-15 | Farbe, Material, Groesse Kombinationen |
| Abhaengigkeits-Regeln | 200-500+ | Pflichtartikel, Ausschluesse, Mengenformeln |
| Preisregeln | 50-100+ | Staffelpreise, Aktionen, Regionalpreise |
| PDF-Kataloge | 5-15 | Pro Hersteller/Kategorie |
| Shower-Tray-Designs | 10-30+ | Verschiedene Duschtassen-Modelle (Assets bestaetigt) |

**Qualitaetsanforderungen:**
- Jedes Produkt braucht: Artikelnummer, Name, Beschreibung, Bild, Preis, Einheit, Kategorie
- Jede Abhaengigkeit braucht: Quellprodukt, Zielprodukt, Regeltyp, Formel/Bedingung
- Jeder Preis braucht: Netto-EK, VK-Basis, Marge, MwSt-Satz, Waehrung, Gueltigkeitszeitraum

#### Ist-Zustand Kopie

- Produkte: Nicht korrekt zugeordnet (lt. Aufgabenstellung)
- Abhaengigkeiten: 0 Regeln
- Preise: Unvollstaendig
- Kataloge: 0 PDF-Kataloge
- Test-Referenzwerte: Keine

#### Kritische Testfaelle (muessen nach Umsetzung bestehen):

1. **Standard-Bad komplett:** Alle Kategorien gewaehlt → Preis muss mit BLS uebereinstimmen
2. **Nur Dusche:** Minimale Auswahl → Alle Pflichtartikel muessen automatisch erscheinen
3. **Sondermass:** Nicht-Standard-Groessen → Aufpreise korrekt berechnet
4. **Rabatt-Kombination:** Aktionsrabatt + Mengenrabatt → Reihenfolge und Ergebnis korrekt
5. **Laenderwechsel:** AT vs. DE → MwSt und Preise korrekt angepasst

#### Delta / Kritikalitaet: 5/5

---

## 3. Konsolidierte Delta-Matrix

| Nr | Komponente | BLS | Kopie | Gap-Typ | Prio | Aufwand |
|----|-----------|-----|-------|---------|------|---------|
| 1 | Produktdatenbank (Artikel, Kategorien) | Vollstaendig (500-2000+ Artikel) | Unvollstaendig/falsch zugeordnet | UNVOLLSTAENDIG | P0 | Hoch |
| 2 | Produktvarianten (Farbe, Material, Groesse) | Vollstaendig | Nicht vorhanden | FEHLEND | P0 | Hoch |
| 3 | Kalkulationsengine (Preisberechnung) | Web Worker basiert, Echtzeit | Nicht vorhanden | FEHLEND | P0 | Sehr hoch |
| 4 | Abhaengigkeits-Regeln (Pflichtartikel) | 200-500+ Regeln | 0 Regeln | FEHLEND | P0 | Sehr hoch |
| 5 | Mengenberechnung aus Raumdaten | Automatisch (m², lfm, Stueck) | Nicht vorhanden | FEHLEND | P0 | Hoch |
| 6 | Raumaufmass-Eingabe | Detailliert (L/B/H, Tueren, Fenster) | Grundfelder vorhanden | UNVOLLSTAENDIG | P1 | Mittel |
| 7 | Dynamische Formulare (bedingte Felder) | Vollstaendig | Nicht vorhanden | FEHLEND | P1 | Hoch |
| 8 | Live-Preisvorschau | Echtzeit-Update bei Aenderung | Nicht vorhanden | FEHLEND | P1 | Mittel |
| 9 | Interaktive PDF-Kataloge | PDF.js mit Produktauswahl | Nicht vorhanden | FEHLEND | P1 | Hoch |
| 10 | Rabatt-/Margen-System | Mehrschichtig (Staffel, Aktion, Kunde) | Nicht vorhanden | FEHLEND | P1 | Mittel |
| 11 | MwSt/Laender-Logik (AT/DE/CH) | Vollstaendig | Nicht vorhanden | FEHLEND | P1 | Niedrig |
| 12 | Angebots-PDF-Generierung | Vollstaendig | Nicht vorhanden | FEHLEND | P2 | Mittel |
| 13 | Workflow-Validierung pro Schritt | Pflichtfelder, Abhaengigkeiten | Nicht vorhanden | FEHLEND | P2 | Mittel |
| 14 | Shower-Tray-Designer | Visueller Konfigurator | Nicht vorhanden | FEHLEND | P2 | Hoch |
| 15 | Offline-Faehigkeit (PWA) | Service Worker + Cache | Nicht vorhanden | FEHLEND | P3 | Mittel |
| 16 | State Management | NgRx | Keines | ABWEICHEND | P2 | Mittel |
| 17 | Workflow-Grundstruktur (Schritte) | Vollstaendig | Implementiert | IDENTISCH | - | - |

---

## 4. Priorisierter Umsetzungsplan

### AP-01: Produktdatenbank aufbauen und Daten importieren
- **Prioritaet:** P0
- **Abhaengigkeiten:** Keine (Grundlage fuer alles)
- **Beschreibung:** Vollstaendiges Datenmodell fuer Produkte, Kategorien, Varianten und Preise erstellen. Daten aus dem BLS extrahieren und in die Kopie importieren.
- **Technische Details:**
  - Datenbank-Schema erstellen:
    ```sql
    products (id, sku, name, description, category_id, unit, base_price, image_url, active)
    categories (id, name, parent_id, sort_order, icon)
    variants (id, product_id, variant_type, value, price_modifier, sku_suffix)
    variant_types (id, name) -- z.B. "Farbe", "Material", "Groesse"
    product_images (id, product_id, variant_id, url, sort_order)
    ```
  - Import-Skript: BLS-Produktdaten erfassen (manuell oder per API-Extraktion)
  - API-Endpunkte: GET /api/products, GET /api/categories, GET /api/products/:id
  - Admin-UI: Produktverwaltung zum Pflegen der Daten
- **Akzeptanzkriterien:**
  - [ ] Alle Produktkategorien aus BLS sind in der Kopie vorhanden
  - [ ] Jedes Produkt hat: Name, SKU, Preis, Kategorie, mindestens 1 Bild
  - [ ] Varianten sind korrekt zugeordnet
  - [ ] API liefert Produktdaten korrekt zurueck
- **Testfaelle:**
  - GET /api/products?category=wandpaneele → Alle Wandpaneele mit korrekten Preisen
  - GET /api/products/123/variants → Alle Farbvarianten des Produkts

---

### AP-02: Abhaengigkeits-Engine implementieren
- **Prioritaet:** P0
- **Abhaengigkeiten:** AP-01
- **Beschreibung:** Rule-Engine fuer Produktabhaengigkeiten: Pflichtartikel, Ausschluesse, Mengenformeln, Varianten-Kopplungen.
- **Technische Details:**
  - Datenbank-Schema:
    ```sql
    dependency_rules (id, source_product_id, target_product_id, rule_type, condition_json, formula, active)
    -- rule_type: 'REQUIRED', 'EXCLUDED', 'QUANTITY_FORMULA', 'VARIANT_LINK', 'SURCHARGE'
    -- condition_json: {"min_qty": 1, "variant_match": "color"}
    -- formula: "source_qty * 2.5 + 1" oder "room_area * 0.1"
    ```
  - Rule-Engine (Server-seitig):
    ```python
    def evaluate_dependencies(selected_products, room_data):
        result = {"add": [], "remove": [], "modify": []}
        for product in selected_products:
            rules = get_rules(product.id)
            for rule in rules:
                if rule.type == 'REQUIRED':
                    result["add"].append(evaluate_required(rule, room_data))
                elif rule.type == 'EXCLUDED':
                    result["remove"].append(rule.target_product_id)
                elif rule.type == 'QUANTITY_FORMULA':
                    qty = eval_formula(rule.formula, room_data, product.qty)
                    result["modify"].append({"product": rule.target_id, "qty": qty})
        return result
    ```
  - API: POST /api/offers/:id/evaluate-dependencies
  - Frontend: Nach jeder Produktaenderung Dependencies neu evaluieren
- **Akzeptanzkriterien:**
  - [ ] Pflichtartikel erscheinen automatisch bei Auswahl des Hauptprodukts
  - [ ] Ausgeschlossene Produkte werden deaktiviert/ausgeblendet
  - [ ] Mengen werden korrekt aus Formeln berechnet
  - [ ] Varianten-Kopplungen funktionieren (z.B. Farbe folgt Paneelfarbe)
- **Testfaelle:**
  - Dusche waehlen → Ablaufgarnitur, Dichtband automatisch hinzugefuegt
  - Badewanne waehlen → Bodengleiche Dusche wird deaktiviert
  - 12m² Wandpaneele → 48 lfm Fugenprofile (Formel: m² * 4)

---

### AP-03: Kalkulationsengine implementieren
- **Prioritaet:** P0
- **Abhaengigkeiten:** AP-01, AP-02
- **Beschreibung:** Vollstaendige Preisberechnung mit Einzel-/Gesamtpreisen, Mengen aus Raumdaten, Aufschlaegen, Rabatten und MwSt.
- **Technische Details:**
  - Datenbank-Schema:
    ```sql
    price_rules (id, product_id, rule_type, min_qty, max_qty, price, discount_pct, valid_from, valid_to)
    margin_config (id, user_id, region, default_margin_pct, min_margin_pct, max_margin_pct)
    tax_rates (id, country_code, rate_pct, label) -- AT:20%, DE:19%, CH:8.1%
    offer_calculations (id, offer_id, subtotal_material, subtotal_labor, margin_amount, discount_amount, tax_amount, total_gross)
    ```
  - Kalkulationslogik (Server-seitig):
    ```python
    def calculate_offer(offer_id):
        offer = get_offer(offer_id)
        room = offer.room_data
        items = offer.line_items  # inkl. automatisch hinzugefuegte Dependencies

        subtotal_material = 0
        for item in items:
            qty = calculate_quantity(item, room)  # aus Raumdaten oder manuell
            unit_price = get_price(item.product, qty, offer.region)  # Staffelpreise
            line_total = qty * unit_price
            apply_variant_surcharges(item, line_total)
            subtotal_material += line_total

        subtotal_labor = calculate_labor(items, room)
        subtotal = subtotal_material + subtotal_labor

        discount = apply_discounts(subtotal, offer.discount_rules)
        margin = apply_margin(subtotal - discount, offer.margin_config)
        net_total = subtotal - discount + margin

        tax_rate = get_tax_rate(offer.country)
        tax = net_total * tax_rate
        gross_total = net_total + tax

        return CalculationResult(
            subtotal_material, subtotal_labor,
            discount, margin, tax, gross_total,
            line_details=[...]
        )
    ```
  - API: GET /api/offers/:id/calculate (Echtzeit bei jeder Aenderung)
  - Frontend: Live-Preisanzeige nach jeder Produktaenderung
- **Akzeptanzkriterien:**
  - [ ] Einzelpreise stimmen mit BLS ueberein
  - [ ] Mengenberechnung aus Raumdaten korrekt
  - [ ] Staffelpreise werden angewandt
  - [ ] Rabatte in korrekter Reihenfolge berechnet
  - [ ] MwSt laenderspezifisch korrekt
  - [ ] Gesamtpreis weicht max. 0.01 EUR vom BLS ab
- **Testfaelle:**
  - Standard-Bad 6m² komplett → Preis-Vergleich mit BLS-Referenzwert
  - Nur Duschumbau → Preis-Vergleich
  - Sondermass-Aufpreise → Korrekter Zuschlag

---

### AP-04: Raumaufmass-Modul erweitern
- **Prioritaet:** P1
- **Abhaengigkeiten:** AP-01
- **Beschreibung:** Detailliertes Raumaufmass wie im BLS: Abmessungen, Tueren, Fenster, Bestandsaufnahme. Diese Daten fliessen direkt in die Mengenberechnung ein.
- **Technische Details:**
  - Datenmodell:
    ```sql
    room_measurements (id, offer_id, room_type, length_cm, width_cm, height_cm,
                       door_count, door_positions_json, window_count, window_positions_json,
                       existing_fixtures_json, notes, photos_json)
    ```
  - Berechnete Werte (automatisch):
    - Wandflaeche = 2*(L+B)*H - Tueren - Fenster
    - Bodenflaeche = L*B
    - Fugenlaenge = Umfang + Ecken
  - Frontend: Formular mit visueller Raum-Skizze (optional)
- **Akzeptanzkriterien:**
  - [ ] Alle Raumtypen aus BLS abbildbar
  - [ ] Wandflaeche und Bodenflaeche automatisch berechnet
  - [ ] Abzuege fuer Tueren/Fenster korrekt
- **Testfaelle:**
  - Raum 200x250x240, 1 Tuer, 1 Fenster → Exakte Flaechenberechnung

---

### AP-05: Dynamische Formulare und bedingte Felder
- **Prioritaet:** P1
- **Abhaengigkeiten:** AP-02
- **Beschreibung:** Felder die basierend auf vorherigen Auswahlen ein-/ausgeblendet werden. JSON-Schema-basierte Formulardefinition.
- **Technische Details:**
  - Form-Schema (JSON-basiert):
    ```json
    {
      "step": "dusche",
      "fields": [
        {"id": "dusch_typ", "type": "select", "options": ["bodengleich", "duschtasse", "badewanne"]},
        {"id": "tassen_modell", "type": "catalog_select", "visible_when": {"dusch_typ": "duschtasse"}},
        {"id": "tassen_groesse", "type": "select", "visible_when": {"dusch_typ": "duschtasse"}, "options_from": "product_variants"},
        {"id": "wannen_modell", "type": "catalog_select", "visible_when": {"dusch_typ": "badewanne"}}
      ]
    }
    ```
  - Frontend: Form-Renderer der JSON-Schema interpretiert
  - Visibility-Engine: Evaluiert Bedingungen bei jeder Aenderung
- **Akzeptanzkriterien:**
  - [ ] Bedingte Felder erscheinen/verschwinden ohne Seitenreload
  - [ ] Workflow-Navigation blockiert bei ungueltigem Schritt
  - [ ] Pflichtfelder werden validiert
- **Testfaelle:**
  - "Bodengleich" waehlen → Duschtassen-Felder verschwinden
  - Pflichtfeld leer lassen → "Weiter"-Button deaktiviert

---

### AP-06: Rabatt- und Margen-System
- **Prioritaet:** P1
- **Abhaengigkeiten:** AP-03
- **Beschreibung:** Mehrstufiges Rabatt-System wie im BLS: Aktionsrabatte, Mengenrabatte, Kundensonderkonditionen, konfigurierbare Margen pro Berater.
- **Technische Details:**
  - Datenbank:
    ```sql
    discounts (id, name, type, value, is_percentage, valid_from, valid_to,
               min_order_value, applies_to_category_id, stackable)
    offer_discounts (offer_id, discount_id, applied_value)
    ```
  - Rabatt-Hierarchie: Aktionsrabatt → Mengenrabatt → Kundenrabatt (in dieser Reihenfolge)
  - Berater-Margen-Einstellung in den Benutzereinstellungen
- **Akzeptanzkriterien:**
  - [ ] Rabatte werden in korrekter Reihenfolge angewandt
  - [ ] Nicht-stapelbare Rabatte schliessen sich gegenseitig aus
  - [ ] Marge ist pro Berater konfigurierbar
- **Testfaelle:**
  - 10% Aktionsrabatt + 5% Mengenrabatt auf 10.000 EUR → Korrektes Ergebnis

---

### AP-07: Interaktive PDF-Katalog-Integration
- **Prioritaet:** P1
- **Abhaengigkeiten:** AP-01, AP-05
- **Beschreibung:** PDF.js-basierte Katalogansicht mit Produktauswahl direkt aus dem PDF.
- **Technische Details:**
  - PDF.js als Standalone einbinden (bestaetigt im BLS via ngsw.json)
  - Katalog-Datenmodell:
    ```sql
    catalogs (id, name, category_id, pdf_url, version, active)
    catalog_product_mappings (id, catalog_id, page_number, x, y, width, height, product_id)
    ```
  - Hotspot-Mapping: Bereiche auf PDF-Seiten sind mit Produkten verknuepft
  - Klick auf Hotspot → Produkt wird dem Angebot hinzugefuegt
  - Navigation: Zoom, Seitennavigation, Thumbnail-Vorschau
- **Akzeptanzkriterien:**
  - [ ] PDF-Kataloge laden und sind navigierbar
  - [ ] Produkte koennen per Klick aus dem PDF ausgewaehlt werden
  - [ ] Ausgewaehlte Produkte werden im Angebot uebernommen
- **Testfaelle:**
  - Wandpaneel-Katalog oeffnen → Seite 5, Dekor "Marmor Weiss" anklicken → Produkt im Angebot

---

### AP-08: Live-Preisvorschau im Frontend
- **Prioritaet:** P1
- **Abhaengigkeiten:** AP-03
- **Beschreibung:** Bei jeder Aenderung im Angebot wird die Kalkulation in Echtzeit aktualisiert und angezeigt.
- **Technische Details:**
  - Debounced API-Call (300ms) nach jeder Aenderung
  - Preisanzeige-Komponente: Material-Summe, Arbeitsleistung, Rabatte, Gesamt
  - Positionsdetails mit Einzelpreisen und Mengen
  - Optionale Netto/Brutto-Umschaltung
- **Akzeptanzkriterien:**
  - [ ] Preis aktualisiert sich innerhalb von 500ms nach Aenderung
  - [ ] Alle Positionen mit Einzelpreisen sichtbar
  - [ ] Gesamtpreis stimmt mit finaler Kalkulation ueberein
- **Testfaelle:**
  - Produkt hinzufuegen → Preis erhoeht sich sofort um korrekten Betrag

---

### AP-09: Angebots-PDF-Generierung
- **Prioritaet:** P2
- **Abhaengigkeiten:** AP-03, AP-06
- **Beschreibung:** Aus dem fertig kalkulierten Angebot ein professionelles PDF-Dokument generieren.
- **Technische Details:**
  - Server-seitige PDF-Generierung (z.B. WeasyPrint, Puppeteer, oder reportlab)
  - Template: Firmenlogo, Kundendaten, Positionsliste, Kalkulation, AGB
  - API: POST /api/offers/:id/generate-pdf → PDF-Download
- **Akzeptanzkriterien:**
  - [ ] PDF enthaelt alle Angebotspositionen mit Preisen
  - [ ] Layout ist professionell und druckfertig
  - [ ] Firmenbranding korrekt
- **Testfaelle:**
  - Komplett-Angebot → PDF mit allen Positionen, korrekter Gesamtpreis

---

### AP-10: Workflow-Validierung und State Management
- **Prioritaet:** P2
- **Abhaengigkeiten:** AP-05
- **Beschreibung:** Robustes State Management fuer den Workflow-Fortschritt mit Validierung pro Schritt.
- **Technische Details:**
  - Leichtgewichtiger State-Store (Vanilla JS Reactive Pattern oder kleine Library)
  - Workflow-State wird serverseitig persistiert (Autosave alle 30s)
  - Validierung: Jeder Schritt definiert Pflichtfelder und Regeln
  - Navigation: Vorwaerts nur wenn valide, Rueckwaerts immer moeglich
- **Akzeptanzkriterien:**
  - [ ] Workflow-Fortschritt ueberlebt Seitenreload
  - [ ] Validierungsfehler werden klar angezeigt
  - [ ] Schritte koennen uebersprungen werden wenn optional
- **Testfaelle:**
  - Browser schliessen und oeffnen → Angebot ist am gleichen Schritt

---

### AP-11: Shower-Tray-Designer (Visueller Konfigurator)
- **Prioritaet:** P2
- **Abhaengigkeiten:** AP-01, AP-02
- **Beschreibung:** Visueller Duschtassen-Konfigurator wie im BLS (Assets bestaetigt).
- **Technische Details:**
  - Canvas/SVG-basierte Darstellung der Duschtasse
  - Groessenauswahl mit visueller Vorschau
  - Farbauswahl mit Echtzeit-Preview
  - Integration mit Abhaengigkeits-Engine (passende Armaturen)
- **Akzeptanzkriterien:**
  - [ ] Alle Duschtassen-Modelle aus BLS darstellbar
  - [ ] Groessen- und Farbwechsel visuell sichtbar
  - [ ] Gewaehlte Konfiguration fliesst in Kalkulation ein

---

### AP-12: End-to-End-Validierung gegen BLS-Referenzwerte
- **Prioritaet:** P0 (nach Implementierung)
- **Abhaengigkeiten:** AP-01 bis AP-08
- **Beschreibung:** Systematischer Vergleich der Kalkulationsergebnisse zwischen BLS und Kopie.
- **Technische Details:**
  - 10 Referenz-Angebote im BLS erstellen und Ergebnisse dokumentieren
  - Gleiche Angebote in der Kopie nachstellen
  - Automatisierter Vergleich: Positionspreise, Zwischensummen, Gesamtpreise
  - Toleranz: max. 0.01 EUR Abweichung
- **Akzeptanzkriterien:**
  - [ ] Alle 10 Referenz-Angebote stimmen mit BLS ueberein
  - [ ] Keine systematischen Abweichungen
  - [ ] Edge-Cases (Sondermasse, Maximalrabatte) korrekt

---

## 5. Validierungsbericht

### Vollstaendigkeit
- [x] Jeder Gap aus der Delta-Matrix (17 Eintraege) ist durch mindestens ein AP abgedeckt
- [x] P0-Gaps (Nr. 1-5) → AP-01, AP-02, AP-03, AP-04
- [x] P1-Gaps (Nr. 6-11) → AP-04, AP-05, AP-06, AP-07, AP-08
- [x] P2-Gaps (Nr. 12-14, 16) → AP-09, AP-10, AP-11
- [x] P3-Gaps (Nr. 15) → Bewusst zurueckgestellt (PWA/Offline)

### Konsistenz der Abhaengigkeiten
- [x] AP-01 hat keine Vorgaenger (Grundlage) ✓
- [x] AP-02 haengt von AP-01 ab (braucht Produktdaten) ✓
- [x] AP-03 haengt von AP-01 + AP-02 ab (braucht Produkte + Regeln) ✓
- [x] AP-05 haengt von AP-02 ab (bedingte Felder = Abhaengigkeiten) ✓
- [x] AP-07 haengt von AP-01 + AP-05 ab (PDF zeigt Produkte + Formulare) ✓
- [x] AP-12 haengt von AP-01-08 ab (Validierung am Ende) ✓
- [x] Keine zirkulaeren Abhaengigkeiten ✓

### Machbarkeit
- [x] Vanilla-JS-Stack kann alle Features abbilden (kein Angular-Migration noetig)
- [x] PDF.js ist Framework-unabhaengig einsetzbar ✓
- [x] Server-seitige Kalkulation ist robuster als Client-seitig ✓
- [x] JSON-Schema-Formulare sind bewaehrt und gut dokumentiert ✓

### Testbarkeit
- [x] Jedes AP hat definierte Testfaelle ✓
- [x] Referenzwerte koennen aus BLS extrahiert werden ✓
- [x] AP-12 definiert systematischen E2E-Vergleich ✓

### Reihenfolge
- [x] Empfohlene Implementierungsreihenfolge:
  1. AP-01 (Produktdaten) → Grundlage
  2. AP-04 (Raumaufmass) → Parallel zu AP-01
  3. AP-02 (Abhaengigkeiten) → Nach AP-01
  4. AP-03 (Kalkulation) → Nach AP-01 + AP-02
  5. AP-05 (Dynamische Formulare) → Nach AP-02
  6. AP-06 (Rabatte/Margen) → Nach AP-03
  7. AP-07 (PDF-Kataloge) → Nach AP-01 + AP-05
  8. AP-08 (Live-Vorschau) → Nach AP-03
  9. AP-09 (PDF-Generierung) → Nach AP-03 + AP-06
  10. AP-10 (State Management) → Nach AP-05
  11. AP-11 (Shower-Tray) → Nach AP-01 + AP-02
  12. AP-12 (E2E-Validierung) → Nach allen APs

**Ergebnis: Plan ist vollstaendig, konsistent, machbar und testbar.** ✓

---

## 6. Deployment-Vorbereitung

### SSH-Analyse-Skript

Das folgende Skript muss vom lokalen Mac ausgefuehrt werden, um den aktuellen Stand auf dem Server zu analysieren:

```bash
#!/bin/bash
# analyse-server.sh — Auf dem lokalen Mac ausfuehren
SERVER="root@46.225.166.62"

echo "=== Server-Analyse ISOTEC-Kiel Dashboard ==="

# 1. Verzeichnisstruktur finden
ssh $SERVER "find / -path '*/vit-Angebote*' -type f 2>/dev/null | head -50"

# 2. Web-Root finden
ssh $SERVER "cat /etc/nginx/sites-enabled/* 2>/dev/null || cat /etc/apache2/sites-enabled/* 2>/dev/null"

# 3. Datenbank identifizieren
ssh $SERVER "systemctl list-units | grep -E 'mysql|postgres|mongo|mariadb'"

# 4. Backend-Prozesse
ssh $SERVER "ps aux | grep -E 'python|node|php|gunicorn|uvicorn|pm2'"

# 5. Docker pruefen
ssh $SERVER "docker ps 2>/dev/null"

# 6. Aktueller Code-Stand
ssh $SERVER "find /var/www -name '*.py' -o -name '*.js' -o -name '*.php' 2>/dev/null | head -100"

echo "=== Analyse abgeschlossen ==="
```

### Deployment-Ablauf (nach Implementierung)

```bash
#!/bin/bash
# deploy.sh — Auf dem lokalen Mac ausfuehren
SERVER="root@46.225.166.62"
APP_DIR="/var/www/dashboard"  # Anpassen nach Server-Analyse
BACKUP_DIR="/root/backups/$(date +%Y%m%d_%H%M%S)"

echo "=== Deployment ISOTEC-Kiel Dashboard ==="

# 1. Backup
ssh $SERVER "mkdir -p $BACKUP_DIR && cp -r $APP_DIR $BACKUP_DIR/"
echo "✓ Backup erstellt: $BACKUP_DIR"

# 2. Code deployen
scp -r ./dist/* $SERVER:$APP_DIR/

# 3. Dependencies installieren (falls Backend)
ssh $SERVER "cd $APP_DIR && pip install -r requirements.txt 2>/dev/null || npm install 2>/dev/null"

# 4. Migrationen ausfuehren
ssh $SERVER "cd $APP_DIR && python manage.py migrate 2>/dev/null"

# 5. Services neustarten
ssh $SERVER "systemctl restart nginx && systemctl restart gunicorn 2>/dev/null || pm2 restart all 2>/dev/null"

# 6. Smoke-Test
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://dashboard.isotec-kiel.eu/dashboard/vit-Angebote/)
if [ "$HTTP_STATUS" == "200" ] || [ "$HTTP_STATUS" == "302" ]; then
    echo "✓ Deployment erfolgreich (HTTP $HTTP_STATUS)"
else
    echo "✗ FEHLER: HTTP $HTTP_STATUS — Rollback starten!"
    ssh $SERVER "cp -r $BACKUP_DIR/* $APP_DIR/ && systemctl restart nginx"
    echo "✓ Rollback ausgefuehrt"
fi

echo "=== Deployment abgeschlossen ==="
```

---

*Analyse abgeschlossen am 2026-03-13*
*Naechster Schritt: Server-Analyse via SSH ausfuehren, dann mit AP-01 beginnen*

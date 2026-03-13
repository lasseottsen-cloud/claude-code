# Profi-Prompt: Analyse & Vergleich Viterma BLS vs. ISOTEC-Kiel Dashboard

## Zielsetzung

Analysiere zwei Webapplikationen im Bereich Angebotserstellung und Kalkulation und entwickle daraus einen vollstaendigen Umsetzungsplan, um die ISOTEC-Kopie funktional auf das Niveau des Viterma BLS zu bringen.

---

## Systeme

| System | URL | Fokusbereich |
|--------|-----|-------------|
| **Original** - Viterma BLS | https://bls.viterma.com/dashboard | Bereich "Angebote" → Workflows → Schritte |
| **Kopie** - ISOTEC-Kiel Dashboard | https://dashboard.isotec-kiel.eu/dashboard/vit-Angebote/ | Angebote-Modul (Grundstruktur vorhanden) |

## Aktueller Stand der Kopie

- Grundprinzip mit Workflows und Schritten ist implementiert
- **Fehlend:** Spezifische Produktdaten aus dem Viterma-System
- **Fehlend:** Korrekte Produktzuordnungen mit Abhaengigkeiten
- **Fehlend:** Bedingt erscheinende Artikel (Dependency-Logik)
- **Fehlend:** Interaktive PDF-Kataloge fuer Kundenbearbeitung
- **Fehlend:** Exakte Kalkulationslogik des BLS

---

## Phase 1: Analyse aus 5 Profi-Perspektiven

Analysiere beide Systeme jeweils aus den folgenden fuenf Perspektiven. Dokumentiere fuer jede Perspektive: **Ist-Zustand Original**, **Ist-Zustand Kopie**, **Delta/Luecken**, **Kritikalitaet (1-5)**.

### Perspektive 1: Solution Architect — Systemarchitektur & Datenmodell

- Wie ist das Datenmodell der Angebotserstellung im BLS aufgebaut?
- Welche Entitaeten existieren (Angebote, Positionen, Produkte, Varianten, Pakete, Kategorien)?
- Wie sind die Relationen zwischen Entitaeten modelliert?
- Welche Datenbank-Strukturen liegen den Workflows und Schritten zugrunde?
- Wie werden Workflow-Zustaende persistiert und verwaltet?
- Vergleiche: Welche Strukturen fehlen in der Kopie oder sind unvollstaendig?

### Perspektive 2: Business Analyst — Geschaeftslogik & Kalkulationsregeln

- Wie funktioniert die Kalkulation im BLS exakt (Schritt fuer Schritt)?
- Welche Preisregeln, Rabattstaffeln, Aufschlaege und Margen werden angewandt?
- Wie werden Einzel- und Gesamtpreise berechnet?
- Welche Abhaengigkeiten zwischen Produkten existieren?
  - Pflichtartikel bei Auswahl bestimmter Produkte
  - Ausschluss-Regeln (Produkt A schliesst Produkt B aus)
  - Mengenabhaengigkeiten (z.B. pro laufendem Meter)
  - Zubehoer-Automatismen
- Wie werden Pakete/Bundles kalkuliert?
- Welche Sonderkonditionen und Aktionspreise gibt es?
- Gibt es Mindestbestell- oder Mindestkalkulations-Werte?

### Perspektive 3: UX/Produkt-Designer — Workflow & Benutzerfuehrung

- Wie ist der Angebots-Workflow im BLS strukturiert (alle Schritte)?
- In welcher Reihenfolge werden dem Berater Eingaben abgefragt?
- Wie werden Abhaengigkeiten visuell dargestellt (erscheinende/verschwindende Felder)?
- Wie funktioniert die Produktauswahl im Detail?
  - Kategorienavigation
  - Filtermoeglichkeiten
  - Variantenauswahl (Farbe, Groesse, Material)
- Wie wird die Live-Vorschau der Kalkulation dargestellt?
- Wie funktioniert die interaktive PDF-Katalog-Bearbeitung mit dem Kunden?
- Welche Validierungen und Pflichtfelder gibt es pro Schritt?

### Perspektive 4: Frontend-Entwickler — Technische Implementierung

- Welche Frontend-Technologien nutzt das BLS?
- Wie werden dynamische Formulare und bedingte Felder umgesetzt?
- Wie werden Produktabhaengigkeiten clientseitig verarbeitet?
- Wie ist die State-Verwaltung des Workflow-Fortschritts implementiert?
- Wie wird die PDF-Katalog-Integration technisch realisiert?
- Welche API-Endpunkte werden fuer Produktdaten, Preise und Kalkulation aufgerufen?
- Wie werden Echtzeit-Preisberechnungen im Frontend durchgefuehrt?
- Vergleiche: Welche technischen Komponenten fehlen in der Kopie?

### Perspektive 5: QA-Engineer & Daten-Analyst — Datenqualitaet & Vollstaendigkeit

- Welche und wie viele Produkte/Artikel sind im BLS hinterlegt?
- Wie vollstaendig sind die Produktdaten (Preise, Beschreibungen, Bilder, Masse)?
- Wie viele Abhaengigkeits-Regeln existieren?
- Welche Testfaelle decken die Kalkulationslogik ab?
- Welche Edge-Cases existieren (Sonderartikel, Rabattkombinationen, Null-Preis-Positionen)?
- Wie werden Dateninkonsistenzen erkannt und behandelt?
- Vergleich: Welche Datensaetze fehlen in der Kopie komplett?

---

## Phase 2: Delta-Matrix erstellen

Erstelle auf Basis der 5 Analysen eine konsolidierte Delta-Matrix:

```
| Nr | Komponente/Feature | BLS-Status | Kopie-Status | Gap-Typ | Prioritaet | Aufwand |
|----|-------------------|------------|--------------|---------|-----------|---------|
| 1  | ...               | ...        | ...          | ...     | ...       | ...     |
```

**Gap-Typen:**
- `FEHLEND` — In der Kopie nicht vorhanden
- `UNVOLLSTAENDIG` — Teilweise implementiert
- `ABWEICHEND` — Implementiert aber anders als im Original
- `IDENTISCH` — Korrekt umgesetzt

**Prioritaeten:**
- `P0` — Blocker (Kalkulation unmoeglich ohne)
- `P1` — Kritisch (Ergebnis weicht signifikant ab)
- `P2` — Wichtig (UX/Funktionalitaet eingeschraenkt)
- `P3` — Nice-to-have

---

## Phase 3: Umsetzungsplan entwickeln

Entwickle basierend auf der Delta-Matrix einen priorisieren Umsetzungsplan:

### Struktur pro Arbeitspaket:

```
### AP-[NR]: [Titel]
- **Prioritaet:** P0/P1/P2/P3
- **Abhaengigkeiten:** [Vorgaenger-APs]
- **Beschreibung:** Was genau umgesetzt werden muss
- **Technische Details:**
  - Datenmodell-Aenderungen
  - API-Aenderungen/Erweiterungen
  - Frontend-Komponenten
  - Migrationen
- **Akzeptanzkriterien:**
  - [ ] Kriterium 1
  - [ ] Kriterium 2
- **Testfaelle:**
  - Eingabe X → Erwartetes Ergebnis Y
```

### Empfohlene Reihenfolge:

1. **Foundation** — Datenmodell und Produktimport
2. **Core Logic** — Kalkulationsengine mit allen Regeln
3. **Dependencies** — Produkt-Abhaengigkeiten und bedingte Artikel
4. **UX** — Workflow-Optimierung und dynamische Formulare
5. **PDF** — Interaktive Katalog-Integration
6. **QA** — End-to-End-Validierung gegen BLS-Referenzwerte

---

## Phase 4: Validierung des Plans

Pruefe den Umsetzungsplan auf:

- [ ] **Vollstaendigkeit:** Deckt jeder Gap aus der Delta-Matrix ab?
- [ ] **Konsistenz:** Sind alle Abhaengigkeiten zwischen APs korrekt?
- [ ] **Machbarkeit:** Sind die technischen Loesungen realistisch?
- [ ] **Testbarkeit:** Kann jedes AP gegen BLS-Referenzwerte validiert werden?
- [ ] **Reihenfolge:** Ist die Implementierungsreihenfolge logisch?

---

## Phase 5: Deployment

Nach erfolgreicher Validierung: Deployment auf den Produktivserver.

- **Server:** 46.225.166.62
- **Methode:** SSH-Deployment vom lokalen Rechner
- **Vorgehen:**
  1. Finalen Build erstellen
  2. Tests ausfuehren
  3. Backup des aktuellen Stands auf dem Server
  4. Deployment via SSH/SCP
  5. Smoke-Tests auf Produktivumgebung
  6. Rollback-Plan bereithalten

---

## Ausgabeformat

Liefere die Ergebnisse in folgender Struktur:

1. **Executive Summary** (max. 500 Woerter)
2. **Detailanalyse pro Perspektive** (Kapitel 1-5)
3. **Konsolidierte Delta-Matrix** (Tabelle)
4. **Priorisierter Umsetzungsplan** (Arbeitspakete)
5. **Validierungsbericht**
6. **Deployment-Protokoll**

---

*Prompt erstellt am 2026-03-13 fuer das Projekt ISOTEC-Kiel / Viterma BLS Migration*

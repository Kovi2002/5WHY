# 5WHY — AI Asistent za Analizo Temeljnih Vzrokov

Spletna aplikacija za vodeno izvedbo metode 5WHY z uporabo umetne inteligence (Claude API). Uporabnik opiše problem ali naloži PDF dokument, AI pa strukturirano izvede analizo vzročno-posledičnih verig in identificira temeljni vzrok (root cause).

---

## Funkcionalnosti

- **Vodena 5WHY analiza** — AI postopoma identificira WHY1–WHY5 in ROOT CAUSE
- **Analiza PDF dokumentov** — naloži poročilo o incidentu, reklamacijo ali zastoj; AI oceni ustreznost in izvede analizo
- **Vizualni diagram** — staircase diagram s puščicami se gradi sproti med analizo
- **Izvoz PDF poročila** — strukturirano poročilo z analizo (dostopno po zaključeni analizi)

---

## Tehnološki sklad

| Komponenta | Tehnologija |
|---|---|
| Backend | Python 3, Flask |
| AI model | Anthropic Claude (`claude-sonnet-4-20250514`) |
| Generiranje PDF | ReportLab |
| Frontend | Vanilla JS, CSS3 |
| Deployment | Railway / Gunicorn |

---

## Lokalno zaganjanje

### 1. Kloniranje repozitorija

```bash
git clone https://github.com/<tvoj-username>/5WHY.git
cd 5WHY
```

### 2. Ustvaritev virtualnega okolja in namestitev odvisnosti

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS

pip install -r requirements.txt
```

### 3. Nastavitev okoljskih spremenljivk

Ustvari datoteko `.env` v korenu projekta:

```
ANTHROPIC_API_KEY=sk-ant-...
```

### 4. Zagon strežnika

```bash
python server.py
```

Odpri brskalnik na `http://localhost:5000`.

---

## Struktura projekta

```
5WHY/
├── server.py          # Flask aplikacija — API endpointi
├── chat.py            # Komunikacija z Anthropic API
├── pdf_handler.py     # Kodiranje PDF dokumentov za API
├── requirements.txt   # Python odvisnosti
├── Procfile           # Konfiguracija za Heroku/Railway
├── railway.json       # Konfiguracija za Railway deployment
└── static/
    ├── index.html     # Glavna stran
    ├── base.css       # Spremenljivke, layout, animacije
    ├── chat.css       # Klepetalnik in vnosno polje
    ├── diagram.css    # 5WHY vizualni diagram
    ├── chat.js        # Logika klepetalnika
    ├── diagram.js     # Parsiranje in izris diagrama
    └── export.js      # Izvoz PDF poročila
```

---

## API endpointi

| Metoda | Pot | Opis |
|---|---|---|
| `GET` | `/` | Glavna stran |
| `POST` | `/chat` | Pošlji sporočilo (z ali brez PDF-a) |
| `POST` | `/export-pdf` | Generiraj PDF poročilo iz diagram podatkov |

### `/chat` — zahtevek brez PDF-a

```json
{
  "messages": [
    { "role": "user", "content": "Stroj se je ustavil." }
  ]
}
```

### `/chat` — zahtevek s PDF-om

```
Content-Type: multipart/form-data
  messages: [{"role": "user", "content": "Izvedi 5WHY analizo."}]
  pdf: <datoteka.pdf>
```

### `/export-pdf` — zahtevek

```json
{
  "diagram": {
    "problem": "Stroj se je ustavil.",
    "whys": ["Pregorel je varovalec.", "Motor je bil preobremenjen.", "..."],
    "rootcause": "Ni določene odgovornosti za vzdrževanje."
  }
}
```

---

## Deployment na Railway

1. Poveži GitHub repozitorij z Railway projektom
2. Nastavi okoljsko spremenljivko `ANTHROPIC_API_KEY`
3. Railway samodejno zazna `railway.json` in zažene `gunicorn server:app`

---

## Okoljske spremenljivke

| Spremenljivka | Opis | Obvezna |
|---|---|---|
| `ANTHROPIC_API_KEY` | API ključ za Anthropic Claude | Da |
| `PORT` | Port strežnika (privzeto: 5000) | Ne |

# AI Stylist Agent

Agent doradzajacy ubior z wykorzystaniem RAG i Function Calling (Gemini 2.0 / Local Stub).

## Instalacja (Wymagany Python 3.12+)
1. Utworz srodowisko: `python3.12 -m venv venv`
2. Aktywuj: `source venv/bin/activate` (macOS/Linux) lub `venv\Scripts\activate` (Win)
3. Instalacja: `pip install -r requirements.txt`

## Konfiguracja (.env)
1. `cp .env.template .env`
2. Ustaw `GOOGLE_API_KEY`.
3. Wybierz tryb w `LLM_PROVIDER`:
   - `gemini`: Pelny tryb AI (wymaga internetu oraz ustawionego api key).
   - `local_stub`: Tryb offline (symulacja do testow/zaliczenia).

## Uruchomienie
Start serwera: `python -m uvicorn src.main_api:app --reload`
Dokumentacja (Swagger): http://127.0.0.1:8000/docs

## Frontend
(taki dodatek, nie trzeba odpalac ale fajnie wyglada)
1. Upewnij sie, ze serwer API dziala.
2. Otworz plik `index.html` w dowolnej przegladarce.
   - Mozesz tez uruchomic prosty serwer: `python3 -m http.server 3000`, a nastepnie wejsc na http://localhost:3000

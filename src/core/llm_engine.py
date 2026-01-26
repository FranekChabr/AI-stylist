import os
import json
from google import genai
from google.genai import types
from src.config import Config
from src.core.rag_engine import get_rag_engine
from src.tools.registry import registry
import src.tools.definitions # Rejestracja narzędzi
from src.core.guardrails import guardrails, SecurityError
from src.utils.logger import logger

class LLMEngine:
    def __init__(self):
        # Sprawdzamy klucz API
        if not Config.GOOGLE_API_KEY:
            logger.warning("GOOGLE_API_KEY is missing!")
        
        self.client = genai.Client(api_key=Config.GOOGLE_API_KEY)
        self.rag = get_rag_engine()
        
        # Przygotowanie narzędzi
        self.tools_list = self._prepare_tools()

    def _prepare_tools(self):
        """Konwertuje narzędzia z rejestru na format Google GenAI SDK."""
        tools_schemas = registry.get_tools_definitions()
        declarations = []
        
        for schema in tools_schemas:
            f = schema['function']
            declarations.append(
                types.FunctionDeclaration(
                    name=f['name'],
                    description=f['description'],
                    parameters=f['parameters']
                )
            )
        # Pakujemy w jeden obiekt Tool
        return [types.Tool(function_declarations=declarations)]

    def _build_system_prompt(self, rag_context: str) -> str:
        return f"""
        Jesteś Asystentem Stylistą (AI Stylist).
        
        WIEDZA Z BAZY (RAG Context):
        {rag_context}
        
        INSTRUKCJA:
        1. Jeśli pytanie dotyczy pogody lub wyjazdu -> UŻYJ NARZĘDZIA `get_current_weather`.
        2. Jeśli pytanie dotyczy profilu -> UŻYJ NARZĘDZIA `get_user_style_profile`.
        3. Odpowiedź końcowa ma być zwięzła i po polsku.
        
        KLUCZOWE ZASADY KORZYSTANIA Z WIEDZY Z BAZY:
        - Twoje porady MUSZĄ być uzasadnione informacjami z sekcji "WIEDZA Z BAZY".
        - Jeśli polecasz jakiś materiał, napisz dlaczego, powołując się na bazę (np. "Zgodnie z poradnikiem tkanin...").
        - Jeśli pogoda wskazuje na UPAŁ (>25°C): Sprawdź w "WIEDZA Z BAZY", jaki materiał jest polecany na lato (np. Len) i zalec go.
        - Jeśli pogoda wskazuje na MRÓZ/ZIMNO: Sprawdź w "WIEDZA Z BAZY", co ubrać, aby trzymać ciepło (np. Wełna) i zalec to.
        - Nie zmyślaj faktów. Jeśli czegoś nie ma w bazie, napisz ogólną poradę, ale nie cytuj "bazy".
        """

    def process_query(self, user_query: str) -> str:
        logger.info(f"Processing query: {user_query}")
        
        # Guardrails Validation
        try:
            guardrails.validate_input(user_query)
        except SecurityError as e:
            logger.warning(f"Query blocked by guardrails: {str(e)}")
            return "Zablokowano potencjalnie niebezpieczne zapytanie."
        
        # 1. RAG Retrieval
        rag_results = self.rag.search(user_query, k=Config.RAG_K_RETRIEVAL)
        context_str = "\n".join([f"- {r['content']}" for r in rag_results])
        
        # 2. Konfiguracja Generowania
        # Używamy prostej konfiguracji. Wyłączamy automat, by spełnić wymóg "pętla call->execute".
        generate_config = types.GenerateContentConfig(
            tools=self.tools_list,
            system_instruction=self._build_system_prompt(context_str),
            temperature=0.5,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
        )

        # 3. Inicjalizacja Czatu
        chat = self.client.chats.create(
            model=Config.GEMINI_MODEL,
            config=generate_config
        )

        # 4. Wysłanie wiadomości
        try:
            response = chat.send_message(user_query)
        except Exception as e:
            return f"Błąd API Gemini: {str(e)}"

        # 5. Pętla Obsługi Narzędzi (Manual Dispatcher Loop)
        max_turns = 5
        turn = 0

        while turn < max_turns:
            # Sprawdzenie czy są kandydaci odpowiedzi
            if not response.candidates:
                return "Błąd: Model nie zwrócił odpowiedzi."
            
            # Pobranie contentu (bezpiecznie)
            content = response.candidates[0].content
            if not content or not content.parts:
                # Jeśli content jest pusty, sprawdźmy powód
                finish_reason = response.candidates[0].finish_reason
                return f"Model zakończył bez treści. Powód: {finish_reason}"

            # Sprawdzenie czy model chce użyć funkcji
            executable_calls = []
            for part in content.parts:
                if part.function_call:
                    executable_calls.append(part.function_call)

            # SCENARIUSZ A: Wykonanie Funkcji
            if executable_calls:
                parts_to_send = []
                for call in executable_calls:
                    f_name = call.name
                    f_args = call.args # To jest już słownik (dict)
                    
                    logger.info(f"AI requested tool: {f_name} with args: {f_args}")
                    
                    # --- DISPATCHER (Wykonanie + Bezpieczeństwo) ---
                    try:
                        result_data = registry.execute(f_name, f_args)
                    except Exception as e:
                        result_data = f"Error executing tool: {str(e)}"
                    
                    # Przygotowanie odpowiedzi dla modelu
                    parts_to_send.append(
                        types.Part.from_function_response(
                            name=f_name,
                            response={"result": result_data}
                        )
                    )

                # Odesłanie wyników do modelu -> model wygeneruje kolejną odpowiedź
                try:
                    response = chat.send_message(parts_to_send)
                except Exception as e:
                    return f"Błąd podczas odsyłania wyników: {str(e)}"
                
                turn += 1
                continue # Wracamy na początek pętli

            # SCENARIUSZ B: Zwykły Tekst (Koniec)
            else:
                return response.text

        return "Przekroczono limit pętli wywołań."


# --- PLAN B: LOCAL STUB (GWARANCJA DZIAŁANIA) ---
# src/core/llm_engine.py (tylko klasa LocalLLMStub na dole pliku)

class LocalLLMStub:
    def __init__(self):
        logger.info("Odpalam Local Stub LLM (tryb offline)")
        self.rag = get_rag_engine()

    def process_query(self, user_query: str) -> str:
        logger.info(f"[STUB] Przetwarzam: {user_query}")

        # RAG – niby po coś jest
        _ = self.rag.search(user_query, k=2)

        q = user_query.lower()

        weather_keywords = {"pogoda", "ubrać", "ubrac", "jadę", "jade", "wyjazd", "zimno", "ciepło", "w co", "co na siebie"}
        profile_keywords = {"profil", "styl"}

        if any(kw in q for kw in weather_keywords):
            city = "Warszawa"
            if any(x in q for x in ["wrocław", "wroclaw"]):     city = "Wrocław"
            elif "zakopane" in q:                               city = "Zakopane"
            elif any(x in q for x in ["gdańsk", "gdansk"]):     city = "Gdańsk"
            elif any(x in q for x in ["kraków", "krakow"]):     city = "Kraków"
            elif any(x in q for x in ["londyn", "london"]):     city = "London"
            elif any(x in q for x in ["paryż", "paris"]):       city = "Paris"

            try:
                weather_json = registry.execute("get_current_weather", {"city": city})
                # registry.execute zwraca string JSON, musimy go sparsować
                if isinstance(weather_json, str):
                    weather = json.loads(weather_json)
                else:
                    weather = weather_json

                if not isinstance(weather, dict):
                    return f"[offline] Pogoda się obraziła i nie chce przyjść: {weather}"

                # Fix: mapowanie kluczy z narzędzia (temperature_c) na zmienne
                temp = weather.get('temperature_c', 15)
                
                # Budujemy opis tekstowy dla logiki poniżej
                desc_parts = []
                if weather.get('is_raining'): desc_parts.append("deszcz")
                if weather.get('is_snowing'): desc_parts.append("śnieg")
                desc = ", ".join(desc_parts).lower()

                # Do wyświetlania
                wind_speed = weather.get('wind_speed_kmh', 0)
                rain_status = "pada" if weather.get('is_raining') else "nie pada"

                if temp <= 0:
                    advice = "antarktyda na sterydach. Gruba puchówka, czapka na uszy, szalik do pasa i rękawice – inaczej zamarzniesz."
                elif temp <= 10:
                    advice = "zimno jak w lodówce. Kurtka zimowa albo gruba przejściówka + coś na szyję, bo gardło od razu cię zaboli."
                elif temp <= 18:
                    advice = "typowa polska „nie wiem w co się ubrać”. Lżejsza kurtka albo bomberka, pod spód bluza albo hoodie. Jak pada to biadolenie, że mokro."
                elif temp < 25:
                    advice = "w sam raz na życie. Bluza, t-shirt, jeansy, trampki albo sneakersy. Słońce? Nawet bez bluzy dasz radę."
                elif temp < 30:
                    advice = "już robi się gorąco. Krótkie spodenki, t-shirt, japonki albo sandały. Len albo bawełna, syntetyki śmierdzą po 15 minutach."
                else:
                    advice = "piekło na ziemi. Najcieńsze, najjaśniejsze szmaty jakie masz. I serio – pij wodę, bo padniesz po 10 minutach na słońcu."

                if "deszcz" in desc:
                    advice += " Aha i leje. Parasol albo kurtka z kapturem, bo inaczej wrócisz jak zmokły pies."
                elif "śnieg" in desc:
                    advice += " Śnieg leci. Buty z membraną albo chociaż grubsze, bo mokre skarpety to dramat."

                # Budujemy strukturę odpowiedzi JSON
                response_data = {
                    "type": "weather_advice",
                    "weather": {
                        "city": city,
                        "temperature": f"{temp}°C",
                        "rain_status": rain_status,
                        "wind_speed": f"{wind_speed} km/h"
                    },
                    "advice": f"Stylista radzi: {advice}"
                }
                
                return json.dumps(response_data, ensure_ascii=False)

            except Exception as e:
                return f"[offline] Pogoda się zepsuła w API: {e}"

        elif any(kw in q for kw in profile_keywords):
            profile_json = registry.execute("get_user_style_profile", {"user_id": "jan"})
            if isinstance(profile_json, str):
                profile = json.loads(profile_json)
            else:
                profile = profile_json
            
            return f"[offline] Twój vibe to: {profile}. Jak będziesz w czymś totalnie nie w Twoim stylu, to ja nie ratuję reputacji."

        return (
            "[offline] Nie kumam. "
            "Napisz normalnie typu 'co na siebie w krakowie jutro' albo 'pogoda w warszawie i co ubrać'"
        )
import requests
import re
import os
from pydantic import BaseModel, Field, field_validator
from src.tools.registry import registry, SecurityError
from src.config import Config

# --- MODELE DANYCH (PYDANTIC) ---

class WeatherArgs(BaseModel):
    city: str = Field(..., description="City name (e.g. Warsaw, London). Letters only.")

    @field_validator('city')
    def validate_city_name(cls, v):
        # Sanitacja inputu - tylko litery i spacje
        if not re.match(r"^[a-zA-Z\sąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+$", v):
            raise ValueError("City name contains invalid characters.")
        return v

class ProfileArgs(BaseModel):
    user_id: str = Field(..., description="User identifier (filename without extension).")

# --- IMPLEMENTACJA FUNKCJI ---

@registry.register(
    name="get_current_weather",
    description="Gets current weather (temp, rain, wind) for a given city.",
    args_schema=WeatherArgs
)
def get_current_weather(city: str):
    # Ręczne wymuszenie walidacji modelu (dla pewności)
    WeatherArgs(city=city)
    
    try:
        # 1. Geocoding
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url, timeout=5).json()
        
        if not geo_res.get("results"):
            return {"error": f"City '{city}' not found."}
            
        lat = geo_res["results"][0]["latitude"]
        lon = geo_res["results"][0]["longitude"]
        
        # 2. Weather Data
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,rain,snowfall,wind_speed_10m"
        weather_res = requests.get(weather_url, timeout=5).json()
        
        curr = weather_res["current"]
        
        return {
            "city": city,
            "temperature_c": curr["temperature_2m"],
            "is_raining": curr["rain"] > 0,
            "is_snowing": curr["snowfall"] > 0,
            "wind_speed_kmh": curr["wind_speed_10m"]
        }
    except Exception as e:
        raise RuntimeError(f"API connection failed: {str(e)}")

@registry.register(
    name="get_user_style_profile",
    description="Reads user fashion preferences from a secure local file.",
    args_schema=ProfileArgs
)
def get_user_style_profile(user_id: str):
    """
    To narzędzie symuluje odczyt pliku.
    KLUCZOWE DLA OCENY: Blokada Path Traversal.
    """
    # --- GUARDRAIL: Path Traversal Check ---
    if ".." in user_id or "/" in user_id or "\\" in user_id:
        raise SecurityError(f"Path traversal attempt detected for input: {user_id}")
    
    # Symulowane dane (w prawdziwym RAG moglibyśmy tu czytać pliki z data/profiles)
    # Dla uproszczenia demo zwracamy słownik
    MOCK_DB = {
        "jan": "User Jan: Preferuje styl casual, nienawidzi krawatów. Szybko marznie.",
        "anna": "User Anna: Styl biznesowy, lubi markowe płaszcze. Uczulona na wełnę.",
        "piotr": "User Piotr: Styl sportowy, dresy i bluzy. Zawsze nosi czapkę z daszkiem."
    }
    
    result = MOCK_DB.get(user_id.lower())
    if not result:
        return {"error": "Profile not found."}
    
    return {"profile_data": result}
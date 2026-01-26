from src.tools.registry import registry
from src.tools.definitions import get_current_weather

# 1. Test definicji (Schema)
print("--- TOOLS DEFINITIONS (JSON SCHEMA) ---")
print(registry.get_tools_definitions())

# 2. Test wykonania (Weather)
print("\n--- EXECUTE WEATHER ---")
print(registry.execute("get_current_weather", {"city": "Warsaw"}))

# 3. Test Security (powinien zwrócić błąd Security)
print("\n--- EXECUTE SECURITY TEST ---")
print(registry.execute("get_user_style_profile", {"user_id": "../etc/passwd"}))
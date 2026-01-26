import json
import functools
import traceback
from typing import Callable, Dict, List, Type, Any, Union # <--- Dodałem Union
from pydantic import BaseModel, ValidationError
from src.utils.logger import logger

# Wyjątki
class ToolError(Exception):
    """Ogólny błąd narzędzia."""
    pass

class SecurityError(ToolError):
    """Błąd bezpieczeństwa (np. path traversal)."""
    pass

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: Dict[str, Dict] = {}

    def register(self, name: str, description: str, args_schema: Type[BaseModel]):
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            
            self._tools[name] = wrapper
            self._schemas[name] = {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": args_schema.model_json_schema()
                }
            }
            logger.info(f"Registered tool: {name}")
            return wrapper
        return decorator

    def get_tools_definitions(self) -> List[Dict]:
        return list(self._schemas.values())

    # --- POPRAWKA TUTAJ ---
    def execute(self, tool_name: str, arguments: Union[dict, str]) -> str: 
    # Było: arguments: dict | str (to działa tylko w Python 3.10+)
        """
        Dispatcher wykonujący narzędzie.
        """
        logger.info(f"Executing tool: {tool_name} with args: {arguments}")
        
        if tool_name not in self._tools:
            logger.warning(f"Tool not found: {tool_name}")
            return json.dumps({"error": f"Tool '{tool_name}' not found or not allowed."})

        try:
            if isinstance(arguments, str):
                args_dict = json.loads(arguments)
            else:
                args_dict = arguments

            tool_func = self._tools[tool_name]
            result = tool_func(**args_dict)
            
            logger.info(f"Tool {tool_name} success.")
            return json.dumps(result, ensure_ascii=False)

        except json.JSONDecodeError:
            msg = "Invalid JSON arguments format."
            logger.error(msg)
            return json.dumps({"error": msg})
            
        except ValidationError as e:
            msg = f"Validation Error: {str(e)}"
            logger.error(f"Tool {tool_name} validation failed: {msg}")
            return json.dumps({"error": msg})
            
        except SecurityError as e:
            msg = f"Security Violation: {str(e)}"
            logger.critical(f"SECURITY ALERT in {tool_name}: {msg}")
            return json.dumps({"error": "Operation blocked by security policy."})
            
        except Exception as e:
            logger.error(f"Tool {tool_name} crashed: {traceback.format_exc()}")
            return json.dumps({"error": f"Internal Tool Error: {str(e)}"})

registry = ToolRegistry()
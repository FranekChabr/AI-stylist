import logging
import sys
import os
from src.config import Config

def setup_logger(name="AI_Stylist"):
    # Tworzymy folder logs jeśli nie istnieje
    log_dir = os.path.join(Config.BASE_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(Config.LOG_LEVEL)
    
    # Format logowania: Czas - Poziom - Wiadomość
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Handler plikowy (do pliku app.log)
    file_handler = logging.FileHandler(os.path.join(log_dir, "app.log"))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler konsolowy (żebyś widział w terminalu co się dzieje)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()
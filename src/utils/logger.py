# Logger - Logging sistemi
import logging
import os
from datetime import datetime


def setup_logger(name: str = "epic_games_collector") -> logging.Logger:
    """Logger'ı kur"""
    
    # Log dizinini oluştur
    log_dir = "data/logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Logger oluştur
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Dosya formatı
    log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y-%m-%d')}.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Konsol formatı
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Handler'ları ekle
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger


# Global logger
logger = setup_logger()

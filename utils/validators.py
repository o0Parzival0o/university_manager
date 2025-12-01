# utils/validators.py
"""
Validatori per i dati
"""

import re
from datetime import datetime


class Validators:
    """Classe con metodi di validazione"""
    
    @staticmethod
    def valida_voto(voto: int) -> bool:
        """Valida un voto (18-30, 31 per 30L)"""
        return 18 <= voto <= 31
    
    @staticmethod
    def valida_crediti(crediti: int) -> bool:
        """Valida i crediti (positivi)"""
        return crediti > 0
    
    @staticmethod
    def valida_email(email: str) -> bool:
        """Valida un'email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def valida_importo(importo: float) -> bool:
        """Valida un importo (positivo)"""
        return importo > 0
    
    @staticmethod
    def valida_data(data_str: str, formato: str = '%Y-%m-%d') -> bool:
        """Valida una stringa data"""
        try:
            datetime.strptime(data_str, formato)
            return True
        except ValueError:
            return False
        
    @staticmethod
    def sanitize_string(text: str) -> str:
        """Pulisce una stringa da caratteri speciali"""
        return text.strip().replace('\n', ' ').replace('\r', '')
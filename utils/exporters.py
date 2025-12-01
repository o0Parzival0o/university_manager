# utils/exporters.py
"""
Esportatori dati in vari formati
"""

import json
import csv
from pathlib import Path
from typing import List
from datetime import datetime


class DataExporter:
    """Esporta dati in vari formati"""
    
    @staticmethod
    def export_to_json(data: dict, filepath: str) -> bool:
        """
        Esporta dati in JSON
        
        Args:
            data: Dizionario con i dati
            filepath: Percorso file output
            
        Returns:
            True se successo, False altrimenti
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Errore export JSON: {e}")
            return False
    
    @staticmethod
    def export_to_csv(data: List[dict], filepath: str, fieldnames: List[str] = None) -> bool:
        """
        Esporta dati in CSV
        
        Args:
            data: Lista di dizionari
            filepath: Percorso file output
            fieldnames: Nomi delle colonne (opzionale)
            
        Returns:
            True se successo, False altrimenti
        """
        if not data:
            return False
        
        try:
            if fieldnames is None:
                fieldnames = list(data[0].keys())
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            return True
        except Exception as e:
            print(f"Errore export CSV: {e}")
            return False
    
    @staticmethod
    def export_to_txt(text: str, filepath: str) -> bool:
        """
        Esporta testo in file TXT
        
        Args:
            text: Testo da esportare
            filepath: Percorso file output
            
        Returns:
            True se successo, False altrimenti
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)
            return True
        except Exception as e:
            print(f"Errore export TXT: {e}")
            return False
    
    @staticmethod
    def create_backup_filename(base_name: str = "backup") -> str:
        """
        Crea un nome file per backup con timestamp
        
        Args:
            base_name: Nome base del file
            
        Returns:
            Nome file con timestamp
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{base_name}_{timestamp}.db"
# core/models.py
"""
Modelli dati per University Manager
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
import json


@dataclass
class Voto:
    """Modello per un voto universitario"""
    materia: str
    data: datetime
    crediti: int
    voto: int  # 18-30, 31 per 30L
    laurea_id: int
    id: Optional[int] = None
    
    def __post_init__(self):
        """Validazione dopo inizializzazione"""
        if not 18 <= self.voto <= 31:
            raise ValueError(f"Voto deve essere tra 18 e 31, ricevuto: {self.voto}")
        if self.crediti <= 0:
            raise ValueError(f"Crediti devono essere positivi, ricevuto: {self.crediti}")
    
    @property
    def voto_display(self) -> str:
        """Voto formattato per visualizzazione"""
        return "30L" if self.voto == 31 else str(self.voto)
    
    @property
    def voto_numerico(self) -> int:
        """Voto numerico per calcoli (30L = 30)"""
        return 30 if self.voto == 31 else self.voto
    
    @property
    def data_formattata(self) -> str:
        """Data formattata in italiano"""
        return self.data.strftime('%d/%m/%Y')
    
    def to_dict(self) -> dict:
        """Converte in dizionario"""
        return {
            'id': self.id,
            'materia': self.materia,
            'data': self.data.strftime('%Y-%m-%d'),
            'crediti': self.crediti,
            'voto': self.voto,
            'laurea_id': self.laurea_id
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Voto':
        """Crea un Voto da dizionario"""
        return cls(
            id=data.get('id'),
            materia=data['materia'],
            data=datetime.strptime(data['data'], '%Y-%m-%d'),
            crediti=data['crediti'],
            voto=data['voto'],
            laurea_id=data['laurea_id']
        )


@dataclass
class Laurea:
    """Modello per un corso di laurea"""
    nome: str
    tipo: str  # "triennale" o "magistrale"
    crediti_totali: int = 180
    id: Optional[int] = None
    
    def __post_init__(self):
        """Validazione dopo inizializzazione"""
        if self.tipo not in ['triennale', 'magistrale']:
            raise ValueError(f"Tipo deve essere 'triennale' o 'magistrale', ricevuto: {self.tipo}")
        if self.crediti_totali <= 0:
            raise ValueError(f"Crediti totali devono essere positivi, ricevuto: {self.crediti_totali}")
    
    @property
    def tipo_display(self) -> str:
        """Tipo formattato per visualizzazione"""
        return "Triennale" if self.tipo == "triennale" else "Magistrale"
    
    def to_dict(self) -> dict:
        """Converte in dizionario"""
        return {
            'id': self.id,
            'nome': self.nome,
            'tipo': self.tipo,
            'crediti_totali': self.crediti_totali
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Laurea':
        """Crea una Laurea da dizionario"""
        return cls(
            id=data.get('id'),
            nome=data['nome'],
            tipo=data['tipo'],
            crediti_totali=data.get('crediti_totali', 180)
        )


@dataclass
class Tassa:
    """Modello per una tassa universitaria"""
    descrizione: str
    importo: float
    scadenza: datetime
    pagata: bool = False
    id: Optional[int] = None
    data_pagamento: Optional[datetime] = None
    
    def __post_init__(self):
        """Validazione dopo inizializzazione"""
        if self.importo <= 0:
            raise ValueError(f"Importo deve essere positivo, ricevuto: {self.importo}")
    
    @property
    def scadenza_formattata(self) -> str:
        """Scadenza formattata"""
        return self.scadenza.strftime('%d/%m/%Y')
    
    @property
    def importo_formattato(self) -> str:
        """Importo formattato con valuta"""
        return f"€ {self.importo:.2f}"
    
    @property
    def stato(self) -> str:
        """Stato del pagamento"""
        if self.pagata:
            return "✅ Pagata"
        elif self.scadenza < datetime.now():
            return "⚠️ Scaduta"
        else:
            return "⏳ Da pagare"
    
    @property
    def giorni_alla_scadenza(self) -> int:
        """Giorni rimanenti alla scadenza"""
        delta = self.scadenza - datetime.now()
        return delta.days
    
    def to_dict(self) -> dict:
        """Converte in dizionario"""
        return {
            'id': self.id,
            'descrizione': self.descrizione,
            'importo': self.importo,
            'scadenza': self.scadenza.strftime('%Y-%m-%d'),
            'pagata': self.pagata,
            'data_pagamento': self.data_pagamento.strftime('%Y-%m-%d') if self.data_pagamento else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Tassa':
        """Crea una Tassa da dizionario"""
        return cls(
            id=data.get('id'),
            descrizione=data['descrizione'],
            importo=data['importo'],
            scadenza=datetime.strptime(data['scadenza'], '%Y-%m-%d'),
            pagata=data.get('pagata', False),
            data_pagamento=datetime.strptime(data['data_pagamento'], '%Y-%m-%d') 
                          if data.get('data_pagamento') else None
        )


@dataclass
class Domanda:
    """Modello per domanda d'esame"""
    materia: str
    anno: str
    testo: str
    id: Optional[int] = None
    difficolta: Optional[str] = None  # "facile", "media", "difficile"
    data_creazione: datetime = field(default_factory=datetime.now)
    
    @property
    def difficolta_emoji(self) -> str:
        """Emoji per la difficoltà"""
        mapping = {
            'facile': '🟢',
            'media': '🟡',
            'difficile': '🔴'
        }
        return mapping.get(self.difficolta, '⚪')
    
    def to_dict(self) -> dict:
        """Converte in dizionario"""
        return {
            'id': self.id,
            'materia': self.materia,
            'anno': self.anno,
            'testo': self.testo,
            'difficolta': self.difficolta,
            'data_creazione': self.data_creazione.strftime('%Y-%m-%d')
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Domanda':
        """Crea una Domanda da dizionario"""
        return cls(
            id=data.get('id'),
            materia=data['materia'],
            anno=data['anno'],
            testo=data['testo'],
            difficolta=data.get('difficolta'),
            data_creazione=datetime.strptime(data['data_creazione'], '%Y-%m-%d') 
                          if data.get('data_creazione') else datetime.now()
        )


@dataclass
class StatisticheVoti:
    """Statistiche calcolate sui voti"""
    media: float
    voto_laurea: int
    crediti_acquisiti: int
    crediti_totali: int
    esami_sostenuti: int
    percentuale_completamento: float
    voto_minimo: Optional[int] = None
    voto_massimo: Optional[int] = None
    
    @property
    def percentuale_display(self) -> str:
        """Percentuale formattata"""
        return f"{self.percentuale_completamento:.1f}%"
    
    @property
    def media_display(self) -> str:
        """Media formattata"""
        return f"{self.media:.2f}"
    
    def to_dict(self) -> dict:
        """Converte in dizionario"""
        return {
            'media': self.media,
            'voto_laurea': self.voto_laurea,
            'crediti_acquisiti': self.crediti_acquisiti,
            'crediti_totali': self.crediti_totali,
            'esami_sostenuti': self.esami_sostenuti,
            'percentuale_completamento': self.percentuale_completamento,
            'voto_minimo': self.voto_minimo,
            'voto_massimo': self.voto_massimo
        }
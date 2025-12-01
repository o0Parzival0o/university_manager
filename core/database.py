# core/database.py
"""
Gestione database SQLite per University Manager
"""

import sqlite3
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import os

from .models import Voto, Laurea, Tassa, Domanda


class Database:
    """Gestione centralizzata del database SQLite"""
    
    def __init__(self, db_path: str = None):
        """
        Inizializza il database
        
        Args:
            db_path: Percorso del file database. Se None, usa la directory home dell'utente
        """
        if db_path is None:
            # Crea directory nella home dell'utente
            home_dir = Path.home()
            app_dir = home_dir / "UniversityManager"
            app_dir.mkdir(exist_ok=True)
            db_path = app_dir / "university_manager.db"
        
        self.db_path = Path(db_path)
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Inizializza il database con le tabelle necessarie"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        # Abilita foreign keys
        cursor.execute('PRAGMA foreign_keys = ON')
        
        # Tabella Lauree
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lauree (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                tipo TEXT NOT NULL CHECK(tipo IN ('triennale', 'magistrale')),
                crediti_totali INTEGER DEFAULT 180,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabella Voti
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voti (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                materia TEXT NOT NULL,
                data DATE NOT NULL,
                crediti INTEGER NOT NULL CHECK(crediti > 0),
                voto INTEGER NOT NULL CHECK(voto >= 18 AND voto <= 31),
                laurea_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (laurea_id) REFERENCES lauree(id) ON DELETE CASCADE
            )
        ''')
        
        # Indice per migliorare le query sui voti
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_voti_laurea 
            ON voti(laurea_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_voti_data 
            ON voti(data)
        ''')
        
        # Tabella Tasse
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasse (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descrizione TEXT NOT NULL,
                importo REAL NOT NULL CHECK(importo > 0),
                scadenza DATE NOT NULL,
                pagata BOOLEAN DEFAULT 0,
                data_pagamento DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Indice per scadenze tasse
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_tasse_scadenza 
            ON tasse(scadenza)
        ''')
        
        # Tabella Domande
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS domande (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                materia TEXT NOT NULL,
                anno TEXT NOT NULL,
                testo TEXT NOT NULL,
                difficolta TEXT CHECK(difficolta IN ('facile', 'media', 'difficile')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Indice per domande per materia/anno
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_domande_materia_anno 
            ON domande(materia, anno)
        ''')
        
        self.conn.commit()
    
    # ========================================================================
    # OPERAZIONI LAUREE
    # ========================================================================
    
    def add_laurea(self, nome: str, tipo: str, crediti_totali: int = 180) -> int:
        """
        Aggiunge una nuova laurea
        
        Returns:
            ID della laurea creata
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO lauree (nome, tipo, crediti_totali) VALUES (?, ?, ?)',
                (nome, tipo, crediti_totali)
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError(f"Esiste già una laurea con nome '{nome}'")
    
    def get_all_lauree(self) -> List[Laurea]:
        """Recupera tutte le lauree ordinate per nome"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM lauree ORDER BY nome')
        rows = cursor.fetchall()
        
        return [Laurea(
            id=row['id'],
            nome=row['nome'],
            tipo=row['tipo'],
            crediti_totali=row['crediti_totali']
        ) for row in rows]
    
    def get_laurea_by_id(self, laurea_id: int) -> Optional[Laurea]:
        """Recupera una laurea per ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM lauree WHERE id = ?', (laurea_id,))
        row = cursor.fetchone()
        
        if row:
            return Laurea(
                id=row['id'],
                nome=row['nome'],
                tipo=row['tipo'],
                crediti_totali=row['crediti_totali']
            )
        return None
    
    def update_laurea(self, laurea_id: int, nome: str = None, 
                     tipo: str = None, crediti_totali: int = None):
        """Aggiorna una laurea esistente"""
        cursor = self.conn.cursor()
        updates = []
        params = []
        
        if nome is not None:
            updates.append('nome = ?')
            params.append(nome)
        if tipo is not None:
            updates.append('tipo = ?')
            params.append(tipo)
        if crediti_totali is not None:
            updates.append('crediti_totali = ?')
            params.append(crediti_totali)
        
        if updates:
            params.append(laurea_id)
            query = f"UPDATE lauree SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            self.conn.commit()
    
    def delete_laurea(self, laurea_id: int):
        """Elimina una laurea e tutti i voti associati (CASCADE)"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM lauree WHERE id = ?', (laurea_id,))
        self.conn.commit()
    
    # ========================================================================
    # OPERAZIONI VOTI
    # ========================================================================
    
    def add_voto(self, materia: str, data: datetime, crediti: int, 
                 voto: int, laurea_id: int) -> int:
        """
        Aggiunge un nuovo voto
        
        Returns:
            ID del voto creato
        """
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO voti (materia, data, crediti, voto, laurea_id) VALUES (?, ?, ?, ?, ?)',
            (materia, data.strftime('%Y-%m-%d'), crediti, voto, laurea_id)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_voti_by_laurea(self, laurea_id: int) -> List[Voto]:
        """Recupera tutti i voti di una laurea ordinati per data"""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM voti WHERE laurea_id = ? ORDER BY data',
            (laurea_id,)
        )
        rows = cursor.fetchall()
        
        return [Voto(
            id=row['id'],
            materia=row['materia'],
            data=datetime.strptime(row['data'], '%Y-%m-%d'),
            crediti=row['crediti'],
            voto=row['voto'],
            laurea_id=row['laurea_id']
        ) for row in rows]
    
    def get_voto_by_id(self, voto_id: int) -> Optional[Voto]:
        """Recupera un voto per ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM voti WHERE id = ?', (voto_id,))
        row = cursor.fetchone()
        
        if row:
            return Voto(
                id=row['id'],
                materia=row['materia'],
                data=datetime.strptime(row['data'], '%Y-%m-%d'),
                crediti=row['crediti'],
                voto=row['voto'],
                laurea_id=row['laurea_id']
            )
        return None
    
    def update_voto(self, voto_id: int, materia: str = None, data: datetime = None,
                    crediti: int = None, voto: int = None):
        """Aggiorna un voto esistente"""
        cursor = self.conn.cursor()
        updates = []
        params = []
        
        if materia is not None:
            updates.append('materia = ?')
            params.append(materia)
        if data is not None:
            updates.append('data = ?')
            params.append(data.strftime('%Y-%m-%d'))
        if crediti is not None:
            updates.append('crediti = ?')
            params.append(crediti)
        if voto is not None:
            updates.append('voto = ?')
            params.append(voto)
        
        if updates:
            params.append(voto_id)
            query = f"UPDATE voti SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            self.conn.commit()
    
    def delete_voto(self, voto_id: int):
        """Elimina un voto"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM voti WHERE id = ?', (voto_id,))
        self.conn.commit()
    
    # ========================================================================
    # OPERAZIONI TASSE
    # ========================================================================
    
    def add_tassa(self, descrizione: str, importo: float, scadenza: datetime) -> int:
        """
        Aggiunge una nuova tassa
        
        Returns:
            ID della tassa creata
        """
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO tasse (descrizione, importo, scadenza) VALUES (?, ?, ?)',
            (descrizione, importo, scadenza.strftime('%Y-%m-%d'))
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_all_tasse(self, ordina_per_scadenza: bool = True) -> List[Tassa]:
        """Recupera tutte le tasse"""
        cursor = self.conn.cursor()
        query = 'SELECT * FROM tasse'
        if ordina_per_scadenza:
            query += ' ORDER BY pagata, scadenza'
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        return [Tassa(
            id=row['id'],
            descrizione=row['descrizione'],
            importo=row['importo'],
            scadenza=datetime.strptime(row['scadenza'], '%Y-%m-%d'),
            pagata=bool(row['pagata']),
            data_pagamento=datetime.strptime(row['data_pagamento'], '%Y-%m-%d') 
                          if row['data_pagamento'] else None
        ) for row in rows]
    
    def get_tasse_non_pagate(self) -> List[Tassa]:
        """Recupera solo le tasse non pagate"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasse WHERE pagata = 0 ORDER BY scadenza')
        rows = cursor.fetchall()
        
        return [Tassa(
            id=row['id'],
            descrizione=row['descrizione'],
            importo=row['importo'],
            scadenza=datetime.strptime(row['scadenza'], '%Y-%m-%d'),
            pagata=False
        ) for row in rows]
    
    def update_tassa(self, tassa_id: int, descrizione: str = None,
                    importo: float = None, scadenza: datetime = None):
        """Aggiorna una tassa esistente"""
        cursor = self.conn.cursor()
        updates = []
        params = []
        
        if descrizione is not None:
            updates.append('descrizione = ?')
            params.append(descrizione)
        if importo is not None:
            updates.append('importo = ?')
            params.append(importo)
        if scadenza is not None:
            updates.append('scadenza = ?')
            params.append(scadenza.strftime('%Y-%m-%d'))
        
        if updates:
            params.append(tassa_id)
            query = f"UPDATE tasse SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            self.conn.commit()
    
    def toggle_pagamento_tassa(self, tassa_id: int):
        """Cambia lo stato di pagamento di una tassa"""
        cursor = self.conn.cursor()
        cursor.execute(
            '''UPDATE tasse 
               SET pagata = NOT pagata,
                   data_pagamento = CASE WHEN pagata = 0 THEN DATE('now') ELSE NULL END
               WHERE id = ?''',
            (tassa_id,)
        )
        self.conn.commit()
    
    def delete_tassa(self, tassa_id: int):
        """Elimina una tassa"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM tasse WHERE id = ?', (tassa_id,))
        self.conn.commit()
    
    # ========================================================================
    # OPERAZIONI DOMANDE
    # ========================================================================
    
    def add_domanda(self, materia: str, anno: str, testo: str, 
                   difficolta: str = None) -> int:
        """
        Aggiunge una nuova domanda
        
        Returns:
            ID della domanda creata
        """
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO domande (materia, anno, testo, difficolta) VALUES (?, ?, ?, ?)',
            (materia, anno, testo, difficolta)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_domande_by_materia(self, materia: str, anno: str = None) -> List[Domanda]:
        """Recupera domande per materia (e opzionalmente anno)"""
        cursor = self.conn.cursor()
        
        if anno:
            cursor.execute(
                'SELECT * FROM domande WHERE materia = ? AND anno = ?',
                (materia, anno)
            )
        else:
            cursor.execute(
                'SELECT * FROM domande WHERE materia = ?',
                (materia,)
            )
        
        rows = cursor.fetchall()
        
        return [Domanda(
            id=row['id'],
            materia=row['materia'],
            anno=row['anno'],
            testo=row['testo'],
            difficolta=row['difficolta'],
            data_creazione=datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S')
        ) for row in rows]
    
    def get_all_anni(self) -> List[str]:
        """Recupera tutti gli anni disponibili"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT DISTINCT anno FROM domande ORDER BY anno')
        return [row['anno'] for row in cursor.fetchall()]
    
    def get_all_materie(self, anno: str = None) -> List[str]:
        """Recupera tutte le materie disponibili (opzionalmente per anno)"""
        cursor = self.conn.cursor()
        
        if anno:
            cursor.execute(
                'SELECT DISTINCT materia FROM domande WHERE anno = ? ORDER BY materia',
                (anno,)
            )
        else:
            cursor.execute('SELECT DISTINCT materia FROM domande ORDER BY materia')
        
        return [row['materia'] for row in cursor.fetchall()]
    
    def update_domanda(self, domanda_id: int, testo: str = None, 
                      difficolta: str = None):
        """Aggiorna una domanda esistente"""
        cursor = self.conn.cursor()
        updates = []
        params = []
        
        if testo is not None:
            updates.append('testo = ?')
            params.append(testo)
        if difficolta is not None:
            updates.append('difficolta = ?')
            params.append(difficolta)
        
        if updates:
            params.append(domanda_id)
            query = f"UPDATE domande SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            self.conn.commit()
    
    def delete_domanda(self, domanda_id: int):
        """Elimina una domanda"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM domande WHERE id = ?', (domanda_id,))
        self.conn.commit()
    
    # ========================================================================
    # UTILITY
    # ========================================================================
    
    def backup_database(self, backup_path: str = None):
        """Crea un backup del database"""
        if backup_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{self.db_path.stem}_backup_{timestamp}.db"
        
        import shutil
        shutil.copy2(self.db_path, backup_path)
        return backup_path
    
    def close(self):
        """Chiude la connessione al database"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
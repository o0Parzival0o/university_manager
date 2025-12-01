# core/calculator.py
"""
Calcolatore di statistiche e proiezioni per i voti
"""

from typing import List, Dict, Tuple
import numpy as np
import datetime
from .models import Voto, StatisticheVoti, Laurea


class CalcolatoreVoti:
    """Calcola statistiche e proiezioni sui voti"""
    
    @staticmethod
    def calcola_media(voti: List[Voto]) -> float:
        """
        Calcola la media ponderata dei voti
        
        Args:
            voti: Lista di voti
            
        Returns:
            Media ponderata (0.0 se nessun voto)
        """
        if not voti:
            return 0.0
        
        somma_ponderata = sum(v.voto_numerico * v.crediti for v in voti)
        crediti_totali = sum(v.crediti for v in voti)
        
        return somma_ponderata / crediti_totali if crediti_totali > 0 else 0.0
    
    @staticmethod
    def calcola_voto_laurea(media: float, bonus_tesi: int = 0) -> int:
        """
        Calcola il voto di laurea
        
        Args:
            media: Media ponderata
            bonus_tesi: Punti bonus per la tesi (default 0)
            
        Returns:
            Voto di laurea base + bonus (max 110L = 113)
        """
        voto_base = round(media * 110 / 30)
        voto_totale = min(voto_base + bonus_tesi, 113)  # 113 = 110L
        return voto_totale
    
    @staticmethod
    def calcola_statistiche(voti: List[Voto], laurea: Laurea) -> StatisticheVoti:
        """
        Calcola statistiche complete sui voti
        
        Args:
            voti: Lista di voti
            laurea: Corso di laurea
            
        Returns:
            Oggetto StatisticheVoti con tutte le statistiche
        """
        if not voti:
            return StatisticheVoti(
                media=0.0,
                voto_laurea=0,
                crediti_acquisiti=0,
                crediti_totali=laurea.crediti_totali,
                esami_sostenuti=0,
                percentuale_completamento=0.0,
                voto_minimo=None,
                voto_massimo=None
            )
        
        media = CalcolatoreVoti.calcola_media(voti)
        crediti_acquisiti = sum(v.crediti for v in voti)
        voti_numerici = [v.voto_numerico for v in voti]
        
        return StatisticheVoti(
            media=media,
            voto_laurea=CalcolatoreVoti.calcola_voto_laurea(media),
            crediti_acquisiti=crediti_acquisiti,
            crediti_totali=laurea.crediti_totali,
            esami_sostenuti=len(voti),
            percentuale_completamento=(crediti_acquisiti / laurea.crediti_totali) * 100,
            voto_minimo=min(voti_numerici),
            voto_massimo=max(voti_numerici)
        )
    
    @staticmethod
    def media_progressiva(voti: List[Voto]) -> List[float]:
        """
        Calcola la media progressiva esame dopo esame
        
        Args:
            voti: Lista di voti (devono essere ordinati cronologicamente)
            
        Returns:
            Lista di medie progressive
        """
        if not voti:
            return []
        
        medie = []
        for i in range(len(voti)):
            voti_subset = voti[:i+1]
            medie.append(CalcolatoreVoti.calcola_media(voti_subset))
        
        return medie
    
    @staticmethod
    def proietta_voti(voti: List[Voto], crediti_prossimo: int = 6) -> Dict[str, Dict]:
        """
        Proietta la media con tutti i voti possibili (18-30, 30L)
        
        Args:
            voti: Lista di voti attuali
            crediti_prossimo: Crediti del prossimo esame
            
        Returns:
            Dizionario con proiezioni per ogni voto possibile
            Formato: {
                "18": {"media": 27.5, "voto_laurea": 101, "delta": -0.3},
                "19": {"media": 27.6, "voto_laurea": 101, "delta": -0.2},
                ...
            }
        """
        if not voti or crediti_prossimo <= 0:
            return {}
        
        media_attuale = CalcolatoreVoti.calcola_media(voti)
        crediti_attuali = sum(v.crediti for v in voti)
        
        proiezioni = {}
        voti_possibili = list(range(18, 31)) + [31]  # 18-30 + 30L
        
        for voto_futuro in voti_possibili:
            voto_calc = 30 if voto_futuro == 31 else voto_futuro
            
            nuova_media = (
                (media_attuale * crediti_attuali + voto_calc * crediti_prossimo) /
                (crediti_attuali + crediti_prossimo)
            )
            
            voto_display = "30L" if voto_futuro == 31 else str(voto_futuro)
            proiezioni[voto_display] = {
                'media': round(nuova_media, 2),
                'voto_laurea': CalcolatoreVoti.calcola_voto_laurea(nuova_media),
                'delta': round(nuova_media - media_attuale, 2)
            }
        
        return proiezioni
    
    @staticmethod
    def calcola_voto_necessario(voti: List[Voto], media_target: float, 
                               crediti_rimanenti: int) -> Tuple[float, bool]:
        """
        Calcola il voto medio necessario per raggiungere una media target
        
        Args:
            voti: Lista di voti attuali
            media_target: Media che si vuole raggiungere
            crediti_rimanenti: Crediti ancora da acquisire
            
        Returns:
            Tupla (voto_necessario, raggiungibile)
            - voto_necessario: Voto medio da prendere nei crediti rimanenti
            - raggiungibile: True se è possibile (voto_necessario <= 30)
        """
        if not voti or crediti_rimanenti <= 0:
            return (0.0, False)
        
        media_attuale = CalcolatoreVoti.calcola_media(voti)
        crediti_attuali = sum(v.crediti for v in voti)
        
        # Formula: media_target = (media_attuale * crediti_attuali + voto_necessario * crediti_rimanenti) 
        #                        / (crediti_attuali + crediti_rimanenti)
        # Risolvendo per voto_necessario:
        voto_necessario = (
            media_target * (crediti_attuali + crediti_rimanenti) - 
            media_attuale * crediti_attuali
        ) / crediti_rimanenti
        
        raggiungibile = 18 <= voto_necessario <= 30
        
        return (round(voto_necessario, 2), raggiungibile)
    
    @staticmethod
    def analizza_andamento(voti: List[Voto], finestra: int = 3) -> Dict:
        """
        Analizza l'andamento recente dei voti
        
        Args:
            voti: Lista di voti ordinati cronologicamente
            finestra: Numero di voti recenti da considerare
            
        Returns:
            Dizionario con analisi dell'andamento
        """
        if len(voti) < 2:
            return {
                'tendenza': 'insufficient_data',
                'descrizione': 'Dati insufficienti per l\'analisi',
                'media_recente': 0.0,
                'media_globale': 0.0
            }
        
        media_globale = CalcolatoreVoti.calcola_media(voti)
        voti_recenti = voti[-finestra:]
        media_recente = CalcolatoreVoti.calcola_media(voti_recenti)
        
        diff = media_recente - media_globale
        
        if diff > 0.5:
            tendenza = 'crescita'
            descrizione = '📈 In miglioramento'
        elif diff < -0.5:
            tendenza = 'decrescita'
            descrizione = '📉 In calo'
        else:
            tendenza = 'stabile'
            descrizione = '➡️ Stabile'
        
        return {
            'tendenza': tendenza,
            'descrizione': descrizione,
            'media_recente': round(media_recente, 2),
            'media_globale': round(media_globale, 2),
            'differenza': round(diff, 2)
        }
    
    @staticmethod
    def distribuzione_voti(voti: List[Voto]) -> Dict[int, int]:
        """
        Calcola la distribuzione dei voti
        
        Args:
            voti: Lista di voti
            
        Returns:
            Dizionario {voto: conteggio}
        """
        distribuzione = {}
        for voto in voti:
            v = voto.voto  # Usa voto originale (31 per 30L)
            distribuzione[v] = distribuzione.get(v, 0) + 1
        
        return dict(sorted(distribuzione.items()))
    
    @staticmethod
    def calcola_percentili(voti: List[Voto]) -> Dict[str, float]:
        """
        Calcola i percentili dei voti
        
        Args:
            voti: Lista di voti
            
        Returns:
            Dizionario con percentili 25, 50 (mediana), 75
        """
        if not voti:
            return {'p25': 0, 'p50': 0, 'p75': 0}
        
        voti_numerici = sorted([v.voto_numerico for v in voti])
        
        return {
            'p25': np.percentile(voti_numerici, 25),
            'p50': np.percentile(voti_numerici, 50),  # Mediana
            'p75': np.percentile(voti_numerici, 75)
        }
    
    @staticmethod
    def suggerisci_strategia(stats: StatisticheVoti, 
                           voto_laurea_target: int = 110) -> Dict:
        """
        Suggerisce una strategia per raggiungere un voto di laurea target
        
        Args:
            stats: Statistiche attuali
            voto_laurea_target: Voto di laurea desiderato
            
        Returns:
            Dizionario con suggerimenti strategici
        """
        media_target = (voto_laurea_target * 30) / 110
        crediti_rimanenti = stats.crediti_totali - stats.crediti_acquisiti
        
        if crediti_rimanenti <= 0:
            return {
                'raggiungibile': stats.voto_laurea >= voto_laurea_target,
                'messaggio': 'Hai completato tutti i crediti!',
                'voto_necessario': None
            }
        
        # Crea lista di voti fittizi per calcolo
        voti_fittizi = [
            Voto(
                materia="dummy",
                data=None,
                crediti=stats.crediti_acquisiti,
                voto=round(stats.media),
                laurea_id=1
            )
        ]
        
        voto_necessario, raggiungibile = CalcolatoreVoti.calcola_voto_necessario(
            voti_fittizi, media_target, crediti_rimanenti
        )
        
        if raggiungibile:
            if voto_necessario <= 24:
                difficolta = 'facile'
                messaggio = f'✅ Obiettivo facilmente raggiungibile! Mantieni una media di {voto_necessario:.1f}'
            elif voto_necessario <= 27:
                difficolta = 'media'
                messaggio = f'🎯 Obiettivo raggiungibile con impegno. Mira a {voto_necessario:.1f} di media'
            else:
                difficolta = 'difficile'
                messaggio = f'💪 Obiettivo impegnativo! Necessaria media di {voto_necessario:.1f}'
        else:
            messaggio = f'❌ Obiettivo non raggiungibile. Sarebbe necessaria media di {voto_necessario:.1f}'
            difficolta = 'impossibile'
        
        return {
            'raggiungibile': raggiungibile,
            'voto_necessario': voto_necessario,
            'crediti_rimanenti': crediti_rimanenti,
            'difficolta': difficolta,
            'messaggio': messaggio
        }


class EsportatoreStatistiche:
    """Esporta statistiche in vari formati"""
    
    @staticmethod
    def esporta_csv(voti: List[Voto], filepath: str):
        """Esporta voti in formato CSV"""
        import csv
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Materia', 'Data', 'Crediti', 'Voto'])
            
            for voto in voti:
                writer.writerow([
                    voto.materia,
                    voto.data_formattata,
                    voto.crediti,
                    voto.voto_display
                ])
    
    @staticmethod
    def esporta_json(voti: List[Voto], filepath: str):
        """Esporta voti in formato JSON"""
        import json
        
        data = {
            'voti': [v.to_dict() for v in voti],
            'esportato_il': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def genera_report_html(voti: List[Voto], stats: StatisticheVoti, 
                          laurea: Laurea, filepath: str):
        """Genera un report HTML completo"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Report Voti - {laurea.nome}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #2196F3; }}
        .stats {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #2196F3; color: white; }}
    </style>
</head>
<body>
    <h1>Report Voti - {laurea.nome}</h1>
    
    <div class="stats">
        <h2>Statistiche</h2>
        <p><strong>Media:</strong> {stats.media_display}</p>
        <p><strong>Voto di Laurea:</strong> {stats.voto_laurea}/110</p>
        <p><strong>Crediti:</strong> {stats.crediti_acquisiti}/{stats.crediti_totali} 
           ({stats.percentuale_display})</p>
        <p><strong>Esami sostenuti:</strong> {stats.esami_sostenuti}</p>
    </div>
    
    <h2>Elenco Voti</h2>
    <table>
        <tr>
            <th>Materia</th>
            <th>Data</th>
            <th>Crediti</th>
            <th>Voto</th>
        </tr>
"""
        
        for voto in voti:
            html += f"""
        <tr>
            <td>{voto.materia}</td>
            <td>{voto.data_formattata}</td>
            <td>{voto.crediti}</td>
            <td>{voto.voto_display}</td>
        </tr>
"""
        
        html += """
    </table>
</body>
</html>
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
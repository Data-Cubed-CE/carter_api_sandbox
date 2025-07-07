import json
import csv
import os
from typing import Dict, Any, Set
from collections import defaultdict

class SimpleJSONLToCSV:
    """
    Prosty konwerter JSONL -> CSV bez filtrowania
    Wyciąga WSZYSTKIE dane do pliku CSV
    """
    
    def __init__(self, jsonl_file: str, csv_file: str):
        self.jsonl_file = jsonl_file
        self.csv_file = csv_file
        self.all_keys = set()
        self.total_records = 0
        
    def convert(self, batch_size: int = 5000, progress_interval: int = 100000):
        """
        Konwertuje cały plik JSONL do CSV
        
        Args:
            batch_size: Ile rekordów zapisywać na raz
            progress_interval: Co ile rekordów pokazać postęp
        """
        
        print(f"🔄 Konwertuję {self.jsonl_file} -> {self.csv_file}")
        print(f"📊 Parametry: batch_size={batch_size}, progress_interval={progress_interval}")
        
        # Krok 1: Skanowanie struktury
        print("\n1️⃣ Skanuję strukturę pliku...")
        self._scan_structure()
        
        # Krok 2: Konwersja
        print(f"\n2️⃣ Konwertuję {self.total_records:,} rekordów...")
        self._convert_data(batch_size, progress_interval)
        
        print(f"\n✅ Gotowe! CSV zapisany w: {self.csv_file}")
        self._print_summary()
    
    def _scan_structure(self):
        """Pierwszy przejazd - zbiera wszystkie możliwe klucze"""
        
        file_size = os.path.getsize(self.jsonl_file)
        processed_bytes = 0
        
        with open(self.jsonl_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        record = json.loads(line)
                        self.total_records += 1
                        
                        # Zbierz wszystkie klucze (płaskie)
                        flat_record = self._flatten_dict(record)
                        self.all_keys.update(flat_record.keys())
                        
                        processed_bytes += len(line.encode('utf-8'))
                        
                        # Progress co 1% pliku
                        if processed_bytes % (file_size // 100 + 1) == 0:
                            progress = (processed_bytes / file_size) * 100
                            print(f"   Postęp skanowania: {progress:.1f}% ({self.total_records:,} rekordów)")
                            
                    except json.JSONDecodeError:
                        continue
        
        print(f"   ✅ Znaleziono {len(self.all_keys)} unikalnych kolumn")
        print(f"   📊 Całkowita liczba rekordów: {self.total_records:,}")
    
    def _convert_data(self, batch_size: int, progress_interval: int):
        """Drugi przejazd - konwertuje dane do CSV"""
        
        # Sortuj kolumny dla konsystentności
        fieldnames = sorted(list(self.all_keys))
        
        batch = []
        processed = 0
        
        with open(self.jsonl_file, 'r', encoding='utf-8') as infile, \
             open(self.csv_file, 'w', newline='', encoding='utf-8') as outfile:
            
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for line_num, line in enumerate(infile, 1):
                if line.strip():
                    try:
                        record = json.loads(line)
                        
                        # Spłaszcz rekord
                        flat_record = self._flatten_dict(record)
                        
                        # Wypełnij brakujące kolumny
                        row = {key: flat_record.get(key, '') for key in fieldnames}
                        
                        # Dodaj do batcha
                        batch.append(row)
                        
                        # Zapisz batch
                        if len(batch) >= batch_size:
                            writer.writerows(batch)
                            processed += len(batch)
                            batch = []
                            
                            if processed % progress_interval == 0:
                                progress = (processed / self.total_records) * 100
                                print(f"   💾 Zapisano: {processed:,}/{self.total_records:,} ({progress:.1f}%)")
                        
                    except json.JSONDecodeError:
                        continue
            
            # Zapisz ostatni batch
            if batch:
                writer.writerows(batch)
                processed += len(batch)
        
        print(f"   ✅ Zapisano {processed:,} rekordów do CSV")
    
    def _flatten_dict(self, data: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, str]:
        """
        Spłaszcza zagnieżdżony słownik do jednego poziomu
        
        Example:
        {'user': {'name': 'John', 'age': 30}} -> {'user_name': 'John', 'user_age': 30}
        """
        items = []
        
        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            
            if isinstance(value, dict):
                # Rekurencyjnie spłaszcz słownik
                items.extend(self._flatten_dict(value, new_key, sep=sep).items())
            elif isinstance(value, list):
                # Konwertuj listę na string
                if value:
                    # Sprawdź typ pierwszego elementu
                    if isinstance(value[0], dict):
                        # Lista słowników - weź pierwszy element i spłaszcz
                        items.extend(self._flatten_dict(value[0], f"{new_key}_0", sep=sep).items())
                        # Dodaj informację o długości listy
                        items.append((f"{new_key}_count", len(value)))
                    else:
                        # Lista prostych wartości - połącz pipe'em
                        items.append((new_key, '|'.join(str(v) for v in value)))
                else:
                    # Pusta lista
                    items.append((new_key, ''))
            else:
                # Prosta wartość
                items.append((new_key, str(value) if value is not None else ''))
        
        return dict(items)
    
    def _print_summary(self):
        """Wyświetla podsumowanie konwersji"""
        
        file_size_mb = os.path.getsize(self.csv_file) / (1024 * 1024)
        
        print(f"\n📋 PODSUMOWANIE:")
        print(f"   📁 Plik źródłowy: {self.jsonl_file}")
        print(f"   📄 Plik docelowy: {self.csv_file}")
        print(f"   📊 Rekordów: {self.total_records:,}")
        print(f"   🗂️ Kolumn: {len(self.all_keys)}")
        print(f"   💾 Rozmiar CSV: {file_size_mb:.1f} MB")
        
        # Pokaż przykładowe kolumny
        sample_keys = sorted(list(self.all_keys))[:20]
        print(f"\n🔍 Przykładowe kolumny (pierwsze 20):")
        for i, key in enumerate(sample_keys, 1):
            print(f"   {i:2d}. {key}")
        
        if len(self.all_keys) > 20:
            print(f"   ... i {len(self.all_keys) - 20} więcej")

# Funkcja do szybkiego użycia
def convert_jsonl_to_csv(jsonl_file: str, csv_file: str = None, 
                        batch_size: int = 5000, progress_interval: int = 100000):
    """
    Szybka funkcja do konwersji JSONL -> CSV
    
    Args:
        jsonl_file: Ścieżka do pliku JSONL
        csv_file: Ścieżka do pliku CSV (opcjonalna)
        batch_size: Rozmiar batcha
        progress_interval: Interwał raportowania postępu
    """
    
    if csv_file is None:
        csv_file = jsonl_file.replace('.jsonl', '.csv').replace('.json', '.csv')
    
    converter = SimpleJSONLToCSV(jsonl_file, csv_file)
    converter.convert(batch_size, progress_interval)
    
    return csv_file

# Optimized version for very large files
class OptimizedJSONLToCSV:
    """
    Zoptymalizowana wersja dla bardzo dużych plików (>10GB)
    """
    
    def __init__(self, jsonl_file: str, csv_file: str):
        self.jsonl_file = jsonl_file
        self.csv_file = csv_file
    
    def convert_streaming(self, sample_size: int = 10000):
        """
        Konwersja streamingowa - próbkuje strukturę z pierwszych N rekordów
        Szybsza dla bardzo dużych plików
        """
        
        print(f"🚀 OPTYMALIZOWANA KONWERSJA")
        print(f"📊 Próbkuję strukturę z pierwszych {sample_size} rekordów")
        
        # Krok 1: Próbkuj strukturę
        all_keys = set()
        with open(self.jsonl_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= sample_size:
                    break
                if line.strip():
                    try:
                        record = json.loads(line)
                        flat_record = self._flatten_dict(record)
                        all_keys.update(flat_record.keys())
                    except json.JSONDecodeError:
                        continue
        
        fieldnames = sorted(list(all_keys))
        print(f"   ✅ Znaleziono {len(fieldnames)} kolumn z próbki")
        
        # Krok 2: Konwertuj cały plik
        print(f"\n🔄 Konwertuję cały plik...")
        
        processed = 0
        batch = []
        batch_size = 10000
        
        with open(self.jsonl_file, 'r', encoding='utf-8') as infile, \
             open(self.csv_file, 'w', newline='', encoding='utf-8') as outfile:
            
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for line_num, line in enumerate(infile, 1):
                if line.strip():
                    try:
                        record = json.loads(line)
                        flat_record = self._flatten_dict(record)
                        row = {key: flat_record.get(key, '') for key in fieldnames}
                        batch.append(row)
                        
                        if len(batch) >= batch_size:
                            writer.writerows(batch)
                            processed += len(batch)
                            batch = []
                            
                            if processed % 500000 == 0:
                                print(f"   💾 Przetworzono: {processed:,} rekordów")
                        
                    except json.JSONDecodeError:
                        continue
            
            # Ostatni batch
            if batch:
                writer.writerows(batch)
                processed += len(batch)
        
        print(f"✅ Gotowe! Przetworzono {processed:,} rekordów")
    
    def _flatten_dict(self, data: dict, parent_key: str = '', sep: str = '_') -> dict:
        """Uproszczona wersja flatten dla szybkości"""
        items = []
        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            if isinstance(value, dict):
                items.extend(self._flatten_dict(value, new_key, sep=sep).items())
            elif isinstance(value, list):
                items.append((new_key, '|'.join(str(v) for v in value) if value else ''))
            else:
                items.append((new_key, str(value) if value is not None else ''))
        return dict(items)

# PRZYKŁADY UŻYCIA
# if __name__ == "__main__":
    
#     print("🏨 JSONL TO CSV CONVERTER")
#     print("="*50)
    
#     # SPOSÓB 1: Podstawowa konwersja
#     print("\n1️⃣ PODSTAWOWA KONWERSJA:")
#     convert_jsonl_to_csv('hotels.jsonl', 'hotels_full.csv')
    
#     # SPOSÓB 2: Z customowymi parametrami
#     print("\n2️⃣ Z CUSTOMOWYMI PARAMETRAMI:")
#     converter = SimpleJSONLToCSV('hotels.jsonl', 'hotels_custom.csv')
#     converter.convert(batch_size=10000, progress_interval=50000)
    
#     # SPOSÓB 3: Optimized dla bardzo dużych plików
#     print("\n3️⃣ OPTIMIZED (dla plików >10GB):")
#     opt_converter = OptimizedJSONLToCSV('hotels.jsonl', 'hotels_optimized.csv')
#     opt_converter.convert_streaming(sample_size=5000)
    
#     print("\n🎯 Wszystkie konwersje zakończone!")

# # CLI Usage
# import sys
# if len(sys.argv) >= 2:
#     input_file = sys.argv[1]
#     output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.jsonl', '.csv')
    
#     print(f"Converting {input_file} -> {output_file}")
#     convert_jsonl_to_csv(input_file, output_file)
import json
import csv

def extract_target_hotels(jsonl_file='hotels.jsonl', output_csv='target_hotels.csv'):
    """
    Prosty ekstraktor hoteli z konkretnych lokalizacji
    """
    
    # Lista krajów które nas interesują (kody ISO)
    target_countries = {
        'AW',  # Aruba
        'AU',  # Australia  
        'ME',  # Czarnogóra
        'DO',  # Dominikana
        'EG',  # Egipt
        'FR',  # Francja
        'GR',  # Grecja
        'ES',  # Hiszpania
        'ID',  # Indonezja
        'IS',  # Islandia
        'MV',  # Malediwy
        'MY',  # Malezja
        'MA',  # Maroko
        'MU',  # Mauritius
        'PT',  # Portugalia
        'QA',  # Qatar
        'ZA',  # RPA
        'SC',  # Seszele
        'SG',  # Singapur
        'CH',  # Szwajcaria
        'TH',  # Tajlandia
        'TR',  # Turcja
        'AE',  # UAE
        'US',  # USA
        'GB',  # Wielka Brytania
        'VN',  # Wietnam
        'IT'   # Włochy
    }
    
    # Lista miast które nas interesują
    target_cities = [
        'sydney', 'hurghada', 'sharm', 'biarritz', 'val thorens',
        'athens', 'ateny', 'chalkidiki', 'costa navarino', 'corfu', 'korfu',
        'crete', 'kreta', 'skiatos', 'andalucia', 'andaluzja', 'majorca', 'majorka',
        'marbella', 'tenerife', 'teneryfa', 'valencia', 'walencja',
        'bali', 'jimbaran', 'nusa dua', 'grindavik', 'langkawi',
        'marrakech', 'marakesz', 'tamuda bay', 'madeira', 'madera', 'porto',
        'doha', 'george', 'andermatt', 'st. moritz', 'krabi', 'pattaya',
        'phi phi', 'phuket', 'yao noi', 'antalya', 'belek',
        'abu dhabi', 'dubai', 'dubaj', 'ras al khaimah', 'miami', 'orlando',
        'scotland', 'szkocja', 'phu quoc', 'dolomites', 'dolomity',
        'lake garda', 'sardinia', 'sardynia', 'sicily', 'sycylia'
    ]
    
    print(f"🔍 Szukam hoteli z konkretnych lokalizacji...")
    print(f"📁 Plik: {jsonl_file} -> {output_csv}")
    
    found_hotels = []
    processed = 0
    
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    hotel = json.loads(line)
                    processed += 1
                    
                    # Sprawdź kraj
                    country = hotel.get('region', {}).get('country_code', '')
                    
                    if country in target_countries:
                        # Sprawdź miasto dla niektórych krajów
                        region_name = hotel.get('region', {}).get('name', '').lower()
                        address = hotel.get('address', '').lower()
                        
                        # Dla małych krajów - bierzemy wszystkie hotele
                        if country in ['AW', 'ME', 'DO', 'MV', 'MU', 'QA', 'SC', 'SG']:
                            found_hotels.append(hotel)
                        else:
                            # Dla dużych krajów - sprawdzamy miasta
                            for city in target_cities:
                                if city in region_name or city in address:
                                    found_hotels.append(hotel)
                                    break
                    
                    # Progress co 100k
                    if processed % 100000 == 0:
                        print(f"📊 Przetworzono: {processed:,} | Znaleziono: {len(found_hotels)}")
                        
                except:
                    continue
    
    print(f"✅ Znaleziono {len(found_hotels)} hoteli z {processed:,} przetworzonych")
    
    # Zapisz do CSV
    if found_hotels:
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'id', 'hid', 'name', 'address', 'country', 'city', 'stars', 
                'latitude', 'longitude', 'closed', 'phone', 'email',
                'image_urls', 'images_count', 'website', 'hotel_chain',
                'check_in_time', 'check_out_time', 'kind', 'postal_code',
                'rooms_number', 'floors_number', 'year_built', 'year_renovated',
                'amenities', 'amenities_count', 'description'
            ])
            
            # Data
            for hotel in found_hotels:
                region = hotel.get('region', {})
                facts = hotel.get('facts', {})
                
                # Zbierz wszystkie zdjęcia
                images = hotel.get('images', []) or []
                images_ext = hotel.get('images_ext', []) or []
                
                # URLs zdjęć
                image_urls = []
                image_urls.extend(images)  # Proste URLs
                
                # URLs z images_ext (bardziej szczegółowe)
                for img in images_ext:
                    if isinstance(img, dict) and 'url' in img:
                        image_urls.append(img['url'])
                
                # Łącz URLs pipe'em
                images_text = '|'.join(image_urls[:5])  # Maksymalnie 5 zdjęć
                
                # Zbierz amenities (udogodnienia)
                amenities = []
                for group in hotel.get('amenity_groups', []):
                    amenities.extend(group.get('amenities', []))
                amenities_text = '|'.join(amenities[:10])  # Pierwsze 10
                
                # Zbierz opis
                description_parts = []
                for desc in hotel.get('description_struct', []):
                    if isinstance(desc, dict) and 'paragraphs' in desc:
                        description_parts.extend(desc['paragraphs'])
                description_text = ' '.join(description_parts)[:500]  # Pierwsze 500 znaków
                
                writer.writerow([
                    hotel.get('id', ''),
                    hotel.get('hid', ''),
                    hotel.get('name', ''),
                    hotel.get('address', ''),
                    region.get('country_code', ''),
                    region.get('name', ''),
                    hotel.get('star_rating', 0),
                    hotel.get('latitude', ''),
                    hotel.get('longitude', ''),
                    hotel.get('is_closed', False),
                    hotel.get('phone', ''),
                    hotel.get('email', ''),
                    images_text,
                    len(image_urls),
                    '',  # website - może być w przyszłości
                    hotel.get('hotel_chain', ''),
                    hotel.get('check_in_time', ''),
                    hotel.get('check_out_time', ''),
                    hotel.get('kind', ''),
                    hotel.get('postal_code', ''),
                    facts.get('rooms_number', ''),
                    facts.get('floors_number', ''),
                    facts.get('year_built', ''),
                    facts.get('year_renovated', ''),
                    amenities_text,
                    len(amenities),
                    description_text.replace('\n', ' ').replace('\r', ' ')  # Usuń nowe linie
                ])
        
        print(f"💾 Zapisano w: {output_csv}")
        
        # Pokaż statystyki
        countries = {}
        for hotel in found_hotels:
            country = hotel.get('region', {}).get('country_code', '')
            countries[country] = countries.get(country, 0) + 1
        
        print(f"\n📊 STATYSTYKI:")
        for country, count in sorted(countries.items()):
            print(f"   {country}: {count}")
    
    return found_hotels

# Export hotel IDs for API testing
def export_hotel_ids(hotels, output_file='hotel_ids.json'):
    """
    Eksportuje ID hoteli dla testów API
    """
    # Weź tylko aktywne hotele
    active_hotels = [
        hotel for hotel in hotels 
        if not hotel.get('is_closed', False) and 
           not hotel.get('deleted', False) and 
           hotel.get('id')
    ]
    
    # Weź maksymalnie 50 hoteli
    hotel_ids = [h['id'] for h in active_hotels[:50]]
    
    # Gotowy request dla Postman
    request_body = {
        "ids": hotel_ids,
        "checkin": "2025-07-15",
        "checkout": "2025-07-17",
        "guests": [{"adults": 2, "children": []}],
        "currency": "EUR",
        "language": "en"
    }
    
    with open(output_file, 'w') as f:
        json.dump(request_body, f, indent=2)
    
    print(f"🔗 Wyeksportowano {len(hotel_ids)} ID hoteli do: {output_file}")
    return request_body

# GŁÓWNA FUNKCJA
if __name__ == "__main__":
    
    print("🎯 PROSTY EKSTRAKTOR HOTELI")
    print("="*40)
    
    # Wyciągnij hotele
    hotels = extract_target_hotels('hotels.jsonl', 'target_hotels.csv')
    
    # Eksportuj IDs dla API
    if hotels:
        export_hotel_ids(hotels, 'hotel_ids_for_api.json')
    
    print("\n🎉 Gotowe!")
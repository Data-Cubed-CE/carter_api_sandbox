# Azure Hotel Search Function

Prosta funkcja Azure w Python, która zwraca prosty JSON z danymi hotelu.

## Funkcje

- **HotelSearchFunction**: HTTP trigger, który zwraca podstawowe dane hotelu w formacie JSON
- **Endpoint**: `/api/hotel-search`
- **Metoda**: GET
- **Poziom autoryzacji**: Function (wymagany klucz funkcji)

## Przykład użycia

```
GET /api/hotel-search
```

## Przykładowa odpowiedź

```json
{
  "hotel_name": "Grand Hotel Warsaw",
  "price": 450,
  "currency": "PLN",
  "pax_room": {
    "adults": 2,
    "children": 0
  },
  "meal_plan": "Breakfast included",
  "promotions": "Early bird discount - 15% off",
  "other_information": "Check-in: 15:00, Check-out: 11:00",
  "price_breakdown": {
    "base_price": 400,
    "taxes": 36,
    "city_tax": 14,
    "total": 450
  },
  "extra_charges": "Breakfast: 45 PLN/person, Parking: 80 PLN/night",
  "deposit": "Credit card authorization required",
  "payment_options": "Credit Card, Bank Transfer, PayPal"
}
```

## Lokalne uruchamianie

1. Zainstaluj Azure Functions Core Tools
2. Zainstaluj zależności:
   ```bash
   pip install -r requirements.txt
   ```
3. Uruchom funkcję lokalnie:
   ```bash
   func start
   ```

## Deployment na Azure

1. Utwórz Function App w Azure Portal
2. Deploy używając Azure Functions Core Tools:
   ```bash
   func azure functionapp publish <nazwa-function-app>
   ```

## Struktura danych

Funkcja zwraca prosty JSON z podstawowymi danymi hotelu:

- **Hotel Name**: Nazwa hotelu
- **Price**: Cena za noc w PLN
- **PAX Room**: Liczba gości (dorośli, dzieci)
- **Meal Plan**: Plan wyżywienia
- **Promotions**: Dostępne promocje
- **Other Information**: Dodatkowe informacje o hotelu
- **Price Breakdown**: Podział ceny (bazowa, podatki, podatek miejski)
- **Extra Charges**: Dodatkowe opłaty
- **Deposit**: Wymagania dotyczące kaucji
- **Payment Options**: Dostępne metody płatności

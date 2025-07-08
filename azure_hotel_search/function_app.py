import azure.functions as func
import json
import logging
from datetime import datetime
import random

app = func.FunctionApp()

@app.function_name(name="HotelSearchFunction")
@app.route(route="hotel-search", auth_level=func.AuthLevel.ANONYMOUS)
def hotel_search(req: func.HttpRequest) -> func.HttpResponse:
    """
    Simple Azure Function that returns a mock hotel search result.
    """
    logging.info('Hotel search function processed a request.')
    
    try:
        # Get query parameters (with defaults for Hotel Bristol search)
        hotel_name = req.params.get('hotel', 'Hotel Bristol')
        city = req.params.get('city', 'Warsaw')
        check_in = req.params.get('check_in', '2025-08-01')
        check_out = req.params.get('check_out', '2025-08-03')
        adults = int(req.params.get('adults', 2))
        children = int(req.params.get('children', 0))
        
        # Generate unique request ID
        request_id = f"req_{random.randint(100000, 999999)}"
        
        # Mock hotel data from 3 different booking APIs - Enterprise Format
        response_data = {
            "meta": {
                "request_id": request_id,
                "timestamp": datetime.now().isoformat() + "Z",
                "total_providers": 3,
                "successful_providers": 3,
                "total_results": 9,
                "processing_time_ms": 1245
            },
            "search_criteria": {
                "hotel_name": hotel_name,
                "city": city,
                "check_in": check_in,
                "check_out": check_out,
                "nights": 2,
                "guests": {
                    "adults": adults,
                    "children": children,
                    "total": adults + children
                }
            },
            "results_by_provider": {
                "rate_hawk": {
                    "status": "success",
                    "response_time_ms": 380,
                    "results_count": 3,
                    "data": [
                        {
                            "hotel_name": "Hotel Bristol Warsaw",
                            "room_type": "Premium",
                            "price": 520,
                            "currency": "PLN",
                            "pax_room": {
                                "adults": adults,
                                "children": children
                            },
                            "meal_plan": "Breakfast included",
                            "promotions": "Summer special - 12% off",
                            "other_information": "Check-in: 15:00, Check-out: 11:00, Historic luxury hotel",
                            "price_breakdown": {
                                "base_price": 460,
                                "taxes": 42,
                                "city_tax": 18,
                                "total": 520
                            },
                            "extra_charges": "Breakfast: 55 PLN/person, Parking: 85 PLN/night",
                            "deposit": "Credit card authorization required - 200 PLN",
                            "payment_options": "Credit Card, Bank Transfer, PayPal"
                        }
                    ]
                },
                "merigo": {
                    "status": "success",
                    "response_time_ms": 290,
                    "results_count": 4,
                    "data": [
                        {
                            "hotel_name": "Hotel Bristol Warsaw",
                            "room_type": "Premium",
                            "price": 495,
                            "currency": "PLN",
                            "pax_room": {
                                "adults": adults,
                                "children": children
                            },
                            "meal_plan": "Half Board",
                            "promotions": "Book now, pay later - 0% interest",
                            "other_information": "Check-in: 14:00, Check-out: 12:00, Free WiFi, Concierge service",
                            "price_breakdown": {
                                "base_price": 440,
                                "taxes": 39,
                                "city_tax": 16,
                                "total": 495
                            },
                            "extra_charges": "Minibar: 25 PLN/item, Spa access: 120 PLN/day",
                            "deposit": "Cash or credit card - 150 PLN",
                            "payment_options": "Credit Card, Cash, Bank Transfer, BLIK"
                        }
                    ]
                },
                "tbo": {
                    "status": "success",
                    "response_time_ms": 575,
                    "results_count": 2,
                    "data": [
                        {
                            "hotel_name": "Hotel Bristol Warsaw",
                            "room_type": "Premium",
                            "price": 485,
                            "currency": "PLN",
                            "pax_room": {
                                "adults": adults,
                                "children": children
                            },
                            "meal_plan": "Room only",
                            "promotions": "Flash sale - 18% off, limited time",
                            "other_information": "Check-in: 15:00, Check-out: 11:00, Business center, Fitness center",
                            "price_breakdown": {
                                "base_price": 425,
                                "taxes": 40,
                                "city_tax": 20,
                                "total": 485
                            },
                            "extra_charges": "Breakfast: 48 PLN/person, Late checkout: 75 PLN",
                            "deposit": "No deposit required",
                            "payment_options": "Credit Card, Debit Card, Digital Wallet, Apple Pay"
                        }
                    ]
                }
            },
            "summary": {
                "price_range": {
                    "min": 485,
                    "max": 520,
                    "currency": "PLN",
                    "average": 500
                },
                "providers_status": {
                    "rate_hawk": "success",
                    "merigo": "success", 
                    "tbo": "success"
                }
            }
        }
        
        return func.HttpResponse(
            json.dumps(response_data, indent=2, ensure_ascii=False),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error in hotel search function: {str(e)}")
        error_response = {
            "error": "Internal server error",
            "message": str(e)
        }
        return func.HttpResponse(
            json.dumps(error_response),
            status_code=500,
            mimetype="application/json"
        )



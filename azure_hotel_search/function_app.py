import azure.functions as func
import json
import logging

app = func.FunctionApp()

@app.function_name(name="HotelSearchFunction")
@app.route(route="hotel-search", auth_level=func.AuthLevel.ANONYMOUS)
def hotel_search(req: func.HttpRequest) -> func.HttpResponse:
    """
    Simple Azure Function that returns a mock hotel search result.
    """
    logging.info('Hotel search function processed a request.')
    
    try:
        # Simple mock hotel data
        response_data = {
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



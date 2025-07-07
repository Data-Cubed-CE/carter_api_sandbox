# Endpoint i nagłówki SOAP
URL = "https://carter.xml.goglobal.travel/xmlwebservice.asmx"
API_AGENCY_ID = "164044"
USERNAME = "CARTERXMLTEST"
PASSWORD = "Q2E4969KJ72"  # jeśli puste, zostaw tak

HEADERS = {
    "Content-Type": "text/xml; charset=utf-8",      # SOAP 1.1
    "SOAPAction": "http://www.goglobal.travel/MakeRequest",
    "API-AgencyID": API_AGENCY_ID
}

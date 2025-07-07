import requests
import xml.etree.ElementTree as ET
import json
import pandas as pd
from tabulate import tabulate
import config

def search_hotels_by_city(
    city_id: str,
    arrival_date: str,
    departure_date: str,
    adults: int = 2,
    children: int = 0,
    child_ages: list = None,
    currency: str = "EUR",
    nationality: str = "PL",
) -> pd.DataFrame:
    """
    Wysyła zapytanie HOTEL_SEARCH_REQUEST (requestType=11) z DestinationSearch,
    zwraca listę hoteli w mieście jako DataFrame.
    """
    if child_ages is None:
        child_ages = []

    # Obliczenie liczby nocy
    d1 = pd.to_datetime(arrival_date).date()
    d2 = pd.to_datetime(departure_date).date()
    nights = (d2 - d1).days
    if nights <= 0:
        raise ValueError("Data wyjazdu musi być po dacie przyjazdu.")

    # Sekcja Rooms
    ages_xml = "".join(f'<Child Age="{age}" />' for age in child_ages)
    children_section = f'<ChildAges>{ages_xml}</ChildAges>' if child_ages else ""
    rooms_xml = f'<Room Adults="{adults}" RoomCount="1" ChildCount="{children}"/>'

    # SOAP Envelope z DestinationSearch
    envelope = f"""<?xml version=\"1.0\" encoding=\"utf-8\"?>
<soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"
               xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\"
               xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">
  <soap:Body>
    <MakeRequest xmlns=\"http://www.goglobal.travel/\">
      <requestType>11</requestType>
      <xmlRequest><![CDATA[
        <Root>
          <Header>
            <Agency>{config.API_AGENCY_ID}</Agency>
            <User>{config.USERNAME}</User>
            <Password>{config.PASSWORD}</Password>
            <Operation>HOTEL_SEARCH_REQUEST</Operation>
            <OperationType>Request</OperationType>
          </Header>
          <Main Version=\"2.3\" ResponseFormat=\"JSON\" IncludeGeo=\"true\" Currency=\"{currency}\">
            <MaximumWaitTime>15</MaximumWaitTime>
            <Nationality>{nationality}</Nationality>
            <DestinationSearch>
              <CityId>{city_id}</CityId>
            </DestinationSearch>
            <ArrivalDate>{arrival_date}</ArrivalDate>
            <Nights>{nights}</Nights>
            <Rooms>
              {rooms_xml}
              {children_section}
            </Rooms>
          </Main>
        </Root>
      ]]></xmlRequest>
    </MakeRequest>
  </soap:Body>
</soap:Envelope>"""

    resp = requests.post(config.URL, headers=config.HEADERS, data=envelope.encode("utf-8"), timeout=30)
    resp.raise_for_status()

    # Parsowanie SOAP i JSON
    ns = {"soap": "http://schemas.xmlsoap.org/soap/envelope/", "gg": "http://www.goglobal.travel/"}
    root = ET.fromstring(resp.text)
    result_el = root.find(".//gg:MakeRequestResult", ns)
    raw = result_el.text.strip() if result_el is not None and result_el.text else ""
    data = json.loads(raw)

    # Normalizacja listy hoteli
    hotels = data.get("Hotels", [])
    df = pd.json_normalize(hotels)
    return df

if __name__ == "__main__":
    # Przykład wyszukiwania po Amsterdam (CityId=75)
    city_id = "75"
    arrival = "2025-07-10"
    departure = "2025-07-12"
    df_hotels = search_hotels_by_city(city_id, arrival, departure)
    if df_hotels.empty:
        print(f"Brak hoteli w city_id={city_id}")
    else:
        print(f"Brak hoteli w city_id={city_id}")
    else:
        # Wyświetl wszystkie dostępne kolumny dla szerokiego widoku
        display_cols = df_hotels.columns.tolist()
        available = [c for c in cols if c in df_hotels.columns]
        print(tabulate(df_hotels[available], headers=available, tablefmt="psql", showindex=False))

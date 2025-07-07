import time
import requests
import xml.etree.ElementTree as ET
import json
import pandas as pd
from tabulate import tabulate
import textwrap
import config

# Symulacja iteracyjna dla różnych parametrów zapytania po HotelId
TEST_CASES = [
    {"hotel_id": "318188", "arrival": "2025-07-10", "departure": "2025-07-12", "adults": 2, "children": 1, "child_ages": [5]},
    {"hotel_id": "318188", "arrival": "2025-09-15", "departure": "2025-09-18", "adults": 3, "children": 0, "child_ages": []},
    {"hotel_id": "318188", "arrival": "2025-07-25", "departure": "2025-07-28", "adults": 2, "children": 2, "child_ages": [4,7]},
    {"hotel_id": "999999", "arrival": "2025-08-01", "departure": "2025-08-05", "adults": 2, "children": 0, "child_ages": []},
]


def search_hotels_by_id(
    hotel_id: str,
    arrival_date: str,
    departure_date: str,
    adults: int = 2,
    children: int = 0,
    child_ages: list = None,
    currency: str = "EUR",
    nationality: str = "PL",
) -> pd.DataFrame:
    if child_ages is None:
        child_ages = []

    # Oblicz liczbę nocy
    d1 = pd.to_datetime(arrival_date).date()
    d2 = pd.to_datetime(departure_date).date()
    nights = (d2 - d1).days
    if nights <= 0:
        raise ValueError("Data wyjazdu musi być po dacie przyjazdu.")

    # Budowa Rooms XML
    ages_xml = "".join(f'<Child Age=\"{age}\" />' for age in child_ages)
    children_section = f'<ChildAges>{ages_xml}</ChildAges>' if child_ages else ""
    rooms_xml = f'<Room Adults=\"{adults}\" RoomCount=\"1\" ChildCount=\"{children}\"/>'

    # SOAP Envelope
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
          <Main Version=\"2.4\" ResponseFormat=\"JSON\" IncludeGeo=\"true\" Currency=\"{currency}\">
            <MaxHotels>100</MaxHotels>
            <MaxOffers>50</MaxOffers>
            <MaximumWaitTime>15</MaximumWaitTime>
            <Nationality>{nationality}</Nationality>
            <Hotels>
              <HotelId>{hotel_id}</HotelId>
            </Hotels>
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

    # Parsowanie SOAP
    ns = {"soap": "http://schemas.xmlsoap.org/soap/envelope/", "gg": "http://www.goglobal.travel/"}
    root = ET.fromstring(resp.text)
    result_el = root.find(".//gg:MakeRequestResult", ns)
    raw = result_el.text.strip() if result_el is not None else ""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print(f"Błąd parsowania JSON dla hotel_id={hotel_id}:")
        print(raw)
        return pd.DataFrame()

    # Znormalizuj oferty
    offers = data.get("Hotels", [])[0].get("Offers", []) if data.get("Hotels") else []
    return pd.json_normalize(offers)


def display_offers(df: pd.DataFrame):
    if df.empty:
        print("Brak ofert.")
        return

    # Wybierz kolumny w logicznej kolejności
    key_cols = [
        "HotelSearchCode", "TotalPrice", "Currency", "Availability", "RoomBasis",
        "CxlDeadLine", "NonRef", "Preferred", "Special"
    ]
    other_cols = [c for c in df.columns if c not in key_cols]
    ordered_cols = key_cols + other_cols

    # Przygotuj DataFrame do wyświetlenia
    df2 = df.reindex(columns=ordered_cols)

    # Skróć długie Remark
    if "Remark" in df2.columns:
        df2["Remark"] = df2["Remark"].fillna("").apply(lambda x: textwrap.shorten(x, width=60, placeholder="..."))

    # Wyświetl z tabulate
    print(tabulate(df2.where(pd.notnull(df2), "NULL"), headers=df2.columns.tolist(), tablefmt="psql", showindex=False))


if __name__ == "__main__":
    for case in TEST_CASES:
        header = f"Test: hotel={case['hotel_id']} | {case['arrival']}→{case['departure']} | adults={case['adults']} kids={case['children']}"
        print(f"\n{'='*len(header)}")
        print(header)
        print(f"{'='*len(header)}")
        df = search_hotels_by_id(
            hotel_id=case['hotel_id'],
            arrival_date=case['arrival'],
            departure_date=case['departure'],
            adults=case['adults'],
            children=case['children'],
            child_ages=case['child_ages'],
        )
        display_offers(df)
        time.sleep(6)  # throttle per sandbox limits

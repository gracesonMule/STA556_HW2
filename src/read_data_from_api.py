import pandas as pd
import numpy as np
import requests
import os
from datetime import date, timedelta, datetime

COLUMN_DTYPES = {
    "Approach Date": "datetime64[us]",
    "miss_distance": "float64",
    "relative_velocity": "float64",
    "object_id": "str",
    "absolute_magnitude_h": "float64",
    "estimated_diameter": "float64",
    "is_potentially_hazardous_asteroid": "bool",
}

def request_data(start_date: str, end_date: str, api_key:str = "DEMO_KEY", url: str = "https://api.nasa.gov/neo/rest/v1/feed") -> dict:
    """Function to request data from NASA's Asteroids - NeoWs API. API only allows requests for seven days at a time.
    
    Params:
        start_date (str): Beginning date of requested data (YYYY-MM-DD)
        end_date (str): End date for requested data (YYYY-MM-DD). Maximum of seven days after start_date
        api_key (str): user's api key. Defaults to DEMO_KEY.
        url (str): url for NASA API. Defaults to NASA's Asteroids - NeoWs API.

    Return:
        Python dictionary containing API data.

    Raises:
        AssertionError: If end_date is more than seven days from start_date.
    
    """

    SESSION = requests.Session()

    # assert (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days <= 7, \
    # "end_date must be at most seven days after start_date"

    response = requests.get(url, timeout=10,
                            params={"api_key": api_key,
                                    "start_date": start_date,
                                    "end_date": end_date})
        
    return response.json()

def neo_to_rows(neo: dict) -> list[dict]:
    """Flatten a single near-earth object into one row per close approach.
 
    The object-level fields (id, magnitude, diameter, hazard flag) are repeated on
    each of that object's approach rows, which is what keeps the object and its
    approaches correctly paired without a join.
 
    Params:
        neo (dict): A single near-earth object as returned by the API.
 
    Returns:
        List of row dicts, one per entry in the object's close_approach_data.
    """
 
    object_fields = {
        "object_id": neo["id"],
        "absolute_magnitude_h": neo["absolute_magnitude_h"],
        "estimated_diameter": neo["estimated_diameter"]["kilometers"]["estimated_diameter_min"],
        "is_potentially_hazardous_asteroid": neo["is_potentially_hazardous_asteroid"],
    }
 
    return [
        {
            "Approach Date": approach["close_approach_date"],
            "miss_distance": float(approach["miss_distance"]["kilometers"]),
            "relative_velocity": float(approach["relative_velocity"]["kilometers_per_hour"]),
            **object_fields,
        }
        for approach in neo["close_approach_data"]
    ]


def api_data_to_dataframe(api_data: dict) -> pd.DataFrame:
    """Function for extracting relevant NEO data from api data and converting it to a Pandas DataFrame.
 
    Params:
        api_data (dict): Python dictionary containing api data.
 
    Returns:
        pd.DataFrame containing relevant information from api, one row per close approach.
 
    Helpers:
        neo_to_rows(neo: dict): Flattens one object into its approach rows.
    """
 
    neos_by_date = api_data["near_earth_objects"]
 
    rows = [
        row
        for neos in neos_by_date.values()
        for neo in neos
        for row in neo_to_rows(neo)
    ]
 
    neos_df = pd.DataFrame(rows, columns=list(COLUMN_DTYPES))
 
    neos_df["Approach Date"] = pd.to_datetime(neos_df["Approach Date"], format="%Y-%m-%d")
    neos_df = neos_df.astype(COLUMN_DTYPES)
 
    # The feed groups objects by date, so an object with two approaches in the
    # window can be listed twice; keep one row per object per approach.
    neos_df = neos_df.drop_duplicates(subset=["object_id", "Approach Date"])
 
    return neos_df.sort_values(by=["object_id", "Approach Date"]).reset_index(drop=True)
def main() -> None:
    data = request_data(start_date= "2026-10-21", end_date="2026-10-28")

    neos_df = api_data_to_dataframe(api_data=data)

    csv_fpath = os.path.join("..", "data", "raw", "neo_data.csv")
    os.makedirs(os.path.dirname(csv_fpath), exist_ok=True)
    neos_df.to_csv(csv_fpath, index=False)

if __name__ == "__main__":
    main()
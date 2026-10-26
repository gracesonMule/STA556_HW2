import pandas as pd
import numpy as np
import requests
import os
from datetime import date, timedelta, datetime

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

def get_close_approach_data(neos: dict, approach_dates: list) -> pd.DataFrame:
    """Helper function for get_object_data to extract approach data.
    
    Params:
        neos (dict): Dictionary containing all NEO data.
        approach_dates (list): Dates for all observations.

    Returns:
        pd.DataFrame containing approach data.
    """

    close_approach_data = {
        "Approach Date": [neos[ad][i]['close_approach_data'][j]['close_approach_date']
                for ad in approach_dates for i in range(len(neos[ad])) 
                for j in range(len(neos[ad][i]['close_approach_data']))],
        
        "miss_distance": [float(neos[ad][i]['close_approach_data'][j]['miss_distance']['kilometers']) 
                for ad in approach_dates for i in range(len(neos[ad])) 
                for j in range(len(neos[ad][i]['close_approach_data']))],

        "relative_velocity": [float(neos[ad][i]['close_approach_data'][j]['relative_velocity']['kilometers_per_hour']) 
                for ad in approach_dates for i in range(len(neos[ad])) 
                for j in range(len(neos[ad][i]['close_approach_data']))],
    }

    return pd.DataFrame(data=close_approach_data)

def get_object_data(neos: dict, approach_dates: list) -> pd.DataFrame:
    """Helper function for get_object_data to extract individual object data.
    
    Params:
        neos (dict): Dictionary containing all NEO data.
        approach_dates (list): Dates for all observations.

    Returns:
        pd.DataFrame containing individual object data.
    """

    object_data = {
        "Approach Date": [ad for ad in neos for _ in range(len(neos[ad]))],

        "object_id": [neos[ad][i]['id'] for ad in approach_dates for i in range(len(neos[ad]))],

        "absolute_magnitude_h": [neos[ad][i]['absolute_magnitude_h'] for ad in approach_dates for i in range(len(neos[ad]))],
        
        "estimated_diameter": [neos[ad][i]['estimated_diameter']['kilometers']['estimated_diameter_min'] 
                            for ad in approach_dates
                                for i in range(len(neos[ad]))],

        "is_potentially_hazardous_asteroid": [neos[ad][i]['is_potentially_hazardous_asteroid']
                                            for ad in approach_dates
                                                for i in range(len(neos[ad]))],
    }

    return pd.DataFrame(data=object_data)



def api_data_to_dataframe(api_data: dict) -> pd.DataFrame:
    """Funciton for extracting relevant NEO data from api data and converting it to a Pandas Dataframe.

    Params:
        api_data(dict): Python dictionary containing api data.

    Returns:
        pd.Dataframe containing relevant information from api.

    Helpers:
        get_close_approach_data(neos: dict, approach_dates: list): Function to extract approach data.
    """

    neos = api_data['near_earth_objects']

    approach_dates = [app_date for app_date in neos]

    close_approach_df = get_close_approach_data(neos=neos, approach_dates=approach_dates)

    object_data_df = get_object_data(neos=neos, approach_dates=approach_dates)

    neos_df = close_approach_df.merge(object_data_df, on="Approach Date", how="left", validate="many_to_many")
    neos_df['Approach Date'] = pd.to_datetime(neos_df['Approach Date'])
    neos_df = neos_df.sort_values(by='object_id')

    return neos_df

def main() -> None:
    data = request_data(start_date= "2026-10-21", end_date="2026-10-28")

    neos_df = api_data_to_dataframe(api_data=data)

    csv_fpath = os.path.join("..", "data", "raw", "neo_data.csv")
    neos_df.dropna()
    neos_df.to_csv(csv_fpath, index=False)

if __name__ == "__main__":
    main()
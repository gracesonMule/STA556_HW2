import pandas as pd
from datetime import datetime


def group_neos_by_hazardous_flag(df: pd.DataFrame, hazardous_flag: bool) -> pd.DataFrame:
    """Group neos as hazardous or not hazardous asteriods.

    Args:
        df (pd.DataFrame): Pandas DataFrame to be filtered.
        hazardous_flag (bool): Flag to indicate hazardous or not hazardous. True for hazardous, False not hazardous.

    Returns:
        pd.DataFrame: Pandas DataFrame containing only potentially hazardous asteriods or not hazardous asteriods based on flag.
    """

    return df.loc[df['is_potentially_hazardous_asteroid'] == hazardous_flag]

def filter_by_date(df: pd.DataFrame, start_date: str, end_date: str, data_column: str ="Approach Date") -> pd.DataFrame:
    """Filter NEO DataFrame by start and end dates.

    Args:
        df (pd.DataFrame): Pandas DataFrame to be filtered.
        start_date (str): Beginning of date filter (YYYY-MM-DD)
        end_date (str): End of date filter (YYYY-MM-DD)

    Returns:
        pd.DataFrame: Pandas DataFrame containing observations between start and end date.
    """
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    return df[df[data_column].between(start_date, end_date)]


def get_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Function to derive summary statistics for meausrements from a NEO Dataframe.

    Args:
        df (pd.DataFrame): Pandas DataFrame to be summarize.

    Return:
        pd.DataFrame: Pandas Dataframes containing sumamry dataframe for NEOs.
    """
    
    measurements = ['miss_distance', 'relative_velocity', 'absolute_magnitude_h', 'estimated_diameter']
    # summary = df[measurements].describe().T
    # summary = df.groupby('object_id')[measurements].describe()
    per_object = df.groupby('object_id').agg(
        n_approaches = ('miss_distance', 'size'),
        miss_min     = ('miss_distance', 'min'),
        miss_median  = ('miss_distance', 'median'),
        miss_max     = ('miss_distance', 'max'),
        vel_min      = ('relative_velocity', 'min'),
        vel_median   = ('relative_velocity', 'median'),
        vel_max      = ('relative_velocity', 'max'),
        absolute_magnitude_h   = ('absolute_magnitude_h', 'first'),
        estimated_diameter     = ('estimated_diameter', 'first'),
        hazardous    = ('is_potentially_hazardous_asteroid', 'first'),
    ).round(2)
    return per_object

def summarize_potentialy_hazardous_neos(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Summarize NEO data by group: hazardous and nonhazardous. The function only summarizes the numerical data.

    Args:
        df (pd.DataFrame): Pandas DataFrame to be summarize.

    Helper Functions:
        get_summary(df: pd.DataFrame): Function to generate summary statistics.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: Tuple of Pandas Dataframes containing sumamry dataframe for hazardous and non-hazardous NEOs.
    """
    hazardous_neos = group_neos_by_hazardous_flag(df=df, hazardous_flag=True)
    hazardous_neos_summary = get_summary(df=hazardous_neos)

    nonhazardous_neos = group_neos_by_hazardous_flag(df=df, hazardous_flag=False)
    nonhazardous_neos_summary = get_summary(df=nonhazardous_neos)

    return hazardous_neos_summary, nonhazardous_neos_summary


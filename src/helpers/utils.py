import pandas as pd

def format_title(title: str):
    """Formats snake_case title into Proper Title."""
    formatted = title.replace("_", " ").title()
    return formatted

def format_list_of_films(films: list):
    return [ format_title(f) for f in films ]

def format_data(df: pd.DataFrame) -> pd.DataFrame:
    # no-op for now, format columns appropriately later
    return df

def read_data(datapath: str) -> pd.DataFrame:
    tmp_df = pd.read_csv(datapath)
    formatted_df = format_data(tmp_df)
    return formatted_df

import pandas as pd

def formatTitle(title: str):
    """Formats snake_case title into Proper Title."""
    formatted = title.replace("_", " ").title()
    return formatted

def unformatTitle(title: str):
    """Converts Proper Title to snake_case."""
    unformatted = title.replace(" ", "_").lower()
    return unformatted

def formatListOfFilms(films: list):
    return [ formatTitle(f) for f in films ]

def formatData(df: pd.DataFrame) -> pd.DataFrame:
    # no-op for now, format columns appropriately later
    return df

def readData(datapath: str) -> pd.DataFrame:
    tmp_df = pd.read_csv(datapath)
    formatted_df = formatData(tmp_df)
    return formatted_df

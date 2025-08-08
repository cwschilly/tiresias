"""
Core manager class to handle all training/testing data.
Pass this around instead of maintaining various dataframes.
"""

import os
import pandas as pd

from src.helpers.ratings import getUserRatings

class DataManager:
    """
    DataManager class. Instantiate with the directory containing
    all data files.

    If the output_dir is given, plots and other output will be
    written there. If not, output will be placed in the
    data directory.

    Test ratio is used to split the full dataset into train
    and testing data. It defaults to 0.25, meaning that
    the one quarter of the original dataset will be set
    aside for testing.
    """

    def __init__(self, data_dir: str, output_dir: str = None, test_ratio = 0.25):
        self.data_dir = data_dir
        self.output_dir = output_dir if output_dir is not None else data_dir

        self.df = pd.DataFrame()
        self.odyssey_df = pd.DataFrame()

        self.test_ratio = test_ratio
        self.is_personalized = False

    def __formatColumns(self, df):
        # no op for now
        return df

    def __personalizedModelInput(self):
        lb_input = input(
            "Would you like to make your own model, "
            "tailored to your preferences? (y, [n]): "
        ).lower().strip()
        while lb_input not in ["", "y", "yes", "n", "no"]:
            lb_input = input("  Sorry, I didn't catch that. Please enter y or n: ")
        is_personalized = lb_input in ["y", "yes"]
        if not is_personalized:
            print("No worries, you can use mine :)")
            print()
        return is_personalized

    def __updateDataFrames(self) -> None:
        # Step 1: Separate the Odyssey from the full dataframe
        last_row = self.df.iloc[-1]
        if last_row["title"] == "the_odyssey":
            self.odyssey_df = last_row.copy()
            self.df = self.df[:-1]

        assert "the_odyssey" not in self.df["title"], \
               "Error: The Odyssey is still in the training data."

        # Step 2: Randomly select the test/training data
        # total_size = len(self.df)
        # test_size = int(total_size * self.test_ratio)
        # shuffled_df = self.df.sample(frac=1, random_state=42).reset_index(drop=True)
        # self.test_df = shuffled_df[:test_size]
        # self.train_df = shuffled_df[test_size:]
        # assert len(self.test_df) == test_size, (
        #        "Error: Test dataset is not the correct size. "
        #        f"({len(self.test_df)} != {test_size})"
        # )

    def setData(self, data_file: str) -> None:
        """
        Initialize the data manager with the default training data.
        Will update the user_ratings column if custom training is enabled.
        """
        data_path = os.path.join(self.data_dir, data_file)
        while not os.path.isfile(data_path):
            data_path = print(f"ERROR: {data_path} not found.")
            data_path = input("Enter correct path: ")
        df = pd.read_csv(data_path)
        df = self.__formatColumns(df)

        self.is_personalized = self.__personalizedModelInput()
        if self.is_personalized:
            user_ratings = getUserRatings()
            df["user_ratings"] = df["title"].map(user_ratings)

        self.df = df.copy()
        self.__updateDataFrames()

    def getOdysseyData(self):
        """Returns the evaluation dataset."""
        return self.odyssey_df

    def getFullDataset(self) -> pd.DataFrame:
        """Returns the full train+test dataset"""
        return self.df

    def getDoCustomModel(self) -> bool:
        """Returns whether or not a custom dataset was used."""
        return self.is_personalized

import os
import pandas as pd

from src.helpers.ratings import getUserRatings

class DataManager:

    def __init__(self, data_dir: str, output_dir: str = None, test_ratio = 0.25):
        self.data_dir = data_dir
        self.output_dir = output_dir if output_dir is not None else data_dir

        self.df = pd.DataFrame()
        self.train_df = pd.DataFrame()
        self.test_df = pd.DataFrame()

        self.odyssey_df = pd.DataFrame()

        self.test_ratio = test_ratio

        self.do_custom_model = False

    def __formatColumns(self, df):
        # no op for now
        return df

    def __personalizedModelInput(self):
        lb_input = input("Would you like to make your own model, using your Letterboxd account and/or manually-entered ratings? (y, [n]): ").lower().strip()
        while lb_input not in ["", "y", "yes", "n", "no"]:
            lb_input = input(f"  Sorry, I didn't catch that. Please enter y or n: ")
        do_custom_model = lb_input == "y" or lb_input == "yes"
        if not do_custom_model:
            print("No worries, you can use mine :)")
            print()
        return do_custom_model

    def __updateDataFrames(self) -> None:
        total_size = len(self.df)
        test_size = int(total_size * self.test_ratio)

        # Step 1: Separate the Odyssey from the full dataframe
        last_row = self.df.iloc[-1]
        if last_row["title"] == "the_odyssey":
            self.odyssey_df = last_row.copy()
            self.df = self.df[:-1]
        assert "the_odyssey" not in self.df["title"], f"Error: The Odyssey is still in the training data."

        # Step 2: Randomly select the test/training data
        shuffled_df = self.df.sample(frac=1, random_state=42).reset_index(drop=True)
        self.test_df = shuffled_df[:test_size]
        self.train_df = shuffled_df[test_size:]
        assert len(self.test_df) == test_size, f"Error: Test dataset is not the correct size. {len(self.test_df)} != {test_size}"

    def setData(self, data_file: str) -> None:
        data_path = os.path.join(self.data_dir, data_file)
        while not os.path.isfile(data_path):
            data_path = print(f"ERROR: {data_path} not found.")
            data_path = input("Enter correct path: ")
        df = pd.read_csv(data_path)
        df = self.__formatColumns(df)

        self.do_custom_model = self.__personalizedModelInput()
        if self.do_custom_model:
            user_ratings = getUserRatings()
            df["user_ratings"] = df["title"].map(user_ratings)

        self.df = df.copy()
        self.__updateDataFrames()

    def getOdysseyData(self, params: dict):
        # TODO: Add params into self.odyssey_df
        return self.odyssey_df

    def getFullDataset(self) -> pd.DataFrame:
        return self.df

    def getDoCustomModel(self) -> bool:
        return self.do_custom_model

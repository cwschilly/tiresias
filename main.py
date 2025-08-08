from src.helpers.manager import DataManager
from src.constants.wordmark import WORDMARK
from src.constants.directories import DATA_DIR, RESULTS_DIR

DATA_FILE = "2025-08-07-dataset.csv"


def main():

    # Welcome to Tiresias!
    WORDMARK()

    # Let's add some data to our DataManager (dm)
    dm = DataManager(DATA_DIR, RESULTS_DIR)
    dm.setData(DATA_FILE)

    # Now we can train the model on the data
    handler = ModelHandler(dm)
    handler.runTuningLoop() # no-op if not using custom model

    # Tiresias is ready. Will we like The Odyssey?
    handler.evaluateModel()

if __name__ == "__main__":
    main()

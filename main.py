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
    # TODO: dm contains whether or not we should train a new
    # custom model, or just use the existing one
    model = runTuningLoop(dm)

    # Now we fill in some hypotheticals...
    print("""
There are a couple unknowns with The Odyssey that might affect our model.
    - Runtime
    - MPAA Rating (PG-13 or R)
""")
    params = {
        "runtime": (90, 200),
        "mpaa": 2
    }
    specify_params = input("Do you want to set your own bounds for these values? (y, [n]): ")
    specify_params = specify_params.lower() == "y"
    if specify_params:
        print("Great! We'll start with the runtime. In minutes, what are the lower and upper bounds you'd like to test? (For example, runtimes between 90 and 200 minutes).")
        runtime_input_active = True
        while runtime_input_active:
            runtime_lb = input("  Runtime lower bound (in minutes) (default: 90):  ")
            runtime_lb = int(runtime_lb) if runtime_lb is not None else 90
            runtime_ub = input("  Runtime upper bound (in minutes) (default: 200): ")
            runtime_ub = int(runtime_ub) if runtime_ub is not None else 200
            if runtime_ub < runtime_lb:
                print(f"    Looks like your upper bound ({runtime_ub}) is actually less than the lower bound ({runtime_lb}). We'll just switch them around for the testing.")
                tmp = runtime_lb
                runtime_lb = runtime_ub
                runtime_ub = tmp
            elif runtime_ub == runtime_lb:
                print(f"    You chose the same value for both the upper and lower bounds ({runtime_ub}), so we'll just run one test with that value.")
            done = input(f"You chose runtime bounds of {runtime_lb} - {runtime_ub} min. Ready to move on? ([y], n)")
            runtime_input_active = done.lower() != "n"

        print()
        print("On to the MPAA rating. The Odyssey will likely be rated either PG-13 or R. Do you want to test with one of these ratings, or with both?")
        mpaa_input_active = True
        while mpaa_input_active:
            mpaa = input("  Test with PG-13 [0], R [1], or both [2]? (Enter the corresponding integer) ")
            try:
                mpaa = int(mpaa)
            except:
                print(f"    Your input ({mpaa}) wasn't parsed correctly. Please enter 0, 1, or 2.")
                continue
            if mpaa not in [0, 1, 2]:
                print(f"    Your input ({mpaa}) must be either 0, 1, or 2.")
                continue
            mpaa_input_active = False
    else:
        print("Great, we'll stick with the defaults.")

    odyssey_data = dm.getOdysseyData(params)

    # Tiresias is ready. Will we like The Odyssey?
    outputs = model(dm.odyssey_data)
    analyzeOutputs(outputs)

if __name__ == "__main__":
    main()

"""Tiresias — three goals, in order:

Goal 1: Validate that the Nolan Index (fabula vs. syuzhet craziness) predicts taste.
Goal 2: Predict The Odyssey's Oscar haul from its position on the index.
Goal 3: Fit each respondent's own ratings against the aggregated index metric,
        and predict their personal rating for The Odyssey.
"""
import argparse

from oscars import predict as oscars
from personalization.predict import fit_user
from plotting.nolan_scatter import plot_nolan_index
from plotting.oscars_metric import plot_oscars_vs_metric
from plotting.user_curve import plot_user_curve
from preprocessing.preprocess import clean, read_responses
from preprocessing.users import get_user_ratings
from site_export import write_pipeline
from validation.validate import print_report, validate_index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true",
                        help="refresh responses from Google Sheets (maintainers only)")
    parser.add_argument("--user", type=int, default=None,
                        help="plot only this respondent's curve by row number, "
                             "instead of every respondent")
    args = parser.parse_args()

    ## Load the data
    raw = read_responses(refresh=args.fetch)
    ratings = clean(raw)
    print(f"Users after filtering: {len(ratings)} of {len(raw)} submitted rows")

    ## Goal 1: is the Nolan Index a suitable predictor?
    report = validate_index(ratings)
    print_report(report)
    plot_nolan_index()

    ## Goal 2: predict Oscars from index position alone
    oscar_report = oscars.validate_oscars()
    oscar_coeffs = oscars.fit_oscar_models()
    oscars.print_report(oscar_report, oscar_coeffs)
    plot_oscars_vs_metric(oscar_coeffs)

    ## Goal 3: fit each respondent's own curve and predict their Odyssey rating
    rows = [args.user] if args.user is not None else range(len(raw))
    for row in rows:
        try:
            user_ratings = get_user_ratings(ratings, row).to_dict()
        except ValueError as err:
            print(f"Row {row}: {err}")
            continue
        prediction = fit_user(user_ratings)
        path = plot_user_curve(row, user_ratings)
        print(f"Row {row}: {prediction.fit.degree}-degree fit, α={prediction.alpha:.1f}, "
              f"R²={prediction.fit.r2_in_sample:.2f} (LOO R²={prediction.fit.r2_loo:.2f}) -> {path}")

    ## Export everything the website needs
    write_pipeline(oscar_coeffs)


if __name__ == "__main__":
    main()

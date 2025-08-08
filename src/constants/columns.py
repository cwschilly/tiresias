FEATURE_COLUMNS = [
    "budget",               # float (millions USD)
    "runtime",              # float (minutes)
    "original_ip",          # bool (0 = IP, 1 = original)
    "release_month",        # int (1-12)
    "star_power",           # float
    "theater_window",       # int
    "film_rating",          # bool (PG-13: 0, R: 1)
    "nolan_index",          # unitless
    "imax_ratio",           # pct
    "avg_annual_box_office" # float (billions USD)
]

TARGET_COLUMNS = [
    "user_rating",          # float
    "letterbox_avg_rating", # float
    "total_box_office_usd", # float (millions USD)
    "oscar_noms"            # int
]

INFO_COLUMNS = [
    "title",
    "composer",
    "year"
]

ALL_COLUMNS = list(FEATURE_COLUMNS + TARGET_COLUMNS + INFO_COLUMNS)

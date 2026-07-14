from scraping.nolan_match import match_nolan_title


def test_matches_exact_title_review():
    headline = "Oppenheimer review – Christopher Nolan's mighty visual achievement"
    assert match_nolan_title(headline) == "Oppenheimer"


def test_disambiguates_dark_knight_from_dark_knight_rises():
    assert match_nolan_title("The Dark Knight Rises review – Batman's last stand") == "The Dark Knight Rises"
    assert match_nolan_title("The Dark Knight review – Heath Ledger is chilling") == "The Dark Knight"


def test_ignores_unrelated_review_sharing_a_word_with_a_title():
    assert match_nolan_title("Following the Money review – a middling documentary") is None


def test_ignores_non_review_mentions():
    assert match_nolan_title("Ten things you didn't know about Tenet") is None

####################################################################
#                                                                  #
#                   Copyright 2025 Caleb Schilly                   #
# See the LICENSE file at the top-level directory of this project. #
#                                                                  #
####################################################################

"""
This file contains various utility functions used
throughout the app.
"""

def formatTitle(title: str):
    """Formats snake_case title into Proper Title."""
    formatted = title.replace("_", " ").title()
    return formatted

def unformatTitle(title: str):
    """Converts Proper Title to snake_case."""
    unformatted = title.replace(" ", "_").lower()
    return unformatted

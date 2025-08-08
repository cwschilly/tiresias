"""
Define location of all key directories, with respect to this file.
"""
import os

CONSTANTS_DIR = os.path.dirname(os.path.realpath(__file__))
SRC_DIR = os.path.dirname(CONSTANTS_DIR)
PROJECT_DIR = os.path.dirname(SRC_DIR)

DATA_DIR = os.path.join(PROJECT_DIR, "data")
RESULTS_DIR = os.path.join(PROJECT_DIR, "results")

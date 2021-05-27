import os
import pandas as pd
from sqlalchemy import create_engine


class DataQueryHelper:
    def __init__(self, file_name=None):

        self.RAW_DATA = pd.read_csv(file_name, low_memory=False)
        self.DATA = self.RAW_DATA
        self.filteredSatData = False
        self.filteredVesData = False

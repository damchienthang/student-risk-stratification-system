import os
import pandas as pd
from typing import Optional

class DataManager:
    _instance = None
    _df: Optional[pd.DataFrame] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
        return cls._instance

    def load_data(self, data_path: str):
        """Load CSV data into memory if not already loaded"""
        if self._df is None:
            if not os.path.exists(data_path):
                print(f"[ERROR] Data file not found at: {data_path}")
                return False
            
            print(f"[DATA] Loading data from {data_path} into memory...")
            self._df = pd.read_csv(data_path)
            print(f"[DATA] Successfully loaded {len(self._df)} rows.")
            return True
        return True

    def get_df(self) -> Optional[pd.DataFrame]:
        return self._df

    def is_loaded(self) -> bool:
        return self._df is not None

# Singleton helper
_data_manager = DataManager()

def get_data_manager():
    return _data_manager

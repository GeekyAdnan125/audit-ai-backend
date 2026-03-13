
import pandas as pd

class FileLoader:

    def load_excel(self, file):
        return pd.read_excel(file)

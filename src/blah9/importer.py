import copy
from pathlib import Path
import pandas as pd


class Importer:
    def __init__(self, descs_n_paths: list[tuple[str, Path]]) -> None:
        self.__dfs: list[tuple[str, pd.DataFrame]] = []
        # Read data into dataframes
        for desc, file_path in descs_n_paths:
            if file_path.suffix == ".csv":
                self.__dfs.append((desc, pd.read_csv(file_path)))
                continue
            if file_path.suffix == ".xml":
                self.__dfs.append((desc, pd.read_xml(file_path)))
                continue
            else:
                raise ValueError("Format not supported")

    def read(
        self,
    ) -> list[tuple[str, pd.DataFrame]]:
        return copy.deepcopy(self.__dfs)

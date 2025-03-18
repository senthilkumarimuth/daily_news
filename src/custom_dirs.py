from dataclasses import dataclass
from typing import List
from pathlib import Path
import os


@dataclass
class RootDirectory:
    path: str

@dataclass
class DataDirectory:
    path: str
    files: List[str]

@dataclass
class ModelDirectory:
    path: str
    models: List[str]


@dataclass
class ReportDirectory:
    path: str
    models: List[str]

current_file_path = Path(__file__)
root_directory = current_file_path.parents[1]

RootDirectory.path = str(root_directory)
DataDirectory.path = str(root_directory) + os.sep + 'data' + os.sep



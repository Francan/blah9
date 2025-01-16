from pathlib import Path
import pandas as pd
from src.blah9.kg_generator import KgGenerator
from src.blah9.importer import Importer

if __name__ == "__main__":
    data_root: Path = Path(__file__).absolute().parent.parent.parent / "data"
    drugbank_dataset_path = data_root / "uci.csv"
    project_tycho_path = data_root / "project_tycho.csv"
    drugbank_explanation_path = data_root / "uci.txt"
    project_tycho_explanation_path = data_root / "project_tycho.txt"
    drugbank_explanation: str = ""
    project_tycho_explanation: str = ""

    with open(drugbank_explanation_path, "r") as f:
        drugbank_explanation = "\n".join(f.readlines())
    with open(project_tycho_explanation_path, "r") as f:
        project_tycho_explanation = "\n".join(f.readlines())

    files: list[tuple[str, Path]] = [
        (drugbank_explanation, drugbank_dataset_path),
        (project_tycho_explanation, project_tycho_path),
    ]
    importer = Importer(files)
    df_n_desc: list[tuple[str, pd.DataFrame]] = importer.read()

    kg_generator = KgGenerator(df_n_desc)
    kg_generator.merge()
    kg_generator.ner()

from pydantic import BaseModel, Field


# Pydantic
class MergerModel(BaseModel):
    """Shared columns and selection of columns for a new dataset from previous datasets"""

    shared_columns: list[dict[str, str]] = Field(
        description="List of dictionaries, where every dictionary contains a collection of shared columns, the key is the source dataset and the value the name of the column"
    )
    combined_dataset_schema: list[str] = Field(
        description="list of column names for a new dataset using a subset of columns from the original datasets if they have some shared columns"
    )
    explanation: str = Field(
        description="Rationale behind why certain columns are shared among datasets"
    )

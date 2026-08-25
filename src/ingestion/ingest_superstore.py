from pathlib import Path

import pandas as pd

from src.utils.config import PROJECT_ROOT, load_config
from src.utils.logger import get_logger


logger = get_logger(__name__)


def load_source_data(file_path: Path) -> pd.DataFrame:
    """Load the source Superstore CSV into a DataFrame."""

    logger.info("Reading source file: %s", file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Source dataset not found: {file_path}"
        )

    dataframe = pd.read_csv(file_path)

    if dataframe.empty:
        raise ValueError("Source dataset contains zero rows.")

    logger.info(
        "Successfully loaded %s rows and %s columns.",
        len(dataframe),
        len(dataframe.columns),
    )

    return dataframe


def profile_data(dataframe: pd.DataFrame) -> None:
    """Log basic source dataset information."""

    logger.info("Dataset columns: %s", list(dataframe.columns))

    duplicate_count = dataframe.duplicated().sum()

    missing_values = dataframe.isna().sum()
    missing_columns = missing_values[missing_values > 0]

    logger.info("Duplicate rows: %s", duplicate_count)

    if missing_columns.empty:
        logger.info("No missing values detected.")
    else:
        logger.info(
            "Columns containing missing values: %s",
            missing_columns.to_dict(),
        )


def prepare_bronze_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Perform only ingestion-level preparation.

    Bronze should remain close to the source.
    """

    dataframe = dataframe.copy()

    if "Order Date" not in dataframe.columns:
        raise ValueError(
            "Expected 'Order Date' column was not found."
        )

    dataframe["Order Date"] = pd.to_datetime(
        dataframe["Order Date"],
        errors="coerce",
    )

    invalid_dates = dataframe["Order Date"].isna().sum()

    logger.info(
        "Rows with invalid Order Date values: %s",
        invalid_dates,
    )

    dataframe["order_year"] = dataframe["Order Date"].dt.year

    return dataframe


def write_partitioned_parquet(
    dataframe: pd.DataFrame,
    output_directory: Path,
    partition_column: str,
) -> None:
    """Write Bronze data as partitioned Parquet files."""

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger.info(
        "Writing Bronze data to: %s",
        output_directory,
    )

    dataframe.to_parquet(
        output_directory,
        engine="pyarrow",
        partition_cols=[partition_column],
        index=False,
    )

    logger.info("Bronze data written successfully.")


def main() -> None:
    """Run the Bronze ingestion pipeline."""

    config = load_config()

    raw_directory = PROJECT_ROOT / config["data"]["raw_path"]
    bronze_directory = PROJECT_ROOT / config["data"]["bronze_path"]

    dataset_filename = config["dataset"]["filename"]
    partition_column = config["bronze"]["partition_column"]

    source_path = raw_directory / dataset_filename

    logger.info("Starting Superstore Bronze ingestion.")

    dataframe = load_source_data(source_path)

    profile_data(dataframe)

    dataframe = prepare_bronze_data(dataframe)

    write_partitioned_parquet(
        dataframe=dataframe,
        output_directory=bronze_directory / "orders",
        partition_column=partition_column,
    )

    logger.info("Bronze ingestion completed successfully.")


if __name__ == "__main__":
    main()
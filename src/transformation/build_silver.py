import re
from pathlib import Path

import pandas as pd

from src.utils.config import PROJECT_ROOT, load_config
from src.utils.logger import get_logger


logger = get_logger(__name__)


COLUMN_RENAME_MAP = {
    "Row ID": "row_id",
    "Order ID": "order_id",
    "Order Date": "order_date",
    "Ship Date": "ship_date",
    "Ship Mode": "ship_mode",
    "Customer ID": "customer_id",
    "Customer Name": "customer_name",
    "Segment": "segment",
    "Country": "country",
    "City": "city",
    "State": "state",
    "Postal Code": "postal_code",
    "Region": "region",
    "Product ID": "product_id",
    "Category": "category",
    "Sub-Category": "sub_category",
    "Product Name": "product_name",
    "Sales": "sales",
    "Quantity": "quantity",
    "Discount": "discount",
    "Profit": "profit",
}


def standardize_column_names(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Convert source column names to analytics-friendly names."""

    dataframe = dataframe.copy()

    dataframe = dataframe.rename(
        columns=COLUMN_RENAME_MAP
    )

    dataframe.columns = [
        re.sub(
            r"[^a-z0-9_]",
            "",
            column.lower().replace(" ", "_"),
        )
        for column in dataframe.columns
    ]

    return dataframe


def standardize_text_columns(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Clean whitespace and standardize categorical text."""

    dataframe = dataframe.copy()

    text_columns = [
        "ship_mode",
        "customer_name",
        "segment",
        "country",
        "city",
        "state",
        "region",
        "category",
        "sub_category",
        "product_name",
    ]

    for column in text_columns:
        if column in dataframe.columns:
            dataframe[column] = (
                dataframe[column]
                .astype("string")
                .str.strip()
            )

    categorical_columns = [
        "segment",
        "region",
        "category",
        "sub_category",
        "ship_mode",
    ]

    for column in categorical_columns:
        if column in dataframe.columns:
            dataframe[column] = (
                dataframe[column]
                .str.replace(
                    r"\s+",
                    " ",
                    regex=True,
                )
            )

    return dataframe


def convert_data_types(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Apply explicit analytical data types."""

    dataframe = dataframe.copy()

    date_columns = [
        "order_date",
        "ship_date",
    ]

    for column in date_columns:
        dataframe[column] = pd.to_datetime(
            dataframe[column],
            errors="coerce",
        )

    numeric_columns = [
        "row_id",
        "postal_code",
        "sales",
        "quantity",
        "discount",
        "profit",
    ]

    for column in numeric_columns:
        if column in dataframe.columns:
            dataframe[column] = pd.to_numeric(
                dataframe[column],
                errors="coerce",
            )

    return dataframe


def remove_exact_duplicates(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Remove exact duplicate records."""

    before = len(dataframe)

    dataframe = dataframe.drop_duplicates()

    removed = before - len(dataframe)

    logger.info(
        "Removed %s exact duplicate rows.",
        removed,
    )

    return dataframe


def handle_missing_values(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Handle missing values according to business meaning."""

    dataframe = dataframe.copy()

    if "postal_code" in dataframe.columns:
        dataframe["postal_code"] = (
            dataframe["postal_code"]
            .astype("Int64")
        )

    return dataframe


def validate_business_rules(
    dataframe: pd.DataFrame,
) -> None:
    """Validate critical business rules before Silver output."""

    if dataframe["order_date"].isna().any():
        raise ValueError(
            "Silver validation failed: "
            "order_date contains null values."
        )

    if dataframe["ship_date"].isna().any():
        raise ValueError(
            "Silver validation failed: "
            "ship_date contains null values."
        )

    invalid_ship_dates = (
        dataframe["ship_date"]
        < dataframe["order_date"]
    )

    if invalid_ship_dates.any():
        invalid_count = int(
            invalid_ship_dates.sum()
        )

        raise ValueError(
            "Silver validation failed: "
            f"{invalid_count} rows have ship_date "
            "before order_date."
        )

    if (dataframe["quantity"] < 1).any():
        raise ValueError(
            "Silver validation failed: "
            "quantity must be at least 1."
        )

    if (
        (dataframe["discount"] < 0)
        | (dataframe["discount"] > 1)
    ).any():
        raise ValueError(
            "Silver validation failed: "
            "discount must be between 0 and 1."
        )


def write_silver(
    dataframe: pd.DataFrame,
    output_path: Path,
) -> None:
    """Write cleaned Silver data as partitioned Parquet."""

    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe["order_year"] = (
        dataframe["order_date"].dt.year
    )

    dataframe.to_parquet(
        output_path,
        engine="pyarrow",
        partition_cols=["order_year"],
        index=False,
    )

    logger.info(
        "Silver data written to %s",
        output_path,
    )


def main():
    """Build the Silver layer."""

    config = load_config()

    bronze_path = (
        PROJECT_ROOT
        / config["data"]["bronze_path"]
        / "orders"
    )

    silver_path = (
        PROJECT_ROOT
        / config["data"]["silver_path"]
        / "orders"
    )

    logger.info(
        "Reading Bronze data from %s",
        bronze_path,
    )

    dataframe = pd.read_parquet(bronze_path)

    logger.info(
        "Bronze rows before transformation: %s",
        len(dataframe),
    )

    dataframe = standardize_column_names(
        dataframe
    )

    dataframe = standardize_text_columns(
        dataframe
    )

    dataframe = convert_data_types(
        dataframe
    )

    dataframe = remove_exact_duplicates(
        dataframe
    )

    dataframe = handle_missing_values(
        dataframe
    )

    validate_business_rules(
        dataframe
    )

    write_silver(
        dataframe,
        silver_path,
    )

    logger.info(
        "Silver transformation completed successfully."
    )


if __name__ == "__main__":
    main()
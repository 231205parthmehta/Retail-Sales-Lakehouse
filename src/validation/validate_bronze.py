from pathlib import Path

import great_expectations as gx

from src.utils.config import PROJECT_ROOT, load_config
from src.utils.logger import get_logger


logger = get_logger(__name__)


def create_validation_context():
    """Create or load a file-backed Great Expectations context."""

    context_root = PROJECT_ROOT / "great_expectations"

    context = gx.get_context(
        mode="file",
        project_root_dir=str(context_root),
    )

    logger.info("Great Expectations context initialized.")

    return context


def build_expectation_suite(context):
    """Create the Bronze data quality expectation suite."""

    suite_name = "bronze_orders_quality"

    try:
        suite = context.suites.get(suite_name)
        logger.info("Existing expectation suite loaded: %s", suite_name)

    except Exception:
        suite = gx.ExpectationSuite(name=suite_name)
        suite = context.suites.add(suite)

        logger.info("Created expectation suite: %s", suite_name)

    suite.expectations = []

    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="Order ID",
            severity="critical",
        )
    )

    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="Order Date",
            severity="critical",
        )
    )

    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="Ship Date",
            severity="critical",
        )
    )

    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="Sales",
            severity="critical",
        )
    )

    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="Profit",
            severity="critical",
        )
    )

    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="Quantity",
            min_value=1,
            severity="critical",
        )
    )

    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="Discount",
            min_value=0,
            max_value=1,
            severity="critical",
        )
    )

    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="Customer ID",
            severity="critical",
        )
    )

    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="Product ID",
            severity="critical",
        )
    )

    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeInSet(
            column="Category",
            value_set=[
                "Furniture",
                "Office Supplies",
                "Technology",
            ],
            severity="warning",
        )
    )

    logger.info(
        "Expectation suite contains %s expectations.",
        len(suite.expectations),
    )

    return suite


def create_batch_definition(context):
    """Create the DataFrame batch definition used by GX."""

    datasource_name = "retail_bronze"
    asset_name = "bronze_orders"
    batch_definition_name = "whole_orders_dataframe"

    try:
        datasource = context.data_sources.get(datasource_name)
    except Exception:
        datasource = context.data_sources.add_pandas(datasource_name)

    try:
        asset = datasource.get_asset(asset_name)
    except Exception:
        asset = datasource.add_dataframe_asset(
            name=asset_name
        )

    try:
        batch_definition = asset.get_batch_definition(
            batch_definition_name
        )
    except Exception:
        batch_definition = (
            asset.add_batch_definition_whole_dataframe(
                batch_definition_name
            )
        )

    logger.info("GX batch definition ready.")

    return batch_definition


def run_validation(context, suite, batch_definition, dataframe):
    """Run the Bronze data quality validation."""

    validation_definition_name = "validate_bronze_orders"

    try:
        validation_definition = (
            context.validation_definitions.get(
                validation_definition_name
            )
        )

    except Exception:
        validation_definition = (
            gx.ValidationDefinition(
                name=validation_definition_name,
                data=batch_definition,
                suite=suite,
            )
        )

        context.validation_definitions.add(
            validation_definition
        )

    logger.info("Running Bronze data quality validation.")

    result = validation_definition.run(
        batch_parameters={
            "dataframe": dataframe,
        }
    )

    logger.info("Validation completed.")

    print(result.describe())

    if not result.success:
        raise ValueError(
            "Bronze data quality validation failed."
        )

    logger.info(
        "Bronze data quality validation PASSED."
    )


def main():
    """Run Bronze data quality validation."""

    config = load_config()

    bronze_path = (
        PROJECT_ROOT
        / config["data"]["bronze_path"]
        / "orders"
    )

    logger.info(
        "Loading Bronze data from %s",
        bronze_path,
    )

    import pandas as pd

    dataframe = pd.read_parquet(bronze_path)

    context = create_validation_context()

    suite = build_expectation_suite(context)

    batch_definition = create_batch_definition(context)

    run_validation(
        context=context,
        suite=suite,
        batch_definition=batch_definition,
        dataframe=dataframe,
    )


if __name__ == "__main__":
    main()
import argparse
import pandas as pd
import xarray as xr

DEFAULT_FILENAMES = [
    "CityPairs_85to88.xls",
    "CityPairs_89to93.xls",
    "CityPairs_94to98.xls",
    "CityPairs_99to2003.xls",
    "CityPairs_2004to2008.xls",
    "CityPairs_2009to2020.xlsx",
]

DEFAULT_COLUMNS = [
    "Month",
    "AustralianPort",
    "ForeignPort",
    "Country",
    "PaxIn",
    "PaxOut",
]

DEFAULT_INDEX = ["AustralianPort", "ForeignPort", "Month"]


def excel_to_cdf(
    files: list = None,
    columns: list = None,
    index: list = None,
    sheet: str = "Data",
    output: str = None,
    mergedate: bool = False,
    verbose: bool = False,
) -> xr.Dataset:
    """Process a list of excel spreadsheets into an xarray format and save as a cdf
    This only includes specific columns in the resulting spreadsheet

    Keyword Arguments:
        files {str} -- List of excel spreadsheet files to process (default: filenames for international city pairs)
        columns {list} -- List of columns to include in the resulting structure (default: columns for international city pairs)
        index {list} -- Ordered list of columns to index the data with (default: index for international city pairs)
        output {str} -- If specified, save the resulting structure to the file (default: {None})

    Returns:
        xr.Dataset -- Concatenated spreadsheets in xarray Dataset form
    """
    # Handle defaults
    files = files if files else DEFAULT_FILENAMES
    columns = columns if columns else DEFAULT_COLUMNS
    index = index if index else DEFAULT_INDEX

    # The data we need is split across multiple spreadsheets, concat all of these together
    # Most columns aren't important - so only take the ones we need
    # This step also has some basic data sanitisation to help keep the data stable
    data = []
    for file in files:
        df = pd.read_excel(file, sheet_name=sheet)
        # Date combining if required
        if mergedate:
            df["Month"] = pd.to_datetime(df[["Year", "Month"]].assign(DAY=1))

        # Strip columns as needed
        df = df[columns]

        # Basic sanitising
        df = df.replace("..", 0)
        if "Passengers" in df.columns:
            df = df[
                ~df.Passengers.str.contains("Data not available for release.", na=False)
            ]

        # Add to the list of parsed spreadsheets
        data.append(df)

        # Logging
        if verbose:
            print(f"Loaded {file}")
            print(f"Row Count: {len(df.index)}")

    # Combine & reshape the data so it's easier to work with
    combined = pd.concat(data)
    combined = combined.set_index(index)
    combined = combined.to_xarray()

    # If an output filename is given, save the file
    if output:
        combined.to_netcdf(output, engine="h5netcdf")

        if verbose:
            print(f"Successfully saved to {output}")

    return combined


def load_cdf(input: str) -> xr.Dataset:
    """Load a cdf file into an xarray dataset

    Arguments:
        input {str} -- Filename to load

    Returns:
        xr.Dataset -- Resulting dataset
    """
    return xr.open_dataset(input)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process a list of Excel spreadsheets into an xarray format"
    )
    parser.add_argument("files", nargs="+", help="Input excel spreadsheets")
    parser.add_argument(
        "--columns", nargs="*", help="Columns to include in the result structure"
    )
    parser.add_argument(
        "--index", nargs="*", help="Ordered list of columns to index by"
    )
    parser.add_argument(
        "--mergedate",
        action="store_true",
        help="Combine year and month columns into a single month column",
    )
    parser.add_argument(
        "--sheet",
        default="Data",
        help="Sheet in the excel spreadsheet containing the data. Defaults to 'Data'",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable additional output logging"
    )
    parser.add_argument("--output", help="Output cdf file. Leave blank for no saving.")
    args = parser.parse_args()

    excel_to_cdf(
        files=args.files,
        sheet=args.sheet,
        columns=args.columns,
        index=args.index,
        output=args.output,
        mergedate=args.mergedate,
        verbose=args.verbose,
    )

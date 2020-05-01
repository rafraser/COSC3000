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
    data = []
    for file in files:
        df = pd.read_excel(file, sheet_name=sheet)
        df = df[columns]
        df = df.replace("..", 0)
        data.append(df)

    # Combine & reshape the data so it's easier to work with
    combined = pd.concat(data)
    combined = combined.set_index(index)
    combined = combined.to_xarray()

    # If an output filename is given, save the file
    if output:
        combined.to_netcdf(output, engine="h5netcdf")

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
        "--columns", nargs="?", help="Columns to include in the result structure"
    )
    parser.add_argument(
        "--index", nargs="?", help="Ordered list of columns to index by"
    )
    parser.add_argument("--output", help="Output cdf file. Leave blank for no saving.")
    args = parser.parse_args()

    excel_to_cdf(
        files=args.files, columns=args.columns, index=args.index, output=args.output,
    )

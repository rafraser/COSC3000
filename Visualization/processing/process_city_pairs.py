import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt

FILENAMES = [
    "CityPairs_85to88.xls",
    "CityPairs_89to93.xls",
    "CityPairs_94to98.xls",
    "CityPairs_99to2003.xls",
    "CityPairs_2004to2008.xls",
    "CityPairs_2009to2020.xlsx",
]


def load_data():
    data = []

    # The data we need is split across multiple spreadsheets, aggregate all of these together
    # We don't care about Freight and Mail numbers either, so drop those from the spreadsheets
    for file in FILENAMES:
        df = pd.read_excel("../datasets/" + file, sheet_name="Data")
        df = df[
            ["Month", "AustralianPort", "ForeignPort", "Country", "PaxIn", "PaxOut"]
        ]
        df = df.replace("..", 0)
        data.append(df)

    # Combine & reshape the data so it's easier to work with
    combined = pd.concat(data)
    combined = combined.set_index(["AustralianPort", "ForeignPort", "Month"])
    combined = combined.to_xarray()
    return combined


if __name__ == "__main__":
    combined = load_data()

    incoming = input("Australian Port: ")
    outgoing = input("Foreign Port: ")

    test = combined.sel(AustralianPort=incoming, ForeignPort=outgoing)[
        ["PaxIn", "PaxOut"]
    ]
    test.to_dataframe().plot()
    plt.title(f"{incoming} - {outgoing}")
    plt.show()

    test.to_dataframe().to_csv("testing.csv")

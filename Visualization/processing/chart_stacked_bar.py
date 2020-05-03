import datetime
import util
import matplotlib.pyplot as plt
import matplotlib.colors as cm
import numpy as np

AUSTRALIAN_CITIES = [
    "Sydney",
    "Melbourne",
    "Brisbane",
    "Perth",
    "Gold Coast",
    "Adelaide",
    "Darwin",
]

COLORS = ["#fc5c65", "#fd9644", "#fed330", "#26de81", "#4b7bec", "#a55eea", "#f368e0"]

if __name__ == "__main__":
    # Load Data
    combined = util.load_cdf("Visualization/international.nc")
    years = combined.coords["Month"].values  # [x for x in range(2014, 2020)]

    data = {}
    for city in AUSTRALIAN_CITIES:
        data[city] = []
        city_data = combined.sel(AustralianPort=city)

        for year in years:
            # Sum all the data for the year
            yearly_total = city_data.sel(Month=year).sum(["ForeignPort"])
            data[city].append(int(yearly_total.PaxIn))

    # Graph the data
    # We're doing a stacked barchart so this will be a little painful
    fig, ax = plt.subplots()
    cumulative = [0] * len(years)

    for i, city in enumerate(data):
        ax.bar(
            years,
            data[city],
            label=city,
            bottom=cumulative,
            width=31.0,
            align="center",
            color=COLORS[i],
        )

        cumulative = [sum(x) for x in zip(cumulative, data[city])]

    # Axis labels
    ax.set_ylabel("Incoming Passengers")
    ax.set_title("Yearly International Arrivals")
    ax.legend()

    fig.tight_layout()
    plt.show()

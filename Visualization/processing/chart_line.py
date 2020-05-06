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
    plt.rcParams.update({"font.size": 14})

    for i, city in enumerate(data):
        ax.plot(
            years, data[city], label=city,
        )

    # Axis labels
    ax.set_ylabel("Incoming Passengers", fontsize=12)
    ax.set_title("Yearly International Arrivals")
    ax.legend()

    fig.tight_layout()
    plt.show()

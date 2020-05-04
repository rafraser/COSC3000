import util
import numpy as np
import datetime
import matplotlib.pyplot as plt
import calendar

if __name__ == "__main__":
    combined = util.load_cdf("Visualization/international.nc")
    years = [x for x in range(2004, 2020)]
    months = [x for x in range(1, 13)]

    # Get the total for Sydney
    sydney_data = {}
    city_data = combined.sel(AustralianPort="Sydney")

    # We need the format of the data to be in a 2D-array format
    # Each column is a month, while each row is a year
    data = np.zeros(shape=(len(years), len(months)))

    for xx, year in enumerate(years):
        for yy, month in enumerate(months):
            date = datetime.datetime(year, month, 1)
            monthly_total = city_data.sel(Month=date).sum(["ForeignPort"])
            data[xx, yy] = int(monthly_total.PaxIn)

    # Setup the polar plot
    fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)

    # Plot the data
    theta = np.linspace(0, 2 * np.pi, len(months) + 1)
    r = np.arange(len(years) + 1)
    cout = ax.pcolormesh(theta, r, data, cmap="plasma")

    # Change the labels
    pos, step = np.linspace(0, 2 * np.pi, len(months), endpoint=False, retstep=True)
    pos += step / 2
    ax.set_xticks(pos)
    ax.set_xticklabels([calendar.month_name[i] for i in months])

    ax.set_yticks(np.arange(len(years)))
    ax.set_yticklabels(years)

    fig.colorbar(cout, ax=ax)
    plt.show()

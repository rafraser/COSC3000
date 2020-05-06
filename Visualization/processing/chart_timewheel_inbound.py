import util
import numpy as np
import datetime
import matplotlib.pyplot as plt
import calendar

AUSTRALIAN_CITIES = ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Darwin"]

if __name__ == "__main__":
    combined = util.load_cdf("Visualization/international.nc")
    years = [x for x in range(2004, 2020)]
    months = [x for x in range(1, 13)]

    # We need the format of the data to be in a 2D-array format
    # Each column is a month, while each row is a year
    data = [
        np.zeros(shape=(len(years), len(months))) for i in range(len(AUSTRALIAN_CITIES))
    ]

    # Generate the dataset
    # Each city gets one array
    for i, city in enumerate(AUSTRALIAN_CITIES):
        city_data = combined.sel(AustralianPort=city)

        for xx, year in enumerate(years):
            for yy, month in enumerate(months):
                date = datetime.datetime(year, month, 1)
                monthly_total = city_data.sel(Month=date).sum(["ForeignPort"])
                data[i][xx, yy] = int(monthly_total.PaxIn)

    # Setup the subplots
    # Use polar coordinates because I'm a cool dude
    fig, axs = plt.subplots(
        2, 3, constrained_layout=True, subplot_kw={"projection": "polar"}
    )
    plt.rcParams.update({"font.size": 14})

    # Draw each dataset
    for pos, ax in np.ndenumerate(axs):
        i = pos[0] * 3 + pos[1]
        city_data = data[i]
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)

        # Plot the data
        theta = np.linspace(0, 2 * np.pi, len(months) + 1)
        r = np.arange(len(years) + 1)
        cout = ax.pcolormesh(theta, r, city_data, cmap="plasma")

        # Change the labels
        pos, step = np.linspace(0, 2 * np.pi, len(months), endpoint=False, retstep=True)
        pos += step / 2
        ax.set_xticks(pos)
        ax.set_xticklabels([calendar.month_name[i] for i in months], fontsize=12)

        # Only show every 2nd year to stop this chart looking atrocious
        ax.set_yticks(np.arange(len(years)))
        ax.set_yticklabels(years, fontsize=10)
        for label in ax.get_yticklabels()[::2]:
            label.set_visible(False)

        ax.set_title(f"{AUSTRALIAN_CITIES[i]} - Total Monthly Arrivals")
        fig.colorbar(cout, ax=ax)

    plt.show()

import util
import numpy as np
import datetime
import matplotlib.pyplot as plt
import calendar

if __name__ == "__main__":
    combined = util.load_cdf("Visualization/domestic.nc")

    origin_airports = combined.coords["Origin"].values
    destination_airports = combined.coords["Destination"].values

    # Setup a nicer datastructure to work with
    # Keep in mind we want this heatmap to work both ways
    all_airports = list(set(origin_airports) | set(destination_airports))
    all_airports = sorted(all_airports)
    airport_indexes = {value: i for i, value in enumerate(all_airports)}
    heatmap_data = np.zeros(shape=(len(all_airports), len(all_airports)))

    # Get data for Dec-2019 by default
    # We'll make this animated later
    data = combined.sel(Month=datetime.datetime(2019, 12, 1))
    for origin in origin_airports:
        origin_index = airport_indexes[origin]
        city_data = data.sel(Origin=origin).dropna(dim="Destination", how="all")

        for row in city_data.Passengers:
            count = int(row.values)
            destination_index = airport_indexes[str(row.coords["Destination"].values)]

            # Set both sides of the array to this value
            heatmap_data[origin_index, destination_index] = count
            heatmap_data[destination_index, origin_index] = count

    # Plot the data
    fig, ax = plt.subplots()
    im = ax.imshow(heatmap_data, cmap="plasma")

    # Adjust ticks
    ax.set_xticks(np.arange(len(all_airports)))
    ax.set_yticks(np.arange(len(all_airports)))
    ax.set_xticklabels(all_airports)
    ax.set_yticklabels(all_airports)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Adjust colorbar
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel("Total Traffic")

    ax.set_title("Domestic Traffic - December 2019")
    fig.tight_layout()
    plt.show()

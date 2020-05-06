import util
import numpy as np
import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation

if __name__ == "__main__":
    combined = util.load_cdf("Visualization/domestic.nc")

    origin_airports = combined.coords["Origin"].values
    destination_airports = combined.coords["Destination"].values
    years = [x for x in range(2004, 2020)]
    months = [
        datetime.datetime(year, month, 1) for year in years for month in range(1, 13)
    ]

    # Setup a nicer datastructure to work with
    # This time around we want one for every month
    all_airports = list(set(origin_airports) | set(destination_airports))
    all_airports = sorted(all_airports)
    airport_indexes = {value: i for i, value in enumerate(all_airports)}
    heatmap_data = [
        np.zeros(shape=(len(all_airports), len(all_airports)))
        for x in range(len(months))
    ]

    # Process all the data in advance
    # This may take a while
    # Efficiency is for nerds
    for i, month in enumerate(months):
        data = combined.sel(Month=month)

        for origin in origin_airports:
            origin_index = airport_indexes[origin]
            city_data = data.sel(Origin=origin).dropna(dim="Destination", how="all")

            for row in city_data.Passengers:
                count = int(row.values)

                destination_index = airport_indexes[
                    str(row.coords["Destination"].values)
                ]

                # Set both sides of the array to this value
                heatmap_data[i][origin_index, destination_index] = count
                heatmap_data[i][destination_index, origin_index] = count

    # Setup the axis
    fig, ax = plt.subplots()
    fig.set_size_inches(16, 9)
    img = ax.imshow(heatmap_data[0], cmap="plasma")

    ax.set_xticks(np.arange(len(all_airports)))
    ax.set_yticks(np.arange(len(all_airports)))
    ax.set_xticklabels(all_airports)
    ax.set_yticklabels(all_airports)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Adjust colorbar
    cbar = ax.figure.colorbar(img, ax=ax)
    cbar.ax.set_ylabel("Total Traffic")

    # Prepare the animation
    def animate(data):
        (i, month) = data
        dataset = heatmap_data[i]

        ax.set_title(month.strftime("%m-%Y"))
        img.set_data(dataset)

    anim = animation.FuncAnimation(
        fig,
        animate,
        interval=1000 / 12,
        repeat=True,
        frames=[(i, month) for i, month in enumerate(months)],
    )

    # Save the animation
    anim.save(
        "Visualization/graphs/domestic_heatmap.mp4", writer="imagemagick", dpi=100
    )

    plt.show()

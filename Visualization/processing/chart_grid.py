import util
import matplotlib.pyplot as plt

AUSTRALIAN_CITIES = [
    "Sydney",
    "Melbourne",
    "Brisbane",
    "Perth",
    "Adelaide",
]
FOREIGN_CITIES = ["Auckland", "Hong Kong", "Singapore", "Kuala Lumpur", "Tokyo"]

if __name__ == "__main__":
    # Load Data
    combined = util.load_cdf("Visualization/international-legacy.nc")

    # Setup the graph
    fig, axes = plt.subplots(nrows=len(AUSTRALIAN_CITIES), ncols=len(FOREIGN_CITIES))

    # Plot each incoming/outgoing pair
    for xx, incoming in enumerate(AUSTRALIAN_CITIES):
        for yy, outgoing in enumerate(FOREIGN_CITIES):
            test = combined.sel(AustralianPort=incoming, ForeignPort=outgoing)[
                ["PaxIn", "PaxOut"]
            ]

            test.to_dataframe().plot(ax=axes[xx, yy], legend=False)
            axes[xx, yy].legend(loc="upper right")

    # Handle axes labels
    for ax, col in zip(axes[0, :], FOREIGN_CITIES):
        ax.set_title(col)

    for ax, row in zip(axes[:, 0], AUSTRALIAN_CITIES):
        ax.set_ylabel(row, size="large")

    for ax in fig.get_axes():
        ax.set_xticks([], [])
        ax.set_yticks([])
        ax.set_xlabel("")
        ax.label_outer()

    # Plot with no gaps
    fig.tight_layout()
    plt.subplots_adjust(wspace=0, hspace=0)
    plt.show()

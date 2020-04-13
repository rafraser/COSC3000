import util
import matplotlib.pyplot as plt

AUSTRALIAN_CITIES = ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide"]
FOREIGN_CITIES = ["Auckland", "Christchurch", "Hong Kong", "Singapore", "Kuala Lumpur"]

if __name__ == "__main__":
    combined = util.load_data()
    fig, axes = plt.subplots(nrows=len(AUSTRALIAN_CITIES), ncols=len(FOREIGN_CITIES))

    for xx, incoming in enumerate(AUSTRALIAN_CITIES):
        for yy, outgoing in enumerate(FOREIGN_CITIES):
            test = combined.sel(AustralianPort=incoming, ForeignPort=outgoing)[
                ["PaxIn", "PaxOut"]
            ]

            test.to_dataframe().plot(ax=axes[xx, yy], legend=False)

    for ax, col in zip(axes[0], AUSTRALIAN_CITIES):
        ax.set_title(col)

    for ax, row in zip(axes[:, 0], FOREIGN_CITIES):
        ax.set_ylabel(row, rotation=0, size="large")

    for ax in axes.reshape(-1):
        ax.axis("off")

    fig.tight_layout()
    plt.subplots_adjust(wspace=0, hspace=0)
    plt.show()

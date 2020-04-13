import util
import matplotlib.pyplot as plt

if __name__ == "__main__":
    combined = util.load_data()

    while True:
        incoming = input("Australian Port: ")
        outgoing = input("Foreign Port: ")

        test = combined.sel(AustralianPort=incoming, ForeignPort=outgoing)[
            ["PaxIn", "PaxOut"]
        ]
        test.to_dataframe().plot()
        plt.title(f"{incoming} - {outgoing}")
        plt.show()

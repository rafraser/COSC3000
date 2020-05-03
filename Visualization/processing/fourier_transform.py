import util
import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import fft

AUSTRALIAN_CITIES = [
    "Sydney",
    "Melbourne",
    "Brisbane",
    "Perth",
    "Adelaide",
]

if __name__ == "__main__":
    combined = util.load_cdf("Visualization/international.nc")
    months = combined.coords["Month"].values

    # Get the total for Sydney
    sydney_data = []
    city_data = combined.sel(AustralianPort=AUSTRALIAN_CITIES[0])

    for month in months:
        # Sum all the data for the year
        yearly_total = city_data.sel(Month=month).sum(["ForeignPort"])
        sydney_data.append(int(yearly_total.PaxIn))

    # plt.plot(months, sydney_data)
    plt.show()

    # Fourier transform code pretty much directly taken from the scipy example
    # https://docs.scipy.org/doc/scipy/reference/tutorial/fft.html
    N = len(months)  # Number of sample points
    T = 1.0 / 800.0  # Samplce spacing
    yf = fft(sydney_data)
    xf = np.linspace(0.0, 1.0 / (2.0 * T), N // 2)

    # I have 0 idea what this graph means
    plt.plot(xf, 2.0 / N * np.abs(yf[0 : N // 2]))
    plt.show()

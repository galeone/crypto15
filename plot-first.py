"""Plots the first element of the shuffled TRFecord that holds every split."""

from datetime import datetime
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import tensorflow_datasets as tfds
import crypto15  # pylint:disable=unused-import


def main():
    """Plots the first element of the shuffled TRFecord that holds every split."""
    datasets, info = tfds.load("crypto15", with_info=True)

    for currency in info.splits.keys():
        dataset = datasets[currency]
        times = []
        prices = []
        # This is a random day, the order in the TFRecord is not
        # the insertion order
        day = next(iter(dataset.take(1)))
        sequence_len = day["timestamp"].shape[0]
        for idx in range(sequence_len):
            times.append(datetime.fromtimestamp(day["timestamp"][idx]))
            prices.append(day["price_usd"][idx])

        start = times[0]
        end = times[-1]
        plt.title(f"{currency}: {start} to {end}; {len(times)} pts")
        plt.subplots_adjust(bottom=0.2)
        plt.xticks(rotation=90)
        ax = plt.gca()
        xfmt = mdates.DateFormatter("%H:%M:%S")
        ax.xaxis.set_major_formatter(xfmt)
        datenums = mdates.date2num(times)
        plt.plot(datenums, prices)
        plt.savefig(f"{currency}.png")
        plt.close()


if __name__ == "__main__":
    main()

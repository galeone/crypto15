"""Crypto15: snapshot captured every 15 minutes of the status of 9 cryptocurrencies.
Version 1: data from 2017-10-26 14:34:10 to 2019-02-25 09:50:02.
Currencies: "BTC", "XRP", "ETH", "LTC", "XMR", "MIOTA", "ZEC", "EOS", "ETC"
"""

from datetime import datetime
import sqlite3
import tensorflow as tf
import tensorflow_datasets as tfds


class Crypto15(tfds.core.GeneratorBasedBuilder):
    """Crypto15: snapshot captured every 15 minutes of the status of 9 cryptocurrencies."""

    VERSION = tfds.core.Version("1.0.0")

    def __init__(self, **builder_kwargs):
        self._currencies = [
            "BTC",
            "XRP",
            "ETH",
            "LTC",
            "XMR",
            "MIOTA",
            "ZEC",
            "EOS",
            "ETC",
        ]
        self._citation = ""

        self._description = """
        Crypto15: snapshot captured every 15 minutes of the status of 9 cryptocurrencies.
            Version 1: data from 2017-10-26 14:34:10 to 2019-02-25 09:50:02.
            Currencies: "BTC", "XRP", "ETH", "LTC", "XMR", "MIOTA", "ZEC", "EOS", "ETC"
        """

        self._url = (
            "https://github.com/galeone/crypto15/blob/master/data/crypto15.db3?raw=true"
        )

        super().__init__(**builder_kwargs)

    def _info(self):
        return tfds.core.DatasetInfo(
            builder=self,
            description=self._description,
            features=tfds.features.SequenceDict(
                {
                    "timestamp": tf.int64,
                    "price_btc": tf.float64,
                    "price_usd": tf.float64,
                    "day_volume_usd": tf.int64,
                    "market_cap_usd": tf.int64,
                    "percent_change_1h": tf.float64,
                    "percent_change_24h": tf.float64,
                    "percent_change_7d": tf.float64,
                }
            ),
            supervised_keys=None,
            urls=[self._url],
            citation=self._citation,
        )

    def _split_generators(self, dl_manager):
        """Returns SplitGenerators."""

        db_path = dl_manager.download(self._url)
        return [
            tfds.core.SplitGenerator(
                name=currency,
                num_shards=1,
                gen_kwargs={"db_path": db_path, "currency": currency},
            )
            for currency in self._currencies
        ]

    def _generate_examples(self, db_path, currency):
        """Yields examples."""

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        current_sequence_date = ""
        daily_sequence = []
        for idx, row in enumerate(
            cursor.execute(
                "SELECT * FROM monitored_currencies WHERE currency = '%s' ORDER BY time ASC"
                % currency
            )
        ):
            element = {
                "timestamp": int(
                    datetime.strptime(row["time"], "%Y-%m-%d %H:%M:%S").timestamp()
                ),
                "price_btc": row["price_btc"],
                "price_usd": row["price_usd"],
                "day_volume_usd": row["day_volume_usd"],
                "market_cap_usd": row["market_cap_usd"],
                "percent_change_1h": row["percent_change_1h"],
                "percent_change_24h": row["percent_change_24h"],
                "percent_change_7d": row["percent_change_7d"],
            }
            row_date = row["time"].split(" ")[0]
            if idx == 0:
                current_sequence_date = row_date
            else:
                if current_sequence_date != row_date:

                    if daily_sequence:
                        print("End of day: ", current_sequence_date)
                        yield daily_sequence
                    else:
                        print("No data for day: ", current_sequence_date)

                    daily_sequence = []
                    current_sequence_date = row_date
            daily_sequence.append(element)

        conn.close()

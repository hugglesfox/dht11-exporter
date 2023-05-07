import logging

from pyudev import Context
from prometheus_client.core import GaugeMetricFamily
from prometheus_client.registry import Collector

from typing import Iterable


class DhtCollector(Collector):
    """A collector for the DHT11/22

    On enter the linux industrial io subsystem will be searched for the given
    sys_name (usually iio:device0 or similar).
    """

    def __init__(self, sys_name: str):
        self._iio = (
            Context().list_devices().match_subsystem("iio").match_sys_name(sys_name)
        )

        self._temp_f = None
        self._humidity_f = None

        self.temp = None
        self.humidity = None

    def __enter__(self):
        for dev in self._iio:
            try:
                logging.info("Trying device at path " + dev.sys_path)
                self._temp_f = open(dev.sys_path + "/in_temp_input", "r")
                self._humidity_f = open(dev.sys_path + "/in_humidityrelative_input", "r")
                break
            except IOError:
                logging.error("Unable to open device")
        else:
            logging.error("No devices found")

        return self

    def __exit__(self, *args):
        if self._temp_f is not None:
            self._temp_f.close()

        if self._humidity_f is not None:
            self._humidity_f.close()

    def read_dht(self):
        if self._temp_f is None or self._humidity_f is None:
            logging.error("Unable to read DHT device")
            return

        try:
            # The linux kernel module multiplies the results by 1000 for some
            # reason
            self.temp = int(self._temp_f.read()) / 1000
            self.humidity = int(self._humidity_f.read()) / 1000
        except (IOError, ValueError):
            # The DHT will sometimes fail to read, in this case using the last
            # known values is fine
            return

    def collect(self) -> Iterable[GaugeMetricFamily]:
        self.read_dht()

        if self.temp is not None:
            yield GaugeMetricFamily(
                "dht_temperature", "Temperature (°C)", value=self.temp
            )

        if self.humidity is not None:
            yield GaugeMetricFamily(
                "dht_humidity", "Relative Humidity (%)", value=self.humidity
            )

import network
import socket
import json
import utime as time
import machine
import webrepl
from unterwasserhandgekloeppelt import http_get

trash_url = "http://hackspace-siegen.de:57000/"
street_file = "/street.txt"
wifi_file = "/wifi.txt"

class Trashbox:
    def __init__(self):
        self.dates = {}
        self._dates_json = ""
        self.year = 0
        self.street = "Effertsufer"
        self.essid = ""
        self.password = ","

        try:
            with open(street_file, "r") as sf:
                self.street = sf.read().strip()
        except:
            print("Could not load street!")

        try:
            with open(wifi_file, "r") as wf:
                wifi = wf.read().split("\n")
                self.essid = wifi[0].strip()
                self.password = wifi[1].strip()
        except:
            print("Could not load wifi!")

        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.wlan.connect(self.essid, self.password)

        while not self.wlan.isconnected():
            time.sleep(1)

        time_retrieved = False
        while not time_retrieved:
            try: 
                self.set_time(2 * 60 * 60)
                time_retrieved = True
            except:
                print("Could not set the time! Retrying in 1 seconds...")
                time.sleep(1)

    def set_time(self, dt=0):
        import ntptime
        t = ntptime.time()
        tm = time.localtime(t + dt)
        tm = tm[0:3] + (0,) + tm[3:6] + (0,)
        machine.RTC().datetime(tm)

    def get_trash(self):
        self._dates_json = ""
        http_get(self._trash_handler, trash_url + self.street)
        self.dates = json.loads(self._dates_json)

        return self.dates

    def _trash_handler(self, line):
        self._dates_json += line

        return True

    def handle_year_changed(self):
        year, _, _, _, _, _, _, _ = time.localtime()

        if year != self.year:
            try:
                self.get_trash()
                self.year = year
            except:
                print("Could not load the trash!")

    def get_trash_tomorrow(self):
        _, month, day, _, _, _, _, _ = time.localtime()
        month_key = "{:02}".format(month)
        day_key = "{:02}".format(day)

        if month_key in self.dates:
            if day_key in self.dates[month_key]:
                return self.dates[month_key][day_key]

        return []

    def set_red(self, val):
        pass

    def set_blue(self, val):
        pass

    def set_white(self, val):
        pass

    def set_yellow(self, val):
        pass

    def run(self):
        while True:
            self.handle_year_changed()

            trash = self.get_trash_tomorrow()
            print("Morgen ({0}):".format(self.street))
            print(trash)

            self.set_red("biotonne" in trash)
            self.set_blue("papier" in trash)
            self.set_white("restmuell" in trash)
            self.set_yellow("gelber_sack" in trash)

            time.sleep(10)

def main():
    trashbox = Trashbox()

    webrepl.start()
    trashbox.run()

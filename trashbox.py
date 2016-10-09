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
change_day_shift_file = "/change_day_shift.txt"

class Trashbox:
    PIN_NUMBER_RED = 12
    PIN_NUMBER_BLUE = 13
    PIN_NUMBER_WHITE = 5
    PIN_NUMBER_YELLOW = 4

    def __init__(self):
        self.dates = {}
        self._dates_json = ""
        self.year = 0
        self.street = "Effertsufer"
        self.essid = ""
        self.password = ","
        self.change_day_shift = 0

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

        try:
            with open(change_day_shift_file, "r") as cdsf:
                self.change_day_shift = int(cdsf.read().strip()) * 60 * 60
        except:
            print("Could not load change day shift!")

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

        self.current_duty = 512

        self.pin_red = machine.Pin(self.PIN_NUMBER_RED)
        self.pwm_red = machine.PWM(self.pin_red)
        self.pwm_red.freq(500)
        self.pwm_red.duty(0)

        self.pin_blue = machine.Pin(self.PIN_NUMBER_BLUE)
        self.pwm_blue = machine.PWM(self.pin_blue)
        self.pwm_blue.freq(500)
        self.pwm_blue.duty(0)

        self.pin_white = machine.Pin(self.PIN_NUMBER_WHITE)
        self.pwm_white = machine.PWM(self.pin_white)
        self.pwm_white.freq(500)
        self.pwm_white.duty(0)

        self.pin_yellow = machine.Pin(self.PIN_NUMBER_YELLOW)
        self.pwm_yellow = machine.PWM(self.pin_yellow)
        self.pwm_yellow.freq(500)
        self.pwm_yellow.duty(0)

        self.adc = machine.ADC(0)

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
        year, _, _, _, _, _, _, _ = time.localtime(time.time() + self.change_day_shift)

        if not isinstance(self.dates, dict) or \
           not "year" in self.dates or \
           year != self.dates["year"]:
            try:
                self.get_trash()
            except:
                print("Could not load the trash!")

    def handle_duty_cycle(self):
        min_duty = 20
        self.current_duty = max(self.adc.read(), min_duty)

    def get_trash_tomorrow(self):
        _, month, day, _, _, _, _, _ = time.localtime(time.time() + self.change_day_shift)
        month_key = "{:02}".format(month)
        day_key = "{:02}".format(day)

        if isinstance(self,dates, dict) and month_key in self.dates:
            if isinstance(self.dates[month_key]) and day_key in self.dates[month_key]:
                return self.dates[month_key][day_key]

        return []

    def set_red(self, val):
        if val:
            self.pwm_red.duty(self.current_duty)
        else:
            self.pwm_red.duty(0)

    def set_blue(self, val):
        if val:
            self.pwm_blue.duty(self.current_duty)
        else:
            self.pwm_blue.duty(0)

    def set_white(self, val):
        if val:
            self.pwm_white.duty(self.current_duty)
        else:
            self.pwm_white.duty(0)

    def set_yellow(self, val):
        if val:
            self.pwm_yellow.duty(self.current_duty)
        else:
            self.pwm_yellow.duty(0)

    def run(self):
        while True:
            self.handle_year_changed()
            self.handle_duty_cycle()

            trash = self.get_trash_tomorrow()

            print(trash)

            self.set_red("biotonne" in trash)
            self.set_blue("papier" in trash)
            self.set_white("restmuell" in trash)
            self.set_yellow("gelber_sack" in trash)

            if not self.wlan.isconnected():
                print("Reconnecting to {0}...".format(self.essid))
                self.wlan.connect(self.essid, self.password)

            time.sleep(10)

def main():
    trashbox = Trashbox()

    webrepl.start()
    trashbox.run()

# Trashbox

Trashbox is quite a simple solution for quite a simple (or complicated?) task: not forgetting to take out the trash.
It's a simple laser cutted box containing four LEDs, a photo resistor a [NodeMCU](https://en.wikipedia.org/wiki/NodeMCU).

<img src="photos/trashbox_open.jpg" height="250">
<img src="photos/trashbox_closed.jpg" height="250">

## Hardware

As already described, you need:

* 4 LEDs: one for each of your trash cans (for example red for the brown can, blue for paper, white for residual waste and yellow for the yellow bag), that and also the number of LEDs may highly depend on where you live of course, please see below for the software part
* Photo resistor: for not getting blind because of the LEDs when you wander through your apartment, you need this photo resistor
* NodeMCU: from somewhere the data must come and also something must control the LEDs, so why not wifi?!

## Software

The software part is written in [MicroPython](https://github.com/micropython/micropython) and depends on having the data available in a certain JSON format. This is why Trashbox, for the moment, only is working for the city Siegen in Germany. I would appreciate if you build stuff such as web scrapers so that this project is useful for others as well!

### Installation

You can either compile MicroPython for the ESP8266 on your own, flash it and put all the script files onto the device, or you can just clone this repository, attach your NodeMCU to your computer and use the install script:

~~~ bash
git clone https://github.com/misterdanb/trashbox
cd trashbox
./install.sh
~~~

The script asks you for some information and then installs the scripts and configurations to a precompiled MicroPython image and flashes this image onto the device.

### About the configuration files

There are three configuration files:

* street.txt: contains the street, for which the trash data is determined
* wifi.txt: contains two lines, in the first line the ssid, in the second line the password
* change_day_shift: contains the number of hours by which the switch to the next day should be performed

### About the Trashcal data

The Trashcal-Server must provide an HTTP interface of the form "http://{host}/{street}", where street requests the corresponding data, and respond with JSON data of the following form:

~~~ bnf
response := { <month>: <month_data> }
month := "01" | "02" | ... | "12"
month_data := { <day>: <day_data> }
day := "01" | "02" | ... | "31"
day_data := [ <day_data_list> ]
day_data_list := <trash_type>, <day_data_list> | <trash_type>
trash_type := "biotonne" | "papier" | "restmuell" | "gelber_sack"
~~~

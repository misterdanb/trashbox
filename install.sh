#!/usr/bin/sh
if [ ! -d "esptool" ]; then
	git clone https://github.com/themadinventor/esptool
fi

echo -n "Serial device: "
read dev

echo -n "SSID: "
read ssid
echo -n "Password: "
read password
echo -n "Street: "
read street

cp trashbox.bin trashbox_configured.bin

sudo su << EOF
mkdir -p mp_mnt

mount -t vfat -o loop,offset=0x90000 trashbox_configured.bin mp_mnt

echo -e "${ssid}\n${password}" > mp_mnt/wifi.txt
echo -e "${street}" > mp_mnt/street.txt

cp trashbox.py mp_mnt/trashbox.py
cp unterwasserhandgekloeppelt.py mp_mnt/unterwasserhandgekloeppelt.py
cp main.py mp_mnt/main.py

umount mp_mnt
sync

rm -r mp_mnt
EOF

python2 esptool/esptool.py --port ${dev} --baud=115200 write_flash --verify --flash_size=8m 0 trashbox_configured.bin

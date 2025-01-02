# Pay 2 Print Extension - <small>[repository](https://github.com/lnbits/pay2print) extension</small>


## share a printer via the network on cups
https://www.cups.org/doc/sharing.html


### 1. install cups and configure printer
```
apt-get install cups
systemctl start cups
systemctl enable cups

lpadmin -p MyPrinterName -o printer-is-shared=true
# set default printer
# lpoptions -d MyPrinterName
cupsctl --share-printers
```

### server where you access the sharedprinter via the network
```
apt-get install cups-client
# check if printer is shared
lpstat -h 10.5.5.2 -a
```

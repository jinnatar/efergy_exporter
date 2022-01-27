# efergy_exporter
Export Efergy metrics to Prometheus via rtl_433.

More documentation to come, but once you know what `-d` value to give rtl_433, just pass it in as an arg `--device` or as an env variable EFERGY_EXPORTER_DEVICE. Do note you'll also need to pass in the `--device` option to Docker. Full example run with a HackRF One utilizing the SoapySDR driver for it:

```
docker run --rm -it -p 9843:9843 --device /dev/bus/usb/002/005 ghcr.io/artanicus/efergy_exporter:latest --device 'driver=hackrf'
```

# efergy_exporter
Export Efergy metrics to Prometheus via rtl_433 & SoapySDR.

If you give the container only the correct USB device, it should be autodetected in most cases and running is as simple as:

```
docker run -p 9843:9843 --device /dev/bus/usb/002/005 ghcr.io/artanicus/efergy_exporter:latest
```

More documentation to come, but the `--device` parameter is passed as the SoapySDR device to use. You can also define it with the env variable `EFERGY_EXPORTER_DEVICE`. You can use ``--port` or `EFERGY_EXPORTER_PORT` to override the listen port.

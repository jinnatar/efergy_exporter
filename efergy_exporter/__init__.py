from absl import app, flags, logging
import json
import os
import time
import asyncio
from prometheus_client import start_http_server, Summary, Counter, Gauge
from collections.abc import Callable

FLAGS = flags.FLAGS

PREFIX = 'EFERGY_EXPORTER'

flags.DEFINE_string('device', os.getenv(f'{PREFIX}_DEVICE', ""), 'Device string to give to rtl_433. Defaults to SoapySDR default.')
flags.DEFINE_integer('port', os.getenv(f'{PREFIX}_PORT', 9843), 'Port to serve data on')




# Protect metrics
PREFIX = 'efergy_'
INFO = Gauge(PREFIX + 'info', 'General information', ['model', 'id'])
BATTERY_OK = Gauge(PREFIX + 'battery_ok', 'Battery status', ['id'])
INTERVAL = Gauge(PREFIX + 'interval', 'Update interval in seconds', ['id'])
CURRENT = Gauge(PREFIX + 'current', 'Current measurement in Amperes', ['id'])

RADIO_RSSI = Gauge(PREFIX + 'radio_rssi', 'Radio RSSI', ['id'])
RADIO_SNR = Gauge(PREFIX + 'radio_snr', 'Radio SNR', ['id'])
RADIO_NOISE = Gauge(PREFIX + 'radio_noise', 'Radio noise level', ['id'])

async def process_metrics(data: str):
    logging.debug('Processing broadcast')
    metrics = json.loads(data)
    # Basic info metrics
    INFO.labels(
            model=metrics['model'],
            id=metrics['id'],
            ).set(1)

    # actual metrics
    BATTERY_OK.labels(id=metrics['id']).set(metrics['battery_ok'])
    INTERVAL.labels(id=metrics['id']).set(metrics['interval'])
    CURRENT.labels(id=metrics['id']).set(metrics['current'])

    # Radio metrics
    RADIO_RSSI.labels(id=metrics['id']).set(metrics['rssi'])
    RADIO_SNR.labels(id=metrics['id']).set(metrics['snr'])
    RADIO_NOISE.labels(id=metrics['id']).set(metrics['noise'])

async def _handle_stream(stream: asyncio.streams.StreamReader, function: Callable[[str], None]):
    while True:
        await asyncio.sleep(0)
        data = await stream.readline()
        if data:
            line = data.decode('utf8')
            asyncio.create_task(function(line))

async def radio_log(message):
    message = message.strip()
    logging.info(f'radio: {message}')

async def looper():
    cmd = f'rtl_433 -d "{FLAGS.device}" -f 433.55e6 -R 36 -M level -F json -v'
    logging.info(f'Starting radio: {cmd}')
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stderr=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE
    )

    asyncio.create_task(_handle_stream(proc.stdout, process_metrics))
    asyncio.create_task(_handle_stream(proc.stderr, radio_log))

    await proc.wait()
    logging.error('Radio has exited, check your --device parameter!')
    while not proc.stderr.at_eof():
        data = await proc.stdout.readline()
        if data:
            logging.error(data)



# Wrap asyncio.run for easy compatibilty with absl.app
def main(argv):
    del argv

    start_http_server(FLAGS.port)
    logging.info(f'Serving metrics at :{FLAGS.port}/metrics')
    asyncio.run(looper())



# script endpoint installed by package
def run():
    app.run(main)


if __name__ == '__main__':
    run()



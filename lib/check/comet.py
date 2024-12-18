from asyncsnmplib.mib.mib_index import MIB_INDEX
from libprobe.asset import Asset
from libprobe.exceptions import CheckException
from ..snmpclient import get_snmp_client
from ..snmpquery import snmpquery
from ..utils import to_float

channels_oid = (1, 3, 6, 1, 4, 1, 22626, 1, 5, 2)

# get channel1
channel1 = MIB_INDEX[(*channels_oid, 1)]

# use that as channel5 which is not present in mib
MIB_INDEX[(*channels_oid, 5)] = channel1
MIB_INDEX['P8641-MIB']['channel5'] = (*channels_oid, 5)

for idx in range(1, 13):
    # get obj for each metric (1-12)
    obj = MIB_INDEX[(*channels_oid, 1, idx)]
    # remove channel_id from the metric name
    obj['name'] = obj['name'][:2] + obj['name'][3:]
    for ch_idx in range(2, 6):
        # use that object for the other channels (2-5)
        MIB_INDEX[(*channels_oid, ch_idx, idx)] = obj


CHANNEL_ALARM_LU = {
    0: 'No alarm',
    1: 'Alarm High',
    2: 'Alarm Low',
}


QUERIES = (
    MIB_INDEX['P8641-MIB']['global'],

    MIB_INDEX['P8641-MIB']['channel1'],
    MIB_INDEX['P8641-MIB']['channel2'],
    MIB_INDEX['P8641-MIB']['channel3'],
    MIB_INDEX['P8641-MIB']['channel4'],
    MIB_INDEX['P8641-MIB']['channel5'],
)


def on_channel(item: dict) -> dict:
    unit = item['chUnit']
    return {
        'name': item['chName'],  # str
        'val': to_float(item['chVal'], unit),
        'alarm': CHANNEL_ALARM_LU.get(item['chAlarm']),
        'limHi': to_float(item['chLimHi'], unit, 0.1),
        'limLo': to_float(item['chLimLo'], unit, 0.1),
        'limHyst': to_float(item['chLimHyst'], unit, 0.1),
        'limDelay': item['chLimDelay'],  # int
        'alarmStr': item['chAlarmStr'],  # str
        'min': to_float(item['chMin'], unit),
        'max': to_float(item['chMax'], unit),
    }


async def check_comet(
        asset: Asset,
        asset_config: dict,
        check_config: dict) -> dict:

    snmp = get_snmp_client(asset, asset_config, check_config)
    state = await snmpquery(snmp, QUERIES)

    globl = state.pop('global', [])

    temperature = [
        on_channel(i)
        for v in state.values()
        for i in v
        if i['chUnit'] in ('°C', '°F')]
    humidity = [
        on_channel(i)
        for v in state.values()
        for i in v
        if i['chUnit'] == '%RH'
    ]

    return {
        'global': globl,
        'temperature': temperature,
        'humidity': humidity,
    }

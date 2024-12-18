from asyncsnmplib.mib.mib_index import MIB_INDEX
from libprobe.asset import Asset
from libprobe.exceptions import IncompleteResultException
from ..snmpclient import get_snmp_client
from ..snmpquery import snmpquery
from ..utils import to_float


CHANNEL_ALARM_LU = {
    0: 'No alarm',
    1: 'Alarm High',
    2: 'Alarm Low',
}


QUERIES = (
    MIB_INDEX['P8641-MIB']['global'],
    MIB_INDEX['P8641-MIB']['channel1'],
)


def on_channel(item: dict) -> dict:
    unit = item['ch1Unit']
    return {
        'name': item['chName'],  # str
        'val': to_float(item['ch1Val'], unit),
        'alarm': CHANNEL_ALARM_LU.get(item['ch1Alarm']),
        'limHi': to_float(item['ch1LimHi'], unit, 0.1),
        'limLo': to_float(item['ch1LimLo'], unit, 0.1),
        'limHyst': to_float(item['ch1LimHyst'], unit, 0.1),
        'limDelay': item['ch1LimDelay'],  # int
        'alarmStr': item['ch1AlarmStr'],  # str
        'min': to_float(item['ch1Min'], unit),
        'max': to_float(item['ch1Max'], unit),
    }


async def check_comet(
        asset: Asset,
        asset_config: dict,
        check_config: dict) -> dict:

    snmp = get_snmp_client(asset, asset_config, check_config)
    state = await snmpquery(snmp, QUERIES)

    globl = state.pop('global', [])

    unknown = None
    temperature = []
    humidity = []

    channel1 = state.pop('channel1', [])
    if channel1:
        # single item
        item = state['channel1'][0]
        unit = item['ch1Unit']

        if unit in ('C', 'F'):
            temperature.append(on_channel(item))
        elif unit == '%RH':
            humidity.append(on_channel(item))
        elif unit not in ('', None):
            unknown = unit

    state = {
        'global': globl,
        'temperature': temperature,
        'humidity': humidity,
    }

    if unknown:
        raise IncompleteResultException(
            f'Unknown sensor unit: {unknown}',
            result=state)

    return state

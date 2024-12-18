import logging
from asyncsnmplib.mib.mib_index import MIB_INDEX
from asyncsnmplib.mib.syntax_funs import SYNTAX_FUNS
from libprobe.asset import Asset
from libprobe.exceptions import IncompleteResultException
from ..snmpclient import get_snmp_client
from ..snmpquery import snmpquery
from ..utils import to_float


def decode_display_string(inp: bytes):
    try:
        return inp.decode()
    except UnicodeDecodeError:
        try:
            return inp.decode('latin-1')
        except Exception:
            return


# add function to syntax function lookup
SYNTAX_FUNS['DisplayString_latin1'] = decode_display_string

# patch the mib index to use that syntax function
MIB_INDEX[MIB_INDEX['P8641-MIB']['ch1Unit']]['syntax'] = {
    'tp': 'CUSTOM', 'func': 'DisplayString_latin1',
}
MIB_INDEX[MIB_INDEX['P8641-MIB']['ch2Unit']]['syntax'] = {
    'tp': 'CUSTOM', 'func': 'DisplayString_latin1',
}
MIB_INDEX[MIB_INDEX['P8641-MIB']['ch3Unit']]['syntax'] = {
    'tp': 'CUSTOM', 'func': 'DisplayString_latin1',
}
MIB_INDEX[MIB_INDEX['P8641-MIB']['ch4Unit']]['syntax'] = {
    'tp': 'CUSTOM', 'func': 'DisplayString_latin1',
}

# TODO
# OR patch all DisplayString syntax funs
# SYNTAX_FUNS['DisplayString'] = decode_display_string

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
)


def on_channel(item: dict, cid: int) -> dict:
    unit = item[f'ch{cid}Unit']
    return {
        'name': item[f'ch{cid}Name'],  # str
        'val': to_float(item[f'ch{cid}Val'], unit),
        'alarm': CHANNEL_ALARM_LU.get(item[f'ch{cid}Alarm']),
        'limHi': to_float(item[f'ch{cid}LimHi'], unit, 0.1),
        'limLo': to_float(item[f'ch{cid}LimLo'], unit, 0.1),
        'limHyst': to_float(item[f'ch{cid}LimHyst'], unit, 0.1),
        'limDelay': item[f'ch{cid}LimDelay'],  # int
        'alarmStr': item[f'ch{cid}AlarmStr'],  # str
        'min': to_float(item[f'ch{cid}Min'], unit),
        'max': to_float(item[f'ch{cid}Max'], unit),
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

    for cid in range(1, 5):
        channel = state.pop(f'channel{cid}', None)
        if channel:
            # single item
            item = channel[0]
            unit = item[f'ch{cid}Unit']

            if unit in ('°C', '°F'):
                temperature.append(on_channel(item, cid))
            elif unit == '%RH':
                humidity.append(on_channel(item, cid))
            elif unit not in ('', None):
                unknown = unit
            else:
                name = item[f'ch{cid}Name']
                logging.debug(f'No unit for item: {name}')
        else:
            logging.debug(f'Channel {cid} missing or empty in state: {state}')

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

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


QUERIES = (
    MIB_INDEX['P8641-MIB']['global'],

    MIB_INDEX['P8641-MIB']['channel1'],
    MIB_INDEX['P8641-MIB']['channel2'],
    MIB_INDEX['P8641-MIB']['channel3'],
    MIB_INDEX['P8641-MIB']['channel4'],
    MIB_INDEX['P8641-MIB']['channel5'],
)


async def check_comet(
        asset: Asset,
        asset_config: dict,
        check_config: dict) -> dict:

    snmp = get_snmp_client(asset, asset_config, check_config)
    state = await snmpquery(snmp, QUERIES)

    globl = state.pop('global', [])

    # TODO not sure if this ever occurs
    # we could also use IncompleteResultException
    for k, v in state.items():
        if not len(v):
            raise CheckException(f'No metrics for channel `{k}`')

    channel = [{
        'name': k,
        **v[0],
        'chVal': to_float(v[0]['chVal']),
        'chMin': to_float(v[0]['chMin']),
        'chMax': to_float(v[0]['chMax']),
    }
        for k, v in state.items()
        if len(v)
    ]

    return {
        'global': globl,
        'channel': channel,
    }

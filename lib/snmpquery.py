import logging
from asyncsnmplib.client import Snmp, SnmpV1, SnmpV3
from asyncsnmplib.exceptions import SnmpNoAuthParams, SnmpNoConnection
from asyncsnmplib.mib.utils import on_result, on_result_base
from libprobe.exceptions import CheckException
from typing import Union, Tuple, Dict, List, Any


async def snmpquery(
    client: Union[Snmp, SnmpV1, SnmpV3],
    oids: Tuple[Tuple[int], ...],
    strip_metric_prefix: bool = False,
) -> Dict[str, List[Dict[str, Any]]]:
    '''Snmpwalk operation on the given oids

    Args:
        client:
            Snmp client
        oids:
            Tuple of oids to query
        strip_metric_prefix (bool, optional):
            Strip metric prefixes i.e. ipAddressOrigin -> Origin
            Defaults to False

    Returns:
        List of results grouped by name of the root oid
    '''
    _on_result = on_result if strip_metric_prefix else on_result_base

    try:
        await client.connect()
    except SnmpNoConnection:
        raise
    except SnmpNoAuthParams:
        logging.warning('unable to connect: failed to set auth params')
        raise
    else:
        results = {}
        for oid in oids:
            result = await client.walk(oid)
            try:
                name, result = _on_result(oid, result)
            except Exception as e:
                msg = str(e) or type(e).__name__
                raise CheckException(
                    f'Failed to parse result. Exception: {msg}')
            else:
                results[name] = result
        return results
    finally:
        # safe to close whatever the connection status is
        client.close()

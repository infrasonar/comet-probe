import logging
from asyncsnmplib.client import Snmp, SnmpV1, SnmpV3
from asyncsnmplib.v3.auth import AUTH_PROTO
from asyncsnmplib.v3.encr import PRIV_PROTO
from libprobe.asset import Asset
from libprobe.exceptions import CheckException
from typing import Union
from . import DOCS_URL


class SnmpInvalidConfig(Exception):
    pass


def get_snmp_client(
        asset: Asset,
        asset_config: dict,
        check_config: dict) -> Union[Snmp, SnmpV1, SnmpV3]:
    address = check_config.get('address')
    if not address:
        address = asset.name

    version = asset_config.get('version', '2c')

    try:
        if version == '2c':
            community = asset_config.get('community', 'public')
            if isinstance(community, dict):
                community = community.get('secret')
            if not isinstance(community, str):
                raise SnmpInvalidConfig('`community` must be a string.')
            cl = Snmp(
                host=address,
                community=community,
            )
        elif version == '3':
            username = asset_config.get('username')
            if not isinstance(username, str):
                raise SnmpInvalidConfig('`username` must be a string.')
            auth = asset_config.get('auth')
            if auth:
                auth_proto = AUTH_PROTO.get(auth.get('type'))
                auth_passwd = auth.get('password')
                if auth_proto is None:
                    raise SnmpInvalidConfig('`auth.type` invalid')
                elif not isinstance(auth_passwd, str):
                    raise SnmpInvalidConfig('`auth.password` must be string')
                auth = (auth_proto, auth_passwd)
            priv = auth and asset_config.get('priv')
            if priv:
                priv_proto = PRIV_PROTO.get(priv.get('type'))
                priv_passwd = priv.get('password')
                if priv_proto is None:
                    raise SnmpInvalidConfig('`priv.type` invalid')
                elif not isinstance(priv_passwd, str):
                    raise SnmpInvalidConfig('`priv.password` must be string')
                priv = (priv_proto, priv_passwd)
            cl = SnmpV3(
                host=address,
                username=username,
                auth=auth,
                priv=priv,
            )
        elif version == '1':
            community = asset_config.get('community', 'public')
            if isinstance(community, dict):
                community = community.get('secret')
            if not isinstance(community, str):
                raise SnmpInvalidConfig('`community` must be a string.')
            cl = SnmpV1(
                host=address,
                community=community,
            )
        else:
            raise SnmpInvalidConfig(f'unsupported snmp version {version}')
    except SnmpInvalidConfig as e:
        msg = str(e) or type(e).__name__
        logging.error(f'Invalid config. Exception: {msg}')
        raise CheckException(
            'Invalid config. Please refer to the following documentation'
            f' for detailed instructions: <{DOCS_URL}>')

    return cl

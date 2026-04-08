import ipaddress
from functools import lru_cache


_CGNAT_NETWORK = ipaddress.ip_network("100.64.0.0/10")


@lru_cache(maxsize=512)
def is_internal_proxy_ip(ip_address: str) -> bool:
    if not ip_address:
        return False

    try:
        parsed_ip = ipaddress.ip_address(ip_address)
    except ValueError:
        return False

    return (
        parsed_ip in _CGNAT_NETWORK
        or parsed_ip.is_private
        or parsed_ip.is_loopback
        or parsed_ip.is_link_local
        or parsed_ip.is_reserved
    )

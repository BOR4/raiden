import json

import networkx
from eth_utils import to_bytes, to_canonical_address, to_checksum_address, to_hex

from raiden.transfer.merkle_tree import LEAVES, compute_layers
from raiden.utils.typing import Address, Callable, Dict, List, Tuple, TypeVar

T = TypeVar('T')
RT = TypeVar('RT')

KT = TypeVar('KT')
VT = TypeVar('VT')
KRT = TypeVar('KRT')
VRT = TypeVar('VRT')


def identity(val: T) -> T:
    return val


def map_dict(
        key_func: Callable[[KT], KRT],
        value_func: Callable[[VT], VRT],
        dict_: Dict[KT, VT],
) -> Dict[KRT, VRT]:
    return {
        key_func(k): value_func(v)
        for k, v in dict_.items()
    }


def map_list(
        value_func: Callable[[VT], RT],
        list_: List[VT],
) -> List[RT]:
    return [
        value_func(v)
        for v in list_
    ]


def serialize_bytes(data: bytes) -> str:
    return to_hex(data)


def deserialize_bytes(data: str) -> bytes:
    return to_bytes(hexstr=data)


def serialize_networkx_graph(graph: networkx.Graph) -> str:
    return json.dumps([
        (to_checksum_address(edge[0]), to_checksum_address(edge[1]))
        for edge in graph.edges
    ])


def deserialize_networkx_graph(data: str) -> networkx.Graph:
    raw_data = json.loads(data)
    canonical_addresses = [
        (to_canonical_address(edge[0]), to_canonical_address(edge[1]))
        for edge in raw_data
    ]
    return networkx.Graph(canonical_addresses)


def serialize_participants_tuple(
        participants: Tuple[Address, Address],
) -> List[str]:
    return [
        to_checksum_address(participants[0]),
        to_checksum_address(participants[1]),
    ]


def deserialize_participants_tuple(
        data: List[str],
) -> Tuple[Address, Address]:
    assert len(data) == 2
    return (
        to_canonical_address(data[0]),
        to_canonical_address(data[1]),
    )


def serialize_merkletree_layers(data) -> List[str]:
    return map_list(serialize_bytes, data[LEAVES])


def deserialize_merkletree_layers(data: List[str]):
    elements = map_list(deserialize_bytes, data)
    if len(elements) == 0:
        from raiden.transfer.state import make_empty_merkle_tree
        return make_empty_merkle_tree().layers

    return compute_layers(elements)


def serialize_queueid_to_queue(data: Dict):
    # QueueId cannot be the key in a JSON dict, so make it a str
    return {
        str(queue_id): (queue_id, queue)
        for queue_id, queue in data.items()
    }


def deserialize_queueid_to_queue(data: Dict):
    return {
        queue_id: queue
        for queue_id, queue in data.values()
    }

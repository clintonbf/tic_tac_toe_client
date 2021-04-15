import socket
from metadata import *


def get_message(s: socket) -> dict:
    f"""
    Gets a message from the server.

    :param s: {socket} TCP socket
    :return: {dict} the header and payload data
    """
    header = get_header(s)

    payload_length = header["payload_length"]

    if payload_length != 0:
        payload = get_payload(s, header)
    else:
        payload = {"payload": None}

    message = {'header': header, 'payload': payload}

    return message


def get_header(s: socket) -> dict:
    f"""
    Gets the header from a TCP packet.

    :param s: {socket} TCP socket
    :return: {dict} details of the packet header
    """
    msg_type = int.from_bytes(s.recv(1), 'big')
    msg_context = int.from_bytes(s.recv(1), 'big')
    payload_length = int.from_bytes(s.recv(1), 'big')

    header = {"msg_type": msg_type, "context": msg_context, "payload_length": payload_length}

    return header


def get_payload(s: socket, header: dict) -> list:
    f"""
    Gets the payload from a server.

    :param s: {socket} TCP socket 
    :param header: {dict} the packet header 
    :return: {list} the payload message
    """

    payload = []

    for i in range(0, header['payload_length']):
        payload.append(int.from_bytes(s.recv(1), 'big'))

    return payload


def handshake(s: socket, game_id: int) -> int:
    f"""
    Sends the handshake for rps.

    :param game_id: {int}
    :param s: {socket}  
    :return: {int} uid of player
    """
    # Start with 4 'empty' bytes
    empty_byte = 0
    confirmation = 1
    rule_set = 1
    payload_length = 2
    protocol_version = 1

    packet = [empty_byte, empty_byte, empty_byte, empty_byte, confirmation, rule_set, payload_length,
              protocol_version, game_id]

    s.sendall(bytes(packet))

    uid = get_uid(s)

    return uid


def get_uid(s: socket) -> int:
    f"""
    Gets the player's uid from the server.

    :param s: {socket} TCP socket connection 
    :return: {int}
    """

    # header = s.recv(2)  # Will this receive into a list of 2?
    msg_type = int.from_bytes(s.recv(1), 'big')
    msg_context = int.from_bytes(s.recv(1), 'big')
    payload_length = int.from_bytes(s.recv(1), 'big')
    uid = int.from_bytes(s.recv(payload_length), ENDIANNESS)

    if msg_type == 32:
        msg_code = uid
        print(STATUS_MESSAGES[msg_code])
        exit(1)

    return uid

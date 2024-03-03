
import binascii
from typing_extensions import Self

def mac_to_bytes(mac_address):
    return binascii.unhexlify(mac_address.replace(':', ''))


class Frame:

    def __init__(self, subtype):
        self.header_revision =  b'\x00'
        self.header_pad =       b'\x00'
        self.header_length =    b'\x0d\x00'
        self.flags =            b'\x00\x00\x00\x00'
        self.data_rate =        b'\x00\x00'
        self.tx_flags =         b'\x00\x00'
        self.data_retries =     b'\x00'
        self.subtype =          subtype.to_bytes(2, byteorder='little')
        self.duration =         b'\x00\x00'
        self.receiver_mac =     None
        self.transmitter_mac =  None
        self.sequence_num =     b'\x00\x00'
        self.reason =           None
    def set_reason(self, reason_code):
        self.reason = reason_code.to_bytes(2, byteorder='little')

    def set_receiver(self, rec_mac="ff:ff:ff:ff:ff:ff"):
        self.receiver_mac = mac_to_bytes(rec_mac)
    
    def set_transmiter(self, trans_mac):
        self.transmitter_mac = mac_to_bytes(trans_mac)

    def get_raw_bytes(self):
        return self.header_revision + \
        self.header_pad + \
        self.header_length + \
        self.flags + \
        self.data_rate + \
        self.tx_flags + \
        self.data_retries + \
        self.subtype + \
        self.duration + \
        self.receiver_mac + \
        self.transmitter_mac + \
        self.transmitter_mac + \
        self.sequence_num + \
        self.reason

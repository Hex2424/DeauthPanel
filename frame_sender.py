import frame
from scapy.all import *


class FrameEngine:
    def init_deauth(self, mac_sender, mac_receiver):
        self.deauth_frame = frame.Frame(192)
        self.deauth_frame.set_receiver(mac_receiver)
        self.deauth_frame.set_transmiter(mac_sender)
        self.deauth_frame.set_reason(7)

    def __init__(self):
        pass

    def send_deauth(self, interface):
        sendp(self.deauth_frame.get_raw_bytes(), iface=interface, verbose=0)

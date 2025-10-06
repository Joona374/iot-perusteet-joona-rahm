# dyiumqtt.py
import usocket as socket
import ustruct as struct
import uselect as select
import utime
import machine
import json

from oled_control import oled


class MQTTClient:
    def __init__(self, callback, client_id=None, server="test.mosquitto.org", port=1883,
                 keepalive_s=60, ping_margin_s=25):
        if client_id is None:
            uid = machine.unique_id()
            # ascii-safe, short, deterministic id
            client_id = "pico-" + "".join("{:02x}".format(b) for b in uid)
        self.client_id = client_id
        self.server = server
        self.port = port
        self.sock = None
        self._cb = None
        self.set_callback(callback)

    def set_callback(self, cb):
        """cb(topic_bytes, msg_bytes)"""
        self._cb = cb

    def _is_online(self):
        return self.sock is not None

    def _safe_send(self, b):
        if not self._is_online():
            raise OSError("MQTT offline")
        self.sock.send(b)

    def ping(self):
        try:
            self._safe_send(b"\xC0\x00")
        except Exception as e:
            print("Error while pinging MQTT:", e)
            self._reconnect_with_backoff()

    def loop(self):
        # process inbound (including PINGRESP)
        self.check_msg()
        # proactively ping (your 5s timer will call ping(); that’s fine)

    def _reconnect_with_backoff(self):
        print("Reconnecting")
        oled.clear_screen()
        oled.write_row("Lost Connection")
        oled.write_row("Reconnecting....")
        self.disconnect()
        utime.sleep_ms(500)  # brief backoff (public broker friendly)
        try:
            self.connect()
        except Exception as e:
            print("Reconnect failed:", e)
            # Leave it to next loop/next call to try again.

    def connect(self):
        oled.clear_screen()
        oled.write_row("Connecting MQTT...")

        addr = socket.getaddrinfo(self.server, self.port)[0][-1]
        s = socket.socket()
        s.connect(addr)
        s.settimeout(8)
        self.sock = s
        oled.write_row("TCP connected")

        var_header = b"\x00\x04MQTT\x04\x02" + struct.pack("!H", 60)
        cid = self.client_id.encode()
        payload = struct.pack("!H", len(cid)) + cid
        rem_len = len(var_header) + len(payload)
        if rem_len >= 128:
            # encode Remaining Length as MQTT varint if you ever cross 127
            raise ValueError("Remaining length >=128: add varint encoding")
        pkt = b"\x10" + bytes([rem_len]) + var_header + payload  # (ok for <128)

        oled.write_row("Sending CONNECT")
        self.sock.send(pkt)

        try:
            resp = self.sock.recv(4)        # CONNACK
        except OSError as e:
            # slow network → try again later instead of hard crash
            print("CONNACK wait timed out:", e)
            self.disconnect()
            raise

        if len(resp) != 4 or resp[0] != 0x20 or resp[3] != 0x00:
            self.disconnect()
            raise OSError("Bad CONNACK")

        oled.write_row("MQTT connected!")

    def publish(self, topic, msg_type, param=None):
        try:
            if not self._is_online():
                # drop or queue – your choice; for temps dropping is fine
                return

            payload = {
            "type": msg_type,
            "param": param
            }
            msg_str = json.dumps(payload)

            topic_bytes = topic.encode()
            msg_bytes = msg_str.encode()
            
            remaining_length = 2 + len(topic_bytes) + len(msg_bytes)
            packet = bytearray(b"\x30")  # PUBLISH header
            packet += bytes([remaining_length])
            packet += bytes([0, len(topic_bytes)]) + topic_bytes + msg_bytes
            self._safe_send(packet)

        except Exception as e:
            print("Error publishing:", e)
            self._reconnect_with_backoff()

    def subscribe(self, topic):
        """QoS0 subscribe; assumes remaining length < 128"""
        topic_b = topic if isinstance(topic, bytes) else topic.encode()
        pkt_id = 1
        payload = struct.pack("!H", len(topic_b)) + topic_b + b"\x00"  # QoS 0
        var_header = struct.pack("!H", pkt_id)
        remaining = len(var_header) + len(payload)

        pkt = bytearray(b"\x82")                # SUBSCRIBE
        pkt += bytes([remaining])               # single-byte remaining length
        pkt += var_header + payload
        self.sock.send(pkt)

        # Minimal SUBACK read (ignore contents)
        if self.sock.recv(1) != b"\x90":        # SUBACK header
            raise OSError("SUBACK not received")
        rl = self.sock.recv(1)[0]               # remaining length
        _ = self.sock.recv(rl)                  # discard


    def _recv_exact(self, n):
        """Non-blocking: try to read exactly n bytes. Return bytes or None if incomplete."""
        buf = bytearray()
        while len(buf) < n:
            try:
                chunk = self.sock.recv(n - len(buf))
                if chunk is None or chunk == b"":
                    # peer closed or would-block
                    return None
                buf.extend(chunk)
            except OSError:
                return None  # would block
        return bytes(buf)

    def _read_varlen(self):
        """Non-blocking MQTT varint. Return (value, consumed_bytes) or (None, 0) if incomplete."""
        val = 0
        mul = 1
        consumed = 0
        while True:
            try:
                b = self.sock.recv(1)
                if not b:
                    return (None, 0)
                consumed += 1
                byte = b[0]
                val += (byte & 0x7F) * mul
                if (byte & 0x80) == 0:
                    return (val, consumed)
                mul *= 128
                if mul > (128**4):
                    return (None, 0)  # malformed
            except OSError:
                return (None, 0)

    def check_msg(self):
        if not self.sock:
            return

        # Is there anything to read?
        try:
            r, _, _ = select.select([self.sock], [], [], 0)
        except Exception:
            self._reconnect_with_backoff()
            return
        if not r:
            return

        # Parse one MQTT control packet, non-blocking
        self.sock.settimeout(0)
        try:
            first = self.sock.recv(1)
            if not first:
                self._reconnect_with_backoff()
                return
        except OSError:
            self._reconnect_with_backoff()
            return

        packet_type = first[0] & 0xF0

        # Remaining length (varint)
        rl, _ = self._read_varlen()
        if rl is None:
            return  # wait for more bytes

        # Handle QoS 0 PUBLISH
        if packet_type == 0x30:
            hdr = self._recv_exact(2)
            if hdr is None:
                return
            tlen = struct.unpack("!H", hdr)[0]

            topic = self._recv_exact(tlen)
            if topic is None:
                return

            payload_len = rl - 2 - tlen
            if payload_len < 0:
                return

            msg = self._recv_exact(payload_len)
            if msg is None:
                return

            # Debug line so you see traffic immediately
            try:
                t = topic.decode()
                m = msg.decode()
            except Exception:
                t, m = str(topic), str(msg)

            # print("MQTT <--", t, m)

            if self._cb:
                try:
                    self._cb(t, m)
                except Exception as e:
                    print("Callback error:", e)
            return

        # Drain other control packets (e.g., PINGRESP 0xD0, SUBACK 0x90, etc.)
        _ = self._recv_exact(rl)
        # Optional debug:
        # print("MQTT ctl:", hex(packet_type), "len", rl)
        return

    def disconnect(self):
        try:
            if self.sock:
                try: self.sock.send(b"\xE0\x00")
                except: pass
                try: self.sock.close()
                except: pass
        finally:
            self.sock = None
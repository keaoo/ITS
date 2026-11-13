#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UDS Data Logger Tool
Based on UDS $22 service (ReadDataByIdentifier)
"""

import time
import struct
import pickle
import csv
from datetime import datetime
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass, field
from threading import Thread, Event

from .doip_client import DoIPClient, DoIPConnectionError


# Configuration
ICB_DOIP_IP = "172.31.6.11"
ICB_DOIP_PORT = 13400
TESTER_LOGICAL_ADDR = 0x0E80

ECU_ADDRESSES = {
    "CCU": 0x1000,
    "ICB": 0x1000,
    "LHZCU": 0x15B0,
    "RHZCU": 0x15B1,
    "EPS": 0x1035,
    "BMS": 0x1044,
}

DEFAULT_DID_LIST = ["B000", "B015", "B016", "B020", "B021"]


# Exceptions
class UDSDataLoggerError(Exception):
    pass

class UDSCommunicationError(UDSDataLoggerError):
    pass

class DIDConfigError(UDSDataLoggerError):
    pass


# Data Structures
@dataclass
class DIDInfo:
    did_id: str
    name: str
    unit: str
    byte: int
    bit: int
    length: int
    factor: float
    offset: float
    minimum: float
    maximum: float
    signed: bool = False
    enum: Dict[int, str] = field(default_factory=dict)


@dataclass
class SampleData:
    timestamp: float
    datetime_str: str
    did_id: str
    name: str
    raw_value: int
    physical_value: float
    unit: str
    status: str = "OK"
    nrc_code: int = 0


# Main Class
class UDSDataLogger:
    def __init__(self, ecu: str = "CCU", ip: str = ICB_DOIP_IP,
                 port: int = ICB_DOIP_PORT, did_config_path: str = None):
        self.ecu = ecu
        self.ip = ip
        self.port = port
        self.target_addr = ECU_ADDRESSES.get(ecu, 0x1000)

        self.did_config: Dict[str, DIDInfo] = {}
        if did_config_path:
            self.load_did_config(did_config_path)

        self.doip = DoIPClient(
            ip=ip, port=port,
            source_addr=TESTER_LOGICAL_ADDR,
            routing_ta=0x0010,
            timeout=5.0
        )

        self._logging = False
        self._log_thread: Optional[Thread] = None
        self._stop_event = Event()
        self._data_buffer: List[SampleData] = []
        self._callback: Optional[Callable] = None
        self._session_active = False
        self._did_list: List[str] = []
        self._interval: float = 1.0

    def load_did_config(self, config_path: str):
        try:
            with open(config_path, 'rb') as f:
                raw_config = pickle.load(f)

            if isinstance(raw_config, dict):
                ecu_data = raw_config.get(self.ecu, {})
                for did_id, did_data in ecu_data.items():
                    self.did_config[did_id] = DIDInfo(
                        did_id=did_id,
                        name=did_data.get('name', ''),
                        unit=did_data.get('unit', ''),
                        byte=did_data.get('byte', 1),
                        bit=did_data.get('bit', 0),
                        length=did_data.get('length', 8),
                        factor=did_data.get('factor', 1.0),
                        offset=did_data.get('offset', 0.0),
                        minimum=did_data.get('minimum', 0.0),
                        maximum=did_data.get('maximum', 65535.0),
                        signed=did_data.get('signed', False),
                        enum=did_data.get('enum', {})
                    )
            print(f"[INFO] Loaded {len(self.did_config)} DID configs ({self.ecu})")
        except Exception as e:
            print(f"[WARN] Failed to load DID config: {e}")

    def connect(self) -> bool:
        try:
            print(f"[INFO] Connecting to {self.ecu} ({self.ip}:{self.port})...")
            self.doip.connect()
            self.doip.routing_activate()
            self._session_active = True
            print(f"[INFO] Connected, target: 0x{self.target_addr:04X}")
            return True
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            return False

    def disconnect(self):
        self.stop_logging()
        self._session_active = False
        self.doip.disconnect()
        print(f"[INFO] Disconnected")

    def _send_uds(self, data: bytes, timeout: float = 2.0) -> Optional[bytes]:
        if not self._session_active:
            raise UDSCommunicationError("Session not active")

        try:
            response = self.doip.send_diagnostic(
                data, target_addr=self.target_addr, timeout=timeout
            )
            return response
        except Exception as e:
            raise UDSCommunicationError(f"UDS communication failed: {e}")

    def read_did(self, did_id: str) -> Optional[SampleData]:
        try:
            did_bytes = bytes.fromhex(did_id)
        except ValueError:
            print(f"[ERROR] Invalid DID ID: {did_id}")
            return None

        request = bytes([0x22]) + did_bytes

        try:
            response = self._send_uds(request, timeout=2.0)

            if not response:
                print(f"[ERROR] No response (DID={did_id})")
                return None

            if response[0] == 0x7F:
                nrc = response[2] if len(response) > 2 else 0
                print(f"[ERROR] NRC 0x{nrc:02X} (DID={did_id})")
                return SampleData(
                    timestamp=time.time(),
                    datetime_str=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                    did_id=did_id,
                    name=self.did_config.get(did_id, DIDInfo(did_id, "", "", 1, 0, 8, 1, 0, 0, 65535)).name,
                    raw_value=0,
                    physical_value=0,
                    unit="",
                    status=f"NRC_{nrc:02X}",
                    nrc_code=nrc
                )

            if response[0] == 0x62 and response[1:3] == did_bytes:
                data_bytes = response[3:]
                raw_value = int.from_bytes(data_bytes, byteorder='big')

                did_info = self.did_config.get(did_id)

                if did_info:
                    physical_value = raw_value * did_info.factor + did_info.offset

                    if did_info.enum and raw_value in did_info.enum:
                        return SampleData(
                            timestamp=time.time(),
                            datetime_str=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                            did_id=did_id,
                            name=did_info.name,
                            raw_value=raw_value,
                            physical_value=did_info.enum[raw_value],
                            unit="",
                            status="OK"
                        )

                    unit = did_info.unit
                    name = did_info.name
                else:
                    physical_value = raw_value
                    unit = ""
                    name = ""

                return SampleData(
                    timestamp=time.time(),
                    datetime_str=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                    did_id=did_id,
                    name=name,
                    raw_value=raw_value,
                    physical_value=physical_value,
                    unit=unit,
                    status="OK"
                )
            else:
                print(f"[ERROR] Unknown response: {response.hex()}")
                return None

        except UDSCommunicationError as e:
            print(f"[ERROR] {e}")
            return None

    def read_did_batch(self, did_list: List[str]) -> List[SampleData]:
        results = []
        for did_id in did_list:
            result = self.read_did(did_id)
            if result:
                results.append(result)
            time.sleep(0.1)
        return results

    def start_logging(self, did_list: List[str] = None, interval: float = 1.0,
                      callback: Callable = None):
        if self._logging:
            print("[WARN] Already logging")
            return

        self._did_list = did_list or DEFAULT_DID_LIST
        self._interval = interval
        self._callback = callback
        self._data_buffer = []
        self._stop_event.clear()
        self._logging = True

        self._log_thread = Thread(target=self._logging_loop, daemon=True)
        self._log_thread.start()
        print(f"[INFO] Start logging: {len(self._did_list)} DIDs, interval {interval}s")

    def stop_logging(self):
        if not self._logging:
            return

        self._logging = False
        self._stop_event.set()
        if self._log_thread:
            self._log_thread.join(timeout=2.0)
            self._log_thread = None
        print(f"[INFO] Stop logging, {len(self._data_buffer)} samples collected")

    def _logging_loop(self):
        while not self._stop_event.is_set():
            start_time = time.time()

            results = self.read_did_batch(self._did_list)
            self._data_buffer.extend(results)

            if self._callback and results:
                try:
                    self._callback(results)
                except Exception as e:
                    print(f"[WARN] Callback error: {e}")

            elapsed = time.time() - start_time
            sleep_time = max(0, self._interval - elapsed)
            if sleep_time > 0:
                self._stop_event.wait(sleep_time)

    def get_data(self) -> List[SampleData]:
        return self._data_buffer.copy()

    def export_to_csv(self, filepath: str):
        if not self._data_buffer:
            print("[WARN] No data to export")
            return

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'DateTime', 'DID', 'Name', 'RawValue', 'Value', 'Unit', 'Status'])
            for row in self._data_buffer:
                writer.writerow([
                    row.timestamp, row.datetime_str, row.did_id, row.name,
                    row.raw_value, row.physical_value, row.unit, row.status
                ])

        print(f"[INFO] Exported {len(self._data_buffer)} samples to {filepath}")

    def export_to_excel(self, filepath: str):
        try:
            import openpyxl
        except ImportError:
            print("[ERROR] Need openpyxl: pip install openpyxl")
            return

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"{self.ecu}_Data"

        ws.append(['Timestamp', 'DateTime', 'DID', 'Name', 'RawValue', 'Value', 'Unit', 'Status'])

        for row in self._data_buffer:
            ws.append([
                row.timestamp, row.datetime_str, row.did_id, row.name,
                row.raw_value, row.physical_value, row.unit, row.status
            ])

        wb.save(filepath)
        print(f"[INFO] Exported {len(self._data_buffer)} samples to {filepath}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="UDS Data Logger")
    parser.add_argument("--ecu", default="CCU", help="ECU name")
    parser.add_argument("--did", nargs="+", help="DID list")
    parser.add_argument("--interval", type=float, default=1.0, help="Interval (s)")
    parser.add_argument("--duration", type=float, default=10.0, help="Duration (s)")
    parser.add_argument("--output", default="data.csv", help="Output file")
    parser.add_argument("--config", help="DID config path")

    args = parser.parse_args()

    logger = UDSDataLogger(ecu=args.ecu, did_config_path=args.config)

    if not logger.connect():
        exit(1)

    try:
        if args.did:
            print(f"\n[INFO] Single read test:")
            for did in args.did:
                result = logger.read_did(did)
                if result:
                    print(f"  {result.did_id}: {result.name} = {result.physical_value} {result.unit}")

        did_list = args.did or DEFAULT_DID_LIST
        print(f"\n[INFO] Logging for {args.duration}s...")
        logger.start_logging(did_list=did_list, interval=args.interval)

        time.sleep(args.duration)
        logger.stop_logging()
        logger.export_to_csv(args.output)

        print(f"\n[INFO] Done:")
        print(f"  Total samples: {len(logger.get_data())}")
        print(f"  Output: {args.output}")

    finally:
        logger.disconnect()

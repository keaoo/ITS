#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UDS Data Logger Quick Test
"""

import sys
import time

sys.path.insert(0, r"D:\Python-project\Project\ITS\Subpy")

from uds_data_logger import UDSDataLogger, SampleData


def test_single_read():
    print("=" * 60)
    print("Test 1: Single DID Read")
    print("=" * 60)

    logger = UDSDataLogger(ecu="CCU")

    if not logger.connect():
        print("[FAIL] Connection failed")
        return

    try:
        result = logger.read_did("B000")
        if result:
            print(f"[OK] {result.did_id}: {result.name} = {result.physical_value} {result.unit}")
            print(f"     Raw: 0x{result.raw_value:04X}, Status: {result.status}")
        else:
            print("[FAIL] Read failed")

        result = logger.read_did("B015")
        if result:
            print(f"[OK] {result.did_id}: {result.name} = {result.physical_value} {result.unit}")
        else:
            print("[FAIL] Read failed")

    finally:
        logger.disconnect()


def test_batch_read():
    print("\n" + "=" * 60)
    print("Test 2: Batch DID Read")
    print("=" * 60)

    logger = UDSDataLogger(ecu="CCU")

    if not logger.connect():
        print("[FAIL] Connection failed")
        return

    try:
        did_list = ["B000", "B015", "B020", "B021"]
        results = logger.read_did_batch(did_list)

        print(f"[OK] Read {len(results)} DIDs:")
        for r in results:
            if r.status == "OK":
                print(f"  {r.did_id}: {r.name} = {r.physical_value} {r.unit}")
            else:
                print(f"  {r.did_id}: {r.status}")

    finally:
        logger.disconnect()


def test_logging():
    print("\n" + "=" * 60)
    print("Test 3: Continuous Logging (5s)")
    print("=" * 60)

    logger = UDSDataLogger(ecu="CCU")

    if not logger.connect():
        print("[FAIL] Connection failed")
        return

    def on_data(results: list):
        latest = results[-1]
        print(f"  [{latest.datetime_str}] {latest.did_id}: {latest.physical_value} {latest.unit}")

    try:
        did_list = ["B000", "B015"]

        logger.start_logging(did_list=did_list, interval=0.5, callback=on_data)
        time.sleep(5)
        logger.stop_logging()

        data = logger.get_data()
        print(f"\n[OK] Logging complete:")
        print(f"  Total samples: {len(data)}")
        print(f"  Unique DIDs: {len(set(d.did_id for d in data))}")

        logger.export_to_csv("test_data.csv")

    finally:
        logger.disconnect()


def test_with_config():
    print("\n" + "=" * 60)
    print("Test 4: With DID Config File")
    print("=" * 60)

    config_path = r"D:\Python-project\Project\ITS\config\did"
    logger = UDSDataLogger(ecu="CCU", did_config_path=config_path)

    print(f"[INFO] Loaded {len(logger.did_config)} DID configs")

    if not logger.connect():
        print("[FAIL] Connection failed")
        return

    try:
        if "B000" in logger.did_config:
            info = logger.did_config["B000"]
            print(f"[INFO] DID B000 config:")
            print(f"  Name: {info.name}")
            print(f"  Unit: {info.unit}")
            print(f"  Range: {info.minimum} - {info.maximum}")
            print(f"  Factor: {info.factor}, Offset: {info.offset}")

        result = logger.read_did("B000")
        if result:
            print(f"\n[OK] Read result: {result.physical_value} {result.unit}")

    finally:
        logger.disconnect()


if __name__ == "__main__":
    print("UDS Data Logger - Quick Test")
    print("=" * 60)

    test_single_read()
    time.sleep(1)

    test_batch_read()
    time.sleep(1)

    test_logging()
    time.sleep(1)

    test_with_config()

    print("\n" + "=" * 60)
    print("All tests complete")
    print("=" * 60)

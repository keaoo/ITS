#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vehicle Data Collector - 车端数据采集上传一体化工具
===================================================
通过 UDS 采集车辆 ECU 数据，实时上传到云端服务器

功能:
  - UDS $22 服务读取 DID 数据
  - MQTT/HTTP 实时上传云端
  - 本地缓存 (断网续传)
  - 多 ECU 支持

服务器: 118.196.86.99
"""

import sys
import time
import argparse
from datetime import datetime

from .uds_data_logger import UDSDataLogger, SampleData
from .cloud_uploader import CloudUploader, CloudConfig, VehicleData


# ===================== 配置 =====================

DEFAULT_CONFIG = {
    "ecu": "CCU",
    "did_list": ["B000", "B015", "B020", "B021"],
    "upload_interval": 1.0,
    "server_ip": "118.196.86.99",
    "mqtt_port": 1883,
    "mqtt_topic": "vehicle/data/upload",
    "device_id": "vehicle_001",
    "upload_mode": "mqtt",  # mqtt / http / both
}


# ===================== 主程序 =====================

class VehicleDataCollector:
    """
    车辆数据采集上传一体化
    
    流程:
      1. 连接 ECU (通过 ICB DoIP 网关)
      2. 循环读取 DID 数据
      3. 打包上传到云端
      4. 本地缓存备份
    """
    
    def __init__(self, config: dict = None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        
        # UDS 采集器
        self.uds_logger = UDSDataLogger(
            ecu=self.config["ecu"],
            did_config_path=self.config.get("did_config")
        )
        
        # 云端上传器
        cloud_config = CloudConfig(
            server_ip=self.config["server_ip"],
            mqtt_port=self.config["mqtt_port"],
            mqtt_topic=self.config["mqtt_topic"],
            mqtt_client_id=self.config["device_id"],
            mqtt_username=self.config.get("mqtt_username", ""),
            mqtt_password=self.config.get("mqtt_password", ""),
            upload_interval=self.config["upload_interval"],
        )
        
        self.cloud_uploader = CloudUploader(
            config=cloud_config,
            upload_mode=self.config["upload_mode"]
        )
        
        # 统计
        self._stats = {
            "start_time": None,
            "upload_count": 0,
            "error_count": 0,
            "last_upload": None
        }
    
    def start(self, duration: float = None):
        """
        开始采集上传
        
        Args:
            duration: 运行时长 (秒)，None 表示持续运行
        """
        print("=" * 60)
        print("Vehicle Data Collector - 车端数据采集上传")
        print("=" * 60)
        print(f"ECU: {self.config['ecu']}")
        print(f"DIDs: {', '.join(self.config['did_list'])}")
        print(f"Server: {self.config['server_ip']}")
        print(f"Upload Mode: {self.config['upload_mode']}")
        print("=" * 60)
        
        # 连接 ECU
        print("\n[STEP 1] Connecting to ECU...")
        if not self.uds_logger.connect():
            print("[ERROR] ECU connection failed")
            return False
        
        # 连接云端
        print("\n[STEP 2] Connecting to cloud...")
        if not self.cloud_uploader.connect():
            print("[WARN] Cloud connection failed, will retry later")
        
        # 设置上传回调
        self.cloud_uploader.set_callback(self._on_upload)
        
        # 启动上传循环
        self.cloud_uploader.start_upload_loop()
        
        print("\n[STEP 3] Starting data collection...")
        self._stats["start_time"] = datetime.now()
        
        try:
            start_time = time.time()
            
            while True:
                # 读取 DID 数据
                results = self.uds_logger.read_did_batch(self.config["did_list"])
                
                if results:
                    # 打包为车辆数据
                    vehicle_data = VehicleData(
                        timestamp=time.time(),
                        datetime_str=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        device_id=self.config["device_id"],
                        ecu_type=self.config["ecu"],
                        data=[
                            {
                                "did": r.did_id,
                                "name": r.name,
                                "value": r.physical_value,
                                "unit": r.unit,
                                "raw_value": r.raw_value,
                                "status": r.status
                            }
                            for r in results
                        ]
                    )
                    
                    # 上传云端
                    self.cloud_uploader.upload_data(vehicle_data)
                    self._stats["upload_count"] += 1
                    self._stats["last_upload"] = datetime.now()
                    
                    # 显示进度
                    elapsed = time.time() - start_time
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"Uploaded {self._stats['upload_count']} batches, "
                          f"{len(results)} DIDs, "
                          f"Elapsed: {elapsed:.1f}s")
                
                else:
                    self._stats["error_count"] += 1
                    print(f"[WARN] Read failed, errors: {self._stats['error_count']}")
                
                # 检查时长
                if duration and (time.time() - start_time) >= duration:
                    break
                
                # 间隔
                time.sleep(self.config["upload_interval"])
        
        except KeyboardInterrupt:
            print("\n[INFO] Stopped by user")
        
        finally:
            self.stop()
        
        return True
    
    def stop(self):
        """停止采集上传"""
        print("\n[STOP] Stopping...")
        
        self.cloud_uploader.stop_upload_loop()
        self.cloud_uploader.disconnect()
        self.uds_logger.disconnect()
        
        # 显示统计
        self._print_stats()
    
    def _on_upload(self, mode: str, success: bool):
        """上传回调"""
        if success:
            pass  # 已在主循环显示
        else:
            print(f"[WARN] Upload failed via {mode}")
    
    def _print_stats(self):
        """打印统计信息"""
        print("\n" + "=" * 60)
        print("Collection Statistics")
        print("=" * 60)
        print(f"Start Time:  {self._stats['start_time']}")
        print(f"End Time:    {datetime.now()}")
        print(f"Uploads:     {self._stats['upload_count']} batches")
        print(f"Errors:      {self._stats['error_count']}")
        
        cloud_stats = self.cloud_uploader.get_stats()
        print(f"Cloud Uploaded: {cloud_stats['uploaded']}")
        print(f"Cloud Cached:   {cloud_stats['cache_size']}")
        print("=" * 60)


# ===================== 命令行 =====================

def main():
    parser = argparse.ArgumentParser(
        description="Vehicle Data Collector - UDS 采集 + 云端上传"
    )
    
    parser.add_argument("--ecu", default="CCU", help="ECU 名称")
    parser.add_argument("--did", nargs="+", help="DID 列表")
    parser.add_argument("--interval", type=float, default=1.0, help="采集间隔 (秒)")
    parser.add_argument("--duration", type=float, help="运行时长 (秒)")
    parser.add_argument("--server", default="118.196.86.99", help="服务器 IP")
    parser.add_argument("--mqtt-port", type=int, default=1883, help="MQTT 端口")
    parser.add_argument("--topic", default="vehicle/data/upload", help="MQTT Topic")
    parser.add_argument("--device-id", default="vehicle_001", help="设备 ID")
    parser.add_argument("--mode", default="mqtt", choices=["mqtt", "http", "both"],
                        help="上传模式")
    parser.add_argument("--config", help="配置文件路径 (JSON)")
    
    args = parser.parse_args()
    
    # 加载配置
    config = {
        "ecu": args.ecu,
        "did_list": args.did or DEFAULT_CONFIG["did_list"],
        "upload_interval": args.interval,
        "server_ip": args.server,
        "mqtt_port": args.mqtt_port,
        "mqtt_topic": args.topic,
        "device_id": args.device_id,
        "upload_mode": args.mode,
    }
    
    # 加载配置文件
    if args.config:
        import json
        with open(args.config, 'r') as f:
            file_config = json.load(f)
            config.update(file_config)
    
    # 运行
    collector = VehicleDataCollector(config=config)
    collector.start(duration=args.duration)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloud Data Uploader - 云端数据上传模块
======================================
将 UDS 采集的车辆数据实时上传到云端服务器

支持:
  - MQTT 协议上传 (推荐)
  - HTTP/HTTPS POST 上传
  - 数据缓存 (网络中断时)
  - 断点续传
  - 压缩传输 (可选)

服务器配置:
  - 服务器：118.196.86.99
  - MQTT Port: 1883 (或 8883 for TLS)
  - HTTP Port: 80/443
"""

import json
import time
import threading
import queue
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
import hashlib

# MQTT 支持 (需要安装：pip install paho-mqtt)
try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    print("[WARN] paho-mqtt not installed, MQTT upload disabled")

# HTTP 支持
import requests


# ===================== 配置 =====================

@dataclass
class CloudConfig:
    """云端配置"""
    # 服务器
    server_ip: str = "118.196.86.99"
    
    # MQTT 配置
    mqtt_port: int = 1883
    mqtt_topic: str = "vehicle/data/upload"
    mqtt_client_id: str = "vehicle_001"
    mqtt_username: str = ""
    mqtt_password: str = ""
    mqtt_use_tls: bool = False
    
    # HTTP 配置
    http_port: int = 8080
    http_endpoint: str = "/api/v1/vehicle/data"
    http_use_https: bool = False
    
    # 上传策略
    upload_interval: float = 1.0  # 上传间隔 (秒)
    batch_size: int = 10  # 批量上传大小
    enable_compression: bool = False  # 启用 gzip 压缩
    enable_cache: bool = True  # 启用本地缓存
    cache_file: str = "data_cache.json"  # 缓存文件路径
    max_cache_size: int = 10000  # 最大缓存条数


# ===================== 数据结构 =====================

@dataclass
class VehicleData:
    """车辆数据结构"""
    timestamp: float  # 时间戳
    datetime_str: str  # 日期时间
    device_id: str  # 设备 ID (如 ICB_001)
    ecu_type: str  # ECU 类型 (CCU/LHZCU/RHZCU 等)
    data: List[Dict[str, Any]]  # 数据列表
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


# ===================== 云端上传器 =====================

class CloudUploader:
    """
    云端数据上传器
    
    功能:
      - 支持 MQTT 和 HTTP 两种上传方式
      - 自动重连
      - 数据缓存 (网络中断时)
      - 断点续传
      - 上传状态监控
    """
    
    def __init__(self, config: CloudConfig = None, upload_mode: str = "mqtt"):
        """
        初始化上传器
        
        Args:
            config: 云端配置
            upload_mode: 上传模式 ("mqtt" | "http" | "both")
        """
        self.config = config or CloudConfig()
        self.upload_mode = upload_mode
        
        # 数据队列
        self._data_queue: queue.Queue = queue.Queue(maxsize=10000)
        self._cache: List[VehicleData] = []
        
        # 上传线程
        self._running = False
        self._upload_thread: Optional[threading.Thread] = None
        
        # 状态
        self._connected = False
        self._mqtt_client: Optional[mqtt.Client] = None if not MQTT_AVAILABLE else None
        self._stats = {
            "uploaded": 0,
            "failed": 0,
            "cached": 0,
            "last_upload_time": None
        }
        
        # 回调
        self._on_upload_callback = None
        
        # 初始化 MQTT
        if MQTT_AVAILABLE and upload_mode in ["mqtt", "both"]:
            self._init_mqtt()
    
    def _init_mqtt(self):
        """初始化 MQTT 客户端"""
        if not MQTT_AVAILABLE:
            return
        
        try:
            self._mqtt_client = mqtt.Client(
                client_id=self.config.mqtt_client_id,
                clean_session=True
            )
            
            if self.config.mqtt_username:
                self._mqtt_client.username_pw_set(
                    self.config.mqtt_username,
                    self.config.mqtt_password
                )
            
            if self.config.mqtt_use_tls:
                self._mqtt_client.tls_set()
            
            # 设置回调
            self._mqtt_client.on_connect = self._on_mqtt_connect
            self._mqtt_client.on_disconnect = self._on_mqtt_disconnect
            self._mqtt_client.on_publish = self._on_mqtt_publish
            
        except Exception as e:
            print(f"[ERROR] MQTT init failed: {e}")
    
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT 连接成功回调"""
        if rc == 0:
            self._connected = True
            print(f"[INFO] MQTT connected to {self.config.server_ip}:{self.config.mqtt_port}")
        else:
            print(f"[ERROR] MQTT connection failed, rc={rc}")
    
    def _on_mqtt_disconnect(self, client, userdata, rc):
        """MQTT 断开回调"""
        self._connected = False
        print(f"[WARN] MQTT disconnected, rc={rc}")
    
    def _on_mqtt_publish(self, client, userdata, mid):
        """MQTT 发布成功回调"""
        self._stats["uploaded"] += 1
        self._stats["last_upload_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if self._on_upload_callback:
            try:
                self._on_upload_callback("mqtt", True)
            except:
                pass
    
    def connect(self) -> bool:
        """连接到云端"""
        if self.upload_mode in ["mqtt", "both"] and MQTT_AVAILABLE:
            try:
                print(f"[INFO] Connecting to MQTT broker {self.config.server_ip}:{self.config.mqtt_port}...")
                self._mqtt_client.connect(
                    self.config.server_ip,
                    self.config.mqtt_port,
                    keepalive=60
                )
                self._mqtt_client.loop_start()
                
                # 等待连接
                time.sleep(2)
                return self._connected
                
            except Exception as e:
                print(f"[ERROR] MQTT connect failed: {e}")
        
        # HTTP 模式不需要预先连接
        if self.upload_mode in ["http", "both"]:
            print(f"[INFO] HTTP upload mode ready (endpoint: {self._get_http_url()})")
            return True
        
        return False
    
    def disconnect(self):
        """断开连接"""
        self._running = False
        
        if self._upload_thread:
            self._upload_thread.join(timeout=2.0)
        
        if self._mqtt_client:
            self._mqtt_client.loop_stop()
            self._mqtt_client.disconnect()
        
        # 保存缓存
        if self.config.enable_cache:
            self._save_cache()
        
        print(f"[INFO] Disconnected from cloud")
    
    def upload_data(self, data: VehicleData):
        """
        上传单条数据
        
        Args:
            data: 车辆数据对象
        """
        if self._data_queue.full():
            # 队列满，丢弃旧数据
            try:
                self._data_queue.get_nowait()
            except:
                pass
        
        self._data_queue.put(data)
    
    def upload_batch(self, data_list: List[VehicleData]):
        """批量上传数据"""
        for data in data_list:
            self.upload_data(data)
    
    def start_upload_loop(self, interval: float = None):
        """启动上传循环"""
        if self._running:
            print("[WARN] Already running")
            return
        
        self._running = True
        interval = interval or self.config.upload_interval
        
        self._upload_thread = threading.Thread(
            target=self._upload_loop,
            daemon=True
        )
        self._upload_thread.start()
        
        print(f"[INFO] Upload loop started (interval={interval}s)")
    
    def stop_upload_loop(self):
        """停止上传循环"""
        self._running = False
        if self._upload_thread:
            self._upload_thread.join(timeout=2.0)
            self._upload_thread = None
        print(f"[INFO] Upload loop stopped")
    
    def _upload_loop(self):
        """上传循环 (后台线程)"""
        batch = []
        
        while self._running:
            try:
                # 从队列取数据
                try:
                    data = self._data_queue.get(timeout=0.5)
                    batch.append(data)
                except queue.Empty:
                    pass
                
                # 达到批量大小或超时时上传
                if len(batch) >= self.config.batch_size:
                    self._upload_batch(batch)
                    batch = []
                
            except Exception as e:
                print(f"[ERROR] Upload loop error: {e}")
                time.sleep(1)
        
        # 上传剩余数据
        if batch:
            self._upload_batch(batch)
    
    def _upload_batch(self, batch: List[VehicleData]):
        """批量上传"""
        if not batch:
            return
        
        success = False
        
        # MQTT 上传
        if self.upload_mode in ["mqtt", "both"] and self._connected:
            success = self._upload_via_mqtt(batch)
        
        # HTTP 上传 (作为备用)
        if not success and self.upload_mode in ["http", "both"]:
            success = self._upload_via_http(batch)
        
        # 缓存失败的数据
        if not success and self.config.enable_cache:
            self._cache.extend(batch)
            self._stats["cached"] += len(batch)
            
            if len(self._cache) > self.config.max_cache_size:
                self._cache = self._cache[-self.config.max_cache_size:]
            
            print(f"[WARN] Data cached ({len(self._cache)} items)")
    
    def _upload_via_mqtt(self, batch: List[VehicleData]) -> bool:
        """通过 MQTT 上传"""
        if not self._connected or not self._mqtt_client:
            return False
        
        try:
            for data in batch:
                payload = data.to_json()
                
                # 可选压缩
                if self.config.enable_compression:
                    import gzip
                    payload = gzip.compress(payload.encode('utf-8'))
                
                result = self._mqtt_client.publish(
                    self.config.mqtt_topic,
                    payload=payload,
                    qos=1
                )
                
                if result.rc != mqtt.MQTT_ERR_SUCCESS:
                    return False
            
            return True
            
        except Exception as e:
            print(f"[ERROR] MQTT upload failed: {e}")
            return False
    
    def _upload_via_http(self, batch: List[VehicleData]) -> bool:
        """通过 HTTP 上传"""
        url = self._get_http_url()
        
        try:
            # 批量打包
            payload = {
                "device_id": batch[0].device_id if batch else "vehicle_001",
                "timestamp": time.time(),
                "count": len(batch),
                "data": [d.to_dict() for d in batch]
            }
            
            # 可选压缩
            headers = {"Content-Type": "application/json"}
            data = json.dumps(payload, ensure_ascii=False)
            
            if self.config.enable_compression:
                import gzip
                data = gzip.compress(data.encode('utf-8'))
                headers["Content-Encoding"] = "gzip"
            
            response = requests.post(
                url,
                data=data,
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                self._stats["uploaded"] += len(batch)
                self._stats["last_upload_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                if self._on_upload_callback:
                    try:
                        self._on_upload_callback("http", True)
                    except:
                        pass
                
                return True
            else:
                print(f"[ERROR] HTTP upload failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] HTTP upload error: {e}")
            return False
    
    def _get_http_url(self) -> str:
        """获取 HTTP 上传 URL"""
        protocol = "https" if self.config.http_use_https else "http"
        return f"{protocol}://{self.config.server_ip}:{self.config.http_port}{self.config.http_endpoint}"
    
    def _load_cache(self):
        """加载缓存数据"""
        if not self.config.enable_cache:
            return
        
        try:
            with open(self.config.cache_file, 'r') as f:
                cache_data = json.load(f)
                self._cache = [VehicleData(**item) for item in cache_data]
            print(f"[INFO] Loaded {len(self._cache)} cached items")
        except:
            pass
    
    def _save_cache(self):
        """保存缓存数据"""
        if not self.config.enable_cache or not self._cache:
            return
        
        try:
            with open(self.config.cache_file, 'w') as f:
                json.dump([asdict(item) for item in self._cache], f, ensure_ascii=False)
            print(f"[INFO] Saved {len(self._cache)} cached items")
        except Exception as e:
            print(f"[ERROR] Save cache failed: {e}")
    
    def flush_cache(self):
        """尝试上传缓存数据"""
        if not self._cache:
            return
        
        print(f"[INFO] Flushing {len(self._cache)} cached items...")
        
        # 分批上传
        batch_size = self.config.batch_size
        for i in range(0, len(self._cache), batch_size):
            batch = self._cache[i:i+batch_size]
            
            success = False
            
            if self.upload_mode in ["mqtt", "both"] and self._connected:
                success = self._upload_via_mqtt(batch)
            
            if not success and self.upload_mode in ["http", "both"]:
                success = self._upload_via_http(batch)
            
            if success:
                self._cache = self._cache[i+batch_size:]
        
        if self._cache:
            print(f"[INFO] {len(self._cache)} items still cached")
        else:
            print("[INFO] Cache flushed successfully")
    
    def get_stats(self) -> dict:
        """获取上传统计"""
        return {
            **self._stats,
            "queue_size": self._data_queue.qsize(),
            "cache_size": len(self._cache),
            "connected": self._connected
        }
    
    def set_callback(self, callback):
        """设置上传回调"""
        self._on_upload_callback = callback


# ===================== 快速上传函数 =====================

def upload_vehicle_data(
    data_list: List[Dict],
    ecu_type: str = "CCU",
    device_id: str = "vehicle_001",
    mode: str = "mqtt",
    config: CloudConfig = None
):
    """
    快速上传车辆数据
    
    Args:
        data_list: 数据列表 (每个元素包含 did_id, name, value, unit 等)
        ecu_type: ECU 类型
        device_id: 设备 ID
        mode: 上传模式 ("mqtt" | "http")
        config: 云端配置
    """
    uploader = CloudUploader(config=config, upload_mode=mode)
    
    if not uploader.connect():
        print("[ERROR] Connect failed")
        return False
    
    try:
        # 转换为 VehicleData 格式
        vehicle_data = VehicleData(
            timestamp=time.time(),
            datetime_str=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            device_id=device_id,
            ecu_type=ecu_type,
            data=data_list
        )
        
        uploader.upload_data(vehicle_data)
        
        # 等待上传
        time.sleep(2)
        
        stats = uploader.get_stats()
        print(f"[INFO] Upload complete: {stats}")
        
        return stats["uploaded"] > 0
        
    finally:
        uploader.disconnect()


# ===================== 测试 =====================

if __name__ == "__main__":
    # 测试上传
    config = CloudConfig(
        server_ip="118.196.86.99",
        mqtt_port=1883,
        mqtt_topic="vehicle/test",
        mqtt_client_id=f"test_{int(time.time())}"
    )
    
    uploader = CloudUploader(config=config, upload_mode="mqtt")
    
    if uploader.connect():
        # 模拟数据
        test_data = VehicleData(
            timestamp=time.time(),
            datetime_str=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            device_id="vehicle_001",
            ecu_type="CCU",
            data=[
                {"did": "B000", "name": "Supply Voltage", "value": 12.5, "unit": "V"},
                {"did": "B015", "name": "Battery Voltage", "value": 380.2, "unit": "V"}
            ]
        )
        
        uploader.upload_data(test_data)
        
        # 等待上传
        time.sleep(3)
        
        print(f"Stats: {uploader.get_stats()}")
        
        uploader.disconnect()
    else:
        print("[ERROR] Connection failed")

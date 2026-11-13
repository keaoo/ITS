#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抓包模块
用于网络数据包捕获和解析
"""

import threading
import queue
import time
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime

try:
    from scapy.all import sniff, get_if_list, conf, Ether, IP, UDP, TCP
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("⚠️  Scapy未安装，抓包功能不可用")


class PacketInfo:
    """数据包信息"""
    
    def __init__(self):
        self.timestamp: float = 0.0
        self.source_ip: str = ''
        self.dest_ip: str = ''
        self.source_port: int = 0
        self.dest_port: int = 0
        self.protocol: str = ''
        self.length: int = 0
        self.raw_data: bytes = b''
        self.is_someip: bool = False
        self.someip_header: Any = None
        self.someip_info: Dict[str, Any] = {}
        self.summary: str = ''
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        dt = datetime.fromtimestamp(self.timestamp)
        time_str = dt.strftime('%H:%M:%S.%f')[:-3]
        
        return {
            'timestamp': time_str,
            'source_ip': self.source_ip,
            'source_port': self.source_port,
            'dest_ip': self.dest_ip,
            'dest_port': self.dest_port,
            'protocol': self.protocol,
            'length': self.length,
            'is_someip': self.is_someip,
            'someip_info': self.someip_info,
            'summary': self.summary
        }


class PacketCapture:
    """数据包捕获器"""
    
    def __init__(self):
        self.capturing: bool = False
        self.capture_thread: Optional[threading.Thread] = None
        self.packet_queue: queue.Queue = queue.Queue(maxsize=10000)
        self.packet_list: List[PacketInfo] = []
        self.packet_callback: Optional[Callable[[PacketInfo], None]] = None
        self.interface: str = ''
        self.filter_bpf: str = ''  # BPF过滤器
        self.max_packets: int = 10000
    
    @staticmethod
    def get_interfaces() -> List[str]:
        """
        获取网络接口列表
        
        Returns:
            网络接口列表
        """
        if not SCAPY_AVAILABLE:
            return []
        
        try:
            interfaces = get_if_list()
            return interfaces
        except Exception as e:
            print(f"⚠️  获取网络接口失败: {e}")
            return []
    
    def start_capture(self, interface: str, filter_str: str = '', max_packets: int = 10000):
        """
        开始抓包
        
        Args:
            interface: 网络接口名称
            filter_str: BPF过滤规则
            max_packets: 最大抓包数量
        """
        if not SCAPY_AVAILABLE:
            print("❌ Scapy未安装，无法开始抓包")
            return False
        
        if self.capturing:
            print("⚠️  抓包已在进行中")
            return False
        
        self.interface = interface
        self.filter_bpf = filter_str
        self.max_packets = max_packets
        self.packet_list.clear()
        self.capturing = True
        
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        
        print(f"✅ 开始抓包 - 接口: {interface}, 过滤器: {filter_str}")
        return True
    
    def stop_capture(self):
        """停止抓包"""
        if not self.capturing:
            return
        
        self.capturing = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
        
        print("🛑 停止抓包")
    
    def _capture_loop(self):
        """抓包循环（在后台线程中运行）"""
        try:
            sniff(
                iface=self.interface,
                prn=self._handle_packet,
                filter=self.filter_bpf,
                stop_filter=lambda x: not self.capturing,
                store=False
            )
        except Exception as e:
            print(f"❌ 抓包过程出错: {e}")
        finally:
            self.capturing = False
    
    def _handle_packet(self, packet):
        """
        处理单个数据包
        
        Args:
            packet: Scapy数据包对象
        """
        try:
            info = PacketInfo()
            info.timestamp = time.time()
            info.raw_data = bytes(packet)
            info.length = len(info.raw_data)
            
            # 解析Ethernet/IP/UDP/TCP
            if IP in packet:
                ip = packet[IP]
                info.source_ip = ip.src
                info.dest_ip = ip.dst
                info.protocol = 'IP'
                
                if UDP in packet:
                    udp = packet[UDP]
                    info.source_port = udp.sport
                    info.dest_port = udp.dport
                    info.protocol = 'UDP'
                    info.summary = f"{ip.src}:{udp.sport} -> {ip.dst}:{udp.dport}"
                    
                    # 检查是否是SOME/IP协议（通常端口30490或SOME/IP-SD）
                    if udp.dport == 30490 or udp.sport == 30490:
                        info.is_someip = True
                        info.protocol = 'SOME/IP'
                        info.summary = f"SOME/IP {ip.src}:{udp.sport} -> {ip.dst}:{udp.dport}"
                        
                        # 解析SOME/IP协议头（延迟解析）
                        if hasattr(packet, 'load'):
                            info.someip_info = {
                                'has_payload': True,
                                'payload_length': len(packet.load)
                            }
                
                elif TCP in packet:
                    tcp = packet[TCP]
                    info.source_port = tcp.sport
                    info.dest_port = tcp.dport
                    info.protocol = 'TCP'
                    info.summary = f"{ip.src}:{tcp.sport} -> {ip.dst}:{tcp.dport}"
            
            # 添加到列表和队列
            self.packet_list.append(info)
            
            # 限制数量
            if len(self.packet_list) > self.max_packets:
                self.packet_list.pop(0)
            
            # 放入队列供UI处理
            try:
                self.packet_queue.put(info, block=False)
            except queue.Full:
                pass
            
            # 回调通知
            if self.packet_callback:
                self.packet_callback(info)
                
        except Exception as e:
            pass  # 忽略错误
    
    def get_packets(self) -> List[PacketInfo]:
        """
        获取捕获的所有数据包
        
        Returns:
            数据包列表
        """
        return self.packet_list.copy()
    
    def get_someip_packets(self) -> List[PacketInfo]:
        """
        获取SOME/IP协议数据包
        
        Returns:
            SOME/IP数据包列表
        """
        return [p for p in self.packet_list if p.is_someip]
    
    def clear_packets(self):
        """清空数据包"""
        self.packet_list.clear()
        print("🗑️ 已清空数据包")

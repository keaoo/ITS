#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LHZCU (Left Head Zone Control Unit) 诊断服务库
===============================================
基于 Part4: 3.0-SOP-LHZCU-ZONE Part4-V4.1-UAES_20250416

功能:
  - $10 诊断会话控制
  - $11 ECU 复位
  - $14 清除 DTC
  - $19 读取 DTC 信息
  - $22 读取 DID 数据
  - $27 安全访问 (算法 0x1010)
  - $2E 写入 DID 数据
  - $2F IO 控制
  - $31 例程控制
  - $3E TesterPresent
  - $85 DTC 设置控制

通信: 通过 ICB DoIP 网关转发
  网关: 172.31.6.11:13400
  目标: 0x15B0 (LHZCU 逻辑地址)
  算法: 0x1010
"""

import time
import struct
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field

from .doip_client import DoIPClient
from .sa_calc import calc_key
from .lhzcu_doip_config import (
    LHZCU_DOIP_IP,
    LHZCU_DOIP_PORT,
    LHZCU_PHYSICAL_ADDR,
    LHZCU_SECURITY_ALGO,
    TESTER_LOGICAL_ADDR,
    LHZCU_DIAG_CONFIG,
)


# ── 异常 ──
class LHZCUDiagnosticError(Exception):
    """LHZCU 诊断异常基类"""
    pass


class LHZCUCommunicationError(LHZCUDiagnosticError):
    """通信异常"""
    pass


class LHZCUSecurityError(LHZCUDiagnosticError):
    """安全访问异常"""
    pass


class LHZCUSessionError(LHZCUDiagnosticError):
    """会话控制异常"""
    pass


# ── 数据结构 ──
@dataclass
class LHZCUInfo:
    """LHZCU 基本信息"""
    vin: str = ""
    part_number: str = ""
    hardware_version: str = ""
    software_version: str = ""
    serial_number: str = ""
    active_session: str = ""


@dataclass
class LHZCUDTC:
    """DTC 故障码"""
    code: int          # DTC 编码 (如 0xC001234)
    status: int        # DTC 状态掩码
    description: str = ""


# ── 诊断客户端 ──
class LHZCUDiagnostics:
    """
    LHZCU 诊断客户端
    
    使用示例:
        diag = LHZCUDiagnostics()
        diag.connect()
        diag.extended_session()
        info = diag.read_info()
        diag.disconnect()
    """
    
    def __init__(self, ip: str = LHZCU_DOIP_IP, port: int = LHZCU_DOIP_PORT,
                 target_addr: int = LHZCU_PHYSICAL_ADDR,
                 security_algo: int = LHZCU_SECURITY_ALGO,
                 timeout: float = 5.0):
        self.target_addr = target_addr
        self.security_algo = security_algo
        self.timeout = timeout
        self._client = DoIPClient(ip=ip, port=port, timeout=timeout)
        self._connected = False
        self._session_active = False
        self._security_unlocked = False
    
    # ── 连接管理 ──
    
    def connect(self) -> bool:
        """建立 DoIP 连接 + 路由激活"""
        try:
            self._client.connect()
            self._client.routing_activate()
            self._connected = True
            self._session_active = False
            self._security_unlocked = False
            return True
        except Exception as e:
            self._connected = False
            raise LHZCUCommunicationError(f"连接失败: {e}")
    
    def disconnect(self):
        """断开连接"""
        self._client.disconnect()
        self._connected = False
        self._session_active = False
        self._security_unlocked = False
    
    def is_connected(self) -> bool:
        return self._connected
    
    def is_session_active(self) -> bool:
        return self._session_active
    
    def is_security_unlocked(self) -> bool:
        return self._security_unlocked
    
    # ── sa_calc 预热 ──
    
    def _warm_sa_calc(self):
        """
        预热 sa_calc daemon
        在请求种子前预先启动 32-bit Python 常驻进程
        避免首次 calc_key() 启动开销导致超过 ECU 1s 时间窗口
        """
        try:
            calc_key("00000000", f"{self.security_algo:08X}")
        except Exception:
            pass  # 种子无效时的错误可忽略，预热目的已达成
    
    # ── 底层通信 ──
    
    def _send_uds(self, request: bytes, timeout: float = None) -> bytes:
        """发送 UDS 请求到 LHZCU"""
        if not self._connected:
            raise LHZCUCommunicationError("请先调用 connect()")
        
        t = timeout or self.timeout
        resp = self._client.send_diagnostic(request, timeout=t, target_addr=self.target_addr)
        
        if resp is None:
            raise LHZCUCommunicationError("UDS 无响应")
        
        # 检查 NRC
        if len(resp) > 0 and resp[0] == 0x7F:
            nrc = resp[2] if len(resp) > 2 else 0
            sid = resp[1] if len(resp) > 1 else 0
            raise LHZCUDiagnosticError(f"NRC 0x{nrc:02X} (服务 0x{sid:02X}): {_nrc_desc(nrc)}")
        
        return resp
    
    def _ensure_session(self, session: str = "03"):
        """确保在指定会话中"""
        if not self._session_active:
            self._switch_session(session)
    
    # ── $10 诊断会话控制 ──
    
    def _switch_session(self, session_id: str = "03") -> Dict:
        """
        切换诊断会话
        
        Args:
            session_id: "01"=默认, "02"=编程, "03"=扩展
        
        Returns:
            {'session': str, 'success': bool}
        """
        try:
            resp = self._send_uds(bytes.fromhex(f"10{session_id}"))
            if resp and len(resp) >= 3 and resp[0] == 0x50 and resp[1] == int(session_id, 16):
                session_map = {0x01: "Default", 0x02: "Programming", 0x03: "Extended"}
                self._session_active = True
                return {
                    'success': True,
                    'session': session_map.get(resp[1], f"0x{resp[1]:02X}")
                }
            raise LHZCUSessionError(f"会话切换失败: {' '.join(f'{b:02X}' for b in resp)}")
        except LHZCUDiagnosticError:
            raise
        except Exception as e:
            raise LHZCUSessionError(f"会话切换异常: {e}")
    
    def default_session(self) -> Dict:
        return self._switch_session("01")
    
    def programming_session(self) -> Dict:
        return self._switch_session("02")
    
    def extended_session(self) -> Dict:
        return self._switch_session("03")
    
    # ── $11 ECU 复位 ──
    
    def ecu_reset(self, reset_type: str = "01") -> Dict:
        """
        ECU 复位
        
        Args:
            reset_type: "01"=硬复位, "02"=KeyOff, "03"=软复位
        """
        try:
            resp = self._send_uds(bytes.fromhex(f"11{reset_type}"))
            if resp and len(resp) >= 2 and resp[0] == 0x51:
                reset_map = {0x01: "Hard Reset", 0x02: "Key Off", 0x03: "Soft Reset"}
                self._session_active = False
                self._security_unlocked = False
                return {
                    'success': True,
                    'type': reset_map.get(resp[1], f"0x{resp[1]:02X}")
                }
            raise LHZCUDiagnosticError(f"复位失败: {' '.join(f'{b:02X}' for b in resp)}")
        except LHZCUDiagnosticError:
            raise
        except Exception as e:
            raise LHZCUDiagnosticError(f"复位异常: {e}")
    
    def hard_reset(self) -> Dict:
        """硬复位"""
        return self.ecu_reset("01")
    
    def soft_reset(self) -> Dict:
        """软复位"""
        return self.ecu_reset("03")
    
    # ── $27 安全访问 ──
    
    def security_access(self, level: str = "01") -> Dict:
        """
        安全访问 ($27)
        
        Args:
            level: "01/02"=Level1, "03/04"=Level2, "05/06"=Level3
        
        流程:
            1. 请求种子 (27 01 → 67 01 + seed)
            2. 计算密钥 (SATURN 算法)
            3. 发送密钥 (27 02 + key)
        """
        # 确保在扩展会话中
        self._ensure_session("03")
        
        # 预热 sa_calc daemon，避免首次调用启动开销超时
        self._warm_sa_calc()
        
        try:
            # Step 1: 请求种子
            req_seed = bytes.fromhex(f"27{level}")
            resp_seed = self._send_uds(req_seed)
            
            if not resp_seed or len(resp_seed) < 4:
                raise LHZCUSecurityError("获取种子失败: 响应过短")
            
            if resp_seed[0] != 0x67:
                raise LHZCUSecurityError(f"获取种子失败: {' '.join(f'{b:02X}' for b in resp_seed)}")
            
            if len(resp_seed) >= 7 and resp_seed[2] == 0x04:
                seed = resp_seed[3:7]  # 67 01 04 + 4字节seed
            else:
                seed = resp_seed[2:6]  # 67 01 + 4字节seed
            seed_hex = seed.hex().upper()
            
            # Step 2: 计算密钥
            algo_str = f"{self.security_algo:08X}"
            key = calc_key(seed_hex, algo_str)
            
            # Step 3: 发送密钥
            level_int = int(level, 16)
            req_key = bytes([0x27, level_int + 1]) + key
            resp_key = self._send_uds(req_key)
            
            if not resp_key or len(resp_key) < 2:
                raise LHZCUSecurityError("发送密钥失败: 无响应")
            
            if resp_key[0] == 0x67:
                self._security_unlocked = True
                return {
                    'success': True,
                    'seed': seed_hex,
                    'key': key.hex().upper(),
                    'level': level,
                }
            else:
                raise LHZCUSecurityError(f"密钥验证失败: {' '.join(f'{b:02X}' for b in resp_key)}")
        
        except LHZCUSecurityError:
            raise
        except Exception as e:
            raise LHZCUSecurityError(f"安全访问异常: {e}")
    
    def security_level1(self) -> Dict:
        """Level 1 安全访问 (01/02)"""
        return self.security_access("01")
    
    # ── $22 读取 DID ──
    
    def read_did(self, did: str) -> Dict:
        """
        读取 DID 数据
        
        Args:
            did: 16进制 DID, 如 "F190"
        
        Returns:
            {'did': str, 'data': bytes, 'hex': str, 'decoded': str}
        """
        self._ensure_session("03")
        
        clean = did.replace('0x', '').replace(' ', '').upper().zfill(4)
        req = bytes.fromhex(f"22{clean}")
        
        resp = self._send_uds(req)
        
        if resp and len(resp) >= 4 and resp[0] == 0x62:
            data = resp[3:]  # 跳过 62 DD DD
            decoded = self._decode_did(clean, data)
            return {
                'did': clean,
                'data': data,
                'hex': ' '.join(f'{b:02X}' for b in data),
                'decoded': decoded,
                'success': True,
            }
        else:
            hex_str = ' '.join(f'{b:02X}' for b in resp) if resp else '空'
            return {'did': clean, 'success': False, 'error': hex_str}
    
    def read_dids(self, did_list: List[str]) -> Dict[str, Dict]:
        """批量读取多个 DID"""
        results = {}
        for did in did_list:
            try:
                results[did] = self.read_did(did)
            except Exception as e:
                results[did] = {'did': did, 'success': False, 'error': str(e)}
        return results
    
    def read_info(self) -> LHZCUInfo:
        """读取 LHZCU 基本信息"""
        info = LHZCUInfo()
        dids = ["F186", "F190", "F191"]
        results = self.read_dids(dids)
        
        for did, result in results.items():
            if result.get('success'):
                data = result['data']
                if did == "F186" and data:
                    session_map = {0x01: "Default", 0x02: "Programming", 0x03: "Extended"}
                    info.active_session = session_map.get(data[0], f"0x{data[0]:02X}")
                elif did == "F190" and data:
                    info.software_version = data.decode('ascii', errors='replace').strip('\x00 ')
                elif did == "F191" and data:
                    info.part_number = data.decode('ascii', errors='replace').strip('\x00 ')
        
        return info
    
    # ── $2E 写入 DID ──
    
    def write_did(self, did: str, data: bytes) -> Dict:
        """写入 DID 数据"""
        self._ensure_session("03")
        
        clean = did.replace('0x', '').replace(' ', '').upper().zfill(4)
        req = bytes.fromhex(f"2E{clean}") + data
        
        resp = self._send_uds(req)
        
        if resp and len(resp) >= 3 and resp[0] == 0x6E:
            return {
                'did': clean,
                'success': True,
                'hex': data.hex().upper(),
            }
        else:
            hex_str = ' '.join(f'{b:02X}' for b in resp) if resp else '空'
            return {'did': clean, 'success': False, 'error': hex_str}
    
    # ── $19 读取 DTC ──
    
    def read_dtc(self, dtc_mask: str = "FF") -> List[LHZCUDTC]:
        """
        读取 DTC 故障码 ($19 02)
        
        Args:
            dtc_mask: DTC 状态掩码, "FF"=全部
        
        Returns:
            [LHZCUDTC, ...]
        """
        self._ensure_session("03")
        
        resp = self._send_uds(bytes.fromhex(f"1902{dtc_mask}"))
        
        dtcs = []
        if resp and resp[0] == 0x59 and len(resp) > 3:
            # 解析 DTC 列表
            # 格式: 59 02 [formatByte] [DTC_H] [DTC_M] [DTC_L] [status] ...
            if len(resp) >= 5:
                i = 3  # 跳过 59 02 formatByte
                while i + 3 < len(resp):
                    dtc_code = (resp[i] << 16) | (resp[i+1] << 8) | resp[i+2]
                    dtc_status = resp[i+3] if i + 3 < len(resp) else 0
                    dtcs.append(LHZCUDTC(code=dtc_code, status=dtc_status))
                    i += 4
        
        return dtcs
    
    def read_dtc_count(self) -> int:
        """读取 DTC 数量 ($19 01)"""
        self._ensure_session("03")
        
        resp = self._send_uds(bytes.fromhex("1901FF"))
        
        if resp and resp[0] == 0x59 and len(resp) >= 2:
            # 59 01 [statusAvailabilityMask] [DTCFormatIdentifier] [DTCCount]
            if len(resp) >= 5:
                return resp[4]
            if len(resp) >= 4:
                return resp[3]
        return 0
    
    def read_dtc_snapshot(self, dtc_code: int) -> bytes:
        """读取 DTC 快照数据 ($19 04)"""
        self._ensure_session("03")
        
        dtc_bytes = struct.pack('>I', dtc_code)[1:]  # 3 bytes
        req = bytes.fromhex("1904") + bytes([0xFF]) + dtc_bytes + bytes([0xFF, 0xFF])
        
        resp = self._send_uds(req)
        
        if resp and resp[0] == 0x59:
            return resp[3:]  # skip 59 04 ...
        return b""
    
    # ── $14 清除 DTC ──
    
    def clear_dtc(self, group: str = "FFFFFF") -> Dict:
        """
        清除 DTC 故障码
        
        Args:
            group: DTC 组码, "FFFFFF"=全部
        """
        self._ensure_session("03")
        
        resp = self._send_uds(bytes.fromhex(f"14{group}"))
        
        if resp and resp[0] == 0x54:
            self._session_active = False  # 清除后会话可能重置
            return {'success': True}
        else:
            hex_str = ' '.join(f'{b:02X}' for b in resp) if resp else '空'
            return {'success': False, 'error': hex_str}
    
    # ── $3E TesterPresent ──
    
    def tester_present(self) -> Dict:
        """TesterPresent 保活"""
        resp = self._send_uds(bytes.fromhex("3E00"))
        return {
            'success': resp and resp[0] == 0x7E
        }
    
    # ── $85 DTC 设置控制 ──
    
    def control_dtc_setting(self, enable: bool = True) -> Dict:
        """控制 DTC 设置"""
        sub = "01" if enable else "02"
        resp = self._send_uds(bytes.fromhex(f"85{sub}"))
        return {
            'success': resp and resp[0] == 0xC5,
            'enabled': enable,
        }
    
    # ── $31 例程控制 ──
    
    def routine_control(self, routine_id: str, control_type: str = "01", data: bytes = b"") -> Dict:
        """
        例程控制
        
        Args:
            routine_id: 例程 ID (hex, 如 "FF00")
            control_type: "01"=Start, "02"=Stop, "03"=GetResult
            data: 可选参数
        """
        self._ensure_session("03")
        
        clean = routine_id.replace('0x', '').replace(' ', '').upper().zfill(4)
        req = bytes.fromhex(f"31{control_type}{clean}") + data
        
        resp = self._send_uds(req)
        
        if resp and resp[0] == 0x71:
            result = resp[3:]  # 跳过 71 01 RID
            return {
                'success': True,
                'routine_id': clean,
                'control_type': control_type,
                'result': result.hex().upper() if result else "",
            }
        else:
            hex_str = ' '.join(f'{b:02X}' for b in resp) if resp else '空'
            return {'success': False, 'error': hex_str}
    
    # ── $2F IO 控制 ──
    
    def io_control(self, did: str, control_type: str = "00", data: bytes = b"") -> Dict:
        """
        IO 控制
        
        Args:
            did: 目标 DID
            control_type: "00"=ReturnControl, "01"=Reset, "02"=FreezeCurrent, 
                         "03"=ShortTermAdjust, "04"=LongTermAdjust
        """
        self._ensure_session("03")
        
        clean = did.replace('0x', '').replace(' ', '').upper().zfill(4)
        req = bytes.fromhex(f"2F{clean}{control_type}") + data
        
        resp = self._send_uds(req)
        
        if resp and resp[0] == 0x6F:
            return {'success': True, 'did': clean, 'control_type': control_type}
        else:
            hex_str = ' '.join(f'{b:02X}' for b in resp) if resp else '空'
            return {'success': False, 'error': hex_str}
    
    # ── 辅助 ──
    
    @staticmethod
    def _decode_did(did: str, data: bytes) -> str:
        """解码常用 DID 数据"""
        if not data:
            return "空"
        
        if did == "F186":
            session_map = {0x01: "Default", 0x02: "Programming", 0x03: "Extended"}
            return session_map.get(data[0], f"0x{data[0]:02X}")
        
        if did in ("F190", "F191", "F194", "F195", "F1A0", "F1A1"):
            return data.decode('ascii', errors='replace').strip('\x00 ')
        
        if did == "F197":
            serial = data.decode('ascii', errors='replace').strip('\x00 ')
            return serial if serial else ' '.join(f'{b:02X}' for b in data)
        
        if did == "E101":
            if len(data) >= 3:
                val = (data[0] << 16) | (data[1] << 8) | data[2]
                return f"{val} km"
            return ' '.join(f'{b:02X}' for b in data)
        
        if did == "010B":
            if len(data) >= 6:
                return f"20{data[0]:02X}-{data[1]:02X}-{data[2]:02X} {data[3]:02X}:{data[4]:02X}:{data[5]:02X}"
            return ' '.join(f'{b:02X}' for b in data)
        
        return ' '.join(f'{b:02X}' for b in data)


def _nrc_desc(nrc: int) -> str:
    """UDS NRC 描述"""
    map = {
        0x10: "GeneralReject",
        0x11: "ServiceNotSupported",
        0x12: "SubfunctionNotSupported",
        0x13: "IncorrectMessageLength",
        0x22: "ConditionsNotCorrect",
        0x24: "RequestSequenceError",
        0x25: "NoResponseFromECU",
        0x26: "FailurePreventsExecution",
        0x31: "RequestOutOfRange",
        0x33: "SecurityAccessDenied",
        0x35: "InvalidKey",
        0x36: "ExceededAttempts",
        0x37: "RequiredTimeDelayNotExpired",
        0x78: "ResponsePending",
    }
    return map.get(nrc, f"Unknown(0x{nrc:02X})")

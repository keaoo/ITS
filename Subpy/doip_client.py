#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DoIP (ISO 13400) 通信客户端 - ICB (ZXD1) 专用
==============================================
实现ICB的DoIP诊断通信

ICB DoIP参数 (实际验证通过):
  DoIP地址:  172.31.6.11:13400  (8295_QNX 核)
  路由激活TA: 0x0010
  诊断目标地址(Activated): 0x1000
  Tester逻辑地址: 0x0E80

Wireshark验证:
  - LabVIEW使用Type=0x0005 (RoutingActivationRequest)
  - 载荷: 0e 80 00 10 00 00 00 (7字节)
  - 响应先到 0x8002 (ACK), 再到 0x8001 (UDS响应)
"""

import socket
import struct
import time
from typing import Optional, Dict, List

_DEBUG = False  # 调试开关

# ===================== DoIP常量 =====================

DOIP_VERSION       = 0x02
DOIP_INVERSION     = 0xFD

# DoIP载荷类型
DOIP_TYPE_NACK           = 0x0000
DOIP_TYPE_VEHICLE_ID_REQ = 0x0003
DOIP_TYPE_VEHICLE_ID_RSP = 0x0004
DOIP_TYPE_ROUTING_REQ    = 0x0005  # ← 路由激活请求!
DOIP_TYPE_ROUTING_RSP    = 0x0006  # ← 路由激活响应!
DOIP_TYPE_DIAG_MSG       = 0x8001  # 诊断消息 (目标→Tester)
DOIP_TYPE_DIAG_ACK       = 0x8002  # 诊断消息ACK
DOIP_TYPE_DIAG_NACK      = 0x8003  # 诊断消息负ACK

# ICB网络地址
ICB_DOIP_IP       = "172.31.6.11"  # 实际IP! (8295_QNX)
ICB_DOIP_PORT     = 13400
ICB_ROUTING_TA    = 0x0000         # IDS 验证：路由激活目标地址 (0x0000 路由更广)
ICB_DIAG_TA       = 0x1000         # 诊断消息目标地址 (路由响应返回)
ICB_LOGICAL_ADDR  = ICB_DIAG_TA    # 别名 (向后兼容)
TESTER_LOGICAL_ADDR = 0x0E80       # Tester逻辑地址


class DoIPError(Exception):
    """DoIP通信异常基类"""
    pass


class DoIPConnectionError(DoIPError):
    """连接异常"""
    pass


class DoIPRoutingError(DoIPError):
    """路由激活异常"""
    pass


class DoIPClient:
    """
    ISO 13400 DoIP 通信客户端 (ICB专用)

    已验证的通信流程:
    1. connect() → TCP连接 172.31.6.11:13400
    2. routing_activate() → Type=0x0005, Payload=0e 80 00 10 00 00 00
    3. send_diagnostic(uds_bytes) → TA=0x1000, 接收ACK+UDS响应

    示例:
        client = DoIPClient()
        client.connect()
        client.routing_activate()
        resp = client.send_diagnostic(bytes.fromhex('3E00'))
        client.disconnect()
    """

    def __init__(self, ip: str = ICB_DOIP_IP, port: int = ICB_DOIP_PORT,
                 source_addr: int = TESTER_LOGICAL_ADDR,
                 routing_ta: int = ICB_ROUTING_TA,
                 timeout: float = 5.0):
        self.ip = ip
        self.port = port
        self.source_addr = source_addr
        self.routing_ta = routing_ta  # 路由激活目标地址
        self.timeout = timeout

        self.sock: Optional[socket.socket] = None
        self.connected = False
        self.routing_activated = False

    # --------------------------------------------------
    # 连接管理
    # --------------------------------------------------

    def connect(self) -> bool:
        """建立TCP连接到DoIP设备"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.sock.connect((self.ip, self.port))
            self.connected = True
            return True
        except Exception as e:
            self.connected = False
            raise DoIPConnectionError(f"连接失败 {self.ip}:{self.port}: {e}")

    def disconnect(self):
        """断开连接"""
        self.routing_activated = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None
        self.connected = False

    # --------------------------------------------------
    # 底层收发
    # --------------------------------------------------

    def _send_doip(self, payload_type: int, payload: bytes):
        """发送DoIP报文"""
        if not self.connected or not self.sock:
            raise DoIPConnectionError("未连接")
        header = struct.pack('!BBHI', DOIP_VERSION, DOIP_INVERSION,
                             payload_type, len(payload))
        self.sock.sendall(header + payload)

    def _recv_all(self, n: int, timeout: float = None) -> Optional[bytes]:
        """精确读取n字节"""
        if not self.sock:
            return None
        old_timeout = self.sock.gettimeout()
        try:
            self.sock.settimeout(timeout or self.timeout)
            data = b''
            while len(data) < n:
                chunk = self.sock.recv(n - len(data))
                if not chunk:
                    print(f"[RECV_DEBUG] _recv_all({n}) 读到空chunk, 已有{len(data)}/{n}字节, timeout={timeout}")
                    return None
                data += chunk
            return data
        except socket.timeout:
            print(f"[RECV_DEBUG] _recv_all({n}) 超时, 已有{len(data)}/{n}字节, timeout={timeout}")
            return None
        finally:
            self.sock.settimeout(old_timeout)

    def _recv_doip(self, timeout: float = None) -> Optional[Dict]:
        """接收一个完整的DoIP报文"""
        if not self.sock:
            return None

        header = self._recv_all(8, timeout)
        if not header or len(header) < 8:
            return None

        pt = struct.unpack('!H', header[2:4])[0]
        pl = struct.unpack('!I', header[4:8])[0]

        if pl > 0:
            payload = self._recv_all(pl, timeout)
            if payload is None:
                return None
        else:
            payload = b''

        return {'type': pt, 'length': pl, 'payload': payload}

    def _recv_all_doip(self, timeout: float = None, broadcast_mode: bool = False) -> List[Dict]:
        """
        接收所有可用的DoIP报文

        使用原始timeout进行首次接收，之后策略：
        - 刚收到ACK (0x8002) 时：继续等 P2* max 时间，用 0.3s 超时
        - 已收到 UDS 响应 (0x8001) 时：
          - 广播模式：等 0.5s 收集所有 CAN ECU 的慢速响应
          - 单ECU模式：等 0.05s（一般不需要等更多数据）
        - 最多等1秒, 但不超过剩余timeout
        """
        msgs = []
        elapsed = 0.0
        import time
        t0 = time.monotonic()

        while True:
            msg = self._recv_doip(timeout)
            if msg is None:
                break
            msgs.append(msg)

            # 调试：打印收到的消息数量和类型
            diag_count = sum(1 for m in msgs if m['type'] == DOIP_TYPE_DIAG_MSG)
            if diag_count > 0 and diag_count <= 30:
                last_diag = [m for m in msgs if m['type'] == DOIP_TYPE_DIAG_MSG][-1]
                if len(last_diag['payload']) >= 4:
                    sa = (last_diag['payload'][0]<<8)|last_diag['payload'][1]
                    print(f"[DOIP_DEBUG] msg#{len(msgs)} type=0x{msg['type']:04X} diag#{diag_count} SA=0x{sa:04X}")

            # 已收到 UDS 响应 → 根据模式决定等待时间
            if any(m['type'] == DOIP_TYPE_DIAG_MSG for m in msgs):
                # 检查是否是 0x78 Response Pending，如果是则等待更长时间
                last_msg = [m for m in msgs if m['type'] == DOIP_TYPE_DIAG_MSG][-1]
                uds = last_msg['payload'][4:] if len(last_msg['payload']) >= 4 else b''
                is_pending = len(uds) >= 3 and uds[0] == 0x7F and uds[2] == 0x78
                if broadcast_mode:
                    wait = 3.0
                elif is_pending:
                    wait = 2.0  # 0x78 需要等待更长时间（IAM 需要约 230ms）
                else:
                    wait = 0.05
            # 只收到 ACK → 给 ECU 留响应时间
            elif any(m['type'] == DOIP_TYPE_DIAG_ACK for m in msgs):
                wait = 0.3
            else:
                wait = 0.5

            elapsed = time.monotonic() - t0
            if timeout is not None:
                remaining = timeout - elapsed
                timeout = min(max(wait, 0.02), remaining)
            else:
                timeout = wait
            if timeout <= 0:
                break
        return msgs

    # --------------------------------------------------
    # 路由激活 (关键流程)
    # --------------------------------------------------

    def routing_activate(self) -> Dict:
        """
        DoIP路由激活（带重试，适配 ICB 网关行为）

        IDT Wireshark 验证:
          ICB 网关对 TA=0x0000 的行为:
            前 1-2 次: TYPE_0007 + 断连接 → 需用新 TCP 连接重试
            第 3 次: 直接回 ROUTING_RSP (~1s)

        Returns:
            {'success': bool, 'code': str, 'activated_addr': int}
        """
        if not self.connected:
            raise DoIPConnectionError("请先连接")

        DOIP_TYPE_0007 = 0x0007
        MAX_RETRIES = 3
        last_error = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                payload = struct.pack('!HH', self.source_addr, self.routing_ta)
                payload += bytes([0x00, 0x00, 0x00])

                self._send_doip(DOIP_TYPE_ROUTING_REQ, payload)

                # 循环跳过 TYPE_0007，等 ROUTING_RSP
                while True:
                    resp = self._recv_doip(timeout=3.0)
                    if not resp:
                        raise DoIPRoutingError(f"第{attempt}次: 无响应")
                    if resp['type'] == DOIP_TYPE_NACK:
                        code = resp['payload'][0] if resp['payload'] else 0xFF
                        raise DoIPRoutingError(f"第{attempt}次: NACK code=0x{code:02X}")
                    if resp['type'] == DOIP_TYPE_0007:
                        continue
                    if resp['type'] != DOIP_TYPE_ROUTING_RSP:
                        raise DoIPRoutingError(f"第{attempt}次: 意外类型 0x{resp['type']:04X}")
                    break

                rsp = resp['payload']
                if len(rsp) < 9:
                    raise DoIPRoutingError(f"第{attempt}次: 响应过短 {len(rsp)}字节")

                client_addr = struct.unpack('!H', rsp[0:2])[0]
                activated_addr = struct.unpack('!H', rsp[2:4])[0]
                code = rsp[4]

                if code not in (0x05, 0x06, 0x0A, 0x0B, 0x10):
                    raise DoIPRoutingError(f"第{attempt}次: 激活失败 code=0x{code:02X}")

                self.routing_activated = True
                if _DEBUG:
                    print(f"  [DoIP] 路由激活成功: Client=0x{client_addr:04X}, "
                          f"Socket=0x{activated_addr:04X}, Code=0x{code:02X}")
                return {'success': True, 'code': hex(code), 'activated_addr': activated_addr}

            except (DoIPRoutingError, ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError) as e:
                last_error = e
                if attempt < MAX_RETRIES:
                    if _DEBUG:
                        print(f"  [DoIP] 第{attempt}次失败: {e}，断连重试...")
                    self.disconnect()
                    import time
                    time.sleep(0.5)
                    self.connect()
                else:
                    raise DoIPRoutingError(f"路由激活失败（{MAX_RETRIES}次重试）: {last_error}")

        raise DoIPRoutingError(f"路由激活失败（{MAX_RETRIES}次重试）: {last_error}")

        return {
            'success': True,
            'code': f"0x{code:02X}",
            'activated_addr': activated_addr,
            'client_addr': client_addr,
        }

    # --------------------------------------------------
    # 诊断消息收发
    # --------------------------------------------------

    def send_diagnostic(self, uds_request: bytes, timeout: float = 5.0, target_addr: Optional[int] = None) -> Optional[bytes]:
        """
        发送UDS诊断消息 (通过DoIP)

        Args:
            uds_request: UDS请求字节 (如 bytes.fromhex('3E00'))
            timeout: 等待响应超时(秒)

        Returns:
            UDS响应字节 或 None (超时/失败)

        注意:
            - 目标地址使用路由激活返回的地址 (ICB=0x1000)
            - 响应先到 0x8002 (ACK), 再到 0x8001 (UDS响应)
        """
        if not self.connected:
            raise DoIPConnectionError("未连接")
        if not self.routing_activated:
            raise DoIPRoutingError("请先调用 routing_activate()")

        # 目标地址：支持自定义 (用于 IPD 转发等)，默认使用 ICB_DIAG_TA (0x1000)
        diag_target = target_addr if target_addr is not None else ICB_DIAG_TA


        # 发送前清空缓冲区中残留的响应（之前超时后延迟到达的包）
        try:
            self._recv_all_doip(timeout=0.1)
        except Exception:
            pass

        # 构造诊断消息: SA(2) + TA(2) + UDS请求
        payload = struct.pack('!HH', self.source_addr, diag_target)
        payload += uds_request

        try:
            self._send_doip(DOIP_TYPE_DIAG_MSG, payload)
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError) as e:
            print(f"DoIP 连接断开：{e}，尝试重连...")
            try:
                self.connect()
                self.routing_activate()
                print("DoIP 重连成功，重试发送")
                self._send_doip(DOIP_TYPE_DIAG_MSG, payload)
            except Exception as e2:
                print(f"DoIP 重连失败：{e2}")
                return None

        # 接收响应 (可能包含多个DoIP报文)
        msgs = self._recv_all_doip(timeout)
        # 遍历所有收到的消息，跳过 0x78 返回最终响应
        last_uds = None
        for msg in msgs:
            if msg['type'] == DOIP_TYPE_DIAG_MSG:
                # 0x8001 = UDS 响应消息
                rsp = msg['payload']
                if len(rsp) >= 4:
                    uds = rsp[4:]
                    last_uds = uds
                    # 跳过 0x78，继续查找最终响应
                    if len(uds) >= 3 and uds[0] == 0x7F and uds[2] == 0x78:
                        continue
                    # 返回非 0x78 响应（59 02 FF 等）
                    return uds

        # 如果只有 0x78，返回 0x78
        return last_uds

    def send_diagnostic_multi(self, uds_request, timeout=3.0, target_addr=None, broadcast_mode=True):
        """Send UDS diagnostic and return ALL ECU responses (for functional broadcast 0xEFFF)"""
        if not self.connected:
            raise DoIPConnectionError("not connected")
        if not self.routing_activated:
            raise DoIPRoutingError("routing not activated")
        diag_target = target_addr if target_addr is not None else ICB_DIAG_TA
        try:
            self._recv_all_doip(timeout=0.1)
        except Exception:
            pass
        payload = struct.pack("!HH", self.source_addr, diag_target)
        payload += uds_request
        try:
            self._send_doip(DOIP_TYPE_DIAG_MSG, payload)
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError) as e:
            try:
                self.connect()
                self.routing_activate()
                self._send_doip(DOIP_TYPE_DIAG_MSG, payload)
            except Exception:
                return []

        # IDS 兼容: 请求发出去后等约 3.5s 收集所有控制器缓慢返回的响应
        # 注意：不发 TesterPresent，仅延长等待窗口
        import time
        all_msgs = []
        phase_timeouts = [1.5, 2.0]  # 先等 1.5s 快速 ECU，再等 2s 慢速 ECU
        for phase_t in phase_timeouts:
            msgs = self._recv_all_doip(phase_t, broadcast_mode=True)
            all_msgs.extend(msgs if msgs else [])

        msgs = all_msgs
        results = []
        seen = set()
        for msg in msgs:
            if msg["type"] == DOIP_TYPE_DIAG_MSG:
                rsp = msg["payload"]
                if len(rsp) >= 4:
                    source_addr = struct.unpack("!H", rsp[0:2])[0]
                    uds = rsp[4:]
                    # 不跳过 NRC 0x78 开头的大消息——ICB 网关常把多个 CAN ECU 的 59 02 FF 段和 0x78 拼在同一个 DoIP 消息里
                    # _parse_dtc_02_response 自己会通过 find(b'\x59\x02') 跳过 0x78 字节
                    if source_addr in seen:
                        for j, r in enumerate(results):
                            if r["source_addr"] == source_addr:
                                results[j]["uds"] = results[j]["uds"] + uds
                                break
                    else:
                        seen.add(source_addr)
                        results.append({"source_addr": source_addr, "uds": uds})
        print(f"[DOIP_DEBUG] send_diagnostic_multi: {len(results)} ECUs from {len(msgs)} messages")
        return results
    def send_raw(self, hex_string: str) -> str:
        """
        发送十六进制UDS指令

        Args:
            hex_string: 如 "22 F1 87" 或 "22F187"

        Returns:
            格式化响应文本
        """
        # 解析hex
        clean = hex_string.replace(' ', '').replace('\t', '').replace('\n', '')
        try:
            request = bytes.fromhex(clean)
        except ValueError as e:
            return f"❌ 十六进制格式错误: {e}"

        response = self.send_diagnostic(request)
        if response is None:
            return "⏰ 无响应"

        # 格式化
        resp_hex = response.hex().upper()
        formatted = ' '.join(resp_hex[i:i+2] for i in range(0, len(resp_hex), 2))

        # 附加解析
        annotation = self._annotate(response)

        return f"{formatted}\n{annotation}"

    def send_raw_with_log(self, hex_string: str) -> Dict:
        """
        发送原始UDS指令并返回结构化结果

        Returns:
            dict: {request, response_hex, response_decoded, success, nrc, nrc_desc, error}
        """
        result = {
            'request': hex_string,
            'response_hex': '',
            'response_decoded': '',
            'success': False,
            'nrc': None,
            'nrc_desc': '',
            'error': None,
        }

        clean = hex_string.replace(' ', '').replace('\t', '').replace('\n', '')
        try:
            request = bytes.fromhex(clean)
        except ValueError as e:
            result['error'] = f"十六进制格式错误: {e}"
            return result

        try:
            response = self.send_diagnostic(request)
        except Exception as e:
            result['error'] = str(e)
            return result

        if response is None:
            result['error'] = '超时无响应'
            return result

        resp_hex = response.hex().upper()
        formatted = ' '.join(resp_hex[i:i+2] for i in range(0, len(resp_hex), 2))
        result['response_hex'] = formatted

        # 解析UDS响应
        if response and len(response) > 0:
            sid = response[0]
            if sid == 0x7F:
                req_sid = response[1] if len(response) > 1 else 0
                nrc = response[2] if len(response) > 2 else 0
                result['success'] = False
                result['nrc'] = nrc
                result['nrc_desc'] = self._nrc_desc(nrc, req_sid)
                result['response_decoded'] = f"❌ NRC 0x{nrc:02X}: {result['nrc_desc']}"
            else:
                result['success'] = True
                svc = response[0] - 0x40
                result['response_decoded'] = f"✓ 服务0x{svc:02X}响应成功"

        return result

    @staticmethod
    def _nrc_desc(nrc: int, sid: int = 0) -> str:
        """UDS NRC错误码描述"""
        nrc_map = {
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
            0x78: "ResponsePending",
        }
        return nrc_map.get(nrc, f"Unknown(0x{nrc:02X})")

    @staticmethod
    def _annotate(response: bytes) -> str:
        """附加UDS响应说明"""
        if not response:
            return "空响应"
        sid = response[0]
        if sid == 0x7F:
            nrc = response[2] if len(response) > 2 else 0
            return f"❌ NRC 0x{nrc:02X}"

        svc = sid - 0x40
        if svc == 0x10:
            return f"✓ 会话切换成功"
        elif svc == 0x22:
            data = ' '.join(f'{b:02X}' for b in response[1:])
            return f"✓ DID数据读取 | {data}"
        elif svc == 0x2E:
            return f"✓ DID写入成功"
        elif svc == 0x19:
            return f"✓ DTC信息"
        elif svc == 0x14:
            return f"✓ DTC清除成功"
        elif svc == 0x3E:
            return f"✓ TesterPresent保活"
        elif svc == 0x31:
            return f"✓ 例程执行结果"
        elif svc == 0x27:
            return f"✓ 安全访问"
        elif svc == 0x2F:
            return f"✓ IO控制"
        return f"✓ 服务0x{svc:02X}响应"


# ===================== 快速测试 =====================

def test_doip_connection():
    """快速验证DoIP通信"""
    client = DoIPClient()

    try:
        print(f"连接 {ICB_DOIP_IP}:{ICB_DOIP_PORT} ...")
        client.connect()
        print("✓ TCP连接成功")

        print(f"路由激活 ...")
        result = client.routing_activate()
        print(f"✓ 路由激活成功! 目标地址: 0x{result['activated_addr']:04X}")

        print(f"\n1. TesterPresent (3E 00):")
        resp = client.send_diagnostic(bytes.fromhex('3E00'))
        print(f"   {' '.join(f'{b:02X}' for b in resp) if resp else '无响应'}")

        print(f"\n2. 读取DID 0xF187 (22 F1 87):")
        resp = client.send_diagnostic(bytes.fromhex('22F187'))
        if resp and len(resp) > 3:
            data = resp[3:]  # 跳过 62 F1 87
            print(f"   数据: {' '.join(f'{b:02X}' for b in data)}")
        else:
            print(f"   {' '.join(f'{b:02X}' for b in resp) if resp else '无响应'}")

        print(f"\n3. 读取DTC (19 01 FF):")
        resp = client.send_diagnostic(bytes.fromhex('1901FF'))
        print(f"   {' '.join(f'{b:02X}' for b in resp) if resp else '无响应'}")

        if resp and resp[0] == 0x59:
            num = (len(resp) - 2) // 4
            print(f"   共{num}条DTC")

    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        client.disconnect()
        print("\n✓ 连接已断开")


if __name__ == '__main__':
    test_doip_connection()




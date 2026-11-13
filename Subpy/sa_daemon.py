"""
sa_daemon.py — 常驻 32-bit Python 进程，保持 sa.dll 加载
通过 stdin/stdout 通信：
  stdin:  <seed_hex> <algo_hex>\n
  stdout: <key_hex>\n
  stderr: ERROR: <msg>\n

启动方式由 sa_calc.py 管理
"""

import sys
import os
import ctypes
import json

DLL_DIR = os.path.join(os.path.dirname(__file__), '..', 'dll')
DLL_PATH = os.path.join(DLL_DIR, 'sa.dll')

os.chdir(DLL_DIR)
os.environ['PATH'] = DLL_DIR + os.pathsep + os.environ.get('PATH', '')

# 加载 sa.dll
try:
    sa = ctypes.WinDLL(DLL_PATH)
    func = sa.saturn_key_generate
    func.argtypes = [
        ctypes.c_void_p, ctypes.c_int, ctypes.c_int,
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int,
        ctypes.POINTER(ctypes.c_int),
    ]
    func.restype = ctypes.c_int
except Exception as e:
    sys.stderr.write(f'ERROR: 加载 sa.dll 失败: {e}\n')
    sys.exit(1)

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

while True:
    line = sys.stdin.readline()
    if not line:
        break  # stdin closed

    line = line.strip()
    if not line:
        continue
    if line == 'EXIT':
        break
    if line == 'PING':
        sys.stdout.write('PONG\n')
        sys.stdout.flush()
        continue

    parts = line.split()
    seed_hex = parts[0] if len(parts) > 0 else ''
    algo_hex = parts[1] if len(parts) > 1 else '00001042'

    try:
        seed = bytes.fromhex(seed_hex)
        algo = bytes.fromhex(algo_hex)
    except ValueError:
        sys.stderr.write(f'ERROR: 无效 hex: {line}\n')
        sys.stderr.flush()
        continue

    # 准备参数
    seed_arr = (ctypes.c_ubyte * len(seed))(*seed)
    algo_arr = (ctypes.c_ubyte * len(algo))(*algo)
    key_arr = (ctypes.c_ubyte * 8)()
    key_len = ctypes.c_int(0)

    r = func(
        ctypes.cast(seed_arr, ctypes.c_void_p),
        len(seed), 1,
        ctypes.cast(algo_arr, ctypes.c_void_p),
        ctypes.cast(key_arr, ctypes.c_void_p),
        len(algo),
        ctypes.byref(key_len),
    )

    if key_len.value > 0:
        key = bytes(key_arr[:key_len.value])
        sys.stdout.write(key.hex().upper() + '\n')
    else:
        sys.stderr.write(f'ERROR: 计算失败 r={r} kLen={key_len.value}\n')

    sys.stdout.flush()
    sys.stderr.flush()
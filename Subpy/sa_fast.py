"""
sa_fast.py - 快速密钥计算 (直接调用 sa.dll，不通过 daemon)
用于对时序要求严格的场景 (如 ICB 安全访问)
"""

import ctypes
import os

# DLL 在 ITS 根目录的 dll 文件夹
DLL_DIR = os.path.join(os.path.dirname(__file__), '..', 'dll')
DLL_DIR = os.path.abspath(DLL_DIR)
DLL_PATH = os.path.join(DLL_DIR, 'sa.dll')

# 加载 sa.dll
os.chdir(DLL_DIR)
os.environ['PATH'] = DLL_DIR + os.pathsep + os.environ.get('PATH', '')

try:
    sa = ctypes.WinDLL(DLL_PATH)
    func = sa.saturn_key_generate
    func.argtypes = [
        ctypes.c_void_p, ctypes.c_int, ctypes.c_int,
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int,
        ctypes.POINTER(ctypes.c_int),
    ]
    func.restype = ctypes.c_int
    _DLL_LOADED = True
except Exception as e:
    print(f"Warning: sa.dll 加载失败：{e}")
    _DLL_LOADED = False


def calc_key_fast(seed_hex: str, algo_hex: str = '00001042') -> bytes:
    """
    快速计算安全访问密钥 (直接调用 DLL，<1ms)
    
    参数：
        seed_hex: 16 进制种子，如 '3155971E'
        algo_hex: 16 进制算法号，如 '00001042'
    
    返回：
        4 字节密钥 bytes
    
    异常：
        RuntimeError: 计算失败
    """
    if not _DLL_LOADED:
        raise RuntimeError("sa.dll 未加载")
    
    # 格式化 seed/algo
    seed_clean = seed_hex.strip().replace(' ', '').replace('0x', '').replace('0X', '')
    algo_clean = algo_hex.strip().replace(' ', '').replace('0x', '').replace('0X', '')
    
    try:
        seed = bytes.fromhex(seed_clean)
        algo = bytes.fromhex(algo_clean)
    except ValueError as e:
        raise RuntimeError(f"无效的 hex 格式：{e}")
    
    # 准备数组
    seed_arr = (ctypes.c_ubyte * len(seed))(*seed)
    algo_arr = (ctypes.c_ubyte * len(algo))(*algo)
    key_arr = (ctypes.c_ubyte * 8)()
    key_len = ctypes.c_int(0)
    
    # 调用 DLL
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
        return key
    else:
        raise RuntimeError(f"密钥计算失败：r={r}, kLen={key_len.value}")


if __name__ == '__main__':
    import time
    # 测试速度
    seed = '3155971E'
    algo = '00001042'
    
    t0 = time.perf_counter()
    key = calc_key_fast(seed, algo)
    dt = time.perf_counter() - t0
    
    print(f"Seed: {seed}")
    print(f"Algo: {algo}")
    print(f"Key: {key.hex().upper()}")
    print(f"Time: {dt*1000:.2f}ms")

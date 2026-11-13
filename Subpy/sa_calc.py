"""
安全访问密钥计算模块 (ICB)
通过 32-bit Python 常驻进程调用 sa.dll 的 saturn_key_generate

常驻进程策略：
- 首次 calc_key() 时启动 32-bit Python daemon 并保持
- sa.dll 常驻加载，避免每次启动 32-bit 进程的开销
- 后续 calc_key() 通过 stdin/stdout 快速通信（毫秒级）

路径策略：
- 打包后：dll/ 放在 sys.executable 同级目录
- 开发时：dll/ 放在项目根目录 (ITS/dll/)
"""

import subprocess
import sys
import os
import atexit
from pathlib import Path

# ── 路径解析 ──
if getattr(sys, 'frozen', False):
    _BASE = Path(sys.executable).parent
else:
    _BASE = Path(__file__).resolve().parent.parent

SA_DIR = _BASE / 'dll'
SA_DLL = SA_DIR / 'sa.dll'
_DAEMON_SCRIPT = SA_DIR / 'sa_daemon.py'
_PY32 = SA_DIR / 'python32' / 'python.exe'

# ── 守护进程 ──
_daemon_proc: subprocess.Popen | None = None


def _start_daemon():
    """启动 32-bit Python daemon"""
    global _daemon_proc
    if _daemon_proc is not None and _daemon_proc.poll() is None:
        return  # 已在运行

    if not _PY32.exists():
        raise RuntimeError(
            f"32-bit Python 未找到: {_PY32}\n"
            f"需要将 python-3.10.11-embed-win32 解压到 {_PY32.parent}"
        )

    env = dict(os.environ)
    env['PATH'] = str(SA_DIR) + os.pathsep + env.get('PATH', '')

    _daemon_proc = subprocess.Popen(
        [str(_PY32), str(_DAEMON_SCRIPT)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(SA_DIR),
        env=env,
        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
    )

    # 验证 daemon 是否存活
    try:
        _daemon_proc.stdin.write(b'PING\n')
        _daemon_proc.stdin.flush()
        pong = _daemon_proc.stdout.readline()
        if pong.strip() != b'PONG':
            raise RuntimeError("daemon PING 失败")
    except Exception as e:
        _stop_daemon()
        raise RuntimeError(f"daemon 启动失败: {e}")

    # 注册退出清理
    atexit.register(_stop_daemon)


def _stop_daemon():
    """停止 daemon 进程"""
    global _daemon_proc
    if _daemon_proc is not None:
        try:
            if _daemon_proc.poll() is None:
                _daemon_proc.stdin.write(b'EXIT\n')
                _daemon_proc.stdin.flush()
                _daemon_proc.wait(timeout=3)
        except Exception:
            try:
                _daemon_proc.kill()
            except Exception:
                pass
        _daemon_proc = None


def calc_key(seed_hex: str, algo_hex: str = '00001042') -> bytes:
    """
    计算安全访问密钥
    通过常驻 32-bit Python daemon 调用 sa.dll

    参数：
        seed_hex: 16进制种子，如 '411B5BD6'
        algo_hex: 16进制算法号，如 '00001042'

    返回：
        4 字节密钥 bytes

    异常：
        RuntimeError: 计算失败
    """
    if not SA_DLL.exists():
        raise RuntimeError(f"sa.dll 未找到: {SA_DLL}")

    # 确保 daemon 在运行
    _start_daemon()

    # 格式化 seed/algo
    seed_clean = seed_hex.strip().replace(' ', '').replace('0x', '').replace('0X', '')
    algo_clean = algo_hex.strip().replace(' ', '').replace('0x', '').replace('0X', '')

    # 发送计算请求
    request = f"{seed_clean} {algo_clean}\n".encode('utf-8')

    try:
        _daemon_proc.stdin.write(request)
        _daemon_proc.stdin.flush()
        response = _daemon_proc.stdout.readline()
    except Exception as e:
        # daemon 挂了，重启一次
        _stop_daemon()
        _start_daemon()
        try:
            _daemon_proc.stdin.write(request)
            _daemon_proc.stdin.flush()
            response = _daemon_proc.stdout.readline()
        except Exception as e2:
            raise RuntimeError(f"密钥计算失败 (daemon重启后仍失败): {e2}")

    if not response:
        raise RuntimeError("密钥计算失败: daemon 无响应")

    key_str = response.decode('utf-8', errors='replace').strip()

    # 检查错误
    if key_str.startswith('ERROR'):
        raise RuntimeError(f"密钥计算错误: {key_str}")

    try:
        key = bytes.fromhex(key_str)
        return key
    except ValueError:
        raise RuntimeError(f"密钥计算失败: 无法解析响应 '{key_str}'")


if __name__ == '__main__':
    import time
    seed = sys.argv[1] if len(sys.argv) > 1 else '411B5BD6'
    algo = sys.argv[2] if len(sys.argv) > 2 else '00001042'

    # 预热测试
    t0 = time.monotonic()
    try:
        key = calc_key(seed, algo)
        dt = time.monotonic() - t0
        print(f'Key: {key.hex().upper()} ({dt*1000:.0f}ms)')

        # 第二次调用（检验热路径速度）
        t0 = time.monotonic()
        key2 = calc_key(seed, algo)
        dt = time.monotonic() - t0
        print(f'Key2: {key.hex().upper()} ({dt*1000:.0f}ms)')
    except Exception as e:
        print(f'ERROR: {e}')
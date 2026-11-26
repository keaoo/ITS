# -*- coding: utf-8 -*-
"""Headless PySide6 smoke test for the ITS main window.

This test only creates the UI and checks that the packaged executable can stay
alive briefly. It does not click vehicle controls or connect to any device.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import traceback
from pathlib import Path


# GitHub-hosted Windows runners do not provide an interactive desktop session.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QAction

from ITS_app import NotepadApp


OUTPUT_DIR = Path(os.environ.get("UI_TEST_OUTPUT", "ui-test-output"))


def process_events(app: QApplication, duration_ms: int) -> None:
    deadline = time.monotonic() + duration_ms / 1000
    while time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.01)
    app.processEvents()


def run_main_window_test(app: QApplication) -> dict[str, object]:
    window = NotepadApp()
    try:
        window.show()
        process_events(app, 100)

        if not window.isVisible():
            raise AssertionError("主窗口没有进入可见状态")

        expected_actions = {
            "综合压测",
            "工具",
            "录音工具",
            "音频探测",
            "视觉设置",
        }
        action_texts = {
            action.text()
            for action in window.findChildren(QAction)
            if action.text()
        }
        missing_actions = sorted(expected_actions - action_texts)
        if missing_actions:
            raise AssertionError(f"关键菜单项缺失: {missing_actions}")

        screenshot_path = OUTPUT_DIR / "main-window.png"
        if not window.grab().save(str(screenshot_path), "PNG"):
            raise AssertionError(f"主窗口截图保存失败: {screenshot_path}")

        if not screenshot_path.is_file() or screenshot_path.stat().st_size == 0:
            raise AssertionError("主窗口截图文件为空")

        return {
            "window_title": window.windowTitle(),
            "window_size": [window.width(), window.height()],
            "visible": window.isVisible(),
            "checked_actions": sorted(expected_actions),
            "screenshot": str(screenshot_path),
        }
    finally:
        window.close()
        process_events(app, 50)


def run_packaged_executable_test(executable: Path) -> dict[str, object]:
    if not executable.is_file():
        raise AssertionError(f"打包后的 EXE 不存在: {executable}")

    creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    process = subprocess.Popen(
        [str(executable)],
        cwd=str(executable.parent),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creation_flags,
    )
    try:
        time.sleep(3)
        return_code = process.poll()
        if return_code is not None:
            raise AssertionError(f"打包后的 EXE 提前退出，返回码: {return_code}")
        return {"executable": str(executable), "alive_after_seconds": 3}
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def main() -> int:
    parser = argparse.ArgumentParser(description="ITS UI smoke test")
    parser.add_argument("--executable", type=Path, help="optional packaged EXE to smoke test")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for output_name in ("main-window.png", "ui-smoke-result.json", "ui-smoke-error.txt"):
        output_file = OUTPUT_DIR / output_name
        if output_file.exists():
            output_file.unlink()
    result: dict[str, object] = {}
    app = QApplication.instance() or QApplication(sys.argv)
    try:
        result["main_window"] = run_main_window_test(app)
        if args.executable:
            result["packaged_executable"] = run_packaged_executable_test(args.executable)
        result_path = OUTPUT_DIR / "ui-smoke-result.json"
        result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception:
        error_path = OUTPUT_DIR / "ui-smoke-error.txt"
        error_path.write_text(traceback.format_exc(), encoding="utf-8")
        print(traceback.format_exc(), file=sys.stderr)
        return 1
    finally:
        app.quit()


if __name__ == "__main__":
    raise SystemExit(main())

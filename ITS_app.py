#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整项目示例：记事本应用 (PySide6 版本)
纯代码实现一个简单的记事本，包含菜单栏、工具栏、文本编辑区
"""
import ctypes
import json
import sys
import os
import subprocess
import datetime
import re
import struct
import uuid
# 🎯 优化：延迟导入大库，只在需要时导入
# import pandas as pd  # 延迟到 red_excel 函数中导入
# import serial.tools.list_ports  # 延迟到需要时导入
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QDialog, QFileDialog, QMessageBox, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QGroupBox, QFormLayout, QTextEdit, QComboBox,
    QLabel, QListWidget, QListWidgetItem, QSizePolicy)
from PySide6.QtGui import QAction, QDoubleValidator, QIntValidator, QColor
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import QSplitter
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QSize
from PySide6.QtWidgets import QTableWidget
from PySide6.QtWidgets import QHeaderView
# ICB DoIP 诊断客户端
from Subpy.doip_client import DoIPClient, ICB_DOIP_IP, ICB_DOIP_PORT, ICB_LOGICAL_ADDR, TESTER_LOGICAL_ADDR, DOIP_TYPE_DIAG_MSG
from Subpy.ipd_doip_config import IPD_DOIP_IP, IPD_DOIP_PORT, IPD_LOGICAL_ADDR
from Subpy.adcu_doip_config import ADCU_DOIP_IP, ADCU_DOIP_PORT, ADCU_LOGICAL_ADDR, ADCU_PHYSICAL_ADDR
from Subpy.dpp_doip_config import DPP_DOIP_IP, DPP_DOIP_PORT, DPP_LOGICAL_ADDR, DPP_PHYSICAL_ADDR, DPP_ROUTING_TA
from Subpy.epmcu_doip_config import EPMCU_DOIP_IP, EPMCU_DOIP_PORT, EPMCU_PHYSICAL_ADDR, EPMCU_ROUTING_TA
from Subpy.icb_doip_config import ICB_SECURITY_ALGO, IPD_SECURITY_ALGO
from Subpy.eps_doip_config import EPS_DOIP_IP, EPS_DOIP_PORT, EPS_PHYSICAL_ADDR, EPS_ROUTING_TA
from Subpy.ibs_doip_config import IBS_DOIP_IP, IBS_DOIP_PORT, IBS_PHYSICAL_ADDR, IBS_RESPONSE_ADDR, IBS_ROUTING_TA
from Subpy.iam_doip_config import IAM_DOIP_IP, IAM_DOIP_PORT, IAM_LOGICAL_ADDR, IAM_PHYSICAL_ADDR, IAM_RESPONSE_ADDR, IAM_ROUTING_TA, IAM_SECURITY_ALGO
from Subpy.lhzcu_doip_config import LHZCU_DOIP_IP, LHZCU_DOIP_PORT, LHZCU_PHYSICAL_ADDR, LHZCU_RESPONSE_ADDR, LHZCU_SECURITY_ALGO
from Subpy.rhzcu_doip_config import RHZCU_DOIP_IP, RHZCU_DOIP_PORT, RHZCU_PHYSICAL_ADDR, RHZCU_RESPONSE_ADDR, RHZCU_SECURITY_ALGO
from Subpy.rlpoda_doip_config import RLPODA_DOIP_IP, RLPODA_DOIP_PORT, RLPODA_PHYSICAL_ADDR, RLPODA_RESPONSE_ADDR, RLPODA_ROUTING_TA, RLPODA_SECURITY_ALGO
from Subpy.rrpoda_doip_config import RRPODA_DOIP_IP, RRPODA_DOIP_PORT, RRPODA_PHYSICAL_ADDR, RRPODA_RESPONSE_ADDR, RRPODA_ROUTING_TA, RRPODA_SECURITY_ALGO
from Subpy.rzcu_doip_config import RZCU_DOIP_IP, RZCU_DOIP_PORT, RZCU_PHYSICAL_ADDR, RZCU_RESPONSE_ADDR, RZCU_SECURITY_ALGO
from Subpy.rwsl_doip_config import RWSL_DOIP_IP, RWSL_DOIP_PORT, RWSL_PHYSICAL_ADDR, RWSL_RESPONSE_ADDR, RWSL_ROUTING_TA, RWSL_SECURITY_ALGO
from Subpy.scm_doip_config import SCM_DOIP_IP, SCM_DOIP_PORT, SCM_PHYSICAL_ADDR, SCM_RESPONSE_ADDR, SCM_ROUTING_TA, SCM_SECURITY_ALGO
from Subpy.sdm_doip_config import SDM_DOIP_IP, SDM_DOIP_PORT, SDM_PHYSICAL_ADDR, SDM_RESPONSE_ADDR, SDM_ROUTING_TA, SDM_SECURITY_ALGO
from Subpy.ess_doip_config import ESS_DOIP_IP, ESS_DOIP_PORT, ESS_PHYSICAL_ADDR, ESS_RESPONSE_ADDR, ESS_ROUTING_TA, ESS_SECURITY_ALGO
from Subpy.racfp_doip_config import RACFP_DOIP_IP, RACFP_DOIP_PORT, RACFP_PHYSICAL_ADDR, RACFP_RESPONSE_ADDR, RACFP_ROUTING_TA, RACFP_SECURITY_ALGO
from Subpy.fdr_doip_config import FDR_DOIP_IP, FDR_DOIP_PORT, FDR_PHYSICAL_ADDR, FDR_RESPONSE_ADDR, FDR_ROUTING_TA, FDR_SECURITY_ALGO
from Subpy.flpoda_doip_config import FLPODA_DOIP_IP, FLPODA_DOIP_PORT, FLPODA_PHYSICAL_ADDR, FLPODA_RESPONSE_ADDR, FLPODA_ROUTING_TA, FLPODA_SECURITY_ALGO
from Subpy.frpoda_doip_config import FRPODA_DOIP_IP, FRPODA_DOIP_PORT, FRPODA_PHYSICAL_ADDR, FRPODA_RESPONSE_ADDR, FRPODA_ROUTING_TA, FRPODA_SECURITY_ALGO
from Subpy.fwm_doip_config import FWM_DOIP_IP, FWM_DOIP_PORT, FWM_PHYSICAL_ADDR, FWM_RESPONSE_ADDR, FWM_ROUTING_TA, FWM_SECURITY_ALGO
from Subpy.nfcsm_doip_config import NFCSM_DOIP_IP, NFCSM_DOIP_PORT, NFCSM_PHYSICAL_ADDR, NFCSM_RESPONSE_ADDR, NFCSM_ROUTING_TA, NFCSM_SECURITY_ALGO
from Subpy.pma_doip_config import PMA_DOIP_IP, PMA_DOIP_PORT, PMA_PHYSICAL_ADDR, PMA_RESPONSE_ADDR, PMA_ROUTING_TA, PMA_SECURITY_ALGO
from Subpy.cf_doip_config import CF_PHYSICAL_ADDR, CF_FUNCTIONAL_ADDR, CF_SECURITY_ALGO
from Subpy.ccu_doip_config import CCU_PHYSICAL_ADDR, CCU_FUNCTIONAL_ADDR, CCU_SECURITY_ALGO
from Subpy.hodm_doip_config import HODM_PHYSICAL_ADDR, HODM_FUNCTIONAL_ADDR, HODM_SECURITY_ALGO
from Subpy.lvbm_doip_config import LVBM_PHYSICAL_ADDR, LVBM_FUNCTIONAL_ADDR, LVBM_SECURITY_ALGO
from Subpy.nfcam_doip_config import NFCAM_PHYSICAL_ADDR, NFCAM_FUNCTIONAL_ADDR, NFCAM_SECURITY_ALGO
from Subpy.tc_doip_config import TC_PHYSICAL_ADDR, TC_FUNCTIONAL_ADDR, TC_SECURITY_ALGO
from Subpy.tdm_doip_config import TDM_PHYSICAL_ADDR, TDM_FUNCTIONAL_ADDR, TDM_SECURITY_ALGO
from Subpy.peu_doip_config import PEU_PHYSICAL_ADDR, PEU_FUNCTIONAL_ADDR, PEU_SECURITY_ALGO
from Subpy.rhpmwc_doip_config import RHPMWC_PHYSICAL_ADDR, RHPMWC_FUNCTIONAL_ADDR, RHPMWC_SECURITY_ALGO
from Subpy.rlss_doip_config import RLSS_PHYSICAL_ADDR, RLSS_FUNCTIONAL_ADDR, RLSS_SECURITY_ALGO
from Subpy.broadcast_doip_config import BROADCAST_DOIP_IP, BROADCAST_DOIP_PORT, BROADCAST_ROUTING_TA, BROADCAST_PHYSICAL_ADDR, BROADCAST_FUNCTIONAL_ADDR, BROADCAST_SECURITY_ALGO

# ECU source address -> name mapping (for functional broadcast DTC source identification)

# ECU 源地址 -> 名称映射 (用于功能广播识别 DTC 来源，已验证于 IDS trace)
ECU_ADDR_MAP = {
    0x1000: "ICB", 0x1001: "ICB",
    0x100A: "IPD", 0x100B: "IPD",
    0x0500: "FDR", 0x0501: "FDR",
    0x0711: "IAM", 0x0791: "IAM",
    0x15B0: "LHZCU", 0x1630: "LHZCU",
    0x15B1: "RHZCU", 0x1631: "RHZCU",
    0x0770: "RZCU", 0x07F0: "RZCU",
    0x0721: "ADCU", 0x07A1: "ADCU",
    0x05A4: "PMA", 0x0624: "PMA",
    0x0730: "SDM", 0x07B0: "SDM",
    0x05A3: "LVBM", 0x0623: "LVBM",
    0x05C2: "NFCAM", 0x0642: "NFCAM",
    0x07E4: "CCU", 0x0864: "CCU",
    0x05E4: "HODM", 0x0664: "HODM",
    0x07E6: "TC", 0x0866: "TC",
    0x05A5: "TDM", 0x0625: "TDM",
    0x05C1: "CF", 0x0641: "CF",
    0x07E2: "PEU", 0x0862: "PEU",
    0x06D4: "RHPMWC", 0x0754: "RHPMWC",
    0x05C0: "RLSS", 0x0640: "RLSS",
    0x07A6: "IBS",
    0x0727: "SCM", 0x07A7: "SCM",
    0x05D3: "RWSL", 0x0653: "RWSL",
    0x07E0: "ESS", 0x0E60: "ESS",
    0x0726: "AMP", 0x07A6: "AMP",
    0x0735: "IPD", 0x0736: "IPD",
    0x0734: "EPMCU",
    0x05B4: "FLPODA", 0x0634: "FLPODA",
    0x05B5: "FRPODA", 0x0635: "FRPODA",
    0x05B6: "RLPODA", 0x0636: "RLPODA",
    0x05B7: "RRPODA", 0x0637: "RRPODA",
    0x05B0: "FWM", 0x0630: "FWM",
    0x05B1: "NFCSM", 0x0631: "NFCSM",
    0x17E3: "RZCU",  # IDS trace: 0x17E3 (RZCU)
    0x06D5: "DPP",    # IDS trace: 0x06D5
    0x0751: "FDR",    # IDS trace: 0x0751 (FDR secondary?)
    0x05C3: "NFCAM",  # IDS trace: 0x05C3
    0x07E5: "CCU",    # IDS trace: 0x07E5
    0x0787: "ICB",    # IDS trace: 0x0787
}

from Subpy.ids_dtc_db import lookup_dtc as ids_lookup_dtc
from Subpy import sa_calc
# IPD DTC 解析器 (嵌入式版本 - 不依赖外部 Part4 文件)
from Subpy import ipd_dtc_parser
# from pygame.examples.audiocapture import sound  # 禁用自动录音


# 🎯 优化：延迟导入子模块，只在需要时导入（避免打包兼容性问题）
# from Subpy.list_selector import ListSelector
# from Subpy.zonghe_testdialog import ZongheTestDialog
# from Subpy.carchoose_testdialog import carchooseDialog
# from Subpy.visual_setting_dialog import VisualSettingDialog


# ==================== 资源路径工具（兼容 PyInstaller 打包） ====================
def resource_path(relative_path):
    """获取资源绝对路径：开发模式从脚本目录读，打包后从 sys._MEIPASS 临时目录读"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


# ==================== 综合压测子界面 ====================
class ScriptWorker(QThread):
    log_signal = Signal(str, str)
    finished_signal = Signal(int)

    def __init__(self, script_path, working_dir=None, screen_name=""):
        super().__init__()
        self.script_path = script_path
        self.working_dir = working_dir or os.path.dirname(script_path)
        self.screen_name = screen_name
        self.process = None


    def terminate(self):
        """终止正在执行的进程"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except:
                try:
                    self.process.kill()
                except:
                    pass

    def run(self):
        try:
            self.log_signal.emit(">>> 开始执行：" + os.path.basename(self.script_path), "#4CAF50")
            self.log_signal.emit("    脚本路径：" + self.script_path, "#888888")
            self.log_signal.emit("-" * 60, "#555555")

            # 检测是否为 PowerShell 脚本
            is_powershell = self.script_path.lower().endswith('.ps1')

            if is_powershell:
                # 使用 PowerShell 执行，不打开新窗口
                self.process = subprocess.Popen(
                    ['powershell', '-ExecutionPolicy', 'Bypass', '-NoProfile', '-NonInteractive', '-File', self.script_path],
                    cwd=self.working_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='gbk',
                    shell=True  # 添加 shell=True 支持带空格的路径
                )
            else:
                # 使用 CMD 执行批处理
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                self.process = subprocess.Popen(
                    'cmd /c "' + self.script_path + '"',
                    cwd=self.working_dir,  # 设置工作目录
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',  # 批处理已设置 chcp 65001 输出 UTF-8
                    errors='replace',  # 替换无法解码的字符
                    startupinfo=startupinfo,  # 隐藏窗口
                    creationflags=subprocess.CREATE_NO_WINDOW  # 不创建新窗口
                )

            for line in self.process.stdout:
                line = line.strip()
                if line:
                    if "error" in line.lower() or "失败" in line:
                        self.log_signal.emit(line, "#FF5252")
                    elif "success" in line.lower() or "成功" in line:
                        self.log_signal.emit(line, "#4CAF50")
                    else:
                        self.log_signal.emit(line, "#000000")

            return_code = self.process.wait()
            # Windows 返回码可能是无符号值，转成 signed int 避免 Qt Signal 溢出
            if return_code >= 0x80000000:
                return_code = return_code - 0x100000000
            self.log_signal.emit("-" * 60, "#555555")
            if return_code == 0:
                self.log_signal.emit(">>> 执行完成 (返回码：" + str(return_code) + ")", "#4CAF50")
                # 显示日志保存路径（ECUlog 在 Python 执行程序所在目录下）
                if "audio_dump_pull" in self.script_path or "pull_all_map_log" in self.script_path or "diag_display" in self.script_path or "pull_bmlog" in self.script_path or "pull_yuntool" in self.script_path or "eth_dump_pull" in self.script_path or "mic_dump_pull" in self.script_path:
                    eculog_path = os.path.join(self.working_dir, "ECUlog")
                    eculog_path = os.path.normpath(eculog_path)
                    self.log_signal.emit("📁 日志保存路径：" + eculog_path, "#000000")
                # 如果是截图，显示保存路径
                elif hasattr(self, 'screen_name') and self.screen_name:
                    eculog_path = os.path.join(self.working_dir, "ECUlog")
                    eculog_path = os.path.normpath(eculog_path)
                    self.log_signal.emit("📁 截图保存路径：" + eculog_path, "#000000")
            else:
                self.log_signal.emit(">>> 执行失败 (返回码：" + str(return_code) + ")", "#FF5252")
            self.finished_signal.emit(return_code)
        except Exception as e:
            self.log_signal.emit(">>> 执行异常：" + str(e), "#FF5252")
            self.finished_signal.emit(-1)

class NotepadApp(QMainWindow):
    """纯代码实现的记事本应用 (PySide6)"""

    def __init__(self):
        super().__init__()
        self.script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "script")
        self.current_worker = None
        self.current_file = None

        # 🚀 优化1：初始化UI，不立即显示（main() 里会显示）
        self.init_ui()

        # 🚀 优化2：延迟执行非紧急操作
        QTimer.singleShot(0, self._init_after_show)

        # 先初始化必要的变量
        self.testfold_path = ''
        self.heipinglog_path = ''
        self.relay_com_port = ''
        self.relayID_qianjin = ''
        self.relayID_houtui = ''
        self.relayID_zhanzuo = ''
        self.relayID_shache = ''
        self.delaytime_1 = ''
        self.delaytime_2 = ''
        self.delaytime_3 = ''
        self.testcycle = ''
        self.testmode = ''
        self.test_object = '整车'
        self.vehicle_type = 'A车'
        self.project_code = ''
        self.car_model = ''
        self.vehicle_id = ''
        self.vehicle_vin = ''
        self.car_no = ''
        self.test_baseline = 'EP基线'
        self.vehicle_platform = '8295'
        self.selected_items = []
        self.keep_scene_items = []

        # 视频录制相关
        self.record_video = False  # 默认不勾选记录测试视频
        self.video_recorder = None

        # 其他变量先设为 None，延迟初始化
        self.config_file = None
        self.config = {}
        self.test_runner = None

    def _init_after_show(self):
        """窗口显示后的初始化（不影响启动速度）"""
        # 创建配置基准文件夹（打包后在程序目录下，不在临时目录）
        if hasattr(sys, '_MEIPASS'):
            # 打包后：配置文件保存在程序所在目录
            base_path = os.path.dirname(os.path.abspath(sys.executable))
        else:
            # 开发模式：配置文件保存在脚本所在目录
            base_path = os.path.dirname(os.path.abspath(__file__))

        config_dir = os.path.join(base_path, '配置基准文件')
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        self.config_file = os.path.join(config_dir, 'ITS_config.json')

        # 加载配置
        self.load_config()

        # 延迟初始化测试执行器
        QTimer.singleShot(200, self._init_test_runner)  # 200ms 后初始化

    def center_window(self):
        """将窗口居中显示"""
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            window_geometry = self.frameGeometry()
            x = (screen_geometry.width() - window_geometry.width()) // 2
            y = (screen_geometry.height() - window_geometry.height()) // 2
            self.move(x, y)

    def _init_test_runner(self):
        """延迟初始化测试执行器"""
        from Subpy.test_runner import TestRunner
        from Subpy.itms_test_statistics_uploader import (
            DEFAULT_TEST_STATISTICS_PATH,
            ITMSTestStatisticsUploader,
        )
        from Subpy.itms_vehicle_catalog import (
            DEFAULT_ITMS_API_BASE_URL,
            DEFAULT_ITMS_VEHICLE_CATALOG_KEY,
        )
        self.test_runner = TestRunner(self)
        self.test_runner.log_signal.connect(self.append_log)
        self.test_runner.cell_update_signal.connect(self._update_table_cell)
        self.test_runner.finished_signal.connect(self._on_test_finished)
        self.test_runner.instruction_failed_signal.connect(self.on_instruction_failed)  # 连接指令失败信号
        self.test_runner.cycle_wait_time_updated.connect(self._on_cycle_wait_time_updated)  # 连接循环等待时间更新信号
        self.test_runner.cycle_result_signal.connect(self._enqueue_itms_cycle_result)

        queue_file = os.path.join(os.path.dirname(self.config_file), "itms_test_statistics.sqlite3")
        self.itms_stats_uploader = ITMSTestStatisticsUploader(
            api_base_url=self.config.get("itms_api_base_url", DEFAULT_ITMS_API_BASE_URL),
            access_key=self.config.get(
                "itms_test_statistics_key",
                self.config.get("itms_vehicle_catalog_key", DEFAULT_ITMS_VEHICLE_CATALOG_KEY),
            ),
            api_path=self.config.get("itms_test_statistics_path", DEFAULT_TEST_STATISTICS_PATH),
            queue_file=queue_file,
            timeout=self.config.get("itms_test_statistics_timeout", 10),
        )
        self.itms_stats_uploader.start()

        # 初始化语音测试执行器
        self.voice_test_runner = None

    def _enqueue_itms_cycle_result(self, payload):
        """将每个循环的指令结果放入ITMS本地上传队列。"""
        uploader = getattr(self, "itms_stats_uploader", None)
        if uploader is None:
            return
        try:
            event_id = uploader.enqueue(payload)
            self.append_log(
                f"[ITMS] 第{payload.get('cycleNo', '')}次循环结果已加入上传队列: {event_id}"
            )
        except Exception as error:
            self.append_log(f"[ITMS] 结果入队失败，测试结果仍已本地保存: {error}")

    def init_ui(self):
        """初始化整个UI - 全部代码手写"""
        # 🚀 优化：直接设置最终尺寸，快速居中
        self.setWindowTitle("ITS智能座舱测试系统")
        # 🎯 自适应窗口尺寸，确保不超出屏幕
        screen = QApplication.primaryScreen()
        if screen:
            available_geometry = screen.availableGeometry()
            window_width = min(1920, int(available_geometry.width() * 0.9))
            window_height = min(1080, int(available_geometry.height() * 0.9))
            self.resize(window_width, window_height)
        else:
            self.resize(1600, 900)

        # 🚀 优化：设置应用ID和图标（快速操作）
        app_id = "ITS.Test.Tool.v1.0"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        self.setWindowIcon(QIcon(resource_path("image/Car.ico")))

        # 🚀 优化：延迟执行非紧急操作
        QTimer.singleShot(10, self.center_window)  # 10ms 后居中

        #这个是创建了一个中心区域
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)  # 全局不要边距
        layout.setSpacing(0)

        # 🎯 创建分割器，左右分栏
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 1. 左边：tab widget
        self.tab_widget = QTabWidget()
        # 添加标签页（你自己补内容）
        tab1 = QWidget()
        tab2 = QWidget()
        tab3 = QWidget()
        self.tab_widget.addTab(tab1, "自动化测试")
        self.tab_widget.addTab(tab2, "诊断服务")
        self.tab_widget.addTab(tab3, "日志抓取")
        #在tab1里加table widget表格控件
        tab1_layout = QVBoxLayout(tab1)
        tab1_layout.setContentsMargins(0, 0, 0, 0)
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(0)  # 🎯 优化：初始0行，需要时再设置
        #self.table_widget.setColumnCount(1000)
        self.table_widget.setHorizontalHeaderLabels([])
        self.table_widget.verticalHeader().setDefaultSectionSize(10)## 所有行默认高24px
        # 🎯 禁用最后一列自动拉伸
        self.table_widget.horizontalHeader().setStretchLastSection(False)
        # 🎯 冻结第一列（序号列）：设置第一列宽度固定，确保横向滚动时保持可见
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table_widget.setColumnWidth(0, 80)  # 设置第一列宽度为80px
        self.table_widget.horizontalHeader().setFirstSectionMovable(False)  # 第一列不可拖动
        self.table_widget.verticalHeader().setVisible(False)#隐藏行号（垂直表头）- 表格左侧的行号不显示
        # 2. 表格框线都显示黑色（包括表头）
        # =====================================================
        self.table_widget.setStyleSheet("""
            /* 表格网格线 - 黑色 */
            QTableWidget {
                gridline-color: black;
                border: 1px solid black;
                background-color: white;
            }
            /* 水平表头 - 黑色边框 */
            QHeaderView::section:horizontal {
                border: 1px solid black;
                padding: 4px;
                background-color: #f0f0f0;
            }
        """)
        for col in range(1000, 1000):
            self.table_widget.setColumnHidden(col, True)
        tab1_layout.addWidget(self.table_widget)

        #在tab2中添加编辑窗口
        tab2_layout = QVBoxLayout(tab2)
        #tab2_layout.setContentsMargins(0, 0, 0, 0)

        # ========================================================
        # 诊断服务开发 - 布局
        # ========================================================
        diag_splitter = QSplitter(Qt.Horizontal)

        # ── 左侧：控制器列表 ──
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(5, 5, 5, 5)

        self.diag_ecu_list = QListWidget()
        self.diag_ecu_list.setSelectionMode(QListWidget.SingleSelection)
        self.diag_ecu_list.setFocusPolicy(Qt.NoFocus)  # 去掉选中虚线框
        self.diag_ecu_list.setMaximumWidth(180)
        self.diag_ecu_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #cccccc;
                border-radius: 4px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 6px 8px;
            }
            QListWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
        """)
        # 预置控制器列表（ECU 置顶，其余字母序排列）
        ecu_items = [
            ("BROADCAST", "broadcast"),
            ("ADCU", "adcu"),
            ("AMP", "amp"),
            ("CCU", "ccu"),
            ("CF", "cf"),
            ("DPP", "dpp"),
            ("EPMCU", "epmcu"),
            ("EPS", "eps"),
            ("ESS", "ess"),
            ("FDR", "fdr"),
            ("FLPODA", "flpoda"),
            ("FRPODA", "frpoda"),
            ("FWM", "fwm"),
            ("HODM", "hodm"),
            ("IAM", "IAM"),
            ("IBS", "ibs"),
            ("ICB", "icb"),
            ("IPD", "ipd"),
            #("ICC", "icc"),
            ("LHZCU", "lhzcu"),
            ("LVBM", "lvbm"),
            ("NFCAM", "nfcam"),
            ("NFCSM", "nfcsm"),
            ("PEU", "peu"),
            ("PMA", "pma"),
            ("RACFP", "racfp"),
            ("RHPMWC", "rhpmwc"),
            ("RWSL", "rwsl"),
            ("RHZCU", "rhzcu"),
            ("RLPODA", "rlpoda"),
            ("RLSS", "rlss"),
            ("RRPODA", "rrpoda"),
            ("RZCU", "rzcu"),
            ("SCM", "scm"),
            ("SDM", "sdm"),
            ("TC", "tc"),
            ("TDM", "tdm"),
        ]
        for idx, (name, key) in enumerate(ecu_items):

            item = QListWidgetItem()
            item.setData(Qt.UserRole, key)
            if idx == 0:
                # ECU - 顶层节点
                item.setText("  ECU")
                item.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
                item.setForeground(QColor("#1565C0"))
                item.setSizeHint(QSize(0, 36))
            else:
                # 子控制器 - 缩进
                item.setText("    " + name)
                item.setFont(QFont("Microsoft YaHei", 11))
                item.setForeground(QColor("#555555"))
                item.setSizeHint(QSize(0, 28))
            self.diag_ecu_list.addItem(item)
        self.diag_ecu_list.itemClicked.connect(self.on_diag_ecu_selected)
        left_layout.addWidget(self.diag_ecu_list)

        diag_splitter.addWidget(left_widget)

        # ── 右侧面板 ──
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 5, 5, 5)

        # ── 操作按钮 ──
        diag_btn_group = QGroupBox("快捷操作")
        diag_btn_group.setMaximumHeight(80)
        diag_btn_layout = QHBoxLayout(diag_btn_group)

        self.diag_read_btn = QPushButton("🔍 读取故障码")
        self.diag_read_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3; color: white; border: none;
                border-radius: 4px; padding: 8px 16px; font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1976D2; }
            QPushButton:pressed { background-color: #1565C0; }
        """)
        self.diag_read_btn.clicked.connect(self.on_diag_read_clicked)
        diag_btn_layout.addWidget(self.diag_read_btn)

        self.diag_clear_btn = QPushButton("🧹 清除故障码")
        self.diag_clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5722; color: white; border: none;
                border-radius: 4px; padding: 8px 16px; font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #E64A19; }
            QPushButton:pressed { background-color: #D84315; }
        """)
        self.diag_clear_btn.clicked.connect(self.on_diag_clear_clicked)
        diag_btn_layout.addWidget(self.diag_clear_btn)

        # Reset 按钮 - 执行 11 01 硬复位
        self.diag_reset_btn = QPushButton("🔄 Reset")
        self.diag_reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; color: white; border: none;
                border-radius: 4px; padding: 8px 16px; font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #43A047; }
            QPushButton:pressed { background-color: #388E3C; }
        """)
        self.diag_reset_btn.clicked.connect(self.on_diag_reset_clicked)
        diag_btn_layout.addWidget(self.diag_reset_btn)

        diag_btn_layout.addStretch()
        right_layout.addWidget(diag_btn_group)

        # ── 右下：诊断指令输入 ──
        diag_cmd_group = QGroupBox("诊断指令")
        diag_cmd_layout = QVBoxLayout(diag_cmd_group)

        # 指令工具按钮
        diag_toolbar_layout = QHBoxLayout()
        self.diag_cmd_save_btn = QPushButton("💾 保存")
        self.diag_cmd_save_btn.setMaximumWidth(80)
        self.diag_cmd_save_btn.clicked.connect(self.on_diag_cmd_save)
        diag_toolbar_layout.addWidget(self.diag_cmd_save_btn)

        self.diag_cmd_import_btn = QPushButton("📂 导入")
        self.diag_cmd_import_btn.setMaximumWidth(80)
        self.diag_cmd_import_btn.clicked.connect(self.on_diag_cmd_import)
        diag_toolbar_layout.addWidget(self.diag_cmd_import_btn)

        self.diag_cmd_clear_btn = QPushButton("🗑️ 清除")
        self.diag_cmd_clear_btn.setMaximumWidth(80)
        self.diag_cmd_clear_btn.clicked.connect(self.on_diag_cmd_clear)
        diag_toolbar_layout.addWidget(self.diag_cmd_clear_btn)

        self.diag_cmd_send_btn = QPushButton("▶ 发送")
        self.diag_cmd_send_btn.setMaximumWidth(80)
        self.diag_cmd_send_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; color: white; border: none;
                border-radius: 4px; padding: 6px 12px; font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #388E3C; }
        """)
        self.diag_cmd_send_btn.clicked.connect(self.on_diag_cmd_send)
        diag_toolbar_layout.addWidget(self.diag_cmd_send_btn)

        diag_toolbar_layout.addStretch()
        diag_cmd_layout.addLayout(diag_toolbar_layout)

        # 指令输入框
        self.diag_cmd_edit = QTextEdit()
        self.diag_cmd_edit.setPlaceholderText("输入诊断指令，如:\nvapisend -get ctrl.ac.compressor_switch\nadb -host shell systemctl status bt")
        self.diag_cmd_edit.setMaximumHeight(120)
        self.diag_cmd_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 4px;
                font-family: Consolas, monospace;
                font-size: 12px;
            }
        """)
        diag_cmd_layout.addWidget(self.diag_cmd_edit)

        right_layout.addWidget(diag_cmd_group)
        right_layout.addStretch()

        diag_splitter.addWidget(right_widget)
        diag_splitter.setSizes([150, 650])
        tab2_layout.addWidget(diag_splitter)

        # ── 诊断相关变量初始化 ──
        self.selected_ecu_key = "all"
        self.diag_doip_client = None           # DoIP客户端实例
        self.diag_doip_connected = False        # DoIP连接状态
        self.ipd_doip_client = None            # DoIP 客户端实例 (IPD)
        self.ipd_doip_connected = False         # DoIP 连接状态 (IPD)
        self.adcu_doip_client = None           # DoIP 客户端实例 (ADCU)
        self.adcu_doip_connected = False        # DoIP 连接状态 (ADCU)
        self.dpp_doip_client = None            # DoIP 客户端实例 (DPP)
        self.epmcu_doip_client = None
        self.epmcu_doip_connected = False
        self.dpp_doip_client = None            # DoIP 客户端实例 (DPP)
        self.dpp_doip_connected = False         # DoIP 连接状态 (DPP)
        self.eps_doip_client = None            # DoIP 客户端实例 (EPS)
        self.eps_doip_connected = False
        self.iam_doip_client = None
        self.iam_doip_connected = False
        self.ibs_doip_client = None            # DoIP 客户端实例 (IBS)
        self.ibs_doip_connected = False        # DoIP 连接状态 (IBS)
        self.rwsl_doip_client = None           # DoIP 客户端实例 (RWSL)
        self.rwsl_doip_connected = False       # DoIP 连接状态 (RWSL)
        self.rlpoda_doip_client = None        # DoIP 客户端实例 (RLPODA)
        self.rlpoda_doip_connected = False    # DoIP 连接状态 (RLPODA)
        self.rrpoda_doip_client = None        # DoIP 客户端实例 (RRPODA)
        self.rrpoda_doip_connected = False    # DoIP 连接状态 (RRPODA)
        self.scm_doip_client = None            # DoIP 客户端实例 (SCM)
        self.scm_doip_connected = False        # DoIP 连接状态 (SCM)
        self.sdm_doip_client = None            # DoIP 客户端实例 (SDM)
        self.sdm_doip_connected = False        # DoIP 连接状态 (SDM)
        self.ess_doip_client = None            # DoIP 客户端实例 (ESS)
        self.ess_doip_connected = False        # DoIP 连接状态 (ESS)
        self.racfp_doip_client = None          # DoIP 客户端实例 (RACFP)
        self.racfp_doip_connected = False      # DoIP 连接状态 (RACFP)
        self.fdr_doip_client = None           # DoIP 客户端实例 (FDR)
        self.fdr_doip_connected = False       # DoIP 连接状态 (FDR)
        self.flpoda_doip_client = None        # DoIP 客户端实例 (FLPODA)
        self.flpoda_doip_connected = False    # DoIP 连接状态 (FLPODA)
        self.frpoda_doip_client = None        # DoIP 客户端实例 (FRPODA)
        self.frpoda_doip_connected = False    # DoIP 连接状态 (FRPODA)
        self.fwm_doip_client = None           # DoIP 客户端实例 (FWM)
        self.fwm_doip_connected = False       # DoIP 连接状态 (FWM)
        self.hodm_doip_client = None           # DoIP 客户端实例 (HODM)
        self.hodm_doip_connected = False       # DoIP 连接状态 (HODM)
        self.nfcsm_doip_client = None         # DoIP 客户端实例 (NFCSM)
        self.nfcsm_doip_connected = False     # DoIP 连接状态 (NFCSM)
        self.lvbm_doip_client = None           # DoIP 客户端实例 (LVBM)
        self.lvbm_doip_connected = False       # DoIP 连接状态 (LVBM)
        self.nfcam_doip_client = None          # DoIP 客户端实例 (NFCAM)
        self.nfcam_doip_connected = False      # DoIP 连接状态 (NFCAM)
        self.pma_doip_client = None           # DoIP 客户端实例 (PMA)
        self.pma_doip_connected = False       # DoIP 连接状态 (PMA)
        self.cf_doip_client = None             # DoIP 客户端实例 (CF)
        self.cf_doip_connected = False         # DoIP 连接状态 (CF)
        self.ccu_doip_client = None             # DoIP 客户端实例 (CCU)
        self.ccu_doip_connected = False         # DoIP 连接状态 (CCU)
        self.peu_doip_client = None            # DoIP 客户端实例 (PEU)
        self.peu_doip_connected = False        # DoIP 连接状态 (PEU)
        self.rhpmwc_doip_client = None         # DoIP 客户端实例 (RHPMWC)
        self.rhpmwc_doip_connected = False     # DoIP 连接状态 (RHPMWC)
        self.rlss_doip_client = None           # DoIP 客户端实例 (RLSS)
        self.rlss_doip_connected = False       # DoIP 连接状态 (RLSS)
        self.tc_doip_client = None             # DoIP 客户端实例 (TC)
        self.tc_doip_connected = False         # DoIP 连接状态 (TC)
        self.tdm_doip_client = None            # DoIP 客户端实例 (TDM)
        self.broadcast_doip_connected = False
        self.broadcast_doip_client = None
        self.tdm_doip_connected = False        # DoIP 连接状态 (TDM)
        self._diag_pending_cmd = None           # 待执行的诊断指令 (自动连后执行)
        self._diag_pending_action = None        # 待执行的动作: 'cmd'/'dtc_read'/'dtc_clear'

        # 在tab2中添加控制按钮
        tab3_layout = QVBoxLayout(tab3)
        #tab3_layout.setContentsMargins(0, 0, 0, 0)

        adb_group = QGroupBox("adb无线连接")
        #adb_group.setContentsMargins(10, 5, 10, 5)  # 左、上、右、下
        adb_group.setFixedHeight(50)
        adb_layout = QFormLayout()
        adb_group.setLayout(adb_layout)

        adb1_layout  = QHBoxLayout()
        adbconnect_btn = QPushButton("adb无线连接")
        adbconnect_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;  /* 绿色背景 */
                color: white;                /* 白色文字 */
                border: none;                /* 无边框 */
                border-radius: 4px;          /* 圆角 */
                padding: 5px 10px;           /* 内边距 */
                font-size: 12px;             /* 字体大小 */
                font-weight: bold;           /* 粗体 */
            }
            QPushButton:hover {
                background-color: #45a049;   /* 悬停时稍深 */
            }
            QPushButton:pressed {
                background-color: #3d8b40;   /* 按下时更深 */
            }
            QPushButton:disabled {
                background-color: #cccccc;   /* 禁用时灰色 */
                color: #666666;
            }
        """)
        adbconnect_btn.setMaximumWidth(100)
        adb1_layout.addWidget(adbconnect_btn)
        adbconnect_btn.clicked.connect(self.on_adb_connect_clicked)

        adbdisconnect_btn = QPushButton("adb连接断开")
        adbdisconnect_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #FFC107;  /* 绿色背景 */
                        color: white;                /* 白色文字 */
                        border: none;                /* 无边框 */
                        border-radius: 4px;          /* 圆角 */
                        padding: 5px 10px;           /* 内边距 */
                        font-size: 12px;             /* 字体大小 */
                        font-weight: bold;           /* 粗体 */
                    }
                    QPushButton:hover {
                        background-color: #45a049;   /* 悬停时稍深 */
                    }
                    QPushButton:pressed {
                        background-color: #3d8b40;   /* 按下时更深 */
                    }
                    QPushButton:disabled {
                        background-color: #cccccc;   /* 禁用时灰色 */
                        color: #666666;
                    }
                """)
        adbdisconnect_btn.setMaximumWidth(100)
        adb1_layout.addWidget(adbdisconnect_btn)
        adbdisconnect_btn.clicked.connect(self.on_adb_disconnect_clicked)
        adb_layout.addRow("adb无线连接，需要先连接车机热点:", adb1_layout)
        tab3_layout.addWidget(adb_group)

        log8295_group = QGroupBox("智舱日志（8295）")
        #log8295_group.setContentsMargins(10, 5, 10, 10)  # 左、上、右、下
        adb_group.setFixedHeight(60)
        log_layout = QFormLayout()
        log8295_group.setLayout(log_layout)

        log1_layout = QHBoxLayout()
        nav1_btn = QPushButton("打开导航日志")
        nav1_btn.setStyleSheet("""
                 QPushButton {
                     background-color: #03A9F4;  /* 绿色背景 */
                     color: white;                /* 白色文字 */
                     border: none;                /* 无边框 */
                     border-radius: 4px;          /* 圆角 */
                     padding: 5px 10px;           /* 内边距 */
                     font-size: 12px;             /* 字体大小 */
                     font-weight: bold;           /* 粗体 */
                 }
                 QPushButton:hover {
                     background-color: #45a049;   /* 悬停时稍深 */
                 }
                 QPushButton:pressed {
                     background-color: #3d8b40;   /* 按下时更深 */
                 }
                 QPushButton:disabled {
                     background-color: #cccccc;   /* 禁用时灰色 */
                     color: #666666;
                 }
             """)
        nav1_btn.setMaximumWidth(100)
        log1_layout.addWidget(nav1_btn)
        nav1_btn.clicked.connect(self.on_navi_start_clicked)

        nav2_btn = QPushButton("抓取导航日志")
        nav2_btn.setStyleSheet("""
                         QPushButton {
                             background-color: #03A9F4;  /* 绿色背景 */
                             color: white;                /* 白色文字 */
                             border: none;                /* 无边框 */
                             border-radius: 4px;          /* 圆角 */
                             padding: 5px 10px;           /* 内边距 */
                             font-size: 12px;             /* 字体大小 */
                             font-weight: bold;           /* 粗体 */
                         }
                         QPushButton:hover {
                             background-color: #45a049;   /* 悬停时稍深 */
                         }
                         QPushButton:pressed {
                             background-color: #3d8b40;   /* 按下时更深 */
                         }
                         QPushButton:disabled {
                             background-color: #cccccc;   /* 禁用时灰色 */
                             color: #666666;
                         }
                     """)
        nav2_btn.setMaximumWidth(100)
        log1_layout.addWidget(nav2_btn)
        nav2_btn.clicked.connect(self.on_navi_pull_clicked)

        nav3_btn = QPushButton("关闭导航日志")
        nav3_btn.setStyleSheet("""
                                QPushButton {
                                    background-color: #03A9F4;  /* 绿色背景 */
                                    color: white;                /* 白色文字 */
                                    border: none;                /* 无边框 */
                                    border-radius: 4px;          /* 圆角 */
                                    padding: 5px 10px;           /* 内边距 */
                                    font-size: 12px;             /* 字体大小 */
                                    font-weight: bold;           /* 粗体 */
                                }
                                QPushButton:hover {
                                    background-color: #45a049;   /* 悬停时稍深 */
                                }
                                QPushButton:pressed {
                                    background-color: #3d8b40;   /* 按下时更深 */
                                }
                                QPushButton:disabled {
                                    background-color: #cccccc;   /* 禁用时灰色 */
                                    color: #666666;
                                }
                            """)
        nav3_btn.setMaximumWidth(100)
        log1_layout.addWidget(nav3_btn)
        nav3_btn.clicked.connect(self.on_navi_stop_clicked)
        log_layout.addRow("导航:", log1_layout)

        log2_layout = QHBoxLayout()
        screen1_btn = QPushButton("截取A屏")
        screen1_btn.setStyleSheet("""
                         QPushButton {
                             background-color: #03A9F4;  /* 绿色背景 */
                             color: white;                /* 白色文字 */
                             border: none;                /* 无边框 */
                             border-radius: 4px;          /* 圆角 */
                             padding: 5px 10px;           /* 内边距 */
                             font-size: 12px;             /* 字体大小 */
                             font-weight: bold;           /* 粗体 */
                         }
                         QPushButton:hover {
                             background-color: #45a049;   /* 悬停时稍深 */
                         }
                         QPushButton:pressed {
                             background-color: #3d8b40;   /* 按下时更深 */
                         }
                         QPushButton:disabled {
                             background-color: #cccccc;   /* 禁用时灰色 */
                             color: #666666;
                         }
                     """)
        screen1_btn.setMaximumWidth(100)
        log2_layout.addWidget(screen1_btn)
        screen1_btn.clicked.connect(self.on_screen_a_clicked)

        screen2_btn = QPushButton("截取B屏")
        screen2_btn.setStyleSheet("""
                                 QPushButton {
                                     background-color: #03A9F4;  /* 绿色背景 */
                                     color: white;                /* 白色文字 */
                                     border: none;                /* 无边框 */
                                     border-radius: 4px;          /* 圆角 */
                                     padding: 5px 10px;           /* 内边距 */
                                     font-size: 12px;             /* 字体大小 */
                                     font-weight: bold;           /* 粗体 */
                                 }
                                 QPushButton:hover {
                                     background-color: #45a049;   /* 悬停时稍深 */
                                 }
                                 QPushButton:pressed {
                                     background-color: #3d8b40;   /* 按下时更深 */
                                 }
                                 QPushButton:disabled {
                                     background-color: #cccccc;   /* 禁用时灰色 */
                                     color: #666666;
                                 }
                             """)
        screen2_btn.setMaximumWidth(100)
        log2_layout.addWidget(screen2_btn)
        screen2_btn.clicked.connect(self.on_screen_b_clicked)

        screen3_btn = QPushButton("截取C屏")
        screen3_btn.setStyleSheet("""
                                         QPushButton {
                                             background-color: #03A9F4;  /* 绿色背景 */
                                             color: white;                /* 白色文字 */
                                             border: none;                /* 无边框 */
                                             border-radius: 4px;          /* 圆角 */
                                             padding: 5px 10px;           /* 内边距 */
                                             font-size: 12px;             /* 字体大小 */
                                             font-weight: bold;           /* 粗体 */
                                         }
                                         QPushButton:hover {
                                             background-color: #45a049;   /* 悬停时稍深 */
                                         }
                                         QPushButton:pressed {
                                             background-color: #3d8b40;   /* 按下时更深 */
                                         }
                                         QPushButton:disabled {
                                             background-color: #cccccc;   /* 禁用时灰色 */
                                             color: #666666;
                                         }
                                     """)
        screen3_btn.setMaximumWidth(100)
        log2_layout.addWidget(screen3_btn)
        screen3_btn.clicked.connect(self.on_screen_c_clicked)

        screen4_btn = QPushButton("截取全屏")
        screen4_btn.setStyleSheet("""
                                                QPushButton {
                                                    background-color: #03A9F4;  /* 绿色背景 */
                                                    color: white;                /* 白色文字 */
                                                    border: none;                /* 无边框 */
                                                    border-radius: 4px;          /* 圆角 */
                                                    padding: 5px 10px;           /* 内边距 */
                                                    font-size: 12px;             /* 字体大小 */
                                                    font-weight: bold;           /* 粗体 */
                                                }
                                                QPushButton:hover {
                                                    background-color: #45a049;   /* 悬停时稍深 */
                                                }
                                                QPushButton:pressed {
                                                    background-color: #3d8b40;   /* 按下时更深 */
                                                }
                                                QPushButton:disabled {
                                                    background-color: #cccccc;   /* 禁用时灰色 */
                                                    color: #666666;
                                                }
                                            """)
        screen4_btn.setMaximumWidth(100)
        log2_layout.addWidget(screen4_btn)
        screen4_btn.clicked.connect(self.on_screen_full_clicked)

        screen5_btn = QPushButton("黑屏日志")
        screen5_btn.setStyleSheet("""
                                                        QPushButton {
                                                            background-color: #03A9F4;  /* 绿色背景 */
                                                            color: white;                /* 白色文字 */
                                                            border: none;                /* 无边框 */
                                                            border-radius: 4px;          /* 圆角 */
                                                            padding: 5px 10px;           /* 内边距 */
                                                            font-size: 12px;             /* 字体大小 */
                                                            font-weight: bold;           /* 粗体 */
                                                        }
                                                        QPushButton:hover {
                                                            background-color: #45a049;   /* 悬停时稍深 */
                                                        }
                                                        QPushButton:pressed {
                                                            background-color: #3d8b40;   /* 按下时更深 */
                                                        }
                                                        QPushButton:disabled {
                                                            background-color: #cccccc;   /* 禁用时灰色 */
                                                            color: #666666;
                                                        }
                                                    """)
        screen5_btn.setMaximumWidth(100)
        log2_layout.addWidget(screen5_btn)
        screen5_btn.clicked.connect(self.on_black_screen_clicked)

        screen6_btn = QPushButton("A1屏齿轮图")
        screen6_btn.setStyleSheet("""
                                                                QPushButton {
                                                                    background-color: #03A9F4;  /* 绿色背景 */
                                                                    color: white;                /* 白色文字 */
                                                                    border: none;                /* 无边框 */
                                                                    border-radius: 4px;          /* 圆角 */
                                                                    padding: 5px 10px;           /* 内边距 */
                                                                    font-size: 12px;             /* 字体大小 */
                                                                    font-weight: bold;           /* 粗体 */
                                                                }
                                                                QPushButton:hover {
                                                                    background-color: #45a049;   /* 悬停时稍深 */
                                                                }
                                                                QPushButton:pressed {
                                                                    background-color: #3d8b40;   /* 按下时更深 */
                                                                }
                                                                QPushButton:disabled {
                                                                    background-color: #cccccc;   /* 禁用时灰色 */
                                                                    color: #666666;
                                                                }
                                                            """)
        screen6_btn.setMaximumWidth(100)
        log2_layout.addWidget(screen6_btn)
        screen6_btn.clicked.connect(self.on_gear_a1_clicked)
        log_layout.addRow("屏幕:", log2_layout)

        log3_layout = QHBoxLayout()
        screen7_btn = QPushButton("A2屏齿轮图")
        screen7_btn.setStyleSheet("""
                                                                       QPushButton {
                                                                           background-color: #03A9F4;  /* 绿色背景 */
                                                                           color: white;                /* 白色文字 */
                                                                           border: none;                /* 无边框 */
                                                                           border-radius: 4px;          /* 圆角 */
                                                                           padding: 5px 10px;           /* 内边距 */
                                                                           font-size: 12px;             /* 字体大小 */
                                                                           font-weight: bold;           /* 粗体 */
                                                                       }
                                                                       QPushButton:hover {
                                                                           background-color: #45a049;   /* 悬停时稍深 */
                                                                       }
                                                                       QPushButton:pressed {
                                                                           background-color: #3d8b40;   /* 按下时更深 */
                                                                       }
                                                                       QPushButton:disabled {
                                                                           background-color: #cccccc;   /* 禁用时灰色 */
                                                                           color: #666666;
                                                                       }
                                                                   """)
        screen7_btn.setMaximumWidth(100)
        log3_layout.addWidget(screen7_btn)
        screen7_btn.clicked.connect(self.on_gear_a2_clicked)

        screen8_btn = QPushButton("B屏齿轮图")
        screen8_btn.setStyleSheet("""
                                                                              QPushButton {
                                                                                  background-color: #03A9F4;  /* 绿色背景 */
                                                                                  color: white;                /* 白色文字 */
                                                                                  border: none;                /* 无边框 */
                                                                                  border-radius: 4px;          /* 圆角 */
                                                                                  padding: 5px 10px;           /* 内边距 */
                                                                                  font-size: 12px;             /* 字体大小 */
                                                                                  font-weight: bold;           /* 粗体 */
                                                                              }
                                                                              QPushButton:hover {
                                                                                  background-color: #45a049;   /* 悬停时稍深 */
                                                                              }
                                                                              QPushButton:pressed {
                                                                                  background-color: #3d8b40;   /* 按下时更深 */
                                                                              }
                                                                              QPushButton:disabled {
                                                                                  background-color: #cccccc;   /* 禁用时灰色 */
                                                                                  color: #666666;
                                                                              }
                                                                          """)
        screen8_btn.setMaximumWidth(100)
        log3_layout.addWidget(screen8_btn)
        screen8_btn.clicked.connect(self.on_gear_b_clicked)

        screen9_btn = QPushButton("C屏齿轮图")
        screen9_btn.setStyleSheet("""
                                                                                      QPushButton {
                                                                                          background-color: #03A9F4;  /* 绿色背景 */
                                                                                          color: white;                /* 白色文字 */
                                                                                          border: none;                /* 无边框 */
                                                                                          border-radius: 4px;          /* 圆角 */
                                                                                          padding: 5px 10px;           /* 内边距 */
                                                                                          font-size: 12px;             /* 字体大小 */
                                                                                          font-weight: bold;           /* 粗体 */
                                                                                      }
                                                                                      QPushButton:hover {
                                                                                          background-color: #45a049;   /* 悬停时稍深 */
                                                                                      }
                                                                                      QPushButton:pressed {
                                                                                          background-color: #3d8b40;   /* 按下时更深 */
                                                                                      }
                                                                                      QPushButton:disabled {
                                                                                          background-color: #cccccc;   /* 禁用时灰色 */
                                                                                          color: #666666;
                                                                                      }
                                                                                  """)
        screen9_btn.setMaximumWidth(100)
        log3_layout.addWidget(screen9_btn)
        screen9_btn.clicked.connect(self.on_gear_c_clicked)

        screen10_btn = QPushButton("屏幕MCU版本")
        screen10_btn.setStyleSheet("""
                                                                                              QPushButton {
                                                                                                  background-color: #03A9F4;  /* 绿色背景 */
                                                                                                  color: white;                /* 白色文字 */
                                                                                                  border: none;                /* 无边框 */
                                                                                                  border-radius: 4px;          /* 圆角 */
                                                                                                  padding: 5px 10px;           /* 内边距 */
                                                                                                  font-size: 12px;             /* 字体大小 */
                                                                                                  font-weight: bold;           /* 粗体 */
                                                                                              }
                                                                                              QPushButton:hover {
                                                                                                  background-color: #45a049;   /* 悬停时稍深 */
                                                                                              }
                                                                                              QPushButton:pressed {
                                                                                                  background-color: #3d8b40;   /* 按下时更深 */
                                                                                              }
                                                                                              QPushButton:disabled {
                                                                                                  background-color: #cccccc;   /* 禁用时灰色 */
                                                                                                  color: #666666;
                                                                                              }
                                                                                          """)
        screen10_btn.setMaximumWidth(100)
        log3_layout.addWidget(screen10_btn)
        screen10_btn.clicked.connect(self.on_screen_version_clicked)


        log_layout.addRow("", log3_layout)

        log4_layout = QHBoxLayout()
        sou1_btn = QPushButton("开启audio")
        sou1_btn.setStyleSheet("""
                                                                                              QPushButton {
                                                                                                  background-color: #03A9F4;  /* 绿色背景 */
                                                                                                  color: white;                /* 白色文字 */
                                                                                                  border: none;                /* 无边框 */
                                                                                                  border-radius: 4px;          /* 圆角 */
                                                                                                  padding: 5px 10px;           /* 内边距 */
                                                                                                  font-size: 12px;             /* 字体大小 */
                                                                                                  font-weight: bold;           /* 粗体 */
                                                                                              }
                                                                                              QPushButton:hover {
                                                                                                  background-color: #45a049;   /* 悬停时稍深 */
                                                                                              }
                                                                                              QPushButton:pressed {
                                                                                                  background-color: #3d8b40;   /* 按下时更深 */
                                                                                              }
                                                                                              QPushButton:disabled {
                                                                                                  background-color: #cccccc;   /* 禁用时灰色 */
                                                                                                  color: #666666;
                                                                                              }
                                                                                          """)
        sou1_btn.setMaximumWidth(100)
        log4_layout.addWidget(sou1_btn)
        sou1_btn.clicked.connect(self.on_audio_start_clicked)

        sou2_btn = QPushButton("停止audio")
        sou2_btn.setStyleSheet("""
                                                                                                     QPushButton {
                                                                                                         background-color: #03A9F4;  /* 绿色背景 */
                                                                                                         color: white;                /* 白色文字 */
                                                                                                         border: none;                /* 无边框 */
                                                                                                         border-radius: 4px;          /* 圆角 */
                                                                                                         padding: 5px 10px;           /* 内边距 */
                                                                                                         font-size: 12px;             /* 字体大小 */
                                                                                                         font-weight: bold;           /* 粗体 */
                                                                                                     }
                                                                                                     QPushButton:hover {
                                                                                                         background-color: #45a049;   /* 悬停时稍深 */
                                                                                                     }
                                                                                                     QPushButton:pressed {
                                                                                                         background-color: #3d8b40;   /* 按下时更深 */
                                                                                                     }
                                                                                                     QPushButton:disabled {
                                                                                                         background-color: #cccccc;   /* 禁用时灰色 */
                                                                                                         color: #666666;
                                                                                                     }
                                                                                                 """)
        sou2_btn.setMaximumWidth(100)
        log4_layout.addWidget(sou2_btn)
        sou2_btn.clicked.connect(self.on_audio_stop_clicked)

        sou3_btn = QPushButton("抓取audio")
        sou3_btn.setStyleSheet("""
                                                                                                            QPushButton {
                                                                                                                background-color: #03A9F4;  /* 绿色背景 */
                                                                                                                color: white;                /* 白色文字 */
                                                                                                                border: none;                /* 无边框 */
                                                                                                                border-radius: 4px;          /* 圆角 */
                                                                                                                padding: 5px 10px;           /* 内边距 */
                                                                                                                font-size: 12px;             /* 字体大小 */
                                                                                                                font-weight: bold;           /* 粗体 */
                                                                                                            }
                                                                                                            QPushButton:hover {
                                                                                                                background-color: #45a049;   /* 悬停时稍深 */
                                                                                                            }
                                                                                                            QPushButton:pressed {
                                                                                                                background-color: #3d8b40;   /* 按下时更深 */
                                                                                                            }
                                                                                                            QPushButton:disabled {
                                                                                                                background-color: #cccccc;   /* 禁用时灰色 */
                                                                                                                color: #666666;
                                                                                                            }
                                                                                                        """)
        sou3_btn.setMaximumWidth(100)
        log4_layout.addWidget(sou3_btn)
        sou3_btn.clicked.connect(self.on_audio_pull_clicked)

        sou4_btn = QPushButton("打开录音")
        sou4_btn.setStyleSheet("""
                                                                                                                    QPushButton {
                                                                                                                        background-color: #03A9F4;  /* 绿色背景 */
                                                                                                                        color: white;                /* 白色文字 */
                                                                                                                        border: none;                /* 无边框 */
                                                                                                                        border-radius: 4px;          /* 圆角 */
                                                                                                                        padding: 5px 10px;           /* 内边距 */
                                                                                                                        font-size: 12px;             /* 字体大小 */
                                                                                                                        font-weight: bold;           /* 粗体 */
                                                                                                                    }
                                                                                                                    QPushButton:hover {
                                                                                                                        background-color: #45a049;   /* 悬停时稍深 */
                                                                                                                    }
                                                                                                                    QPushButton:pressed {
                                                                                                                        background-color: #3d8b40;   /* 按下时更深 */
                                                                                                                    }
                                                                                                                    QPushButton:disabled {
                                                                                                                        background-color: #cccccc;   /* 禁用时灰色 */
                                                                                                                        color: #666666;
                                                                                                                    }
                                                                                                                """)
        sou4_btn.setMaximumWidth(100)
        log4_layout.addWidget(sou4_btn)
        sou4_btn.clicked.connect(self.on_mic_start_clicked)

        sou5_btn = QPushButton("关闭录音")
        sou5_btn.setStyleSheet("""
                                                                                                                            QPushButton {
                                                                                                                                background-color: #03A9F4;  /* 绿色背景 */
                                                                                                                                color: white;                /* 白色文字 */
                                                                                                                                border: none;                /* 无边框 */
                                                                                                                                border-radius: 4px;          /* 圆角 */
                                                                                                                                padding: 5px 10px;           /* 内边距 */
                                                                                                                                font-size: 12px;             /* 字体大小 */
                                                                                                                                font-weight: bold;           /* 粗体 */
                                                                                                                            }
                                                                                                                            QPushButton:hover {
                                                                                                                                background-color: #45a049;   /* 悬停时稍深 */
                                                                                                                            }
                                                                                                                            QPushButton:pressed {
                                                                                                                                background-color: #3d8b40;   /* 按下时更深 */
                                                                                                                            }
                                                                                                                            QPushButton:disabled {
                                                                                                                                background-color: #cccccc;   /* 禁用时灰色 */
                                                                                                                                color: #666666;
                                                                                                                            }
                                                                                                                        """)
        sou5_btn.setMaximumWidth(100)
        log4_layout.addWidget(sou5_btn)
        sou5_btn.clicked.connect(self.on_mic_stop_clicked)

        sou6_btn = QPushButton("抓取录音")
        sou6_btn.setStyleSheet("""
                                                                                                                            QPushButton {
                                                                                                                                background-color: #03A9F4;  /* 绿色背景 */
                                                                                                                                color: white;                /* 白色文字 */
                                                                                                                                border: none;                /* 无边框 */
                                                                                                                                border-radius: 4px;          /* 圆角 */
                                                                                                                                padding: 5px 10px;           /* 内边距 */
                                                                                                                                font-size: 12px;             /* 字体大小 */
                                                                                                                                font-weight: bold;           /* 粗体 */
                                                                                                                            }
                                                                                                                            QPushButton:hover {
                                                                                                                                background-color: #45a049;   /* 悬停时稍深 */
                                                                                                                            }
                                                                                                                            QPushButton:pressed {
                                                                                                                                background-color: #3d8b40;   /* 按下时更深 */
                                                                                                                            }
                                                                                                                            QPushButton:disabled {
                                                                                                                                background-color: #cccccc;   /* 禁用时灰色 */
                                                                                                                                color: #666666;
                                                                                                                            }
                                                                                                                        """)
        sou6_btn.setMaximumWidth(100)
        log4_layout.addWidget(sou6_btn)
        sou6_btn.clicked.connect(self.on_mic_pull_clicked)


        log_layout.addRow("音频:", log4_layout)

        log5_layout = QHBoxLayout()
        tcp1_btn = QPushButton("打开TCP")
        tcp1_btn.setStyleSheet("""
                                                                                                     QPushButton {
                                                                                                         background-color: #03A9F4;  /* 绿色背景 */
                                                                                                         color: white;                /* 白色文字 */
                                                                                                         border: none;                /* 无边框 */
                                                                                                         border-radius: 4px;          /* 圆角 */
                                                                                                         padding: 5px 10px;           /* 内边距 */
                                                                                                         font-size: 12px;             /* 字体大小 */
                                                                                                         font-weight: bold;           /* 粗体 */
                                                                                                     }
                                                                                                     QPushButton:hover {
                                                                                                         background-color: #45a049;   /* 悬停时稍深 */
                                                                                                     }
                                                                                                     QPushButton:pressed {
                                                                                                         background-color: #3d8b40;   /* 按下时更深 */
                                                                                                     }
                                                                                                     QPushButton:disabled {
                                                                                                         background-color: #cccccc;   /* 禁用时灰色 */
                                                                                                         color: #666666;
                                                                                                     }
                                                                                                 """)
        tcp1_btn.setMaximumWidth(100)
        log5_layout.addWidget(tcp1_btn)
        tcp1_btn.clicked.connect(self.on_eth_start_clicked)

        tcp2_btn = QPushButton("关闭TCP")
        tcp2_btn.setStyleSheet("""
                                                                                                            QPushButton {
                                                                                                                background-color: #03A9F4;  /* 绿色背景 */
                                                                                                                color: white;                /* 白色文字 */
                                                                                                                border: none;                /* 无边框 */
                                                                                                                border-radius: 4px;          /* 圆角 */
                                                                                                                padding: 5px 10px;           /* 内边距 */
                                                                                                                font-size: 12px;             /* 字体大小 */
                                                                                                                font-weight: bold;           /* 粗体 */
                                                                                                            }
                                                                                                            QPushButton:hover {
                                                                                                                background-color: #45a049;   /* 悬停时稍深 */
                                                                                                            }
                                                                                                            QPushButton:pressed {
                                                                                                                background-color: #3d8b40;   /* 按下时更深 */
                                                                                                            }
                                                                                                            QPushButton:disabled {
                                                                                                                background-color: #cccccc;   /* 禁用时灰色 */
                                                                                                                color: #666666;
                                                                                                            }
                                                                                                        """)
        tcp2_btn.setMaximumWidth(100)
        log5_layout.addWidget(tcp2_btn)
        tcp2_btn.clicked.connect(self.on_eth_stop_clicked)

        tcp3_btn = QPushButton("抓取TCP")
        tcp3_btn.setStyleSheet("""
                                                                                                                    QPushButton {
                                                                                                                        background-color: #03A9F4;  /* 绿色背景 */
                                                                                                                        color: white;                /* 白色文字 */
                                                                                                                        border: none;                /* 无边框 */
                                                                                                                        border-radius: 4px;          /* 圆角 */
                                                                                                                        padding: 5px 10px;           /* 内边距 */
                                                                                                                        font-size: 12px;             /* 字体大小 */
                                                                                                                        font-weight: bold;           /* 粗体 */
                                                                                                                    }
                                                                                                                    QPushButton:hover {
                                                                                                                        background-color: #45a049;   /* 悬停时稍深 */
                                                                                                                    }
                                                                                                                    QPushButton:pressed {
                                                                                                                        background-color: #3d8b40;   /* 按下时更深 */
                                                                                                                    }
                                                                                                                    QPushButton:disabled {
                                                                                                                        background-color: #cccccc;   /* 禁用时灰色 */
                                                                                                                        color: #666666;
                                                                                                                    }
                                                                                                                """)
        tcp3_btn.setMaximumWidth(100)
        log5_layout.addWidget(tcp3_btn)
        tcp3_btn.clicked.connect(self.on_eth_pull_clicked)
        log_layout.addRow("TCP:", log5_layout)

        log10_layout = QHBoxLayout()
        bmlog_btn = QPushButton("BMLog")
        bmlog_btn.setStyleSheet("""
                                                                                                  QPushButton {
                                                                                                      background-color: #03A9F4;  /* 绿色背景 */
                                                                                                      color: white;                /* 白色文字 */
                                                                                                      border: none;                /* 无边框 */
                                                                                                      border-radius: 4px;          /* 圆角 */
                                                                                                      padding: 5px 10px;           /* 内边距 */
                                                                                                      font-size: 12px;             /* 字体大小 */
                                                                                                      font-weight: bold;           /* 粗体 */
                                                                                                  }
                                                                                                  QPushButton:hover {
                                                                                                      background-color: #45a049;   /* 悬停时稍深 */
                                                                                                  }
                                                                                                  QPushButton:pressed {
                                                                                                      background-color: #3d8b40;   /* 按下时更深 */
                                                                                                  }
                                                                                                  QPushButton:disabled {
                                                                                                      background-color: #cccccc;   /* 禁用时灰色 */
                                                                                                      color: #666666;
                                                                                                  }
                                                                                              """)
        bmlog_btn.setMaximumWidth(100)
        log10_layout.addWidget( bmlog_btn)
        bmlog_btn.clicked.connect(self.on_bmlog_clicked)

        yuntoollog_btn = QPushButton("yuntoollog")
        yuntoollog_btn.setStyleSheet("""
                                                                                                          QPushButton {
                                                                                                              background-color: #03A9F4;  /* 绿色背景 */
                                                                                                              color: white;                /* 白色文字 */
                                                                                                              border: none;                /* 无边框 */
                                                                                                              border-radius: 4px;          /* 圆角 */
                                                                                                              padding: 5px 10px;           /* 内边距 */
                                                                                                              font-size: 12px;             /* 字体大小 */
                                                                                                              font-weight: bold;           /* 粗体 */
                                                                                                          }
                                                                                                          QPushButton:hover {
                                                                                                              background-color: #45a049;   /* 悬停时稍深 */
                                                                                                          }
                                                                                                          QPushButton:pressed {
                                                                                                              background-color: #3d8b40;   /* 按下时更深 */
                                                                                                          }
                                                                                                          QPushButton:disabled {
                                                                                                              background-color: #cccccc;   /* 禁用时灰色 */
                                                                                                              color: #666666;
                                                                                                          }
                                                                                                      """)
        yuntoollog_btn.setMaximumWidth(100)
        log10_layout.addWidget(yuntoollog_btn)
        yuntoollog_btn.clicked.connect(self.on_yuntool_clicked)

        versionlog_btn = QPushButton("8295info")
        versionlog_btn.setStyleSheet("""
                                                                                                               QPushButton {
                                                                                                                   background-color: #03A9F4;  /* 绿色背景 */
                                                                                                                   color: white;                /* 白色文字 */
                                                                                                                   border: none;                /* 无边框 */
                                                                                                                   border-radius: 4px;          /* 圆角 */
                                                                                                                   padding: 5px 10px;           /* 内边距 */
                                                                                                                   font-size: 12px;             /* 字体大小 */
                                                                                                                   font-weight: bold;           /* 粗体 */
                                                                                                               }
                                                                                                               QPushButton:hover {
                                                                                                                   background-color: #45a049;   /* 悬停时稍深 */
                                                                                                               }
                                                                                                               QPushButton:pressed {
                                                                                                                   background-color: #3d8b40;   /* 按下时更深 */
                                                                                                               }
                                                                                                               QPushButton:disabled {
                                                                                                                   background-color: #cccccc;   /* 禁用时灰色 */
                                                                                                                   color: #666666;
                                                                                                               }
                                                                                                           """)
        versionlog_btn.setMaximumWidth(100)
        log10_layout.addWidget(versionlog_btn)
        versionlog_btn.clicked.connect(self.on_8295_version_clicked)
        reboot8295_btn = QPushButton("重启 8295")
        reboot8295_btn.setStyleSheet("""
                                                                                                               QPushButton {
                                                                                                                   background-color: #03A9F4;  /* 绿色背景 */
                                                                                                                   color: white;                /* 白色文字 */
                                                                                                                   border: none;                /* 无边框 */
                                                                                                                   border-radius: 4px;          /* 圆角 */
                                                                                                                   padding: 5px 10px;           /* 内边距 */
                                                                                                                   font-size: 12px;             /* 字体大小 */
                                                                                                                   font-weight: bold;           /* 粗体 */
                                                                                                               }
                                                                                                               QPushButton:hover {
                                                                                                                   background-color: #45a049;   /* 悬停时稍深 */
                                                                                                               }
                                                                                                               QPushButton:pressed {
                                                                                                                   background-color: #3d8b40;   /* 按下时更深 */
                                                                                                               }
                                                                                                               QPushButton:disabled {
                                                                                                                   background-color: #cccccc;   /* 禁用时灰色 */
                                                                                                                   color: #666666;
                                                                                                               }
                                                                                                           """)
        reboot8295_btn.setMaximumWidth(100)
        log10_layout.addWidget(reboot8295_btn)
        reboot8295_btn.clicked.connect(self.on_reboot_8295_clicked)



        log_layout.addRow("其他", log10_layout)





        tab3_layout.addWidget(log8295_group)




        # 2. 右边：文本编辑器
        self.text_edit1 = QTextEdit()
        self.text_edit1.setLineWrapMode(QTextEdit.NoWrap)
        self.text_edit1.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.text_edit1.textChanged.connect(self._scroll_log_to_bottom)
        self.text_edit1.setPlaceholderText(
            "1.运行试验前选择要执行的指令，然后需要先执行保存基准文件...\n"
            "2.更换新软件的时候，可以将上次软件文件夹下的配置基准文件夹拷贝到新程序目标下，这样避免重新配置..."
        )

        # 把两个控件加到分割器里
        splitter.addWidget(self.tab_widget)
        splitter.addWidget(self.text_edit1)

        # 🎯 设置初始宽度比例
        # 左边 tab 初始 800px，右边编辑器占剩下的
        splitter.setSizes([800, 1000])  # 两个数字是左右的初始宽度

        # 可以设置最小宽度，防止拉得太小
        self.tab_widget.setMinimumWidth(400)
        self.text_edit1.setMinimumWidth(400)

        # 把分割器加到主布局
        layout.addWidget(splitter)



        # 1. 创建菜单栏（纯代码）
        self.create_menubar()

        # 2. 创建工具栏（纯代码）
        self.create_toolbar()

        # 3. 创建状态栏（纯代码）
        self.create_statusbar()

    def create_menubar(self):
        """创建菜单栏 - 纯代码实现"""
        # 文件菜单
        file_menu = self.menuBar().addMenu("文件")

        # 新建文件
        new_action = QAction("车型/模式选择", self)
        #new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.open_carchoose_dialog)
        file_menu.addAction(new_action)

        # 保存文件
        save_action = QAction("保存(&S)", self)
        #save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_config)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        # 退出
        exit_action = QAction("退出(&X)", self)
        #exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 设置菜单
        setting_menu = self.menuBar().addMenu("设置")

        # 🎯 综合压测（可勾选）
        zonghe_action = QAction("综合压测", self)
        zonghe_action.setCheckable(True)
        zonghe_action.setChecked(True)  # 默认选中
        zonghe_action.triggered.connect(self.on_zonghe_action_clicked)
        self.zonghe_action = zonghe_action
        setting_menu.addAction(zonghe_action)

        # 🎯 语音测试（可勾选+配置）
        voice_action = QAction("语音测试", self)
        voice_action.setCheckable(True)
        voice_action.setChecked(False)
        voice_action.triggered.connect(self.on_voice_action_clicked)
        self.voice_action = voice_action
        setting_menu.addAction(voice_action)

        # 工具菜单
        tool_menu = self.menuBar().addMenu("工具")
        robot1_action = QAction("机器人", self)
        robot1_action.triggered.connect(self.open_robot_control)
        tool_menu.addAction(robot1_action)

        recorder_action = QAction("录音工具", self)
        recorder_action.triggered.connect(self.open_voice_recorder)
        tool_menu.addAction(recorder_action)

        detector_action = QAction("音频探测", self)
        detector_action.triggered.connect(self.open_audio_detector)
        tool_menu.addAction(detector_action)

        huanxing_action = QAction("语音唤醒", self)
        huanxing_action.triggered.connect(self.show_about)
        tool_menu.addAction(huanxing_action)

        camera_action = QAction("视觉设置", self)
        camera_action.triggered.connect(self.open_visual_setting)
        tool_menu.addAction(camera_action)

        relay_action = QAction("继电器", self)
        relay_action.triggered.connect(self.open_relay_control)
        tool_menu.addAction(relay_action)

        packet_action = QAction("SOME/IP抓包工具", self)
        packet_action.triggered.connect(self.open_packet_capture)
        tool_menu.addAction(packet_action)

        soa_action = QAction("以太网数据监控", self)
        soa_action.triggered.connect(self.show_about)
        tool_menu.addAction(soa_action)

        upload_action = QAction("上传JS脚本", self)
        upload_action.triggered.connect(self.show_about)
        tool_menu.addAction(upload_action)

        dtms_action = QAction("上传DTMS", self)
        dtms_action.triggered.connect(self.show_about)
        tool_menu.addAction(dtms_action)

    def create_toolbar(self):
        """创建工具栏 - 纯代码"""
        toolbar = self.addToolBar("主工具栏")
        toolbar.setMovable(True)#false
        # 🎯 工具栏按钮悬停动效
        #toolbar.setStyleSheet("""
            #QToolBar {
                #background-color: #f5f5f5;
                #border: 1px solid #d0d0d0;;
                #spacing: 4px;
                #padding: 2px;
            #}
            #QToolButton {
                #border: 2px solid transparent;
                #border-radius: 6px;
                #padding: 6px;
                #margin: 2px;
                #background-color: transparent;
            #}
            #QToolButton:hover {
                #background-color: #e3f2fd;
                #border: 2px solid #90caf9;
            #}
            #QToolButton:pressed {
                #background-color: #bbdefb;
                #border: 2px solid #42a5f5;
                #padding: 7px 5px 5px 7px;
            #}
        #""")
        # 运行按钮
        self.play_act = QAction(self)
        self.play_act.setIcon(QIcon(resource_path("image/play.png")))
        self.play_act.setToolTip("开始测试")
        self.play_act.triggered.connect(self.play_clicked)
        self.play_act.setEnabled(True)

        self.pause_act = QAction(self)
        self.pause_act.setIcon(QIcon(resource_path("image/pause.png")))
        self.pause_act.setToolTip("暂停/继续")
        self.pause_act.triggered.connect(self.pause_clicked)
        self.pause_act.setEnabled(False)

        self.stop_act = QAction(self)
        self.stop_act.setIcon(QIcon(resource_path("image/stop.png")))
        self.stop_act.setToolTip("停止测试")
        self.stop_act.triggered.connect(self.stop_clicked)
        self.stop_act.setEnabled(False)

        toolbar.addAction(self.play_act)
        toolbar.addAction(self.pause_act)
        toolbar.addAction(self.stop_act)

        toolbar1 = self.addToolBar("工具栏1")
        toolbar1.setMovable(True)  # false
        # 添加"发飞书消息"复选框
        from PySide6.QtWidgets import QCheckBox, QWidget, QHBoxLayout
        checkbox_widget = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_widget)
        checkbox_layout.setContentsMargins(5, 0, 5, 0)

        self.send_feishu_checkbox = QCheckBox("发飞书消息")
        self.send_feishu_checkbox.setChecked(True)  # 默认勾选

        # 🎯 美化复选框样式
        self.send_feishu_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 12px;
                font-weight: 500;
                spacing: 6px;
                padding: 2px 4px;
                color: #333;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border: 2px solid #2196F3;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border-color: #1976D2;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #64B5F6;
                background-color: #E3F2FD;
            }
            QCheckBox::indicator:checked:hover {
                background-color: #1976D2;
            }
        """)

        checkbox_layout.addWidget(self.send_feishu_checkbox)
        # 🎯 添加"记录测试视频"复选框
        self.record_video_checkbox = QCheckBox("记录测试视频")
        self.record_video_checkbox.setChecked(False)  # 默认不勾选
        self.record_video_checkbox.toggled.connect(self._on_record_video_toggled)

        # 🎯 美化复选框样式
        self.record_video_checkbox.setStyleSheet("""
                                QCheckBox {
                                font-size: 12px;
                                font-weight: 500;
                                spacing: 6px;
                                padding: 2px 4px;
                                color: #333;
                            }
                            QCheckBox::indicator {
                                width: 14px;
                                height: 14px;
                                border: 2px solid #2196F3;
                                border-radius: 3px;
                                background-color: white;
                            }
                            QCheckBox::indicator:checked {
                                background-color: #2196F3;
                                border-color: #1976D2;
                            }
                            QCheckBox::indicator:hover {
                                border: 2px solid #64B5F6;
                                background-color: #E3F2FD;
                            }
                            QCheckBox::indicator:checked:hover {
                                background-color: #1976D2;
                            }
                        """)

        checkbox_layout.addWidget(self.record_video_checkbox)

        #添加黑屏保持现场复选框

        self.keepxc_checkbox = QCheckBox("黑屏保持现场")
        self.keepxc_checkbox.setChecked(False)  # 默认勾选

        # 🎯 美化复选框样式
        self.keepxc_checkbox.setStyleSheet("""
                    QCheckBox {
                        font-size: 12px;
                        font-weight: 500;
                        spacing: 6px;
                        padding: 2px 4px;
                        color: #333;
                    }
                    QCheckBox::indicator {
                        width: 14px;
                        height: 14px;
                        border: 2px solid #2196F3;
                        border-radius: 3px;
                        background-color: white;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #2196F3;
                        border-color: #1976D2;
                    }
                    QCheckBox::indicator:hover {
                        border: 2px solid #64B5F6;
                        background-color: #E3F2FD;
                    }
                    QCheckBox::indicator:checked:hover {
                        background-color: #1976D2;
                    }
                """)

        checkbox_layout.addWidget(self.keepxc_checkbox)

        toolbar1.addWidget(checkbox_widget)


    def append_log_color(self, text, color=None):
        """添加日志 (纯文本黑色)"""
        self.text_edit1.append(text)
        self._scroll_log_to_bottom()

    def append_log_batch(self, lines: list):
        """批量添加日志 (禁用 UI 更新以提高性能)"""
        self.text_edit1.setUpdatesEnabled(False)
        try:
            for line in lines:
                self.text_edit1.append(line)
        finally:
            self.text_edit1.setUpdatesEnabled(True)
            self._scroll_log_to_bottom()

    def on_adb_connect_clicked(self):
        """ADB 连接"""
        self.append_log_color("正在连接设备...", "#2196F3")
        script_path = os.path.join(self.script_dir, "adb_connect.bat")
        self._execute_script(script_path)

    def on_adb_disconnect_clicked(self):
        """ADB 断开连接"""
        self.append_log_color("正在断开 ADB 连接...", "#FF5722")
        script_path = os.path.join(self.script_dir, "adb_kill_server.bat")
        self._execute_script_nolock(script_path)

    def _execute_script(self, script_path, screen_name=""):
        """执行脚本
        Args:
            script_path: 脚本路径
            show_path: 是否在完成后显示保存路径
        """
        if self.current_worker and self.current_worker.isRunning():
            self.append_log_color("已有脚本正在执行，请稍候...", "#FFC107")
            return
        # 使用项目根目录作为工作目录（脚本中的相对路径都是相对于项目根目录）
        project_root = os.path.dirname(os.path.abspath(__file__))
        self.current_worker = ScriptWorker(script_path, project_root, screen_name)
        self.current_worker.log_signal.connect(self.append_log_color)
        self.current_worker.finished_signal.connect(self.on_script_finished)
        self.current_worker.start()

    def _execute_script_nolock(self, script_path):
        """绕过互斥锁直接执行脚本（用于停止类操作）
        在隐藏窗口中运行，不影响正在执行的录制任务
        """
        project_root = os.path.dirname(os.path.abspath(__file__))
        self.append_log_color(f"⏹️ 正在执行：{os.path.basename(script_path)}", "#FFC107")
        subprocess.Popen(
            f'cmd /c "{script_path}"',
            cwd=project_root,
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )



    def on_screen_a_clicked(self):
        """截取 A 屏"""
        self.append_log_color("📸 正在截取 A 屏...", "#2196F3")
        script_path = os.path.join(self.script_dir, "screen_shot_A.bat")
        self._execute_script(script_path, "A 屏")

    def on_screen_b_clicked(self):
        """截取 B 屏"""
        self.append_log_color("📸 正在截取 B 屏...", "#2196F3")
        script_path = os.path.join(self.script_dir, "screen_shot_B.bat")
        self._execute_script(script_path, "B 屏")

    def on_screen_c_clicked(self):
        """截取 C 屏"""
        self.append_log_color("📸 正在截取 C 屏...", "#2196F3")
        script_path = os.path.join(self.script_dir, "screen_shot_C.bat")
        self._execute_script(script_path, "C 屏")

    def on_screen_full_clicked(self):
        """截取全屏"""
        self.append_log_color("📸 正在截取全屏...", "#2196F3")
        script_path = os.path.join(self.script_dir, "screen_shot.bat")
        self._execute_script(script_path, "全屏")

    def on_script_finished(self, return_code):
        """脚本完成"""
        if return_code == 0:
            self.append_log_color("操作完成", "#4CAF50")
        else:
            self.append_log_color("操作失败 (返回码：" + str(return_code) + ")", "#FF5252")


    def on_navi_start_clicked(self):
        """打开导航日志"""
        self.append_log_color("🗺️ 正在打开导航日志...", "#2196F3")
        script_path = os.path.join(self.script_dir, "start_map_log.ps1")
        self._execute_script(script_path)

    def on_navi_pull_clicked(self):
        """抓取导航日志"""
        self.append_log_color("📥 正在抓取导航日志...", "#2196F3")
        script_path = os.path.join(self.script_dir, "pull_all_map_log.ps1")
        self._execute_script(script_path, show_path=True)

    def on_navi_stop_clicked(self):
        """停止导航日志"""
        self.append_log_color("⏹️ 正在停止导航日志...", "#FF5722")
        script_path = os.path.join(self.script_dir, "stop_map_log.ps1")
        self._execute_script_nolock(script_path)

    def on_black_screen_clicked(self):
        """抓取黑屏日志"""
        self.append_log_color("📋 正在抓取黑屏日志...", "#2196F3")
        script_path = os.path.join(self.script_dir, "8295/diag_display.bat")
        self._execute_script(script_path, "")

    def on_gear_a1_clicked(self):
        """A1 屏齿轮图"""
        self.append_log_color("⚙️ 执行 A1 屏齿轮图...", "#03A9F4")
        script_path = os.path.join(self.script_dir, "gearA1.bat")
        self._execute_script(script_path, "A1 屏齿轮")

    def on_gear_a2_clicked(self):
        """A2 屏齿轮图"""
        self.append_log_color("⚙️ 执行 A2 屏齿轮图...", "#03A9F4")
        script_path = os.path.join(self.script_dir, "gearA2.bat")
        self._execute_script(script_path, "A2 屏齿轮")

    def on_gear_b_clicked(self):
        """B 屏齿轮图"""
        self.append_log_color("⚙️ 执行 B 屏齿轮图...", "#03A9F4")
        script_path = os.path.join(self.script_dir, "gearB.bat")
        self._execute_script(script_path, "B 屏齿轮")

    def on_gear_c_clicked(self):
        """C 屏齿轮图"""
        self.append_log_color("⚙️ 执行 C 屏齿轮图...", "#03A9F4")
        script_path = os.path.join(self.script_dir, "gearC.bat")
        self._execute_script(script_path, "C 屏齿轮")

    def on_audio_start_clicked(self):
        """开启 audio"""
        self.append_log_color("🎙️ 开启 audio 录制...", "#03A9F4")
        script_path = os.path.join(self.script_dir, "audio_dump_start.bat")
        self._execute_script(script_path, "")

    def on_audio_stop_clicked(self):
        """停止 audio"""
        self.append_log_color("⏹️ 停止 audio 录制...", "#FF5722")
        script_path = os.path.join(self.script_dir, "audio_dump_stop.bat")
        self._execute_script_nolock(script_path)

    def on_audio_pull_clicked(self):
        """抓取 audio"""
        self.append_log_color("📥 抓取 audio 日志...", "#03A9F4")
        script_path = os.path.join(self.script_dir, "audio_dump_pull.bat")
        self._execute_script(script_path, "")

    def on_bmlog_clicked(self):
        """抓取 BMLog"""
        self.append_log_color("📥 正在抓取 BMLog...", "#03A9F4")
        script_path = os.path.join(self.script_dir, "pull_bmlog.bat")
        self._execute_script(script_path, "")

    def on_yuntool_clicked(self):
        """抓取 yuntoollog"""
        self.append_log_color("📥 正在抓取 yuntoollog...", "#03A9F4")
        script_path = os.path.join(self.script_dir, "pull_yuntool.bat")
        self._execute_script(script_path, "")

    def on_reboot_8295_clicked(self):
        """重启 8295 按钮 - 执行 adb reboot"""
        self.append_log_color("Rebooting 8295...", "#FF5722")
        try:
            import subprocess
            result = subprocess.run(
                ['adb', '-host', 'shell', 'reboot', '-f'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.append_log_color("Reboot command sent", "#4CAF50")
            else:
                self.append_log_color("Reboot error: " + str(result.stderr), "#FF9800")
        except subprocess.TimeoutExpired:
            self.append_log_color("Reboot timeout", "#FF9800")
        except Exception as e:
            self.append_log_color("Reboot failed: " + str(e), "#FF5252")

    def on_8295_version_clicked(self):
        """获取 8295 版本信息（纯 Python 实现，避免编码问题）"""
        self.append_log_color("📥 正在获取 8295 版本信息...", "#03A9F4")
        self._get_8295_version_info()

    def _get_8295_version_info(self):
        """获取 8295 版本信息的内部实现"""
        import subprocess
        work_dir = self.script_dir
        version_file = os.path.join(work_dir, "version.txt")

        def run_adb(cmd):
            """执行 adb 命令并返回输出"""
            try:
                result = subprocess.run(
                    ['adb', '-host', 'shell'] + cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=10,
                    encoding='utf-8',
                    errors='replace'
                )
                return result.stdout.strip()
            except Exception as e:
                return f"Error: {e}"

        # 获取各项信息
        date_val = run_adb("date")
        sys_ver = run_adb("getprop ro.yunos.build.version.release")
        sw_ver = run_adb("getprop ro.zxq.release.version")
        branch = run_adb("getprop ro.product.branch")

        # MCU 版本（解析 sys-test 输出）
        mcu_raw = run_adb("sys-test --get-ver")
        mcu_ver = mcu_raw.split(':_')[-1] if ':_' in mcu_raw else mcu_raw

        # DSP 版本（解析 dsp_upgrade 输出）
        dsp_raw = run_adb("dsp_upgrade --get_ver")
        dsp_ver = dsp_raw.split(':', 1)[-1].strip() if ':' in dsp_raw else dsp_raw

        sn = run_adb("getprop ro.serialno")
        vin = run_adb("getprop persist.sys.vin")

        # UUID
        uuid_raw = run_adb("getprop | findstr uuid")

        # 显示到日志窗口
        self.append_log_color(f"当前时间：{date_val}", "#000000")
        self.append_log_color(f"系统版本：{sys_ver}", "#000000")
        self.append_log_color(f"软件版本：{sw_ver}", "#000000")
        self.append_log_color(f"版本分支：{branch}", "#000000")
        self.append_log_color(f"MCU 版本：{mcu_ver}", "#000000")
        self.append_log_color(f"DSP 版本：{dsp_ver}", "#000000")
        self.append_log_color(f"SN: {sn}", "#000000")
        self.append_log_color(f"VIN: {vin}", "#000000")
        self.append_log_color(f"UUID: {uuid_raw}", "#000000")

        # 保存到文件
        try:
            with open(version_file, 'w', encoding='utf-8') as f:
                f.write(f"当前时间：{date_val}\n")
                f.write(f"系统版本：{sys_ver}\n")
                f.write(f"软件版本：{sw_ver}\n")
                f.write(f"版本分支：{branch}\n")
                f.write(f"MCU 版本：{mcu_ver}\n")
                f.write(f"DSP 版本：{dsp_ver}\n")
                f.write(f"SN: {sn}\n")
                f.write(f"VIN: {vin}\n")
                f.write(f"UUID: {uuid_raw}\n")
            self.append_log_color(f"📁 已保存到：{version_file}", "#4CAF50")
        except Exception as e:
            self.append_log_color(f"❌ 保存失败：{e}", "#FF5252")

    def on_eth_start_clicked(self):
        """打开以太网TCP抓包"""
        self.append_log_color("🌐 正在打开以太网TCP抓包...", "#03A9F4")
        script_path = os.path.join(self.script_dir, "8295", "eth_dump_start.bat")
        self._execute_script(script_path, "")

    def on_eth_stop_clicked(self):
        """关闭以太网TCP抓包"""
        self.append_log_color("⏹️ 正在关闭以太网TCP抓包...", "#FF5722")
        script_path = os.path.join(self.script_dir, "8295", "eth_dump_stop.bat")
        self._execute_script_nolock(script_path)

    def on_eth_pull_clicked(self):
        """抓取以太网TCP数据"""
        self.append_log_color("📥 正在抓取以太网TCP数据...", "#03A9F4")
        script_path = os.path.join(self.script_dir, "8295", "eth_dump_pull.bat")
        self._execute_script(script_path, "")

    def on_mic_start_clicked(self):
        """打开录音"""
        self.append_log_color("🎙️ 正在打开录音...", "#03A9F4")
        script_path = os.path.join(self.script_dir, "8295", "mic_dump_start.bat")
        self._execute_script(script_path, "")

    def on_mic_stop_clicked(self):
        """关闭录音"""
        self.append_log_color("⏹️ 正在关闭录音...", "#FF5722")
        script_path = os.path.join(self.script_dir, "8295", "mic_dump_stop.bat")
        self._execute_script_nolock(script_path)

    def on_mic_pull_clicked(self):
        """抓取录音"""
        self.append_log_color("📥 正在抓取录音...", "#03A9F4")
        script_path = os.path.join(self.script_dir, "8295", "mic_dump_pull.bat")
        self._execute_script(script_path, "")

    def on_screen_version_clicked(self):
        """查询屏幕MCU版本"""
        self.append_log_color("🖥️ 正在查询屏幕MCU版本...", "#03A9F4")
        script_path = os.path.join(self.script_dir, "screen_version.bat")
        self._execute_script(script_path, "")

    # ================================================================
    # 诊断服务 - 事件处理
    # ================================================================

    def on_diag_ecu_selected(self, item):
        """控制器选择"""
        self.selected_ecu_key = item.data(Qt.UserRole)
        ecu_name = item.text().strip()
        self.append_log_color(f"📌 已选择控制器: {ecu_name}", "#2196F3")
        # LHZCU/RHZCU/RZCU/PODA 系列通过 ICB 转发，选择时自动连接 ICB
        if self.selected_ecu_key in ["lhzcu", "rhzcu", "rzcu", "flpoda", "frpoda", "rlpoda", "rrpoda", "cf", "peu", "rhpmwc", "rlss", "ccu", "hodm", "lvbm", "nfcam", "tc", "tdm", "broadcast"]:
            if not self.diag_doip_connected:
                self.append_log_color(f"🔄 自动连接 ICB 网关...", "#2196F3")
                self._connect_doip_async("icb")


    def _connect_doip_async(self, ecu_key="icb"):
        """异步连接 DoIP (ICB 或 IPD)"""
        class ConnectThread(QThread):
            finished = Signal(bool, str, object)
            def __init__(self, ecu):
                super().__init__()
                self.ecu = ecu
            def run(self):
                try:
                    if self.ecu == "icb":
                        client = DoIPClient(ICB_DOIP_IP, ICB_DOIP_PORT)
                        client.connect()
                        result = client.routing_activate()
                        self.finished.emit(True, "ICB 连接成功", client)
                    elif self.ecu == "ipd":
                        client = DoIPClient(IPD_DOIP_IP, IPD_DOIP_PORT)
                        client.connect()
                        result = client.routing_activate()
                        self.finished.emit(True, "IPD 连接成功", client)
                except Exception as e:
                    try:
                        client.disconnect()
                    except:
                        pass
                    self.finished.emit(False, str(e), None)

        self._diag_connect_thread = ConnectThread(ecu_key)
        self._diag_connect_thread.finished.connect(self._on_doip_connect_result)
        self._diag_connect_thread.start()

    def _on_doip_connect_result(self, success, msg, client):
        """DoIP连接结果回调"""
        if success:
            if self.selected_ecu_key == "icb":
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功", "#4CAF50")
                # 预热 daemon (不切换会话，保持 ECU 当前状态)
                try:
                    sa_calc.calc_key('00000000', '00001042')
                except:
                    pass
            elif self.selected_ecu_key == "ipd":
                # IPD 通过 ICB 转发，复用 ICB 的连接
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.ipd_doip_connected = True
                self.ipd_doip_client = client
                self.append_log_color(f"✅ IPD DoIP 连接成功 (通过 ICB 转发)", "#4CAF50")
            elif self.selected_ecu_key == "lhzcu":
                # LHZCU 通过 ICB 转发，复用 ICB 的连接
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (LHZCU 网关已就绪)", "#4CAF50")
            elif self.selected_ecu_key == "rhzcu":
                # RHZCU 通过 ICB 转发，复用 ICB 的连接
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (RHZCU 网关已就绪)", "#4CAF50")
            elif self.selected_ecu_key == "rzcu":
                # RZCU 通过 ICB 转发，复用 ICB 的连接
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (RZCU 网关已就绪)", "#4CAF50")
            elif self.selected_ecu_key == "lvbm":
                # LVBM 通过 ICB 转发，复用 ICB 的连接
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.lvbm_doip_connected = True
                self.lvbm_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (LVBM 网关已就绪)", "#4CAF50")
            elif self.selected_ecu_key == "nfcam":
                # NFCAM 通过 ICB 转发，复用 ICB 的连接
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.nfcam_doip_connected = True
                self.nfcam_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (NFCAM 网关已就绪)", "#4CAF50")

            elif self.selected_ecu_key == "rwsl":
                # RWSL 通过 ICB 转发，复用 ICB 的连接
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (RWSL 网关已就绪)", "#4CAF50")
            elif self.selected_ecu_key == "rlpoda":
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.rlpoda_doip_connected = True
                self.rlpoda_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (RLPODA 网关已就绪)", "#4CAF50")
            elif self.selected_ecu_key == "rrpoda":
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.rrpoda_doip_connected = True
                self.rrpoda_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (RRPODA 网关已就绪)", "#4CAF50")
            # 检查是否有待执行的动作
            elif self.selected_ecu_key == "scm":
                # SCM 通过 ICB 转发，复用 ICB 的连接
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (SCM 网关已就绪)", "#4CAF50")
            elif self.selected_ecu_key == "sdm":
                # SDM 通过 ICB 转发，复用 ICB 的连接
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (SDM 网关已就绪)", "#4CAF50")
            elif self.selected_ecu_key == "ess":
                # ESS 通过 ICB 转发，复用 ICB 的连接
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (ESS 网关已就绪)", "#4CAF50")
            elif self.selected_ecu_key == "racfp":
                # RACFP 通过 ICB 转发，复用 ICB 的连接
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (RACFP 网关已就绪)", "#4CAF50")
            elif self.selected_ecu_key == "fdr":
                # FDR 通过 ICB 转发，复用 ICB 的连接
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (FDR 网关已就绪)", "#4CAF50")
            elif self.selected_ecu_key == "flpoda":
                # FLPODA 通过 ICB 转发，复用 ICB 的连接
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.flpoda_doip_connected = True
                self.flpoda_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (FLPODA 网关已就绪)", "#4CAF50")
            elif self.selected_ecu_key == "frpoda":
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.frpoda_doip_connected = True
                self.frpoda_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (FRPODA 网关已就绪)", "#4CAF50")
            elif self.selected_ecu_key == "fwm":
                # FWM 通过 ICB 转发，复用 ICB 的连接
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (FWM 网关已就绪)", "#4CAF50")
            elif self.selected_ecu_key == "hodm":
                # HODM 通过 ICB 转发，复用 ICB 的连接
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.hodm_doip_connected = True
                self.hodm_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (HODM 网关已就绪)", "#4CAF50")
            elif self.selected_ecu_key == "nfcsm":
                # NFCSM 通过 ICB 转发，复用 ICB 的连接
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (NFCSM 网关已就绪)", "#4CAF50")
            elif self.selected_ecu_key == "pma":
                # PMA 通过 ICB 转发，复用 ICB 的连接
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (PMA 网关已就绪)", "#4CAF50")
            elif self.selected_ecu_key == "cf":
                # CF 通过 ICB 转发，复用 ICB 的连接
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.cf_doip_connected = True
                self.cf_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (CF 网关已就绪)", "#4CAF50")
            elif self.selected_ecu_key == "ccu":
                # CCU 通过 ICB 转发，复用 ICB 的连接
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.ccu_doip_connected = True
                self.ccu_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (CCU 网关已就绪)", "#4CAF50")
            elif self.selected_ecu_key == "peu":
                # PEU 通过 ICB 转发，复用 ICB 的连接
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.peu_doip_connected = True
                self.peu_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (PEU 网关已就绪)", "#4CAF50")
            elif self.selected_ecu_key == "rhpmwc":
                # RHPMWC 通过 ICB 转发，复用 ICB 的连接
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.rhpmwc_doip_connected = True
                self.rhpmwc_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (RHPMWC 网关已就绪)", "#4CAF50")
            elif self.selected_ecu_key == "rlss":
                # RLSS 通过 ICB 转发，复用 ICB 的连接
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.rlss_doip_connected = True
                self.rlss_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (RLSS 网关已就绪)", "#4CAF50")
            elif self.selected_ecu_key == "tc":
                # TC 通过 ICB 转发，复用 ICB 的连接
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.tc_doip_connected = True
                self.tc_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (TC 网关已就绪)", "#4CAF50")
            elif self.selected_ecu_key == "tdm":
                # TDM 通过 ICB 转发，复用 ICB 的连接
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.tdm_doip_connected = True
                self.tdm_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (TDM 网关已就绪)", "#4CAF50")
            elif self.selected_ecu_key == "broadcast":
                # BROADCAST 通过 ICB 转发，复用 ICB 的连接
                self.diag_doip_connected = True
                self.diag_doip_client = client
                self.broadcast_doip_connected = True
                self.broadcast_doip_client = client
                self.append_log_color(f"✅ ICB DoIP 连接成功 (BROADCAST 0xEFFF 网关已就绪)", "#4CAF50")
            self._execute_pending_diag_action()
        else:
            self.diag_doip_connected = False
            self.append_log_color(f"❌ ICB连接失败: {msg}", "#FF5252")
            self._diag_pending_cmd = None
            self._diag_pending_action = None

    def _execute_pending_diag_action(self):
        """连接成功后执行待处理的诊断动作"""
        action = self._diag_pending_action
        cmd = self._diag_pending_cmd
        self._diag_pending_action = None
        self._diag_pending_cmd = None

        if action == 'cmd' and cmd:
            if self.selected_ecu_key == "icb":
                self._icb_send_uds_cmd(cmd)
            elif self.selected_ecu_key == "ipd":
                self._ipd_send_uds_cmd(cmd)
            elif self.selected_ecu_key == "rwsl":
                self._rwsl_send_uds_cmd(cmd)
            elif self.selected_ecu_key == "rlpoda":
                self._rlpoda_send_uds_cmd(cmd)
            elif self.selected_ecu_key == "rrpoda":
                self._rrpoda_send_uds_cmd(cmd)
            elif self.selected_ecu_key == "scm":
                self._scm_send_uds_cmd(cmd)
            elif self.selected_ecu_key == "sdm":
                self._sdm_send_uds_cmd(cmd)
            elif self.selected_ecu_key == "ess":
                self._ess_send_uds_cmd(cmd)
            elif self.selected_ecu_key == "racfp":
                self._racfp_send_uds_cmd(cmd)
            elif self.selected_ecu_key == "fdr":
                self._fdr_send_uds_cmd(cmd)
            elif self.selected_ecu_key == "flpoda":
                self._flpoda_send_uds_cmd(cmd)
            elif self.selected_ecu_key == "frpoda":
                self._frpoda_send_uds_cmd(cmd)
            elif self.selected_ecu_key == "fwm":
                self._fwm_send_uds_cmd(cmd)
            elif self.selected_ecu_key == "nfcsm":
                self._nfcsm_send_uds_cmd(cmd)
            elif self.selected_ecu_key == "pma":
                self._pma_send_uds_cmd(cmd)
            elif self.selected_ecu_key == "cf":
                self._cf_send_uds_cmd(cmd)
            elif self.selected_ecu_key == "peu":
                self._peu_send_uds_cmd(cmd)
            elif self.selected_ecu_key == "rhpmwc":
                self._rhpmwc_send_uds_cmd(cmd)
            elif self.selected_ecu_key == "rlss":
                self._rlss_send_uds_cmd(cmd)
            elif self.selected_ecu_key == "ccu":
                self._ccu_send_uds_cmd(cmd)
            elif self.selected_ecu_key == "hodm":
                self._hodm_send_uds_cmd(cmd)
            elif self.selected_ecu_key == "lvbm":
                self._lvbm_send_uds_cmd(cmd)
            elif self.selected_ecu_key == "nfcam":
                self._nfcam_send_uds_cmd(cmd)
            elif self.selected_ecu_key == "tc":
                self._tc_send_uds_cmd(cmd)
            elif self.selected_ecu_key == "tdm":
                self._tdm_send_uds_cmd
                self._broadcast_send_uds_cmd(cmd)
        elif action == 'reset':
            if self.selected_ecu_key == "icb":
                self._icb_reset_ecu()
            elif self.selected_ecu_key == "ipd":
                self._ipd_reset_ecu()
            elif self.selected_ecu_key == "rwsl":
                self._rwsl_reset_ecu()
            elif self.selected_ecu_key == "rlpoda":
                self._rlpoda_reset_ecu()
            elif self.selected_ecu_key == "rrpoda":
                self._rrpoda_reset_ecu()
            elif self.selected_ecu_key == "scm":
                self._scm_reset_ecu()
            elif self.selected_ecu_key == "sdm":
                self._sdm_reset_ecu()
            elif self.selected_ecu_key == "ess":
                self._ess_reset_ecu()
            elif self.selected_ecu_key == "racfp":
                self._racfp_reset_ecu()
            elif self.selected_ecu_key == "fdr":
                self._fdr_reset_ecu()
            elif self.selected_ecu_key == "flpoda":
                self._flpoda_reset_ecu()
            elif self.selected_ecu_key == "frpoda":
                self._frpoda_reset_ecu()
            elif self.selected_ecu_key == "fwm":
                self._fwm_reset_ecu()
            elif self.selected_ecu_key == "nfcsm":
                self._nfcsm_reset_ecu()
            elif self.selected_ecu_key == "pma":
                self._pma_reset_ecu()
            elif self.selected_ecu_key == "cf":
                self._cf_reset_ecu()
            elif self.selected_ecu_key == "peu":
                self._peu_reset_ecu()
            elif self.selected_ecu_key == "rhpmwc":
                self._rhpmwc_reset_ecu()
            elif self.selected_ecu_key == "rlss":
                self._rlss_reset_ecu()
            elif self.selected_ecu_key == "ccu":
                self._ccu_reset_ecu()
            elif self.selected_ecu_key == "hodm":
                self._hodm_reset_ecu()
            elif self.selected_ecu_key == "lvbm":
                self._lvbm_reset_ecu()
            elif self.selected_ecu_key == "nfcam":
                self._nfcam_reset_ecu()
            elif self.selected_ecu_key == "tc":
                self._tc_reset_ecu()
            elif self.selected_ecu_key == "tdm":
                self._tdm_reset_ecu()
        elif action == 'reset' and self.selected_ecu_key == 'broadcast':
            self._broadcast_reset_ecu()
        elif action == 'dtc_read':
            if self.selected_ecu_key == "icb":
                self._icb_read_dtc()
            elif self.selected_ecu_key == "ipd":
                self._ipd_read_dtc()
            elif self.selected_ecu_key == "rwsl":
                self._rwsl_read_dtc()
            elif self.selected_ecu_key == "rlpoda":
                self._rlpoda_read_dtc()
            elif self.selected_ecu_key == "rrpoda":
                self._rrpoda_read_dtc()
            elif self.selected_ecu_key == "scm":
                self._scm_read_dtc()
            elif self.selected_ecu_key == "sdm":
                self._sdm_read_dtc()
            elif self.selected_ecu_key == "ess":
                self._ess_read_dtc()
            elif self.selected_ecu_key == "racfp":
                self._racfp_read_dtc()
            elif self.selected_ecu_key == "fdr":
                self._fdr_read_dtc()
            elif self.selected_ecu_key == "flpoda":
                self._flpoda_read_dtc()
            elif self.selected_ecu_key == "frpoda":
                self._frpoda_read_dtc()
            elif self.selected_ecu_key == "fwm":
                self._fwm_read_dtc()
            elif self.selected_ecu_key == "nfcsm":
                self._nfcsm_read_dtc()
            elif self.selected_ecu_key == "pma":
                self._pma_read_dtc()
            elif self.selected_ecu_key == "cf":
                self._cf_read_dtc()
            elif self.selected_ecu_key == "peu":
                self._peu_read_dtc()
            elif self.selected_ecu_key == "rhpmwc":
                self._rhpmwc_read_dtc()
            elif self.selected_ecu_key == "rlss":
                self._rlss_read_dtc()
            elif self.selected_ecu_key == "ccu":
                self._ccu_read_dtc()
            elif self.selected_ecu_key == "hodm":
                self._hodm_read_dtc()
            elif self.selected_ecu_key == "lvbm":
                self._lvbm_read_dtc()
            elif self.selected_ecu_key == "nfcam":
                self._nfcam_read_dtc()
            elif self.selected_ecu_key == "tc":
                self._tc_read_dtc()
            elif self.selected_ecu_key == "tdm":
                self._tdm_read_dtc()
        elif action == 'dtc_read' and self.selected_ecu_key == 'broadcast':
            self._broadcast_read_dtc()
        elif action == 'dtc_clear':
            if self.selected_ecu_key == "icb":
                self._icb_clear_dtc()
            elif self.selected_ecu_key == "ipd":
                self._ipd_clear_dtc()
            elif self.selected_ecu_key == "rwsl":
                self._rwsl_clear_dtc()
            elif self.selected_ecu_key == "rlpoda":
                self._rlpoda_clear_dtc()
            elif self.selected_ecu_key == "rrpoda":
                self._rrpoda_clear_dtc()
            elif self.selected_ecu_key == "scm":
                self._scm_clear_dtc()
            elif self.selected_ecu_key == "sdm":
                self._sdm_clear_dtc()
            elif self.selected_ecu_key == "ess":
                self._ess_clear_dtc()
            elif self.selected_ecu_key == "racfp":
                self._racfp_clear_dtc()
            elif self.selected_ecu_key == "fdr":
                self._fdr_clear_dtc()
            elif self.selected_ecu_key == "flpoda":
                self._flpoda_clear_dtc()
            elif self.selected_ecu_key == "frpoda":
                self._frpoda_clear_dtc()
            elif self.selected_ecu_key == "fwm":
                self._fwm_clear_dtc()
            elif self.selected_ecu_key == "nfcsm":
                self._nfcsm_clear_dtc()
            elif self.selected_ecu_key == "pma":
                self._pma_clear_dtc()
            elif self.selected_ecu_key == "cf":
                self._cf_clear_dtc()
            elif self.selected_ecu_key == "peu":
                self._peu_clear_dtc()
            elif self.selected_ecu_key == "rhpmwc":
                self._rhpmwc_clear_dtc()
            elif self.selected_ecu_key == "rlss":
                self._rlss_clear_dtc()
            elif self.selected_ecu_key == "ccu":
                self._ccu_clear_dtc()
            elif self.selected_ecu_key == "hodm":
                self._hodm_clear_dtc()
            elif self.selected_ecu_key == "lvbm":
                self._lvbm_clear_dtc()
            elif self.selected_ecu_key == "nfcam":
                self._nfcam_clear_dtc()
            elif self.selected_ecu_key == "tc":
                self._tc_clear_dtc()
            elif self.selected_ecu_key == "tdm":
                self._tdm_clear_dtc()
        elif self._diag_pending_action == 'dtc_clear' and self.selected_ecu_key == 'broadcast':
            self._broadcast_clear_dtc()

    def on_diag_read_clicked(self):
        """读取故障码"""
        ecu_name = self._get_selected_ecu_name()
        self.append_log_color(f"🔍 正在读取 {ecu_name} 故障码...", "#2196F3")

        if self.selected_ecu_key == "icb":
            if not self.diag_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 ICB未连接，正在自动连接...", "#2196F3")
                self._connect_doip_async()
                return
            self._icb_read_dtc()
        elif self.selected_ecu_key == "ipd":
            if not self.diag_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 IPD 未连接，正在自动连接...", "#2196F3")
                self._connect_doip_async()
                return
            self._ipd_read_dtc()
        elif self.selected_ecu_key == "adcu":
            if not self.adcu_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 ADCU 未连接，正在自动连接...", "#2196F3")
                self._connect_adcu_doip()
                return
            self._adcu_read_dtc()
        elif self.selected_ecu_key == "dpp":
            if not self.dpp_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 DPP 未连接，正在自动连接...", "#2196F3")
                self._connect_dpp_doip()
                return
            self._dpp_read_dtc()
        elif self.selected_ecu_key == "epmcu":
            if not self.epmcu_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 EPMCU 未连接，正在自动连接...", "#2196F3")
                self._connect_epmcu_doip()
                return
            self._epmcu_read_dtc()
        elif self.selected_ecu_key == "eps":
            if not self.eps_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 EPS 未连接，正在自动连接...", "#2196F3")
                self._connect_eps_doip()
                return
            self._eps_read_dtc()
        elif self.selected_ecu_key == "IAM":
            if not self.iam_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 IAM 未连接，正在自动连接...", "#2196F3")
                self._connect_iam_doip()
                return
            self._iam_read_dtc()
        elif self.selected_ecu_key == "ibs":
            if not self.ibs_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 IBS 未连接，正在自动连接...", "#2196F3")
                self._connect_ibs_doip()
                return
            self._ibs_read_dtc()
        elif self.selected_ecu_key == "lhzcu":
            if not self.diag_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 ICB 未连接，无法转发 LHZCU 诊断", "#2196F3")
                self._connect_doip_async()
                return
            self._lhzcu_read_dtc()
        elif self.selected_ecu_key == "rhzcu":
            if not self.diag_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 ICB 未连接，无法转发 RHZCU 诊断", "#2196F3")
                self._connect_doip_async()
                return
            self._rhzcu_read_dtc()
        elif self.selected_ecu_key == "rzcu":
            if not self.diag_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 ICB 未连接，无法转发 RZCU 诊断", "#2196F3")
                self._connect_doip_async()
                return
            self._rzcu_read_dtc()
        elif self.selected_ecu_key == "rwsl":
            if not self.rwsl_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 RWSL 未连接，正在自动连接...", "#2196F3")
                self._connect_rwsl_doip()
                return
            self._rwsl_read_dtc()
        elif self.selected_ecu_key == "rlpoda":
            if not self.rlpoda_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 RLPODA 未连接，正在自动连接...", "#2196F3")
                self._connect_rlpoda_doip()
                return
            self._rlpoda_read_dtc()
        elif self.selected_ecu_key == "rrpoda":
            if not self.rrpoda_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 RRPODA 未连接，正在自动连接...", "#2196F3")
                self._connect_rrpoda_doip()
                return
            self._rrpoda_read_dtc()
        elif self.selected_ecu_key == "scm":
            if not self.scm_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 SCM 未连接，正在自动连接...", "#2196F3")
                self._connect_scm_doip()
                return
            self._scm_read_dtc()
        elif self.selected_ecu_key == "sdm":
            if not self.sdm_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 SDM 未连接，正在自动连接...", "#2196F3")
                self._connect_sdm_doip()
                return
            self._sdm_read_dtc()
        elif self.selected_ecu_key == "ess":
            if not self.ess_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 ESS 未连接，正在自动连接...", "#2196F3")
                self._connect_ess_doip()
                return
            self._ess_read_dtc()
        elif self.selected_ecu_key == "racfp":
            if not self.racfp_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 RACFP 未连接，正在自动连接...", "#2196F3")
                self._connect_racfp_doip()
                return
            self._racfp_read_dtc()
        elif self.selected_ecu_key == "fdr":
            if not self.fdr_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 FDR 未连接，正在自动连接...", "#2196F3")
                self._connect_fdr_doip()
                return
            self._fdr_read_dtc()
        elif self.selected_ecu_key == "flpoda":
            if not self.flpoda_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 FLPODA 未连接，正在自动连接...", "#2196F3")
                self._connect_flpoda_doip()
                return
            self._flpoda_read_dtc()
        elif self.selected_ecu_key == "frpoda":
            if not self.frpoda_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 FRPODA 未连接，正在自动连接...", "#2196F3")
                self._connect_frpoda_doip()
                return
            self._frpoda_read_dtc()
        elif self.selected_ecu_key == "fwm":
            if not self.fwm_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 FWM 未连接，正在自动连接...", "#2196F3")
                self._connect_fwm_doip()
                return
            self._fwm_read_dtc()
        elif self.selected_ecu_key == "nfcsm":
            if not self.nfcsm_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 NFCSM 未连接，正在自动连接...", "#2196F3")
                self._connect_nfcsm_doip()
                return
            self._nfcsm_read_dtc()
        elif self.selected_ecu_key == "pma":
            if not self.pma_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 PMA 未连接，正在自动连接...", "#2196F3")
                self._connect_pma_doip()
                return
            self._pma_read_dtc()
        elif self.selected_ecu_key == "cf":
            if not self.cf_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 CF 未连接，正在自动连接...", "#2196F3")
                self._connect_cf_doip()
                return
            self._cf_read_dtc()
        elif self.selected_ecu_key == "peu":
            if not self.peu_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 PEU 未连接，正在自动连接...", "#2196F3")
                self._connect_peu_doip()
                return
            self._peu_read_dtc()
        elif self.selected_ecu_key == "rhpmwc":
            if not self.rhpmwc_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 RHPMWC 未连接，正在自动连接...", "#2196F3")
                self._connect_rhpmwc_doip()
                return
            self._rhpmwc_read_dtc()
        elif self.selected_ecu_key == "rlss":
            if not self.rlss_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 RLSS 未连接，正在自动连接...", "#2196F3")
                self._connect_rlss_doip()
                return
            self._rlss_read_dtc()
        elif self.selected_ecu_key == "ccu":
            if not self.ccu_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 CCU 未连接，正在自动连接...", "#2196F3")
                self._connect_ccu_doip()
                return
            self._ccu_read_dtc()
        elif self.selected_ecu_key == "hodm":
            if not self.hodm_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 HODM 未连接，正在自动连接...", "#2196F3")
                self._connect_hodm_doip()
                return
            self._hodm_read_dtc()
        elif self.selected_ecu_key == "lvbm":
            if not self.lvbm_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 LVBM 未连接，正在自动连接...", "#2196F3")
                self._connect_lvbm_doip()
                return
            self._lvbm_read_dtc()
        elif self.selected_ecu_key == "nfcam":
            if not self.nfcam_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 NFCAM 未连接，正在自动连接...", "#2196F3")
                self._connect_nfcam_doip()
                return
            self._nfcam_read_dtc()
        elif self.selected_ecu_key == "tc":
            if not self.tc_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 TC 未连接，正在自动连接...", "#2196F3")
                self._connect_tc_doip()
                return
            self._tc_read_dtc()
        elif self.selected_ecu_key == "tdm":
            if not self.tdm_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 TDM 未连接，正在自动连接...", "#2196F3")
                self._connect_tdm_doip()
                return
            self._tdm_read_dtc()
        elif self.selected_ecu_key == "broadcast":
            if not self.diag_doip_connected:
                self._diag_pending_action = 'dtc_read'
                self.append_log_color("🔄 ICB 未连接，无法转发 BROADCAST 诊断", "#2196F3")
                self._connect_doip_async()
                return
            self._broadcast_read_dtc()
        elif self.selected_ecu_key == "all":
            self._execute_diag_cmd("读取故障码", "all")
        else:
            self._execute_diag_cmd("读取故障码", self.selected_ecu_key)

    def _icb_send_uds_raw(self, data: bytes, timeout: float = 2.0):
        """发送UDS指令到ICB并返回原始响应(bytes), 失败返回None"""
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            return None
        try:
            return client.send_diagnostic(data, timeout=timeout)
        except Exception:
            return None

    def _icb_read_dtc(self):
        """通过DoIP读取ICB的DTC故障码 (IDS方式)"""
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ ICB未连接，请先连接", "#FF5252")
            return

        try:
            # Step 1: 19 02 2C - 按状态掩码读取有效DTC (pending + confirmed + testFailedSinceClear)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x1000 19 02 2C", "#64B5F6")
            QApplication.processEvents()
            resp = self._icb_send_uds_raw(bytes([0x19, 0x02, 0x2C]))
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC列表超时", "#FF5252")
                return
            formatted = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x1000 {formatted}", "#81C784")
            QApplication.processEvents()

            # 解析DTC列表
            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color("  ✅ 无有效DTC", "#4CAF50")
                return

            self.append_log_color(f"  发现 {len(dtc_records)} 个DTC", "#FF9800")

            # Step 2: 对每个 DTC 查询详细快照 (19 04) 和扩展数据 (19 06)
            # 优化：收集所有日志，最后批量写入
            log_lines = []

            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']  # 3 bytes DTC code
                dtc_label = dtc['label']  # e.g. "B1A87_87"

                # 19 04 - 快照数据
                ts = self._diag_timestamp()
                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                log_lines.append(f"{ts} tx 0x1000 {' '.join(f'{b:02X}' for b in cmd_04)}")
                resp_04 = self._icb_send_uds_raw(cmd_04, timeout=0.3)
                if resp_04:
                    f = ' '.join(f'{b:02X}' for b in resp_04)
                    log_lines.append(f"{self._diag_timestamp()} rx 0x1000 {f}")
                    dtc['snapshot_raw'] = resp_04

                # 19 06 - 扩展数据
                ts = self._diag_timestamp()
                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                log_lines.append(f"{ts} tx 0x1000 {' '.join(f'{b:02X}' for b in cmd_06)}")
                resp_06 = self._icb_send_uds_raw(cmd_06, timeout=0.3)
                if resp_06:
                    f = ' '.join(f'{b:02X}' for b in resp_06)
                    log_lines.append(f"{self._diag_timestamp()} rx 0x1000 {f}")
                    dtc['extended_raw'] = resp_06

            # 批量写入日志
            self.append_log_batch(log_lines)

            # Step 3: 显示结果（表格格式）
            self._display_dtc_table(dtc_records)


        except Exception as e:
            self._diag_on_socket_error(e)
            self.append_log_color(f"❌ DTC读取异常: {e}", "#FF5252")
            import traceback
            self.append_log_color(traceback.format_exc(), "#FF5252")

    def _parse_dtc_02_response(self, resp: bytes) -> list:
        """解析 19 02 响应, 返回DTC列表 [{raw, label, status_hex, status_bits}]
        支持多段 59 02 FF 拼接 (ICB网关把多个CAN ECU的响应聚合到一起)"""
        dtcs = []
        pos = 0
        while pos < len(resp):
            # 寻找下一段 59 02
            idx = resp.find(b'\x59\x02', pos)
            if idx < 0:
                break
            if idx + 4 > len(resp):  # 至少 59 02 XX + 1字节status mask
                break

            # 找下一段 59 02 作为当前段的结束边界
            next_idx = resp.find(b'\x59\x02', idx + 1)
            if next_idx < 0:
                seg = resp[idx:]
            else:
                seg = resp[idx:next_idx]

            # 找本段结尾的 59 FF (7F FF 等非59 02的格式也可能是段尾)
            # 但实际上协议规定 59 02 是开始标记，所以取到下一个 59 02 之前就行

            seg_offset = 2  # skip 59 02

            # DTCStatusAvailabilityMask (1字节, 如 FF)
            if seg_offset < len(seg):
                seg_offset += 1

            # 每4字节 = DTC(3) + Status(1)
            while seg_offset + 4 <= len(seg):
                d = seg[seg_offset:seg_offset+3]
                status = seg[seg_offset+3]
                seg_offset += 4

                # 解码DTC编码
                dtc_code = (d[0] << 16) | (d[1] << 8) | d[2]
                prefix_map = {0: 'P', 1: 'C', 2: 'B', 3: 'U'}
                prefix = prefix_map.get((d[0] >> 6) & 0x03, '?')
                high = d[0] & 0x3F
                mid = d[1]
                low = d[2]
                dtc_label = f"{prefix}{high:X}{mid:02X}_{low:02X}"

                # 状态位解析
                bits = []
                if status & 0x01: bits.append("testFailed")
                if status & 0x02: bits.append("testFailedThisOpCycle")
                if status & 0x04: bits.append("pendingDTC")
                if status & 0x08: bits.append("confirmedDTC")
                if status & 0x10: bits.append("testNotCompletedSinceClear")
                if status & 0x20: bits.append("testFailedSinceClear")

                dtcs.append({
                    'raw': d,
                    'code': dtc_code,
                    'label': dtc_label,
                    'status_hex': f"{status:02X}",
                    'status_bits': ' '.join(bits),
                    'status_byte': status,
                    'snapshot_raw': None,
                    'extended_raw': None,
                })

            # 跳到下一个段
            pos = idx + 1 if next_idx < 0 else next_idx

        return dtcs


    def _parse_extended_06(self, data):
        """Parse 59 06 extended data response (RecordNumber 0x01).
        Format: 59 06 DTC(3) Status(1) RecordNum(1) [fault_cnt, pending_cnt, aged_cnt, aging_cnt]
        """
        result = {
            "fault_cnt": 0,
            "pending_cnt": 0,
            "aged_cnt": 0,
            "aging_cnt": 0,
        }
        if not data or len(data) < 8 or data[0] != 0x59 or data[1] != 0x06:
            return result
        # Skip: 59 06 (2) + DTC(3) + Status(1) = 6 bytes header
        # Then: RecordNumber(1) + data
        pos = 6
        if pos >= len(data):
            return result
        rec_num = data[pos]
        pos += 1
        remaining = data[pos:]
        if rec_num == 0x01 and len(remaining) >= 4:
            # IDS format: [fault_cnt, pending_cnt, aged_cnt, aging_cnt]
            result["fault_cnt"] = remaining[0]
            result["pending_cnt"] = remaining[1]
            result["aged_cnt"] = remaining[2]
            result["aging_cnt"] = remaining[3]
        elif len(remaining) >= 2:
            # Fallback: generic parsing
            result["fault_cnt"] = remaining[0] if remaining[0] < 250 else 0
            if len(remaining) >= 4:
                result["aging_cnt"] = remaining[3]
        return result
    def _display_dtc_table(self, dtc_records: list):
        """显示 DTC 结果表格到信息窗口 - 支持 Part4 DTC 解析"""

        def vis_width(s):
            """计算字符串在等宽字体下的显示宽度 (CJK 汉字占 2 格)"""
            w = 0
            for ch in s:
                if '\u4e00' <= ch <= '\u9fff' or '\u3000' <= ch <= '\u303f' or '\uff00' <= ch <= '\uffef':
                    w += 2
                else:
                    w += 1
            return w

        def pad_left(s, w):
            """按显示宽度左对齐填充空格，超出则至少留 1 格分割"""
            avail = w - vis_width(s)
            if avail < 0:
                return s + ' '  # 超出时至少留 1 格
            return s + ' ' * avail  # 左对齐：内容 + 空格

        # IDS 风格：Tab 分隔
        tab_sep = chr(9)
        headers = ['ECU', 'DTC', '故障掩码', '故障状态', '亮灯请求',
                   '故障计数', '待定计数', '已经老化', '老化计数',
                   '电源模式', '供电电压', '里程读数', '记录时刻', '故障含义']
        self.append_log_color(tab_sep.join(headers), "#90CAF9")

        # 如果没有 DTC，显示提示
        if not dtc_records:
            self.append_log_color("无故障码", "#4CAF50")
            return

        # Part4 DTC 解析器 (ICB/IPD 补充)
        parser = ipd_dtc_parser.get_ipd_parser() if 'ipd_dtc_parser' in globals() else None

        for dtc in dtc_records:
            dtc_key = ''.join(f'{b:02X}' for b in dtc['raw']).upper()
            dtc_label = dtc['label']
            status_byte = dtc['status_byte']

            # 获取 DTC 含义 (IDS 数据库优先，Part4 解析器作为 ICB/IPD 的补充)
            meaning = ''
            ids_ecu_map = {
                'icb': 'ICB', 'ipd': 'IPD', 'iam': 'IAM', 'eps': 'EPS',
                'adcu': 'ADCU', 'dpp': 'DPP', 'epmcu': 'EPMCU',
                'lhzcu': 'LHZCU', 'rhzcu': 'RHZCU', 'rlpoda': 'RLPODA', 'rrpoda': 'RRPODA', 'rzcu': 'RZCU',
                'ibs': 'IBS', 'amp': 'AMP', 'pma': 'PMA',
                'rwsl': 'RWSL', 'scm': 'SCM', 'sdm': 'SDM',
                'racfp': 'RACFP',
                'fdr': 'FDR',
                'flpoda': 'FLPODA',
                'frpoda': 'FRPODA',
                'fwm': 'FWM',
                'cf': 'CF',
                'peu': 'PEU',
                'rhpmwc': 'RHPMWC',
                'ccu': 'CCU',
                'hodm': 'HODM',
                'lvbm': 'LVBM',
                'nfcam': 'NFCAM',
                'tc': 'TC',
                'tdm': 'TDM',
    'broadcast': 'BROADCAST',
                'rlss': 'RLSS',
            }
            ids_ecu = ids_ecu_map.get(self.selected_ecu_key.lower(), '')
            # 优先使用 IDS 数据库查询
            if ids_ecu and dtc_label:
                meaning = ids_lookup_dtc(dtc_label, ids_ecu)
            # 如果 IDS 未查到，回退到 Part4 解析器 (ICB/IPD 专有)
            if not meaning and parser and parser.loaded:
                dtc_info = parser.get_dtc(dtc_label)
                if dtc_info:
                    meaning = dtc_info.description_cn if dtc_info.description_cn else dtc_info.description_en

            # 解析状态字节
            status_bin = format(status_byte, '08b')

            # ISO 14229-1 状态字节定义
            test_failed = bool(status_byte & 0x01)  # Bit 0: 当前故障
            confirmed = bool(status_byte & 0x08)    # Bit 3: 已确认 DTC
            pending = bool(status_byte & 0x04)      # Bit 2: 待定 DTC
            lamp_req = bool(status_byte & 0x80)     # Bit 7: 亮灯请求

            # 中文显示
            if test_failed:
                fault_state_text = "当前故障"
            elif confirmed:
                fault_state_text = "已确认"
            elif pending:
                fault_state_text = "待定"
            else:
                fault_state_text = "历史故障"

            lamp_req_text = "请求过" if lamp_req else "未请求"

            # 解析扩展数据 (故障/老化计数器)
            ext_parsed = {}
            ext_raw = dtc.get('extended_raw', '')
            if ext_raw:
                try:
                    ext_parsed = self._parse_extended_06(bytes.fromhex(ext_raw))
                except:
                    pass
            fault_cnt = ext_parsed.get('fault_cnt', 0)
            pending_cnt = ext_parsed.get('pending_cnt', 0)
            aging = ext_parsed.get('aged_cnt', 0)
            aging_cnt = ext_parsed.get('aging_cnt', 0)
            power_mode = voltage = mileage = timestamp_str = ''

            # 解析快照数据
            snap = dtc.get('snapshot_raw')
            if snap and len(snap) > 10:
                for e in self._parse_snapshot_04(snap).get('raw_idents', []):
                    name = e.get('name', '')
                    decoded = e.get('decoded', '')
                    if not decoded:
                        continue
                    if name == 'SupplyVoltage':
                        voltage = decoded.replace('V', '')
                    elif name == 'Odometer':
                        mileage = decoded.split()[0]
                    elif name == 'DateTime':
                        timestamp_str = decoded
                    elif name == 'VehicleState':
                        # 简化显示：只显示 Mode 值
                        if 'Mode=' in decoded:
                            parts = decoded.split()
                            power_mode = parts[0] if parts else decoded
                        else:
                            power_mode = decoded

            # ECU 名称
            ecu_key = getattr(self, 'selected_ecu_key', '')
            ecu_name_map = {
                'icb': 'ICB',
                'ipd': 'IPD',
                'iam': 'IAM',
                'eps': 'EPS',
                'epmcu': 'EPMCU',
                'dpp': 'DPP',
                'lhzcu': 'LHZCU',
                'rhzcu': 'RHZCU',
                'rlpoda': 'RLPODA',
                'rrpoda': 'RRPODA',
                'rzcu': 'RZCU',
                'adcu': 'ADCU',
                'ibs': 'IBS',
                'ess': 'ESS',
                'pma': 'PMA',
                'racfp': 'RACFP',
                'fdr': 'FDR',
                'flpoda': 'FLPODA',
                'frpoda': 'FRPODA',
                'fwm': 'FWM',
                'nfcsm': 'NFCSM',
                'ccu': 'CCU',
                'hodm': 'HODM',
                'lvbm': 'LVBM',
                'nfcam': 'NFCAM',
                'tc': 'TC',
                'tdm': 'TDM',
                'cf': 'CF',
                'peu': 'PEU',
                'rhpmwc': 'RHPMWC',
                'rlss': 'RLSS',
            }
            # 功能广播：优先使用 DTC 来源 ECU
            ecu_source = dtc.get('ecu_source', '')
            ecu_name = ecu_source if ecu_source else ecu_name_map.get(ecu_key.lower(), 'ICB')
            values = [ecu_name, dtc_label, status_bin, fault_state_text, lamp_req_text,
                      str(fault_cnt), str(pending_cnt), str(aging), str(aging_cnt),
                      power_mode, voltage, mileage, timestamp_str, meaning]

            # IDS 风格：Tab 分隔 (不写 "\t" 字面，用 chr(9))
            tab_sep = chr(9)
            self.append_log_color(tab_sep.join(values), "#FFD54F")

        # 不显示 (共X个 DTC) 行



    def _display_single_dtc(self, dtc: dict, dtc_meaning: dict):
        """显示单个 DTC 结果（流式显示）"""
        dtc_key = ''.join(f'{b:02X}' for b in dtc['raw']).upper()
        meaning = dtc_meaning.get(dtc_key, '')

        status_bin = format(dtc['status_byte'], '08b')
        fault_state = 1 if dtc['status_byte'] & 0x08 else 0
        lamp_req = 1 if dtc['status_byte'] & 0x20 else 0
        fault_cnt = pending_cnt = aging = aging_cnt = 0
        power_mode = voltage = mileage = timestamp_str = ''

        snap = dtc.get('snapshot_raw')
        if snap and len(snap) > 10:
            for e in self._parse_snapshot_04(snap).get('raw_idents', []):
                name = e.get('name', '')
                decoded = e.get('decoded', '')
                if not decoded:
                    continue
                if name == 'SupplyVoltage':
                    voltage = decoded
                elif name == 'Odometer':
                    mileage = decoded.split()[0]
                elif name == 'DateTime':
                    timestamp_str = decoded
                elif name == 'VehicleState':
                    # 简化显示：只显示 Mode 值
                    if 'Mode=' in decoded:
                        parts = decoded.split()
                        power_mode = parts[0] if parts else decoded
                    else:
                        power_mode = decoded

        # 根据当前选择的 ECU 显示名称
        ecu_name = 'IPD' if self.selected_ecu_key == 'ipd' else 'ICB'

        # 左对齐显示
        def vis_width(s):
            w = 0
            for ch in s:
                if '\u4e00' <= ch <= '\u9fff' or '\u3000' <= ch <= '\u303f' or '\uff00' <= ch <= '\uffef':
                    w += 2
                else:
                    w += 1
            return w

        fault_state_text = "当前故障" if fault_state else "已确认"
        lamp_req_text = "请求过" if lamp_req else "未请求"

        # IDS 风格：表格对齐
        col_widths = [4, 12, 10, 10, 10, 10, 10, 10, 10, 12, 10, 10, 22, 0]
        values = [ecu_name, dtc['label'], status_bin, fault_state_text, lamp_req_text,
                  str(fault_cnt), str(pending_cnt), str(aging), str(aging_cnt),
                  power_mode, voltage, mileage, timestamp_str, meaning]

        line = ''
        for i, v in enumerate(values):
            w = col_widths[i]
            if w > 0:
                vw = vis_width(v)
                line += v + ' ' * (w - vw + 2)
            else:
                line += v
        self.append_log_color(line, "#FFD54F")

    def _parse_snapshot_04(self, data: bytes) -> dict:
        """解析 59 04 快照响应 (按ICB Part4规范)"""
        result = {'raw_idents': []}
        if len(data) < 10 or data[0] != 0x59 or data[1] != 0x04:
            return result

        # 59 04 | DTC(3) | Status(1) | RecordNum(1) | NumIdentifiers(1) = 8 bytes
        num_idents = data[7]
        pos = 8

        # DID定义表: (size, name, decoder_func)
        did_defs = {
            0x0112: (1, 'SupplyVoltage'),
            0xE101: (3, 'Odometer'),
            0x010B: (6, 'DateTime'),
            0xE010: (2, 'VehicleSpeed'),
            0xD002: (1, 'VehicleState'),
            0xD001: (1, 'PowerMode'),
        }

        for _ in range(num_idents):
            if pos + 3 > len(data):
                break
            did = (data[pos] << 8) | data[pos+1]
            pos += 2

            spec = did_defs.get(did)
            if spec:
                data_len = spec[0]
            else:
                data_len = 2  # 未识别DID默认2字节

            if pos + data_len > len(data):
                break

            raw_hex = ' '.join(f'{data[pos+k]:02X}' for k in range(data_len))
            raw_bytes = data[pos:pos+data_len]

            # 解码
            decoded = ''
            name = spec[1] if spec else f'UNKNOWN_{did:04X}'
            if did == 0x0112 and len(raw_bytes) >= 1:
                vol = raw_bytes[0] * 0.1
                decoded = f'{vol:.1f}V'
            elif did == 0xE101 and len(raw_bytes) >= 3:
                odom = (raw_bytes[0] << 16) | (raw_bytes[1] << 8) | raw_bytes[2]
                decoded = f'{odom} km'
            elif did == 0x010B and len(raw_bytes) >= 6:
                yr = 2000 + raw_bytes[0]
                mo = raw_bytes[1]
                dy = raw_bytes[2]
                hr = raw_bytes[3]
                mi = raw_bytes[4]
                sc = raw_bytes[5]
                decoded = f'{yr:04d}/{mo:02d}/{dy:02d} {hr:02d}:{mi:02d}:{sc:02d}'
            elif did == 0xE010 and len(raw_bytes) >= 2:
                speed = (raw_bytes[0] << 8) | raw_bytes[1]
                decoded = f'{speed} km/h'
            elif did == 0xD002 and len(raw_bytes) >= 1:
                vm = (raw_bytes[0] >> 4) & 0x0F
                um = raw_bytes[0] & 0x0F
                decoded = f'Mode={vm} Usage={um}'

            result['raw_idents'].append({
                'did': f'{did:04X}',
                'name': name,
                'raw': raw_hex,
                'decoded': decoded,
            })
            pos += data_len

        return result

    def _save_dtc_excel(self, dtc_records: list):
        """保存DTC到Excel (类似IDS)"""
        if not dtc_records:
            return
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "DTC"

            # 表头
            headers = ['ECU', 'DTC码', '故障掩码', '故障状态', '亮灯请求', '故障计数', '待定计数', '已老化', '老化计数', '电源模式', '供电电压(V)', '里程读数(km)', '记录时刻', '故障含义']
            header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
            header_font = Font(bold=True, color='FFFFFF', size=11)
            thin_border = Border(
                left=Side(style='thin'), right=Side(style='thin'),
                top=Side(style='thin'), bottom=Side(style='thin'))

            for col, h in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=h)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.border = thin_border

            # 数据行
            for row_idx, dtc in enumerate(dtc_records, 2):
                snap = dtc.get('snapshot_raw')
                parsed = self._parse_snapshot_04(snap) if snap else {}

                # 默认值
                status_bin = format(dtc['status_byte'], '08b')
                fault_state = 1 if dtc['status_byte'] & 0x08 else 0
                lamp_req = 1 if dtc['status_byte'] & 0x20 else 0
                # 解析扩展数据
                ext_parsed = {}
                ext_raw = dtc.get('extended_raw', '')
                if ext_raw:
                    try:
                        ext_parsed = self._parse_extended_06(bytes.fromhex(ext_raw))
                    except:
                        pass
                fault_cnt = ext_parsed.get('fault_cnt', 0)
                pending_cnt = ext_parsed.get('pending_cnt', 0)
                aging = ext_parsed.get('aged_cnt', 0)
                aging_cnt = ext_parsed.get('aging_cnt', 0)
                power_mode = ''
                voltage = ''
                mileage = ''
                ts = ''

                idents = parsed.get('raw_idents', [])
                for e in idents:
                    name = e.get('name', '')
                    decoded = e.get('decoded', '')
                    if not decoded:
                        continue
                    if name == 'SupplyVoltage':
                        voltage = decoded
                    elif name == 'Odometer':
                        mileage = decoded.split()[0]
                    elif name == 'DateTime':
                        ts = decoded
                    elif name == 'VehicleState':
                        power_mode = decoded

                # 来源 ECU 名称（功能广播优先）
                ecu_source = dtc.get('ecu_source', '')
                if not ecu_source:
                    ecu_name_map = {
                    'icb': 'ICB', 'ipd': 'IPD', 'iam': 'IAM', 'eps': 'EPS',
                    'epmcu': 'EPMCU', 'dpp': 'DPP', 'lhzcu': 'LHZCU',
                    'rhzcu': 'RHZCU', 'rzcu': 'RZCU', 'rlpoda': 'RLPODA', 'rrpoda': 'RRPODA', 'adcu': 'ADCU', 'ibs': 'IBS',
                    'amp': 'AMP', 'pma': 'PMA', 'rwsl': 'RWSL',
                    'scm': 'SCM', 'sdm': 'SDM',
                    'ess': 'ESS',
                    'racfp': 'RACFP', 'fdr': 'FDR', 'flpoda': 'FLPODA',
                    'frpoda': 'FRPODA',
                    'fwm': 'FWM',
                    'nfcsm': 'NFCSM',
                    'cf': 'CF', 'peu': 'PEU',
                    'rhpmwc': 'RHPMWC', 'rlss': 'RLSS',
                    'ccu': 'CCU', 'hodm': 'HODM', 'lvbm': 'LVBM',
                    'nfcam': 'NFCAM', 'tc': 'TC', 'tdm': 'TDM',
                    'broadcast': 'BROADCAST',
                }
                ecu_name = ecu_source if ecu_source else ecu_name_map.get(self.selected_ecu_key.lower(), 'ICB')
                # 使用 IDS 数据库查询 DTC 含义
                dtc_meaning_val = ids_lookup_dtc(dtc['label'], ecu_name)
                ws.cell(row=row_idx, column=1, value=ecu_name).border = thin_border
                ws.cell(row=row_idx, column=2, value=dtc['label']).border = thin_border
                ws.cell(row=row_idx, column=3, value=status_bin).border = thin_border
                ws.cell(row=row_idx, column=4, value=fault_state).border = thin_border
                ws.cell(row=row_idx, column=5, value=lamp_req).border = thin_border
                ws.cell(row=row_idx, column=6, value=fault_cnt).border = thin_border
                ws.cell(row=row_idx, column=7, value=pending_cnt).border = thin_border
                ws.cell(row=row_idx, column=8, value=aging).border = thin_border
                ws.cell(row=row_idx, column=9, value=aging_cnt).border = thin_border
                ws.cell(row=row_idx, column=10, value=power_mode).border = thin_border
                ws.cell(row=row_idx, column=11, value=voltage).border = thin_border
                ws.cell(row=row_idx, column=12, value=mileage).border = thin_border
                ws.cell(row=row_idx, column=13, value=ts).border = thin_border
                ws.cell(row=row_idx, column=14, value=dtc_meaning_val).border = thin_border

            # 自适应列宽
            for col in range(1, len(headers) + 1):
                max_len = len(str(headers[col-1]))
                for row in range(2, len(dtc_records) + 2):
                    val = ws.cell(row=row, column=col).value
                    if val:
                        max_len = max(max_len, len(str(val)))
                ws.column_dimensions[chr(64 + col)].width = max_len + 4

            # 保存到程序目录下的DTC文件夹
            if hasattr(sys, '_MEIPASS'):
                base_dir = os.path.dirname(os.path.abspath(sys.executable))
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
            save_dir = os.path.join(base_dir, 'DTC')
            os.makedirs(save_dir, exist_ok=True)
            dtc_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            # 根据当前选择的 ECU 命名文件
            ecu_name_map = {
                'icb': 'ICB', 'ipd': 'IPD', 'iam': 'IAM', 'eps': 'EPS',
                'epmcu': 'EPMCU', 'dpp': 'DPP', 'lhzcu': 'LHZCU',
                'rhzcu': 'RHZCU', 'rlpoda': 'RLPODA', 'rrpoda': 'RRPODA', 'rzcu': 'RZCU', 'adcu': 'ADCU', 'ibs': 'IBS',
                'ess': 'ESS',
                'pma': 'PMA',
                'racfp': 'RACFP',
                'fdr': 'FDR',
                'flpoda': 'FLPODA',
                'frpoda': 'FRPODA',
                'fwm': 'FWM',
                'nfcsm': 'NFCSM',
                'ccu': 'CCU',
                'hodm': 'HODM',
                'lvbm': 'LVBM',
                'nfcam': 'NFCAM',
                'tc': 'TC',
                'tdm': 'TDM',
                'cf': 'CF',
                'peu': 'PEU',
                'rhpmwc': 'RHPMWC',
                'rlss': 'RLSS',
            }
            ecu_prefix = ecu_name_map.get(self.selected_ecu_key.lower(), 'ICB')
            filepath = os.path.join(save_dir, f"{ecu_prefix}_DTC_{dtc_time}.xlsx")
            wb.save(filepath)
            self.append_log_color(f"  💾 DTC已保存: {filepath}", "#81C784")

        except ImportError:
            self.append_log_color("  ⚠ openpyxl未安装, 跳过Excel保存", "#FF9800")
        except Exception as e:
            self.append_log_color(f"  ⚠ Excel保存失败: {e}", "#FF9800")

    def _parse_and_display_dtc(self, resp: bytes):
        """解析并显示DTC结果 (旧方式 - 不再使用)"""
        # 保留作为隐式调用兼容
        pass

    def on_diag_clear_clicked(self):
        """清除故障码"""
        ecu_name = self._get_selected_ecu_name()
        self.append_log_color(f"🧹 正在清除 {ecu_name} 故障码...", "#FF5722")

        if self.selected_ecu_key == "icb":
            if not self.diag_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 ICB未连接，正在自动连接...", "#2196F3")
                self._connect_doip_async()
                return
            self._icb_clear_dtc()
        elif self.selected_ecu_key == "ipd":
            if not self.diag_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 IPD 未连接，正在自动连接...", "#2196F3")
                self._connect_doip_async()
                return
            self._ipd_clear_dtc()
        elif self.selected_ecu_key == "adcu":
            if not self.adcu_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 ADCU 未连接，正在自动连接...", "#2196F3")
                self._connect_adcu_doip()
                return
            self._adcu_clear_dtc()
        elif self.selected_ecu_key == "dpp":
            if not self.dpp_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 DPP 未连接，正在自动连接...", "#2196F3")
                self._connect_dpp_doip()
                return
            self._dpp_clear_dtc()
        elif self.selected_ecu_key == "epmcu":
            if not self.epmcu_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 EPMCU 未连接，正在自动连接...", "#2196F3")
                self._connect_epmcu_doip()
                return
            self._epmcu_clear_dtc()
        elif self.selected_ecu_key == "eps":
            if not self.eps_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 EPS 未连接，正在自动连接...", "#2196F3")
                self._connect_eps_doip()
                return
            self._eps_clear_dtc()
        elif self.selected_ecu_key == "IAM":
            if not self.iam_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 IAM 未连接，正在自动连接...", "#2196F3")
                self._connect_iam_doip()
                return
            self._iam_clear_dtc()
        elif self.selected_ecu_key == "ibs":
            if not self.ibs_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 IBS 未连接，正在自动连接...", "#2196F3")
                self._connect_ibs_doip()
                return
            self._ibs_clear_dtc()
        elif self.selected_ecu_key == "lhzcu":
            if not self.diag_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 ICB 未连接，无法转发 LHZCU 诊断", "#2196F3")
                self._connect_doip_async()
                return
            self._lhzcu_clear_dtc()
        elif self.selected_ecu_key == "rhzcu":
            if not self.diag_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 ICB 未连接，无法转发 RHZCU 诊断", "#2196F3")
                self._connect_doip_async()
                return
            self._rhzcu_clear_dtc()
        elif self.selected_ecu_key == "rzcu":
            if not self.diag_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 ICB 未连接，无法转发 RZCU 诊断", "#2196F3")
                self._connect_doip_async()
                return
            self._rzcu_clear_dtc()
        elif self.selected_ecu_key == "rwsl":
            if not self.rwsl_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 RWSL 未连接，正在自动连接...", "#2196F3")
                self._connect_rwsl_doip()
                return
            self._rwsl_clear_dtc()
        elif self.selected_ecu_key == "rlpoda":
            if not self.rlpoda_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 RLPODA 未连接，正在自动连接...", "#2196F3")
                self._connect_rlpoda_doip()
                return
            self._rlpoda_clear_dtc()
        elif self.selected_ecu_key == "rrpoda":
            if not self.rrpoda_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 RRPODA 未连接，正在自动连接...", "#2196F3")
                self._connect_rrpoda_doip()
                return
            self._rrpoda_clear_dtc()
        elif self.selected_ecu_key == "scm":
            if not self.scm_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 SCM 未连接，正在自动连接...", "#2196F3")
                self._connect_scm_doip()
                return
            self._scm_clear_dtc()
        elif self.selected_ecu_key == "sdm":
            if not self.sdm_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 SDM 未连接，正在自动连接...", "#2196F3")
                self._connect_sdm_doip()
                return
            self._sdm_clear_dtc()
        elif self.selected_ecu_key == "ess":
            if not self.ess_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 ESS 未连接，正在自动连接...", "#2196F3")
                self._connect_ess_doip()
                return
            self._ess_clear_dtc()
        elif self.selected_ecu_key == "racfp":
            if not self.racfp_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 RACFP 未连接，正在自动连接...", "#2196F3")
                self._connect_racfp_doip()
                return
            self._racfp_clear_dtc()
        elif self.selected_ecu_key == "fdr":
            if not self.fdr_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 FDR 未连接，正在自动连接...", "#2196F3")
                self._connect_fdr_doip()
                return
            self._fdr_clear_dtc()
        elif self.selected_ecu_key == "flpoda":
            if not self.flpoda_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 FLPODA 未连接，正在自动连接...", "#2196F3")
                self._connect_flpoda_doip()
                return
            self._flpoda_clear_dtc()
        elif self.selected_ecu_key == "frpoda":
            if not self.frpoda_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 FRPODA 未连接，正在自动连接...", "#2196F3")
                self._connect_frpoda_doip()
                return
            self._frpoda_clear_dtc()
        elif self.selected_ecu_key == "fwm":
            if not self.fwm_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 FWM 未连接，正在自动连接...", "#2196F3")
                self._connect_fwm_doip()
                return
            self._fwm_clear_dtc()
        elif self.selected_ecu_key == "nfcsm":
            if not self.nfcsm_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 NFCSM 未连接，正在自动连接...", "#2196F3")
                self._connect_nfcsm_doip()
                return
            self._nfcsm_clear_dtc()
        elif self.selected_ecu_key == "pma":
            if not self.pma_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 PMA 未连接，正在自动连接...", "#2196F3")
                self._connect_pma_doip()
                return
            self._pma_clear_dtc()
        elif self.selected_ecu_key == "cf":
            if not self.cf_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 CF 未连接，正在自动连接...", "#2196F3")
                self._connect_cf_doip()
                return
            self._cf_clear_dtc()
        elif self.selected_ecu_key == "peu":
            if not self.peu_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 PEU 未连接，正在自动连接...", "#2196F3")
                self._connect_peu_doip()
                return
            self._peu_clear_dtc()
        elif self.selected_ecu_key == "rhpmwc":
            if not self.rhpmwc_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 RHPMWC 未连接，正在自动连接...", "#2196F3")
                self._connect_rhpmwc_doip()
                return
            self._rhpmwc_clear_dtc()
        elif self.selected_ecu_key == "rlss":
            if not self.rlss_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 RLSS 未连接，正在自动连接...", "#2196F3")
                self._connect_rlss_doip()
                return
            self._rlss_clear_dtc()
        elif self.selected_ecu_key == "ccu":
            if not self.ccu_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 CCU 未连接，正在自动连接...", "#2196F3")
                self._connect_ccu_doip()
                return
            self._ccu_clear_dtc()
        elif self.selected_ecu_key == "hodm":
            if not self.hodm_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 HODM 未连接，正在自动连接...", "#2196F3")
                self._connect_hodm_doip()
                return
            self._hodm_clear_dtc()
        elif self.selected_ecu_key == "lvbm":
            if not self.lvbm_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 LVBM 未连接，正在自动连接...", "#2196F3")
                self._connect_lvbm_doip()
                return
            self._lvbm_clear_dtc()
        elif self.selected_ecu_key == "nfcam":
            if not self.nfcam_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 NFCAM 未连接，正在自动连接...", "#2196F3")
                self._connect_nfcam_doip()
                return
            self._nfcam_clear_dtc()
        elif self.selected_ecu_key == "tc":
            if not self.tc_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 TC 未连接，正在自动连接...", "#2196F3")
                self._connect_tc_doip()
                return
            self._tc_clear_dtc()
        elif self.selected_ecu_key == "tdm":
            if not self.tdm_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 TDM 未连接，正在自动连接...", "#2196F3")
                self._connect_tdm_doip()
                return
            self._tdm_clear_dtc()
        elif self.selected_ecu_key == "broadcast":
            if not self.diag_doip_connected:
                self._diag_pending_action = 'dtc_clear'
                self.append_log_color("🔄 ICB 未连接，无法转发 BROADCAST 诊断", "#2196F3")
                self._connect_doip_async()
                return
            self._broadcast_clear_dtc()
        elif self.selected_ecu_key == "all":
            self._execute_diag_cmd("清除故障码", "all")
        else:
            self._execute_diag_cmd("清除故障码", self.selected_ecu_key)

    def on_diag_reset_clicked(self):
        """执行 ECU Reset (11 01 硬复位)"""
        ecu_name = self._get_selected_ecu_name()
        self.append_log_color(f"🔄 正在对 {ecu_name} 执行 ECU Reset (11 01)...", "#FF9800")

        if self.selected_ecu_key == "icb":
            if not self.diag_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 ICB 未连接，正在自动连接...", "#2196F3")
                self._connect_doip_async("icb")
                return
            self._icb_reset_ecu()
        elif self.selected_ecu_key == "ipd":
            # IPD 通过 ICB 转发，复用 ICB 的 DoIP 连接
            if not self.diag_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 IPD 通过 ICB 转发，正在连接 ICB...", "#2196F3")
                self._connect_doip_async("icb")
                return
            self._ipd_reset_ecu()
        elif self.selected_ecu_key == "adcu":
            if not self.adcu_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 ADCU 未连接，正在自动连接...", "#2196F3")
                self._connect_adcu_doip()
                return
            self._adcu_reset_ecu()
        elif self.selected_ecu_key == "dpp":
            if not self.dpp_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 DPP 未连接，正在自动连接...", "#2196F3")
                self._connect_dpp_doip()
                return
            self._dpp_reset_ecu()
        elif self.selected_ecu_key == "epmcu":
            if not self.epmcu_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 EPMCU 未连接，正在自动连接...", "#2196F3")
                self._connect_epmcu_doip()
                return
            self._epmcu_reset_ecu()
        elif self.selected_ecu_key == "eps":
            if not self.eps_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 EPS 未连接，正在自动连接...", "#2196F3")
                self._connect_eps_doip()
                return
            self._eps_reset_ecu()
        elif self.selected_ecu_key == "IAM":
            if not self.iam_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 IAM 未连接，正在自动连接...", "#2196F3")
                self._connect_iam_doip()
                return
            self._iam_reset_ecu()
        elif self.selected_ecu_key == "ibs":
            if not self.ibs_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 IBS 未连接，正在自动连接...", "#2196F3")
                self._connect_ibs_doip()
                return
            self._ibs_reset_ecu()
        elif self.selected_ecu_key == "rwsl":
            if not self.rwsl_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 RWSL 未连接，正在自动连接...", "#2196F3")
                self._connect_rwsl_doip()
                return
            self._rwsl_reset_ecu()
        elif self.selected_ecu_key == "rlpoda":
            if not self.rlpoda_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 RLPODA 未连接，正在自动连接...", "#2196F3")
                self._connect_rlpoda_doip()
                return
            self._rlpoda_reset_ecu()
        elif self.selected_ecu_key == "rrpoda":
            if not self.rrpoda_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 RRPODA 未连接，正在自动连接...", "#2196F3")
                self._connect_rrpoda_doip()
                return
            self._rrpoda_reset_ecu()
        elif self.selected_ecu_key == "scm":
            if not self.scm_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 SCM 未连接，正在自动连接...", "#2196F3")
                self._connect_scm_doip()
                return
            self._scm_reset_ecu()
        elif self.selected_ecu_key == "sdm":
            if not self.sdm_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 SDM 未连接，正在自动连接...", "#2196F3")
                self._connect_sdm_doip()
                return
            self._sdm_reset_ecu()
        elif self.selected_ecu_key == "ess":
            if not self.ess_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 ESS 未连接，正在自动连接...", "#2196F3")
                self._connect_ess_doip()
                return
            self._ess_reset_ecu()
        elif self.selected_ecu_key == "racfp":
            if not self.racfp_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 RACFP 未连接，正在自动连接...", "#2196F3")
                self._connect_racfp_doip()
                return
            self._racfp_reset_ecu()
        elif self.selected_ecu_key == "fdr":
            if not self.fdr_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 FDR 未连接，正在自动连接...", "#2196F3")
                self._connect_fdr_doip()
                return
            self._fdr_reset_ecu()
        elif self.selected_ecu_key == "flpoda":
            if not self.flpoda_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 FLPODA 未连接，正在自动连接...", "#2196F3")
                self._connect_flpoda_doip()
                return
            self._flpoda_reset_ecu()
        elif self.selected_ecu_key == "frpoda":
            if not self.frpoda_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 FRPODA 未连接，正在自动连接...", "#2196F3")
                self._connect_frpoda_doip()
                return
            self._frpoda_reset_ecu()
        elif self.selected_ecu_key == "fwm":
            if not self.fwm_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 FWM 未连接，正在自动连接...", "#2196F3")
                self._connect_fwm_doip()
                return
            self._fwm_reset_ecu()
        elif self.selected_ecu_key == "nfcsm":
            if not self.nfcsm_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 NFCSM 未连接，正在自动连接...", "#2196F3")
                self._connect_nfcsm_doip()
                return
            self._nfcsm_reset_ecu()
        elif self.selected_ecu_key == "pma":
            if not self.pma_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 PMA 未连接，正在自动连接...", "#2196F3")
                self._connect_pma_doip()
                return
            self._pma_reset_ecu()
        elif self.selected_ecu_key == "cf":
            if not self.cf_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 CF 未连接，正在自动连接...", "#2196F3")
                self._connect_cf_doip()
                return
            self._cf_reset_ecu()
        elif self.selected_ecu_key == "peu":
            if not self.peu_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 PEU 未连接，正在自动连接...", "#2196F3")
                self._connect_peu_doip()
                return
            self._peu_reset_ecu()
        elif self.selected_ecu_key == "rhpmwc":
            if not self.rhpmwc_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 RHPMWC 未连接，正在自动连接...", "#2196F3")
                self._connect_rhpmwc_doip()
                return
            self._rhpmwc_reset_ecu()
        elif self.selected_ecu_key == "rlss":
            if not self.rlss_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 RLSS 未连接，正在自动连接...", "#2196F3")
                self._connect_rlss_doip()
                return
            self._rlss_reset_ecu()
        elif self.selected_ecu_key == "ccu":
            if not self.ccu_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 CCU 未连接，正在自动连接...", "#2196F3")
                self._connect_ccu_doip()
                return
            self._ccu_reset_ecu()
        elif self.selected_ecu_key == "hodm":
            if not self.hodm_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 HODM 未连接，正在自动连接...", "#2196F3")
                self._connect_hodm_doip()
                return
            self._hodm_reset_ecu()
        elif self.selected_ecu_key == "lvbm":
            if not self.lvbm_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 LVBM 未连接，正在自动连接...", "#2196F3")
                self._connect_lvbm_doip()
                return
            self._lvbm_reset_ecu()
        elif self.selected_ecu_key == "nfcam":
            if not self.nfcam_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 NFCAM 未连接，正在自动连接...", "#2196F3")
                self._connect_nfcam_doip()
                return
            self._nfcam_reset_ecu()
        elif self.selected_ecu_key == "tc":
            if not self.tc_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 TC 未连接，正在自动连接...", "#2196F3")
                self._connect_tc_doip()
                return
            self._tc_reset_ecu()
        elif self.selected_ecu_key == "tdm":
            if not self.tdm_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 TDM 未连接，正在自动连接...", "#2196F3")
                self._connect_tdm_doip()
                return
            self._tdm_reset_ecu()
        elif self.selected_ecu_key == "broadcast":
            if not self.diag_doip_connected:
                self._diag_pending_action = 'reset'
                self.append_log_color("🔄 ICB 未连接，无法转发 BROADCAST 诊断", "#2196F3")
                self._connect_doip_async()
                return
            self._broadcast_reset_ecu()
        elif self.selected_ecu_key == "all":
            self.append_log_color("❌ 请选择具体控制器后再执行 Reset", "#FF5252")
        else:
            self.append_log_color("❌ 该控制器暂不支持 Reset 功能", "#FF5252")

    def _icb_reset_ecu(self):
        """通过 DoIP 发送 ICB 的 ECU Reset (11 01)"""
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ ICB 未连接，请先连接", "#FF5252")
            return
        try:
            # 快速检查连接是否有效
            if not client.sock or client.sock.fileno() == -1:
                self.append_log_color("⚠️ 连接已断开，正在重连...", "#2196F3")
                self._diag_pending_action = 'reset'
                self._connect_doip_async()
                return

            # 发送 11 01 (ECU Reset - Hard Reset)
            cmd_11_01 = bytes([0x11, 0x01])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x1000 11 01", "#64B5F6")
            QApplication.processEvents()

            # ICB Reset 使用逻辑地址 0x1000
            resp = client.send_diagnostic(cmd_11_01, target_addr=ICB_LOGICAL_ADDR, timeout=2.0)
            if resp is None:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 无响应 (超时)", "#FF5252")
                return

            resp_hex = resp.hex().upper()
            formatted = ' '.join(resp_hex[i:i+2] for i in range(0, len(resp_hex), 2))
            ts_rx = self._diag_timestamp()

            ecu_name = self._get_selected_ecu_name()
            if resp[0] == 0x51:
                self.append_log_color(f"{ts_rx} rx 0x1000 {formatted} ✅ {ecu_name} Reset 成功", "#4CAF50")
                self.append_log_color(f"💡 提示：{ecu_name} 即将重启，可能需要等待几秒后重新连接", "#FF9800")
            elif resp[0] == 0x7F:
                nrc = resp[2] if len(resp) > 2 else 0
                nrc_desc = self._diag_nrc_desc(nrc)
                # NRC 0x78 (Response Pending) 是 Reset 的正常响应
                if nrc == 0x78:
                    self.append_log_color(f"{ts_rx} rx 0x1000 {formatted} ℹ️ NRC 0x78 等待响应 ({ecu_name} 正在重启...)", "#FF9800")
                    self.append_log_color(f"💡 提示：{ecu_name} 正在执行 Reset，可能需要等待 10-30 秒后重新连接", "#2196F3")
                else:
                    self.append_log_color(f"{ts_rx} rx 0x1000 {formatted} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
            else:
                self.append_log_color(f"{ts_rx} rx 0x1000 {formatted}", "#81C784")
        except Exception as e:
            self.append_log_color(f"❌ Reset 失败：{str(e)}", "#FF5252")

    def _icb_clear_dtc(self):
        """通过DoIP清除ICB的DTC"""
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ ICB未连接，请先连接", "#FF5252")
            return
        try:
            # 快速检测连接是否有效
            if not client.sock or client.sock.fileno() == -1:
                self.append_log_color("🔄 连接已断开，正在重连...", "#2196F3")
                self._diag_pending_action = 'dtc_clear'
                self._connect_doip_async()
                return

            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x1000 14 FF FF FF", "#64B5F6")
            resp = client.send_diagnostic(bytes([0x14, 0xFF, 0xFF, 0xFF]))
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x54:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x1000 {formatted}  ✅ DTC清除成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x1000 {formatted}  ❌ NRC 0x{nrc:02X}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC清除超时（无响应）", "#FF5252")
        except Exception as e:
            self._diag_on_socket_error(e)
            self.append_log_color(f"❌ DTC清除异常: {e}", "#FF5252")

    def on_diag_cmd_save(self):
        """保存诊断指令"""
        cmd_text = self.diag_cmd_edit.toPlainText().strip()
        if not cmd_text:
            self.append_log_color("⚠️ 指令为空，无法保存", "#FFC107")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存诊断指令", "", "文本文件 (*.txt);;所有文件 (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(cmd_text)
                self.append_log_color(f"💾 指令已保存到: {file_path}", "#4CAF50")
            except Exception as e:
                self.append_log_color(f"❌ 保存失败: {e}", "#FF5252")

    def on_diag_cmd_import(self):
        """导入诊断指令"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入诊断指令", "", "文本文件 (*.txt);;所有文件 (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.diag_cmd_edit.setPlainText(content)
                self.append_log_color(f"📂 已导入: {file_path}", "#4CAF50")
            except Exception as e:
                self.append_log_color(f"❌ 导入失败: {e}", "#FF5252")

    def on_diag_cmd_clear(self):
        """清除诊断指令输入框"""
        self.diag_cmd_edit.clear()
        self.append_log_color("🗑️ 已清除指令输入框", "#FFC107")

    def on_diag_cmd_send(self):
        """发送诊断指令 (ICB使用DoIP, 其他ECU使用批处理)"""
        cmd_text = self.diag_cmd_edit.toPlainText().strip()
        if not cmd_text:
            self.append_log_color("⚠️ 指令为空，无法发送", "#FFC107")
            return

        # ICB → 使用DoIP发送, 未连接则自动连接
        # 检查是否选择了 ECU
        if not hasattr(self, 'selected_ecu_key') or self.selected_ecu_key == "all":
            self.append_log_color("❌ 请先选择要诊断的控制器！", "#FF5252")
            return

        if self.selected_ecu_key == "icb":
            if not self.diag_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 ICB未连接，正在自动连接...", "#2196F3")
                self._connect_doip_async("icb")
                return
            self._icb_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "ipd":
            if not self.ipd_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 IPD未连接，正在自动连接...", "#2196F3")
                self._connect_doip_async("ipd")
                return
            self._ipd_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "adcu":
            if not self.adcu_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 ADCU 未连接，正在自动连接...", "#2196F3")
                self._connect_adcu_doip()
                return
            self._adcu_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "dpp":
            if not self.dpp_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 DPP 未连接，正在自动连接...", "#2196F3")
                self._connect_dpp_doip()
                return
            self._dpp_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "epmcu":
            if not self.epmcu_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 EPMCU 未连接，正在自动连接...", "#2196F3")
                self._connect_epmcu_doip()
                return
            self._epmcu_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "eps":
            if not self.eps_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 EPS 未连接，正在自动连接...", "#2196F3")
                self._connect_eps_doip()
                return
            self._eps_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "IAM":
            if not self.iam_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 IAM 未连接，正在自动连接...", "#2196F3")
                self._connect_iam_doip()
                return
            self._iam_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "ibs":
            if not self.ibs_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 IBS 未连接，正在自动连接...", "#2196F3")
                self._connect_ibs_doip()
                return
            self._ibs_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "lhzcu":
            if not self.diag_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 ICB 未连接，无法转发 LHZCU 诊断", "#2196F3")
                self._connect_doip_async()
                return
            self._lhzcu_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "rhzcu":
            if not self.diag_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 ICB 未连接，无法转发 RHZCU 诊断", "#2196F3")
                self._connect_doip_async()
                return
            self._rhzcu_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "rzcu":
            if not self.diag_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 ICB 未连接，无法转发 RZCU 诊断", "#2196F3")
                self._connect_doip_async()
                return
            self._rzcu_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "rwsl":
            if not self.rwsl_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 RWSL 未连接，正在自动连接...", "#2196F3")
                self._connect_rwsl_doip()
                return
            self._rwsl_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "rlpoda":
            if not self.rlpoda_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 RLPODA 未连接，正在自动连接...", "#2196F3")
                self._connect_rlpoda_doip()
                return
            self._rlpoda_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "rrpoda":
            if not self.rrpoda_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 RRPODA 未连接，正在自动连接...", "#2196F3")
                self._connect_rrpoda_doip()
                return
            self._rrpoda_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "scm":
            if not self.scm_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 SCM 未连接，正在自动连接...", "#2196F3")
                self._connect_scm_doip()
                return
            self._scm_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "sdm":
            if not self.sdm_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 SDM 未连接，正在自动连接...", "#2196F3")
                self._connect_sdm_doip()
                return
            self._sdm_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "ess":
            if not self.ess_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 ESS 未连接，正在自动连接...", "#2196F3")
                self._connect_ess_doip()
                return
            self._ess_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "racfp":
            if not self.racfp_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 RACFP 未连接，正在自动连接...", "#2196F3")
                self._connect_racfp_doip()
                return
            self._racfp_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "fdr":
            if not self.fdr_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 FDR 未连接，正在自动连接...", "#2196F3")
                self._connect_fdr_doip()
                return
            self._fdr_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "flpoda":
            if not self.flpoda_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 FLPODA 未连接，正在自动连接...", "#2196F3")
                self._connect_flpoda_doip()
                return
            self._flpoda_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "frpoda":
            if not self.frpoda_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 FRPODA 未连接，正在自动连接...", "#2196F3")
                self._connect_frpoda_doip()
                return
            self._frpoda_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "fwm":
            if not self.fwm_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 FWM 未连接，正在自动连接...", "#2196F3")
                self._connect_fwm_doip()
                return
            self._fwm_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "nfcsm":
            if not self.nfcsm_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 NFCSM 未连接，正在自动连接...", "#2196F3")
                self._connect_nfcsm_doip()
                return
            self._nfcsm_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "pma":
            if not self.pma_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 PMA 未连接，正在自动连接...", "#2196F3")
                self._connect_pma_doip()
                return
            self._pma_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "cf":
            if not self.cf_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 CF 未连接，正在自动连接...", "#2196F3")
                self._connect_cf_doip()
                return
            self._cf_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "peu":
            if not self.peu_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 PEU 未连接，正在自动连接...", "#2196F3")
                self._connect_peu_doip()
                return
            self._peu_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "rhpmwc":
            if not self.rhpmwc_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 RHPMWC 未连接，正在自动连接...", "#2196F3")
                self._connect_rhpmwc_doip()
                return
            self._rhpmwc_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "rlss":
            if not self.rlss_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 RLSS 未连接，正在自动连接...", "#2196F3")
                self._connect_rlss_doip()
                return
            self._rlss_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "ccu":
            if not self.ccu_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 CCU 未连接，正在自动连接...", "#2196F3")
                self._connect_ccu_doip()
                return
            self._ccu_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "hodm":
            if not self.hodm_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 HODM 未连接，正在自动连接...", "#2196F3")
                self._connect_hodm_doip()
                return
            self._hodm_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "lvbm":
            if not self.lvbm_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 LVBM 未连接，正在自动连接...", "#2196F3")
                self._connect_lvbm_doip()
                return
            self._lvbm_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "nfcam":
            if not self.nfcam_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 NFCAM 未连接，正在自动连接...", "#2196F3")
                self._connect_nfcam_doip()
                return
            self._nfcam_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "tc":
            if not self.tc_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 TC 未连接，正在自动连接...", "#2196F3")
                self._connect_tc_doip()
                return
            self._tc_send_uds_cmd(cmd_text)
            return

        elif self.selected_ecu_key == "tdm":
            if not self.tdm_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 TDM 未连接，正在自动连接...", "#2196F3")
                self._connect_tdm_doip()
                return
            self._tdm_send_uds_cmd(cmd_text)
            return

        # BROADCAST (ECU 全扫) → 通过 ICB DoIP 网关转发
        elif self.selected_ecu_key == "broadcast":
            if not self.broadcast_doip_connected:
                self._diag_pending_cmd = cmd_text
                self._diag_pending_action = 'cmd'
                self.append_log_color("🔄 正在连接 ICB 网关转发 BROADCAST...", "#2196F3")
                self._connect_broadcast_doip()
                return
            self._broadcast_send_uds_cmd(cmd_text)
            return

        # 其他 ECU → 不支持 UDS 诊断指令
        ecu_name = self._get_selected_ecu_name()
        self.append_log_color(f"❌ {ecu_name} 暂不支持 UDS 诊断指令", "#FF5252")
        self.append_log_color("💡 提示：请在左侧选择 ICB、IPD、ADCU、DPP、EPMCU、IAM、LHZCU、RHZCU 或 RZCU 控制器后发送 UDS 指令", "#FF9800")


    def _icb_send_uds_cmd(self, cmd_text: str):
        """
        通过DoIP发送UDS诊断指令到ICB
        支持多行指令，支持十六进制和注释
        """
        import re
        import time
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ ICB未连接，请先连接", "#FF5252")
            return

        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            # 去除注释
            if '#' in line:
                line = line.split('#')[0].strip()
            if '//' in line:
                line = line.split('//')[0].strip()
            if not line:
                continue

            # 检查是否是 sleep 命令 (不区分大小写，不区分空格)
            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"⏸️ Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                # 使用非阻塞方式 sleep
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)  # 每次只 sleep 0.1 秒
                    QApplication.processEvents()  # 保持 UI 响应
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue

            # 去除空格
            hex_str = line.replace(' ', '').replace('\t', '')

            try:
                uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效的十六进制: '{line}'", "#FF5252")
                continue

            # 格式化tx日志: 带时间戳
            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x1000 {formatted_tx}", "#64B5F6")
            QApplication.processEvents()

            try:
                # ICB 使用逻辑地址 0x1000
                resp = client.send_diagnostic(uds_data, target_addr=ICB_LOGICAL_ADDR)
                if resp is None:
                    self.append_log_color(f"{self._diag_timestamp()} ⏰ 无响应 (超时)", "#FF5252")
                    continue

                # 先打印rx日志 (让用户看到响应内容)
                resp_hex = resp.hex().upper()
                formatted_rx = ' '.join(resp_hex[i:i+2] for i in range(0, len(resp_hex), 2))
                ts_rx = self._diag_timestamp()

                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    self.append_log_color(f"{ts_rx} rx 0x1000 {formatted_rx}  ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF8A80")
                else:
                    self.append_log_color(f"{ts_rx} rx 0x1000 {formatted_rx}", "#81C784")
                    QApplication.processEvents()

                    # 附加解析
                    sid = resp[0] - 0x40
                    if sid == 0x22 and len(resp) > 2:
                        if uds_data[:2] == bytes.fromhex('22F1') and uds_data[2] == 0x90:
                            data = resp[3:]
                            vin = data.decode('ascii', errors='replace').strip('\x00').strip()
                            self.append_log_color(f"  └─ ICB VIN: {vin}", "#FFD54F")
                        else:
                            data = resp[3:]
                            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data)
#                             self.append_log_color(f"  └─ {self.selected_ecu_key.upper() if hasattr(self, 'selected_ecu_key') else 'ECU'} 数据: {ascii_str}", "#90CAF9")
                    elif sid == 0x19:
                        self.append_log_color(f"  └─ DTC信息", "#A5D6A7")

                # 自动安全访问: 收到 67 01 + seed → 算key发 27 02
                # (注意: 日志已在上方打过, 这里只做逻辑动作)
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        key = sa_calc.calc_key(seed_hex, f'{ICB_SECURITY_ALGO:08X}')
                        # 发送 27 02 + key (使用 _icb_send_uds_raw，与 EPS 一致)
                        if client and client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key
                            # 调试：显示完整命令
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x1000 {cmd_27_02.hex().upper()} (len={len(cmd_27_02)})", "#64B5F6")
                            resp2 = self._icb_send_uds_raw(cmd_27_02)
                            # 收到响应后再更新 UI
                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x1000 67 02 ✅ 安全访问成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x1000 7F 27 {nrc2:02X} ❌ 安全访问失败", "#FF5252")
                            if not resp2:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败: {se}", "#FF5252")

            except Exception as e:
                self._diag_on_socket_error(e)
                self.append_log_color(f"{self._diag_timestamp()} ❌ 发送异常: {e}", "#FF5252")

    @staticmethod
    def _diag_timestamp() -> str:
        """返回格式化时间戳 HH:MM:SS.mmm"""
        now = datetime.datetime.now()
        return now.strftime('%H:%M:%S.') + f"{now.microsecond // 1000:03d}"

    def _diag_on_socket_error(self, e: Exception):
        """诊断socket异常处理: 标记连接断开"""
        err_str = str(e)
        if '10053' in err_str or '10054' in err_str or 'closed' in err_str.lower():
            self.diag_doip_connected = False
            self.append_log_color("🔄 连接已断开", "#FF9800")

    @staticmethod
    def _diag_nrc_desc(nrc: int) -> str:
        """NRC描述"""
        nrc_map = {
            0x10: "General Reject", 0x11: "Service Not Supported",
            0x12: "Sub-function Not Supported", 0x13: "Incorrect Message Length",
            0x22: "Conditions Not Correct", 0x24: "Request Sequence Error",
            0x31: "Request Out Of Range", 0x33: "Security Access Denied",
            0x35: "Invalid Key", 0x36: "Exceeded Number of Attempts (ECU 锁定)",
            0x37: "Required Time Delay Not Expired", 0x78: "Response Pending",
            # ICB特有
            0x25: "A核未响应", 0x26: "8295未响应",
            0x27: "A核+8295均未响应", 0x28: "8295错误(EOL写入失败)",
            0x30: "A核数据格式错误", 0x31: "8295数据格式错误",
            0x71: "C971写入值≠0x0",
            0x7F: "当前会话不支持该服务",
        }
        return nrc_map.get(nrc, f"未知(0x{nrc:02X})")

    def _ipd_send_uds_cmd(self, cmd_text: str):
        """
        通过 DoIP 发送 UDS 诊断指令到 IPD (通过 ICB 转发)
        支持多行指令，支持十六进制和注释
        """
        import re
        import time

        # IPD 通过 ICB 转发，复用 ICB 的 DoIP 客户端
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ ICB 未连接，无法转发 IPD 诊断", "#FF5252")
            return

        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            # 去除注释
            if '#' in line:
                line = line.split('#')[0].strip()
            if '//' in line:
                line = line.split('//')[0].strip()
            if not line:
                continue

            # 检查是否是 sleep 命令
            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"⏸️ Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue

            # 去除空格
            hex_str = line.replace(' ', '').replace('\t', '')

            try:
                uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效的十六进制：'{line}'", "#FF5252")
                continue

            # 格式化 tx 日志
            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{IPD_LOGICAL_ADDR:04X} {formatted_tx}", "#64B5F6")
            QApplication.processEvents()

            try:
                # 💡 优化：如果是 27 01 请求，提前预热 daemon（避免 seed→key 延迟）
                if uds_data[0] == 0x27 and uds_data[1] == 0x01:
                    try:
                        sa_calc.calc_key('00000000', f'{IPD_SECURITY_ALGO:08X}')  # 预热，不关心结果
                    except:
                        pass

                # IPD 使用不同的逻辑地址 (通过 ICB 转发)
                resp = client.send_diagnostic(uds_data, target_addr=IPD_LOGICAL_ADDR)
                if resp is None:
                    self.append_log_color(f"{self._diag_timestamp()} ⏰ 无响应 (超时)", "#FF5252")
                    continue

                resp_hex = resp.hex().upper()
                formatted_rx = ' '.join(resp_hex[i:i+2] for i in range(0, len(resp_hex), 2))
                ts_rx = self._diag_timestamp()

                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    self.append_log_color(f"{ts_rx} rx 0x{IPD_LOGICAL_ADDR:04X} {formatted_rx}  ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF8A80")
                else:
                    self.append_log_color(f"{ts_rx} rx 0x{IPD_LOGICAL_ADDR:04X} {formatted_rx}", "#81C784")
                    QApplication.processEvents()

                # IPD 自动安全访问：收到 67 01 + seed 后，自动计算 key 并发送 27 02
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        # ✅ IPD 算法号：00001043
                        key = sa_calc.calc_key(seed_hex, f'{IPD_SECURITY_ALGO:08X}')  # 返回 bytes
                        cmd_27_02 = bytes([0x27, 0x02]) + key
                        formatted_tx2 = ' '.join(f'{b:02X}' for b in cmd_27_02)
                        self.append_log_color(f"{self._diag_timestamp()} tx 0x{IPD_LOGICAL_ADDR:04X} {formatted_tx2}  🔑 自动发送 KEY", "#4CAF50")
                        QApplication.processEvents()
                        resp2 = client.send_diagnostic(cmd_27_02, target_addr=IPD_LOGICAL_ADDR)
                        if resp2:
                            f2 = resp2.hex().upper()
                            formatted_f2 = ' '.join(f2[i:i+2] for i in range(0, len(f2), 2))
                            if resp2[0] == 0x67:
                                self.append_log_color(f"{self._diag_timestamp()} rx 0x{IPD_LOGICAL_ADDR:04X} {formatted_f2} ✅ 安全认证成功", "#4CAF50")
                            elif resp2[0] == 0x7F:
                                nrc2 = resp2[2] if len(resp2) > 2 else 0
                                nrc_desc2 = self._diag_nrc_desc(nrc2)
                                self.append_log_color(f"{self._diag_timestamp()} rx 0x{IPD_LOGICAL_ADDR:04X} {formatted_f2} ❌ 安全认证失败 NRC 0x{nrc2:02X} {nrc_desc2}", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} rx 0x{IPD_LOGICAL_ADDR:04X} {formatted_f2} ❌ 安全认证失败", "#FF5252")
                    except Exception as e2:
                        self.append_log_color(f"❌ 安全访问计算失败：{str(e2)}", "#FF5252")
            except Exception as e:
                self.append_log_color(f"❌ 发送失败：{str(e)}", "#FF5252")

    def _ipd_reset_ecu(self):
        """通过 DoIP 发送 IPD 的 ECU Reset (11 01) - 通过 ICB 转发"""
        # IPD 通过 ICB 转发，复用 ICB 的 DoIP 客户端
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ ICB 未连接，无法转发 IPD 诊断", "#FF5252")
            return
        try:
            if not client.sock or client.sock.fileno() == -1:
                self.append_log_color("⚠️ 连接已断开，正在重连...", "#2196F3")
                self._diag_pending_action = 'reset'
                self._connect_doip_async("ipd")
                return

            cmd_11_01 = bytes([0x11, 0x01])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{IPD_LOGICAL_ADDR:04X} 11 01", "#64B5F6")
            QApplication.processEvents()

            # IPD 使用不同的逻辑地址 (通过 ICB 转发)
            resp = client.send_diagnostic(cmd_11_01, target_addr=IPD_LOGICAL_ADDR)
            if resp is None:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 无响应 (超时)", "#FF5252")
                return

            resp_hex = resp.hex().upper()
            formatted = ' '.join(resp_hex[i:i+2] for i in range(0, len(resp_hex), 2))
            ts_rx = self._diag_timestamp()

            ecu_name = self._get_selected_ecu_name()
            if resp[0] == 0x51:
                self.append_log_color(f"{ts_rx} rx 0x{IPD_LOGICAL_ADDR:04X} {formatted} ✅ {ecu_name} Reset 成功", "#4CAF50")
                self.append_log_color(f"💡 提示：{ecu_name} 即将重启，可能需要等待几秒后重新连接", "#FF9800")
            elif resp[0] == 0x7F:
                nrc = resp[2] if len(resp) > 2 else 0
                nrc_desc = self._diag_nrc_desc(nrc)
                if nrc == 0x78:
                    self.append_log_color(f"{ts_rx} rx 0x{IPD_LOGICAL_ADDR:04X} {formatted} ℹ️ NRC 0x78 等待响应 ({ecu_name} 正在重启...)", "#FF9800")
                    self.append_log_color(f"💡 提示：{ecu_name} 正在执行 Reset，可能需要等待 10-30 秒后重新连接", "#2196F3")
                else:
                    self.append_log_color(f"{ts_rx} rx 0x{IPD_LOGICAL_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
            else:
                self.append_log_color(f"{ts_rx} rx 0x{IPD_LOGICAL_ADDR:04X} {formatted}", "#81C784")
        except Exception as e:
            self.append_log_color(f"❌ Reset 失败：{str(e)}", "#FF5252")

    def _ipd_read_dtc(self):
        """通过 DoIP 读取 IPD 的 DTC 故障码 (IDS 方式) - 通过 ICB 转发"""
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ ICB 未连接，无法转发 IPD 诊断", "#FF5252")
            return

        try:
            # Step 1: 19 02 2C - 读取状态信息的有效 DTC
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{IPD_LOGICAL_ADDR:04X} 19 02 2C", "#64B5F6")
            QApplication.processEvents()

            resp = client.send_diagnostic(bytes([0x19, 0x02, 0x2C]), target_addr=IPD_LOGICAL_ADDR)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return

            formatted = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x{IPD_LOGICAL_ADDR:04X} {formatted}", "#81C784")
            QApplication.processEvents()

            # 解析 DTC 列表
            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color("  ✅ 无有效 DTC", "#4CAF50")
                return

            self.append_log_color(f"  📋 发现 {len(dtc_records)} 条 DTC", "#FF9800")

            # Step 2: 对每个 DTC 查询详细信息 (19 04) 和扩展信息 (19 06)
            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']  # 3 bytes DTC code
                dtc_label = dtc['label']

                # 19 04 - 故障快照
                ts = self._diag_timestamp()
                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                self.append_log_color(f"{ts} tx 0x{IPD_LOGICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_04)}", "#64B5F6")
                resp_04 = client.send_diagnostic(cmd_04, target_addr=IPD_LOGICAL_ADDR, timeout=1.5)
                if resp_04:
                    f = ' '.join(f'{b:02X}' for b in resp_04)
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{IPD_LOGICAL_ADDR:04X} {f}", "#81C784")
                    dtc['snapshot_raw'] = resp_04
                QApplication.processEvents()

                # 19 06 - 扩展信息
                ts = self._diag_timestamp()
                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                self.append_log_color(f"{ts} tx 0x{IPD_LOGICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_06)}", "#64B5F6")
                resp_06 = client.send_diagnostic(cmd_06, target_addr=IPD_LOGICAL_ADDR, timeout=1.5)
                if resp_06:
                    f = ' '.join(f'{b:02X}' for b in resp_06)
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{IPD_LOGICAL_ADDR:04X} {f}", "#81C784")
                    dtc['extended_raw'] = resp_06
                QApplication.processEvents()

            # Step 3: 显示结果（表格格式）
            self._display_dtc_table(dtc_records)

            # Step 4: 保存到 Excel
            self._save_dtc_excel(dtc_records)

        except Exception as e:
            self._diag_on_socket_error(e)

    def _ipd_clear_dtc(self):
        """通过 DoIP 清除 IPD 的 DTC 故障码 - 通过 ICB 转发"""
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ ICB 未连接，无法转发 IPD 诊断", "#FF5252")
            return

        try:
            # 14 FF FF FF - 清除所有 DTC
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{IPD_LOGICAL_ADDR:04X} 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()

            resp = client.send_diagnostic(bytes([0x14, 0xFF, 0xFF, 0xFF]), target_addr=IPD_LOGICAL_ADDR)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 清除 DTC 超时", "#FF5252")
                return

            formatted = ' '.join(f'{b:02X}' for b in resp)
            if resp[0] == 0x54:
                self.append_log_color(f"{self._diag_timestamp()} rx 0x{IPD_LOGICAL_ADDR:04X} {formatted} ✅ 清除成功", "#4CAF50")
            elif resp[0] == 0x7F:
                nrc = resp[2] if len(resp) > 2 else 0
                nrc_desc = self._diag_nrc_desc(nrc)
                self.append_log_color(f"{self._diag_timestamp()} rx 0x{IPD_LOGICAL_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} rx 0x{IPD_LOGICAL_ADDR:04X} {formatted}", "#81C784")

        except Exception as e:
            self._diag_on_socket_error(e)

    # ==================== ADCU 诊断功能 ====================
    def _connect_adcu_doip(self):
        """连接 ADCU DoIP"""
        try:
            self.append_log_color("🔗 正在连接 ADCU...", "#2196F3")
            client = DoIPClient(ADCU_DOIP_IP, ADCU_DOIP_PORT, routing_ta=ADCU_ROUTING_TA)
            client.connect()
            client.routing_activate()
            self.adcu_doip_client = client
            self.adcu_doip_connected = True
            self.append_log_color("✅ ADCU 连接成功", "#4CAF50")

            # 如果有待执行的诊断动作，立即执行
            if self._diag_pending_action == 'dtc_read':
                self._diag_pending_action = None
                self._adcu_read_dtc()
            elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
                cmd = self._diag_pending_cmd
                self._diag_pending_action = None
                self._diag_pending_cmd = None
                self._adcu_send_uds_cmd(cmd)
            return True
        except Exception as e:
            self.append_log_color(f"❌ ADCU 连接失败：{e}", "#FF5252")
            return False

    def _adcu_send_uds_raw(self, data: bytes, timeout: float = 2.0):
        """发送 UDS 指令到 ADCU 并返回原始响应 (bytes), 失败返回 None"""
        client = self.adcu_doip_client
        if not client or not client.routing_activated:
            return None
        try:
            # 使用物理地址 0x0785
            resp = client.send_diagnostic(data, target_addr=ADCU_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ ADCU UDS 发送失败：{e}", "#FF9800")
            return None

    def _adcu_read_dtc(self):
        """通过 DoIP 读取 ADCU 的 DTC 故障码"""
        client = self.adcu_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ ADCU 未连接", "#FF5252")
            return

        try:
            # Step 1: 19 02 2C - 读取有效 DTC 列表
            log_lines = [f"{self._diag_timestamp()} tx 0x0785 19 02 2C"]
            resp = self._adcu_send_uds_raw(bytes([0x19, 0x02, 0x2C]))
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return

            log_lines.append(f"{self._diag_timestamp()} rx 0x0785 {' '.join(f'{b:02X}' for b in resp)}")

            # 解析 DTC 列表
            dtc_records = self._parse_dtc_02_response(resp)

            # 先写入日志（包括 tx/rx）
            log_lines.append(f"  发现 {len(dtc_records)} 个 DTC")
            self.append_log_batch(log_lines)

            # 如果没有 DTC，到此为止
            if not dtc_records:
                return

            # Step 2: 对每个 DTC 查询详细快照 (19 04) 和扩展数据 (19 06)
            log_lines = []
            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']

                # 19 04 - 快照数据
                ts = self._diag_timestamp()
                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                log_lines.append(f"{ts} tx 0x0785 {' '.join(f'{b:02X}' for b in cmd_04)}")
                resp_04 = self._adcu_send_uds_raw(cmd_04, timeout=0.3)
                if resp_04:
                    f = ' '.join(f'{b:02X}' for b in resp_04)
                    log_lines.append(f"{self._diag_timestamp()} rx 0x0785 {f}")
                    dtc['snapshot_raw'] = resp_04

                # 19 06 - 扩展数据
                ts = self._diag_timestamp()
                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                log_lines.append(f"{ts} tx 0x0785 {' '.join(f'{b:02X}' for b in cmd_06)}")
                resp_06 = self._adcu_send_uds_raw(cmd_06, timeout=0.3)
                if resp_06:
                    f = ' '.join(f'{b:02X}' for b in resp_06)
                    log_lines.append(f"{self._diag_timestamp()} rx 0x0785 {f}")
                    dtc['extended_raw'] = resp_06

            # 批量写入日志
            self.append_log_batch(log_lines)

            # Step 3: 显示结果（表格格式）
            self._display_dtc_table(dtc_records)

        except Exception as e:
            self.append_log_color(f"❌ DTC 读取异常：{e}", "#FF5252")

    def _adcu_clear_dtc(self):
        """通过 DoIP 清除 ADCU 的 DTC 故障码"""
        client = self.adcu_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ ADCU 未连接", "#FF5252")
            return

        try:
            # 14 FF FF FF - 清除所有 DTC
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x0785 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()

            resp = self._adcu_send_uds_raw(bytes([0x14, 0xFF, 0xFF, 0xFF]))
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 清除 DTC 超时", "#FF5252")
                return

            formatted = ' '.join(f'{b:02X}' for b in resp)
            if resp[0] == 0x54:
                self.append_log_color(f"{self._diag_timestamp()} rx 0x0785 {formatted} ✅ 清除成功", "#4CAF50")
            elif resp[0] == 0x7F:
                nrc = resp[2] if len(resp) > 2 else 0
                nrc_desc = self._diag_nrc_desc(nrc)
                self.append_log_color(f"{self._diag_timestamp()} rx 0x0785 {formatted} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} rx 0x0785 {formatted}", "#81C784")

        except Exception as e:
            self.append_log_color(f"❌ 清除 DTC 异常：{e}", "#FF5252")

    def _adcu_reset_ecu(self):
        """通过 DoIP 复位 ADCU"""
        client = self.adcu_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ ADCU 未连接", "#FF5252")
            return

        try:
            # 11 01 - 硬复位
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x0785 11 01", "#64B5F6")
            QApplication.processEvents()

            resp = self._adcu_send_uds_raw(bytes([0x11, 0x01]))
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 复位超时", "#FF5252")
                return

            formatted = ' '.join(f'{b:02X}' for b in resp)
            if resp[0] == 0x51:
                self.append_log_color(f"{self._diag_timestamp()} rx 0x0785 {formatted} ✅ 复位成功", "#4CAF50")
            elif resp[0] == 0x7F:
                nrc = resp[2] if len(resp) > 2 else 0
                nrc_desc = self._diag_nrc_desc(nrc)
                self.append_log_color(f"{self._diag_timestamp()} rx 0x0785 {formatted} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} rx 0x0785 {formatted}", "#81C784")

        except Exception as e:
            self.append_log_color(f"❌ 复位异常：{e}", "#FF5252")

    # ==================== DPP 诊断功能 ====================
    def _connect_dpp_doip(self):
        """连接 DPP DoIP"""
        try:
            self.append_log_color("🔗 正在连接 DPP...", "#2196F3")
            client = DoIPClient(DPP_DOIP_IP, DPP_DOIP_PORT, routing_ta=DPP_ROUTING_TA)
            client.connect()
            client.routing_activate()
            self.dpp_doip_client = client
            self.dpp_doip_connected = True
            self.append_log_color("✅ DPP 连接成功", "#4CAF50")

            # 如果有待执行的诊断动作，立即执行
            if self._diag_pending_action == 'dtc_read':
                self._diag_pending_action = None
                self._dpp_read_dtc()
            elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
                cmd = self._diag_pending_cmd
                self._diag_pending_action = None
                self._diag_pending_cmd = None
                self._dpp_send_uds_cmd(cmd)
            return True
        except Exception as e:
            self.append_log_color(f"❌ DPP 连接失败：{e}", "#FF5252")
            return False

    def _dpp_send_uds_raw(self, data: bytes, timeout: float = 2.0):
        """发送 UDS 指令到 DPP 并返回原始响应 (bytes), 失败返回 None"""
        client = self.dpp_doip_client
        if not client or not client.routing_activated:
            return None
        try:
            # 使用物理地址 0x06D5
            resp = client.send_diagnostic(data, target_addr=DPP_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ DPP UDS 发送失败：{e}", "#FF9800")
            return None

    def _dpp_read_dtc(self):
        """通过 DoIP 读取 DPP 的 DTC 故障码"""
        client = self.dpp_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ DPP 未连接", "#FF5252")
            return

        try:
            # Step 1: 19 02 2C - 读取有效 DTC 列表
            log_lines = [f"{self._diag_timestamp()} tx 0x06D5 19 02 2C"]
            resp = self._dpp_send_uds_raw(bytes([0x19, 0x02, 0x2C]))
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return

            log_lines.append(f"{self._diag_timestamp()} rx 0x06D5 {' '.join(f'{b:02X}' for b in resp)}")

            # 解析 DTC 列表
            dtc_records = self._parse_dtc_02_response(resp)

            # 先写入日志（包括 tx/rx）
            log_lines.append(f"  发现 {len(dtc_records)} 个 DTC")
            self.append_log_batch(log_lines)

            # 调用显示函数（即使没有 DTC 也会显示表头）
            self._display_dtc_table(dtc_records)

            # 如果没有 DTC，到此为止
            if not dtc_records:
                return

            # Step 2: 对每个 DTC 查询详细快照 (19 04) 和扩展数据 (19 06)
            log_lines = []
            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']

                # 19 04 - 快照数据
                ts = self._diag_timestamp()
                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                log_lines.append(f"{ts} tx 0x06D5 {' '.join(f'{b:02X}' for b in cmd_04)}")
                resp_04 = self._dpp_send_uds_raw(cmd_04, timeout=0.3)
                if resp_04:
                    f = ' '.join(f'{b:02X}' for b in resp_04)
                    log_lines.append(f"{self._diag_timestamp()} rx 0x06D5 {f}")
                    dtc['snapshot_raw'] = resp_04

                # 19 06 - 扩展数据
                ts = self._diag_timestamp()
                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                log_lines.append(f"{ts} tx 0x06D5 {' '.join(f'{b:02X}' for b in cmd_06)}")
                resp_06 = self._dpp_send_uds_raw(cmd_06, timeout=0.3)
                if resp_06:
                    f = ' '.join(f'{b:02X}' for b in resp_06)
                    log_lines.append(f"{self._diag_timestamp()} rx 0x06D5 {f}")
                    dtc['extended_raw'] = resp_06

            # 批量写入日志
            self.append_log_batch(log_lines)

            # Step 3: 显示结果（表格格式）
            self._display_dtc_table(dtc_records)

        except Exception as e:
            self.append_log_color(f"❌ DTC 读取异常：{e}", "#FF5252")

    def _dpp_clear_dtc(self):
        """通过 DoIP 清除 DPP 的 DTC 故障码"""
        client = self.dpp_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ DPP 未连接", "#FF5252")
            return

        try:
            # 14 FF FF FF - 清除所有 DTC
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x06D5 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()

            resp = self._dpp_send_uds_raw(bytes([0x14, 0xFF, 0xFF, 0xFF]))
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 清除 DTC 超时", "#FF5252")
                return

            formatted = ' '.join(f'{b:02X}' for b in resp)
            if resp[0] == 0x54:
                self.append_log_color(f"{self._diag_timestamp()} rx 0x06D5 {formatted} ✅ 清除成功", "#4CAF50")
            elif resp[0] == 0x7F:
                nrc = resp[2] if len(resp) > 2 else 0
                nrc_desc = self._diag_nrc_desc(nrc)
                self.append_log_color(f"{self._diag_timestamp()} rx 0x06D5 {formatted} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} rx 0x06D5 {formatted}", "#81C784")

        except Exception as e:
            self.append_log_color(f"❌ 清除 DTC 异常：{e}", "#FF5252")

    def _dpp_reset_ecu(self):
        """通过 DoIP 复位 DPP"""
        client = self.dpp_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ DPP 未连接", "#FF5252")
            return

        try:
            # 11 01 - 硬复位
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x06D5 11 01", "#64B5F6")
            QApplication.processEvents()

            resp = self._dpp_send_uds_raw(bytes([0x11, 0x01]))
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 复位超时", "#FF5252")
                return

            formatted = ' '.join(f'{b:02X}' for b in resp)
            if resp[0] == 0x51:
                self.append_log_color(f"{self._diag_timestamp()} rx 0x06D5 {formatted} ✅ 复位成功", "#4CAF50")
            elif resp[0] == 0x7F:
                nrc = resp[2] if len(resp) > 2 else 0
                nrc_desc = self._diag_nrc_desc(nrc)
                self.append_log_color(f"{self._diag_timestamp()} rx 0x06D5 {formatted} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} rx 0x06D5 {formatted}", "#81C784")

        except Exception as e:
            self.append_log_color(f"❌ 复位异常：{e}", "#FF5252")

    # ==================== ADCU 自定义 UDS 指令 ====================
    def _adcu_send_uds_cmd(self, cmd_text: str):
        """通过 DoIP 发送 UDS 诊断指令到 ADCU"""
        import re
        import time

        client = self.adcu_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ ADCU 未连接", "#FF5252")
            return

        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            # 去除注释
            if '#' in line:
                line = line.split('#')[0].strip()
            if '//' in line:
                line = line.split('//')[0].strip()
            if not line:
                continue

            # 检查是否是 sleep 命令
            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"⏳ Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue

            # 去除空格
            hex_str = line.replace(' ', '').replace('\t', '')

            try:
                uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue

            # 格式化 tx 日志
            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x0785 {formatted_tx}", "#64B5F6")
            QApplication.processEvents()

            # 发送并接收响应
            resp = self._adcu_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x0785 {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x0785 {formatted_rx}", "#81C784")

                # ICB 自动安全访问：需要在默认会话下进行
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        key = sa_calc.calc_key(seed_hex, f'{ICB_SECURITY_ALGO:08X}')
                        # 发送 27 02 + key
                        client = self.adcu_doip_client
                        if client and client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key
                            formatted_tx2 = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x0785 {formatted_tx2}", "#64B5F6")
                            resp2 = self._adcu_send_uds_raw(cmd_27_02)
                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x0785 {f2} ✅ 安全访问成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    nrc_desc2 = self._diag_nrc_desc(nrc2)
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x0785 {f2} ❌ 安全访问失败 NRC 0x{nrc2:02X} {nrc_desc2}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x0785 {f2} ❌ 安全访问失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    # ==================== DPP 自定义 UDS 指令 ====================
    def _dpp_send_uds_cmd(self, cmd_text: str):
        """通过 DoIP 发送 UDS 诊断指令到 DPP"""
        import re
        import time

        client = self.dpp_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ DPP 未连接", "#FF5252")
            return

        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            # 去除注释
            if '#' in line:
                line = line.split('#')[0].strip()
            if '//' in line:
                line = line.split('//')[0].strip()
            if not line:
                continue

            # 检查是否是 sleep 命令
            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"⏳ Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue

            # 去除空格
            hex_str = line.replace(' ', '').replace('\t', '')

            try:
                uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue

            # 格式化 tx 日志
            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x06D5 {formatted_tx}", "#64B5F6")
            QApplication.processEvents()

            # 发送并接收响应
            resp = self._dpp_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x06D5 {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x06D5 {formatted_rx}", "#81C784")

                # ICB 自动安全访问：需要在默认会话下进行
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        # DPP 算法号：00001098
                        key = sa_calc.calc_key(seed_hex, '00001098')
                        # 发送 27 02 + key
                        client = self.dpp_doip_client
                        if client and client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key
                            formatted_tx2 = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x06D5 {formatted_tx2}", "#64B5F6")
                            resp2 = self._dpp_send_uds_raw(cmd_27_02)
                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x06D5 {f2} ✅ 安全访问成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    nrc_desc2 = self._diag_nrc_desc(nrc2)
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x06D5 {f2} ❌ 安全访问失败 NRC 0x{nrc2:02X} {nrc_desc2}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x06D5 {f2} ❌ 安全访问失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")



    # ==================== EPMCU 诊断功能 ====================
    def _connect_epmcu_doip(self):
        """连接 EPMCU DoIP"""
        try:
            self.append_log_color("🔗 正在连接 EPMCU...", "#2196F3")
            client = DoIPClient(EPMCU_DOIP_IP, EPMCU_DOIP_PORT, routing_ta=EPMCU_ROUTING_TA)
            client.connect()
            client.routing_activate()
            self.epmcu_doip_client = client
            self.epmcu_doip_connected = True
            self.append_log_color("✅ EPMCU 连接成功", "#4CAF50")

            # 如果有待执行的诊断动作，立即执行
            if self._diag_pending_action == 'dtc_read':
                self._diag_pending_action = None
                self._epmcu_read_dtc()
            elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
                cmd = self._diag_pending_cmd
                self._diag_pending_action = None
                self._diag_pending_cmd = None
                self._epmcu_send_uds_cmd(cmd)
            return True
        except Exception as e:
            self.append_log_color(f"❌ EPMCU 连接失败：{e}", "#FF5252")
            return False

    def _epmcu_send_uds_raw(self, data: bytes, timeout: float = 2.0):
        """发送 UDS 指令到 EPMCU 并返回原始响应 (bytes), 失败返回 None"""
        client = self.epmcu_doip_client
        if not client or not client.routing_activated:
            return None
        try:
            # 使用物理地址 0x0775
            resp = client.send_diagnostic(data, target_addr=EPMCU_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ EPMCU UDS 发送失败：{e}", "#FF9800")
            return None

    def _epmcu_read_dtc(self):
        """通过 DoIP 读取 EPMCU 的 DTC 故障码"""
        client = self.epmcu_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ EPMCU 未连接", "#FF5252")
            return

        try:
            # Step 1: 19 02 2C - 读取有效 DTC 列表
            log_lines = [f"{self._diag_timestamp()} tx 0x0775 19 02 2C"]
            resp = self._epmcu_send_uds_raw(bytes([0x19, 0x02, 0x2C]))
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return

            log_lines.append(f"{self._diag_timestamp()} rx 0x0775 {' '.join(f'{b:02X}' for b in resp)}")

            # 解析 DTC 列表
            dtc_records = self._parse_dtc_02_response(resp)

            # 先写入日志（包括 tx/rx）
            log_lines.append(f"  发现 {len(dtc_records)} 个 DTC")
            self.append_log_batch(log_lines)

            # 调用显示函数（即使没有 DTC 也会显示表头）
            self._display_dtc_table(dtc_records)

            # 如果没有 DTC，到此为止
            if not dtc_records:
                return

            # Step 2: 对每个 DTC 查询详细快照 (19 04) 和扩展数据 (19 06)
            log_lines = []
            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']

                # 19 04 - 快照数据
                ts = self._diag_timestamp()
                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                log_lines.append(f"{ts} tx 0x0775 {' '.join(f'{b:02X}' for b in cmd_04)}")
                resp_04 = self._epmcu_send_uds_raw(cmd_04, timeout=0.3)
                if resp_04:
                    f = ' '.join(f'{b:02X}' for b in resp_04)
                    log_lines.append(f"{self._diag_timestamp()} rx 0x0775 {f}")
                    dtc['snapshot_raw'] = resp_04

                # 19 06 - 扩展数据
                ts = self._diag_timestamp()
                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                log_lines.append(f"{ts} tx 0x0775 {' '.join(f'{b:02X}' for b in cmd_06)}")
                resp_06 = self._epmcu_send_uds_raw(cmd_06, timeout=0.3)
                if resp_06:
                    f = ' '.join(f'{b:02X}' for b in resp_06)
                    log_lines.append(f"{self._diag_timestamp()} rx 0x0775 {f}")
                    dtc['extended_raw'] = resp_06

            # 批量写入日志
            self.append_log_batch(log_lines)

            # Step 3: 显示结果（表格格式）
            self._display_dtc_table(dtc_records)

        except Exception as e:
            self.append_log_color(f"❌ DTC 读取异常：{e}", "#FF5252")

    def _epmcu_clear_dtc(self):
        """通过 DoIP 清除 EPMCU 的 DTC 故障码"""
        client = self.epmcu_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ EPMCU 未连接", "#FF5252")
            return

        try:
            # 14 FF FF FF - 清除所有 DTC
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x0775 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()

            resp = self._epmcu_send_uds_raw(bytes([0x14, 0xFF, 0xFF, 0xFF]))
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 清除 DTC 超时", "#FF5252")
                return

            formatted = ' '.join(f'{b:02X}' for b in resp)
            if resp[0] == 0x54:
                self.append_log_color(f"{self._diag_timestamp()} rx 0x0775 {formatted} ✅ 清除成功", "#4CAF50")
            elif resp[0] == 0x7F:
                nrc = resp[2] if len(resp) > 2 else 0
                nrc_desc = self._diag_nrc_desc(nrc)
                self.append_log_color(f"{self._diag_timestamp()} rx 0x0775 {formatted} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} rx 0x0775 {formatted}", "#81C784")

        except Exception as e:
            self.append_log_color(f"❌ 清除 DTC 异常：{e}", "#FF5252")

    def _epmcu_reset_ecu(self):
        """通过 DoIP 复位 EPMCU"""
        client = self.epmcu_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ EPMCU 未连接", "#FF5252")
            return

        try:
            # 11 01 - 硬复位
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x0775 11 01", "#64B5F6")
            QApplication.processEvents()

            resp = self._epmcu_send_uds_raw(bytes([0x11, 0x01]))
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 复位超时", "#FF5252")
                return

            formatted = ' '.join(f'{b:02X}' for b in resp)
            if resp[0] == 0x51:
                self.append_log_color(f"{self._diag_timestamp()} rx 0x0775 {formatted} ✅ 复位成功", "#4CAF50")
            elif resp[0] == 0x7F:
                nrc = resp[2] if len(resp) > 2 else 0
                nrc_desc = self._diag_nrc_desc(nrc)
                self.append_log_color(f"{self._diag_timestamp()} rx 0x0775 {formatted} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} rx 0x0775 {formatted}", "#81C784")

        except Exception as e:
            self.append_log_color(f"❌ 复位异常：{e}", "#FF5252")

    def _epmcu_send_uds_cmd(self, cmd_text: str):
        """通过 DoIP 发送 UDS 诊断指令到 EPMCU"""
        import re
        import time

        client = self.epmcu_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ EPMCU 未连接", "#FF5252")
            return

        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            # 去除注释
            if '#' in line:
                line = line.split('#')[0].strip()
            if '//' in line:
                line = line.split('//')[0].strip()
            if not line:
                continue

            # 检查是否是 sleep 命令
            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"⏳ Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue

            # 去除空格
            hex_str = line.replace(' ', '').replace('\t', '')

            try:
                uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue

            # 格式化 tx 日志
            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x0775 {formatted_tx}", "#64B5F6")
            QApplication.processEvents()

            # 发送并接收响应
            resp = self._epmcu_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x0775 {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x0775 {formatted_rx}", "#81C784")

                # ICB 自动安全访问：需要在默认会话下进行
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        # EPMCU 算法号：00001044
                        key = sa_calc.calc_key(seed_hex, '00001044')
                        # 发送 27 02 + key
                        client = self.epmcu_doip_client
                        if client and client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key
                            formatted_tx2 = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x0775 {formatted_tx2}", "#64B5F6")
                            resp2 = self._epmcu_send_uds_raw(cmd_27_02)
                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x0775 {f2} ✅ 安全访问成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    nrc_desc2 = self._diag_nrc_desc(nrc2)
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x0775 {f2} ❌ 安全访问失败 NRC 0x{nrc2:02X} {nrc_desc2}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x0775 {f2} ❌ 安全访问失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")



    # ==================== EPS 诊断功能 ====================
    def _connect_eps_doip(self):
        """连接 EPS DoIP"""
        try:
            self.append_log_color("🔗 正在连接 EPS...", "#2196F3")
            client = DoIPClient(EPS_DOIP_IP, EPS_DOIP_PORT, routing_ta=EPS_ROUTING_TA)
            client.connect()
            client.routing_activate()
            self.eps_doip_client = client
            self.eps_doip_connected = True
            self.append_log_color("✅ EPS 连接成功", "#4CAF50")

            # 如果有待执行的诊断动作，立即执行
            if self._diag_pending_action == 'dtc_read':
                self._diag_pending_action = None
                self._eps_read_dtc()
            elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
                cmd = self._diag_pending_cmd
                self._diag_pending_action = None
                self._diag_pending_cmd = None
                self._eps_send_uds_cmd(cmd)
            return True
        except Exception as e:
            self.append_log_color(f"❌ EPS 连接失败：{e}", "#FF5252")
            return False

    def _connect_ibs_doip(self):
        """连接 IBS DoIP (通过 ICB 转发)"""
        try:
            self.append_log_color("🔗 正在连接 IBS...", "#2196F3")
            client = DoIPClient(IBS_DOIP_IP, IBS_DOIP_PORT, routing_ta=IBS_ROUTING_TA)
            client.connect()
            client.routing_activate()
            self.ibs_doip_client = client
            self.ibs_doip_connected = True
            self.append_log_color("✅ IBS 连接成功", "#4CAF50")

            # 如果有待执行的诊断动作，立即执行
            if self._diag_pending_action == 'dtc_read':
                self._diag_pending_action = None
                self._ibs_read_dtc()
            elif self._diag_pending_action == 'dtc_clear':
                self._diag_pending_action = None
                self._ibs_clear_dtc()
            elif self._diag_pending_action == 'reset':
                self._diag_pending_action = None
                self._ibs_reset_ecu()
            elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
                cmd = self._diag_pending_cmd
                self._diag_pending_action = None
                self._diag_pending_cmd = None
                self._ibs_send_uds_cmd(cmd)
            return True
        except Exception as e:
            self.append_log_color(f"❌ IBS 连接失败：{e}", "#FF5252")
            return False

    def _ibs_send_uds_raw(self, data: bytes, timeout: float = 2.0):
        """发送 UDS 指令到 IBS 并返回原始响应 (bytes), 失败返回 None

        Args:
            data: UDS 请求数据
            timeout: 超时时间（秒）
        """
        client = self.ibs_doip_client
        if not client or not client.routing_activated:
            return None
        try:
            # 使用物理地址 0x0726
            resp = client.send_diagnostic(data, target_addr=IBS_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ IBS UDS 发送失败：{e}", "#FF9800")
            return None

    def _ibs_send_uds_cmd(self, cmd_text: str):
        """通过 DoIP 发送 UDS 诊断指令到 IBS"""
        import re
        import time

        client = self.ibs_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ IBS 未连接", "#FF5252")
            return

        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            # 去除注释
            if '#' in line:
                line = line.split('#')[0].strip()
            if '//' in line:
                line = line.split('//')[0].strip()
            if not line:
                continue

            # 检查是否是 sleep 指令
            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"💤 Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue

            # 去除空格
            hex_str = line.replace(' ', '').replace('\t', '')

            try:
                uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效的十六进制：'{line}'", "#FF5252")
                continue

            # 格式化 tx 日志
            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x0726 {formatted_tx}", "#64B5F6")
            QApplication.processEvents()

            # 发送并接收响应
            resp = self._ibs_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    if nrc == 0x78:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x0726 {formatted_rx} ⏳ {nrc_desc}", "#FF9800")
                    else:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x0726 {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x0726 {formatted_rx}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    def _ibs_read_dtc(self):
        """通过 DoIP 读取 IBS 的 DTC 故障码 (IDS 方式) - 通过 ICB 转发"""
        client = self.ibs_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ IBS 未连接", "#FF5252")
            return

        try:
            # Step 1: 19 02 2C - 读取有效 DTC
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{IBS_PHYSICAL_ADDR:04X} 19 02 2C", "#64B5F6")
            QApplication.processEvents()

            resp = self._ibs_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=2.0)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return

            formatted = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x{IBS_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            QApplication.processEvents()

            # 解析 DTC 列表
            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color("  ✅ 无有效 DTC", "#4CAF50")
                return

            self.append_log_color(f"  📋 发现 {len(dtc_records)} 条 DTC", "#FF9800")

            # Step 2: 对每个 DTC 查询快照 (19 04) 和扩展数据 (19 06)
            log_lines = []
            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']

                # 19 04 - 故障快照
                ts = self._diag_timestamp()
                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                log_lines.append(f"{ts} tx 0x{IBS_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_04)}")
                resp_04 = self._ibs_send_uds_raw(cmd_04, timeout=1.5)
                if resp_04:
                    f = ' '.join(f'{b:02X}' for b in resp_04)
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{IBS_RESPONSE_ADDR:04X} {f}")
                    dtc['snapshot_raw'] = resp_04

                # 19 06 - 扩展信息
                ts = self._diag_timestamp()
                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                log_lines.append(f"{ts} tx 0x{IBS_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_06)}")
                resp_06 = self._ibs_send_uds_raw(cmd_06, timeout=1.5)
                if resp_06:
                    f = ' '.join(f'{b:02X}' for b in resp_06)
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{IBS_RESPONSE_ADDR:04X} {f}")
                    dtc['extended_raw'] = resp_06

            # 批量写入日志
            self.append_log_batch(log_lines)

            # Step 3: 显示结果（表格格式）
            self._display_dtc_table(dtc_records)

            # Step 4: 保存到 Excel
            self._save_dtc_excel(dtc_records)

        except Exception as e:
            self._diag_on_socket_error(e)
            self.append_log_color(f"❌ DTC 读取异常: {e}", "#FF5252")
            import traceback
            self.append_log_color(traceback.format_exc(), "#FF5252")

    def _ibs_clear_dtc(self):
        """通过 DoIP 清除 IBS 的 DTC 故障码"""
        self._ibs_send_uds_cmd("14 FF FF FF")

    def _ibs_reset_ecu(self):
        """通过 DoIP 复位 IBS ECU"""
        client = self.ibs_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ IBS 未连接", "#FF5252")
            return
        try:
            cmd_11_01 = bytes([0x11, 0x01])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x0726 11 01", "#64B5F6")
            QApplication.processEvents()

            resp = self._ibs_send_uds_raw(cmd_11_01, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x51:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x0726 {formatted} ✅ IBS Reset 成功", "#4CAF50")
                    self.append_log_color(f"💡 提示：IBS 正在重启，连接可能需要等待 10-30 秒后恢复", "#FF9800")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    if nrc == 0x78:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x0726 {formatted} ⏳ NRC 0x78 等待响应 (IBS 正在重启...)", "#FF9800")
                    else:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x0726 {formatted} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x0726 {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ Reset 失败：{str(e)}", "#FF5252")


    # ==================== RWSL 诊断功能 ====================
    def _connect_rwsl_doip(self):
        """连接 RWSL DoIP (通过 ICB 转发)"""
        try:
            self.append_log_color("🔗 正在连接 RWSL...", "#2196F3")
            client = DoIPClient(RWSL_DOIP_IP, RWSL_DOIP_PORT, routing_ta=RWSL_ROUTING_TA)
            client.connect()
            client.routing_activate()
            self.rwsl_doip_client = client
            self.rwsl_doip_connected = True
            self.append_log_color("✅ RWSL 连接成功", "#4CAF50")

            # 如果有待执行的诊断动作，立即执行
            if self._diag_pending_action == 'dtc_read':
                self._diag_pending_action = None
                self._rwsl_read_dtc()
            elif self._diag_pending_action == 'dtc_clear':
                self._diag_pending_action = None
                self._rwsl_clear_dtc()
            elif self._diag_pending_action == 'reset':
                self._diag_pending_action = None
                self._rwsl_reset_ecu()
            elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
                cmd = self._diag_pending_cmd
                self._diag_pending_action = None
                self._diag_pending_cmd = None
                self._rwsl_send_uds_cmd(cmd)
            return True
        except Exception as e:
            self.append_log_color(f"❌ RWSL 连接失败：{e}", "#FF5252")
            return False

    def _rwsl_send_uds_raw(self, data: bytes, timeout: float = 2.0):
        """发送 UDS 指令到 RWSL 并返回原始响应 (bytes), 失败返回 None"""
        client = self.rwsl_doip_client
        if not client or not client.routing_activated:
            return None
        try:
            resp = client.send_diagnostic(data, target_addr=RWSL_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ RWSL UDS 发送失败：{e}", "#FF9800")
            return None

    def _rwsl_send_uds_cmd(self, cmd_text: str):
        """通过 DoIP 发送 UDS 诊断指令到 RWSL"""
        import re
        import time

        client = self.rwsl_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ RWSL 未连接", "#FF5252")
            return

        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            if '#' in line:
                line = line.split('#')[0].strip()
            if '//' in line:
                line = line.split('//')[0].strip()
            if not line:
                continue

            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"💤 Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue

            hex_str = line.replace(' ', '').replace('\t', '')
            try:
                uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue

            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{RWSL_PHYSICAL_ADDR:04X} {formatted_tx}", "#64B5F6")
            QApplication.processEvents()

            resp = self._rwsl_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    if nrc == 0x78:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{RWSL_RESPONSE_ADDR:04X} {formatted_rx} ⏳ {nrc_desc}", "#FF9800")
                    else:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{RWSL_RESPONSE_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RWSL_RESPONSE_ADDR:04X} {formatted_rx}", "#81C784")

                # RWSL 自动安全访问：收到 67 01 + seed 后，自动计算 key 并发送 27 02
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        # RWSL 算法号：0000104A
                        key = sa_calc.calc_key(seed_hex, '0000104A')
                        client = self.rwsl_doip_client
                        if client and client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key
                            formatted_tx2 = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x{RWSL_PHYSICAL_ADDR:04X} {formatted_tx2}  🔑 自动发送 KEY", "#64B5F6")
                            QApplication.processEvents()

                            resp2 = None
                            for retry in range(10):
                                resp2 = self._rwsl_send_uds_raw(cmd_27_02, timeout=2.0)
                                if resp2:
                                    if len(resp2) >= 3 and resp2[0] == 0x7F and resp2[2] == 0x78:
                                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{RWSL_RESPONSE_ADDR:04X} 7F 27 78 ⏳ Response Pending，等待中...", "#FF9800")
                                        time.sleep(0.5)
                                        continue
                                    break
                                time.sleep(0.3)

                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RWSL_RESPONSE_ADDR:04X} {f2} ✅ 安全认证成功", "#4CAF50")
                                    self.append_log_color(f"💡 已解锁安全访问，后续诊断功能可用", "#FF9800")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    nrc_desc2 = self._diag_nrc_desc(nrc2)
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RWSL_RESPONSE_ADDR:04X} {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X} {nrc_desc2}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RWSL_RESPONSE_ADDR:04X} {f2} ❌ 安全认证失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    def _rwsl_read_dtc(self):
        """通过 DoIP 读取 RWSL 的 DTC 故障码 (IDS 方式) - 通过 ICB 转发"""
        client = self.rwsl_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ RWSL 未连接", "#FF5252")
            return

        try:
            # Step 1: 19 02 2C - 读取有效 DTC
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{RWSL_PHYSICAL_ADDR:04X} 19 02 2C", "#64B5F6")
            QApplication.processEvents()

            resp = self._rwsl_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=2.0)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return

            formatted = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x{RWSL_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            QApplication.processEvents()

            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color("  ✅ 无有效 DTC", "#4CAF50")
                return

            self.append_log_color(f"  📋 发现 {len(dtc_records)} 条 DTC", "#FF9800")

            # Step 2: 对每个 DTC 查询快照 (19 04) 和扩展数据 (19 06)
            log_lines = []
            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']

                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{RWSL_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_04)}")
                resp_04 = self._rwsl_send_uds_raw(cmd_04, timeout=1.5)
                if resp_04:
                    f = ' '.join(f'{b:02X}' for b in resp_04)
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{RWSL_RESPONSE_ADDR:04X} {f}")
                    dtc['snapshot_raw'] = resp_04

                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{RWSL_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_06)}")
                resp_06 = self._rwsl_send_uds_raw(cmd_06, timeout=1.5)
                if resp_06:
                    f = ' '.join(f'{b:02X}' for b in resp_06)
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{RWSL_RESPONSE_ADDR:04X} {f}")
                    dtc['extended_raw'] = resp_06

            self.append_log_batch(log_lines)
            self._display_dtc_table(dtc_records)
            self._save_dtc_excel(dtc_records)

        except Exception as e:
            self._diag_on_socket_error(e)
            self.append_log_color(f"❌ DTC 读取异常: {e}", "#FF5252")
            import traceback
            self.append_log_color(traceback.format_exc(), "#FF5252")

    def _rwsl_clear_dtc(self):
        """通过 DoIP 清除 RWSL 的 DTC 故障码"""
        client = self.rwsl_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ RWSL 未连接", "#FF5252")
            return
        try:
            cmd_14 = bytes([0x14, 0xFF, 0xFF, 0xFF])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{RWSL_PHYSICAL_ADDR:04X} 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()

            resp = self._rwsl_send_uds_raw(cmd_14, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x54:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RWSL_RESPONSE_ADDR:04X} {formatted} ✅ DTC 清除成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RWSL_RESPONSE_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RWSL_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 清除超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ DTC 清除异常: {e}", "#FF5252")


    # ==================== SCM 诊断功能 ====================
    def _connect_scm_doip(self):
        """连接 SCM DoIP (通过 ICB 转发)"""
        try:
            self.append_log_color("🔗 正在连接 SCM...", "#2196F3")
            client = DoIPClient(SCM_DOIP_IP, SCM_DOIP_PORT, routing_ta=SCM_ROUTING_TA)
            client.connect()
            client.routing_activate()
            self.scm_doip_client = client
            self.scm_doip_connected = True
            self.append_log_color("✅ SCM 连接成功", "#4CAF50")

            if self._diag_pending_action == 'dtc_read':
                self._diag_pending_action = None
                self._scm_read_dtc()
            elif self._diag_pending_action == 'dtc_clear':
                self._diag_pending_action = None
                self._scm_clear_dtc()
            elif self._diag_pending_action == 'reset':
                self._diag_pending_action = None
                self._scm_reset_ecu()
            elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
                cmd = self._diag_pending_cmd
                self._diag_pending_action = None
                self._diag_pending_cmd = None
                self._scm_send_uds_cmd(cmd)
            return True
        except Exception as e:
            self.append_log_color(f"❌ SCM 连接失败：{e}", "#FF5252")
            return False

    def _scm_send_uds_raw(self, data: bytes, timeout: float = 2.0):
        client = self.scm_doip_client
        if not client or not client.routing_activated:
            return None
        try:
            resp = client.send_diagnostic(data, target_addr=SCM_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ SCM UDS 发送失败：{e}", "#FF9800")
            return None

    def _scm_send_uds_cmd(self, cmd_text: str):
        import re, time
        client = self.scm_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ SCM 未连接", "#FF5252")
            return

        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            if '#' in line: line = line.split('#')[0].strip()
            if '//' in line: line = line.split('//')[0].strip()
            if not line: continue

            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"💤 Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue

            hex_str = line.replace(' ', '').replace('\t', '')
            try:
                uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue

            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{SCM_PHYSICAL_ADDR:04X} {formatted_tx}", "#64B5F6")
            QApplication.processEvents()

            resp = self._scm_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    if nrc == 0x78:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{SCM_RESPONSE_ADDR:04X} {formatted_rx} ⏳ {nrc_desc}", "#FF9800")
                    else:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{SCM_RESPONSE_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{SCM_RESPONSE_ADDR:04X} {formatted_rx}", "#81C784")

                # SCM 自动安全访问
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        key = sa_calc.calc_key(seed_hex, '00001049')
                        client = self.scm_doip_client
                        if client and client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key
                            formatted_tx2 = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x{SCM_PHYSICAL_ADDR:04X} {formatted_tx2}  🔑 自动发送 KEY", "#64B5F6")
                            QApplication.processEvents()

                            resp2 = None
                            for retry in range(10):
                                resp2 = self._scm_send_uds_raw(cmd_27_02, timeout=2.0)
                                if resp2:
                                    if len(resp2) >= 3 and resp2[0] == 0x7F and resp2[2] == 0x78:
                                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{SCM_RESPONSE_ADDR:04X} 7F 27 78 ⏳ Response Pending，等待中...", "#FF9800")
                                        time.sleep(0.5)
                                        continue
                                    break
                                time.sleep(0.3)

                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{SCM_RESPONSE_ADDR:04X} {f2} ✅ 安全认证成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    nrc_desc2 = self._diag_nrc_desc(nrc2)
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{SCM_RESPONSE_ADDR:04X} {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X} {nrc_desc2}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{SCM_RESPONSE_ADDR:04X} {f2} ❌ 安全认证失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    def _scm_read_dtc(self):
        client = self.scm_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ SCM 未连接", "#FF5252")
            return
        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{SCM_PHYSICAL_ADDR:04X} 19 02 2C", "#64B5F6")
            QApplication.processEvents()
            resp = self._scm_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=2.0)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return
            formatted = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x{SCM_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            QApplication.processEvents()

            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color("  ✅ 无有效 DTC", "#4CAF50")
                return
            self.append_log_color(f"  📋 发现 {len(dtc_records)} 条 DTC", "#FF9800")

            log_lines = []
            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']
                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{SCM_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_04)}")
                resp_04 = self._scm_send_uds_raw(cmd_04, timeout=1.5)
                if resp_04:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{SCM_RESPONSE_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_04)}")
                    dtc['snapshot_raw'] = resp_04
                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{SCM_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_06)}")
                resp_06 = self._scm_send_uds_raw(cmd_06, timeout=1.5)
                if resp_06:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{SCM_RESPONSE_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_06)}")
                    dtc['extended_raw'] = resp_06

            self.append_log_batch(log_lines)
            self._display_dtc_table(dtc_records)
            self._save_dtc_excel(dtc_records)
        except Exception as e:
            self._diag_on_socket_error(e)
            self.append_log_color(f"❌ DTC 读取异常: {e}", "#FF5252")
            import traceback
            self.append_log_color(traceback.format_exc(), "#FF5252")

    def _scm_clear_dtc(self):
        client = self.scm_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ SCM 未连接", "#FF5252")
            return
        try:
            cmd_14 = bytes([0x14, 0xFF, 0xFF, 0xFF])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{SCM_PHYSICAL_ADDR:04X} 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()
            resp = self._scm_send_uds_raw(cmd_14, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x54:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{SCM_RESPONSE_ADDR:04X} {formatted} ✅ DTC 清除成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{SCM_RESPONSE_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{SCM_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 清除超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ DTC 清除异常: {e}", "#FF5252")

    def _scm_reset_ecu(self):
        client = self.scm_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ SCM 未连接", "#FF5252")
            return
        try:
            cmd_11_01 = bytes([0x11, 0x01])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{SCM_PHYSICAL_ADDR:04X} 11 01", "#64B5F6")
            QApplication.processEvents()
            resp = self._scm_send_uds_raw(cmd_11_01, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x51:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{SCM_RESPONSE_ADDR:04X} {formatted} ✅ SCM Reset 成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{SCM_RESPONSE_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{SCM_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ Reset 超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ Reset 失败：{str(e)}", "#FF5252")
    def _rwsl_reset_ecu(self):
        """通过 DoIP 复位 RWSL ECU"""
        client = self.rwsl_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ RWSL 未连接", "#FF5252")
            return
        try:
            cmd_11_01 = bytes([0x11, 0x01])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{RWSL_PHYSICAL_ADDR:04X} 11 01", "#64B5F6")
            QApplication.processEvents()

            resp = self._rwsl_send_uds_raw(cmd_11_01, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x51:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RWSL_RESPONSE_ADDR:04X} {formatted} ✅ RWSL Reset 成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RWSL_RESPONSE_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RWSL_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ Reset 超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ Reset 失败：{str(e)}", "#FF5252")

    # ==================== RLPODA 诊断功能 ====================
    def _connect_rlpoda_doip(self):
        """RLPODA 通过 ICB 转发，复用 ICB 的连接"""
        if not self.diag_doip_connected or not self.diag_doip_client:
            self.append_log_color("🔗 正在连接 ICB 网关以转发 RLPODA...", "#2196F3")
            self._connect_doip_async("icb")
            return False
        self.rlpoda_doip_connected = True
        self.rlpoda_doip_client = self.diag_doip_client
        self.append_log_color("✅ RLPODA 网关已就绪 (共享 ICB 连接)", "#4CAF50")
        if self._diag_pending_action == 'dtc_read':
            self._diag_pending_action = None; self._rlpoda_read_dtc()
        elif self._diag_pending_action == 'dtc_clear':
            self._diag_pending_action = None; self._rlpoda_clear_dtc()
        elif self._diag_pending_action == 'reset':
            self._diag_pending_action = None; self._rlpoda_reset_ecu()
        elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
            cmd = self._diag_pending_cmd; self._diag_pending_action = None; self._diag_pending_cmd = None
            self._rlpoda_send_uds_cmd(cmd)
        return True

    def _rlpoda_send_uds_raw(self, data, timeout=2.0):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("⚠ RLPODA: 共享 ICB 连接未就绪", "#FF9800")
            return None
        try:
            resp = client.send_diagnostic(data, target_addr=RLPODA_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ RLPODA UDS 发送失败：{e}", "#FF9800")
            return None

    def _rlpoda_send_uds_cmd(self, cmd_text):
        import re, time
        client = self.rlpoda_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ RLPODA 未连接", "#FF5252")
            return
        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            if '#' in line: line = line.split('#')[0].strip()
            if '//' in line: line = line.split('//')[0].strip()
            if not line: continue
            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"💤 Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue
            hex_str = line.replace(' ', '').replace('\t', '')
            try: uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue
            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{RLPODA_PHYSICAL_ADDR:04X} {formatted_tx}", "#64B5F6")
            QApplication.processEvents()
            resp = self._rlpoda_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    if nrc == 0x78:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLPODA_RESPONSE_ADDR:04X} {formatted_rx} ⏳ {nrc_desc}", "#FF9800")
                    else:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLPODA_RESPONSE_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLPODA_RESPONSE_ADDR:04X} {formatted_rx}", "#81C784")
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        key = sa_calc.calc_key(seed_hex, '00001071')
                        client = self.rlpoda_doip_client
                        if client and client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key
                            f2tx = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x{RLPODA_PHYSICAL_ADDR:04X} {f2tx}  🔑 自动发送 KEY", "#64B5F6")
                            QApplication.processEvents()
                            resp2 = None
                            for retry in range(10):
                                resp2 = self._rlpoda_send_uds_raw(cmd_27_02, timeout=2.0)
                                if resp2:
                                    if len(resp2) >= 3 and resp2[0] == 0x7F and resp2[2] == 0x78:
                                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLPODA_RESPONSE_ADDR:04X} 7F 27 78 ⏳ Response Pending，等待中...", "#FF9800")
                                        time.sleep(0.5)
                                        continue
                                    break
                                time.sleep(0.3)
                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLPODA_RESPONSE_ADDR:04X} {f2} ✅ 安全认证成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLPODA_RESPONSE_ADDR:04X} {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLPODA_RESPONSE_ADDR:04X} {f2} ❌ 安全认证失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    def _rlpoda_read_dtc(self):
        client = self.rlpoda_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ RLPODA 未连接", "#FF5252")
            return
        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{RLPODA_PHYSICAL_ADDR:04X} 19 02 2C", "#64B5F6")
            QApplication.processEvents()
            resp = self._rlpoda_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=2.0)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return
            formatted = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLPODA_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            QApplication.processEvents()
            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color("  ✅ 无有效 DTC", "#4CAF50")
                return
            self.append_log_color(f"  📋 发现 {len(dtc_records)} 条 DTC", "#FF9800")
            log_lines = []
            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']
                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{RLPODA_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_04)}")
                resp_04 = self._rlpoda_send_uds_raw(cmd_04, timeout=1.5)
                if resp_04:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{RLPODA_RESPONSE_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_04)}")
                    dtc['snapshot_raw'] = resp_04
                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{RLPODA_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_06)}")
                resp_06 = self._rlpoda_send_uds_raw(cmd_06, timeout=1.5)
                if resp_06:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{RLPODA_RESPONSE_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_06)}")
                    dtc['extended_raw'] = resp_06
            self.append_log_batch(log_lines)
            self._display_dtc_table(dtc_records)
            self._save_dtc_excel(dtc_records)
        except Exception as e:
            self._diag_on_socket_error(e)
            self.append_log_color(f"❌ DTC 读取异常: {e}", "#FF5252")
            import traceback; self.append_log_color(traceback.format_exc(), "#FF5252")

    def _rlpoda_clear_dtc(self):
        client = self.rlpoda_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ RLPODA 未连接", "#FF5252")
            return
        try:
            cmd_14 = bytes([0x14, 0xFF, 0xFF, 0xFF])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{RLPODA_PHYSICAL_ADDR:04X} 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()
            resp = self._rlpoda_send_uds_raw(cmd_14, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x54:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLPODA_RESPONSE_ADDR:04X} {formatted} ✅ DTC 清除成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLPODA_RESPONSE_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLPODA_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 清除超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ DTC 清除异常: {e}", "#FF5252")

    def _rlpoda_reset_ecu(self):
        client = self.rlpoda_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ RLPODA 未连接", "#FF5252")
            return
        try:
            cmd_11_01 = bytes([0x11, 0x01])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{RLPODA_PHYSICAL_ADDR:04X} 11 01", "#64B5F6")
            QApplication.processEvents()
            resp = self._rlpoda_send_uds_raw(cmd_11_01, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x51:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLPODA_RESPONSE_ADDR:04X} {formatted} ✅ RLPODA Reset 成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLPODA_RESPONSE_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLPODA_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ Reset 超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ Reset 失败：{str(e)}", "#FF5252")

    # ==================== RRPODA 诊断功能 ====================
    def _connect_rrpoda_doip(self):
        """RRPODA 通过 ICB 转发，复用 ICB 的连接"""
        if not self.diag_doip_connected or not self.diag_doip_client:
            self.append_log_color("🔗 正在连接 ICB 网关以转发 RRPODA...", "#2196F3")
            self._connect_doip_async("icb")
            return False
        self.rrpoda_doip_connected = True
        self.rrpoda_doip_client = self.diag_doip_client
        self.append_log_color("✅ RRPODA 网关已就绪 (共享 ICB 连接)", "#4CAF50")
        if self._diag_pending_action == 'dtc_read':
            self._diag_pending_action = None; self._rrpoda_read_dtc()
        elif self._diag_pending_action == 'dtc_clear':
            self._diag_pending_action = None; self._rrpoda_clear_dtc()
        elif self._diag_pending_action == 'reset':
            self._diag_pending_action = None; self._rrpoda_reset_ecu()
        elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
            cmd = self._diag_pending_cmd; self._diag_pending_action = None; self._diag_pending_cmd = None
            self._rrpoda_send_uds_cmd(cmd)
        return True

    def _rrpoda_send_uds_raw(self, data, timeout=2.0):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("⚠ RRPODA: 共享 ICB 连接未就绪", "#FF9800")
            return None
        try:
            resp = client.send_diagnostic(data, target_addr=RRPODA_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ RRPODA UDS 发送失败：{e}", "#FF9800")
            return None

    def _rrpoda_send_uds_cmd(self, cmd_text):
        import re, time
        client = self.rrpoda_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ RRPODA 未连接", "#FF5252")
            return
        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            if '#' in line: line = line.split('#')[0].strip()
            if '//' in line: line = line.split('//')[0].strip()
            if not line: continue
            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"💤 Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue
            hex_str = line.replace(' ', '').replace('\t', '')
            try: uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue
            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{RRPODA_PHYSICAL_ADDR:04X} {formatted_tx}", "#64B5F6")
            QApplication.processEvents()
            resp = self._rrpoda_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    if nrc == 0x78:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{RRPODA_RESPONSE_ADDR:04X} {formatted_rx} ⏳ {nrc_desc}", "#FF9800")
                    else:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{RRPODA_RESPONSE_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RRPODA_RESPONSE_ADDR:04X} {formatted_rx}", "#81C784")
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        key = sa_calc.calc_key(seed_hex, '00001071')
                        client = self.rrpoda_doip_client
                        if client and client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key
                            f2tx = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x{RRPODA_PHYSICAL_ADDR:04X} {f2tx}  🔑 自动发送 KEY", "#64B5F6")
                            QApplication.processEvents()
                            resp2 = None
                            for retry in range(10):
                                resp2 = self._rrpoda_send_uds_raw(cmd_27_02, timeout=2.0)
                                if resp2:
                                    if len(resp2) >= 3 and resp2[0] == 0x7F and resp2[2] == 0x78:
                                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{RRPODA_RESPONSE_ADDR:04X} 7F 27 78 ⏳ Response Pending，等待中...", "#FF9800")
                                        time.sleep(0.5)
                                        continue
                                    break
                                time.sleep(0.3)
                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RRPODA_RESPONSE_ADDR:04X} {f2} ✅ 安全认证成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RRPODA_RESPONSE_ADDR:04X} {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RRPODA_RESPONSE_ADDR:04X} {f2} ❌ 安全认证失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    def _rrpoda_read_dtc(self):
        client = self.rrpoda_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ RRPODA 未连接", "#FF5252")
            return
        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{RRPODA_PHYSICAL_ADDR:04X} 19 02 2C", "#64B5F6")
            QApplication.processEvents()
            resp = self._rrpoda_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=2.0)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return
            formatted = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x{RRPODA_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            QApplication.processEvents()
            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color("  ✅ 无有效 DTC", "#4CAF50")
                return
            self.append_log_color(f"  📋 发现 {len(dtc_records)} 条 DTC", "#FF9800")
            log_lines = []
            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']
                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{RRPODA_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_04)}")
                resp_04 = self._rrpoda_send_uds_raw(cmd_04, timeout=1.5)
                if resp_04:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{RRPODA_RESPONSE_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_04)}")
                    dtc['snapshot_raw'] = resp_04
                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{RRPODA_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_06)}")
                resp_06 = self._rrpoda_send_uds_raw(cmd_06, timeout=1.5)
                if resp_06:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{RRPODA_RESPONSE_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_06)}")
                    dtc['extended_raw'] = resp_06
            self.append_log_batch(log_lines)
            self._display_dtc_table(dtc_records)
            self._save_dtc_excel(dtc_records)
        except Exception as e:
            self._diag_on_socket_error(e)
            self.append_log_color(f"❌ DTC 读取异常: {e}", "#FF5252")
            import traceback; self.append_log_color(traceback.format_exc(), "#FF5252")

    def _rrpoda_clear_dtc(self):
        client = self.rrpoda_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ RRPODA 未连接", "#FF5252")
            return
        try:
            cmd_14 = bytes([0x14, 0xFF, 0xFF, 0xFF])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{RRPODA_PHYSICAL_ADDR:04X} 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()
            resp = self._rrpoda_send_uds_raw(cmd_14, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x54:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RRPODA_RESPONSE_ADDR:04X} {formatted} ✅ DTC 清除成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RRPODA_RESPONSE_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RRPODA_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 清除超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ DTC 清除异常: {e}", "#FF5252")

    def _rrpoda_reset_ecu(self):
        client = self.rrpoda_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ RRPODA 未连接", "#FF5252")
            return
        try:
            cmd_11_01 = bytes([0x11, 0x01])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{RRPODA_PHYSICAL_ADDR:04X} 11 01", "#64B5F6")
            QApplication.processEvents()
            resp = self._rrpoda_send_uds_raw(cmd_11_01, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x51:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RRPODA_RESPONSE_ADDR:04X} {formatted} ✅ RRPODA Reset 成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RRPODA_RESPONSE_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RRPODA_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ Reset 超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ Reset 失败：{str(e)}", "#FF5252")

    # ==================== SDM 诊断功能 ====================
    def _connect_sdm_doip(self):
        """连接 SDM DoIP (通过 ICB 转发)"""
        try:
            self.append_log_color("🔗 正在连接 SDM...", "#2196F3")
            client = DoIPClient(SDM_DOIP_IP, SDM_DOIP_PORT, routing_ta=SDM_ROUTING_TA)
            client.connect()
            client.routing_activate()
            self.sdm_doip_client = client
            self.sdm_doip_connected = True
            self.append_log_color("✅ SDM 连接成功", "#4CAF50")

            if self._diag_pending_action == 'dtc_read':
                self._diag_pending_action = None
                self._sdm_read_dtc()
            elif self._diag_pending_action == 'dtc_clear':
                self._diag_pending_action = None
                self._sdm_clear_dtc()
            elif self._diag_pending_action == 'reset':
                self._diag_pending_action = None
                self._sdm_reset_ecu()
            elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
                cmd = self._diag_pending_cmd
                self._diag_pending_action = None
                self._diag_pending_cmd = None
                self._sdm_send_uds_cmd(cmd)
            return True
        except Exception as e:
            self.append_log_color(f"❌ SDM 连接失败：{e}", "#FF5252")
            return False

    def _sdm_send_uds_raw(self, data: bytes, timeout: float = 2.0):
        client = self.sdm_doip_client
        if not client or not client.routing_activated:
            return None
        try:
            resp = client.send_diagnostic(data, target_addr=SDM_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ SDM UDS 发送失败：{e}", "#FF9800")
            return None

    def _sdm_send_uds_cmd(self, cmd_text: str):
        import re, time
        client = self.sdm_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ SDM 未连接", "#FF5252")
            return

        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            if '#' in line: line = line.split('#')[0].strip()
            if '//' in line: line = line.split('//')[0].strip()
            if not line: continue

            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"💤 Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue

            hex_str = line.replace(' ', '').replace('\t', '')
            try:
                uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue

            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{SDM_PHYSICAL_ADDR:04X} {formatted_tx}", "#64B5F6")
            QApplication.processEvents()

            resp = self._sdm_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    if nrc == 0x78:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{SDM_RESPONSE_ADDR:04X} {formatted_rx} ⏳ {nrc_desc}", "#FF9800")
                    else:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{SDM_RESPONSE_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{SDM_RESPONSE_ADDR:04X} {formatted_rx}", "#81C784")

                # SDM 自动安全访问
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        key = sa_calc.calc_key(seed_hex, '00001019')
                        client = self.sdm_doip_client
                        if client and client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key
                            formatted_tx2 = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x{SDM_PHYSICAL_ADDR:04X} {formatted_tx2}  🔑 自动发送 KEY", "#64B5F6")
                            QApplication.processEvents()
                            resp2 = None
                            for retry in range(10):
                                resp2 = self._sdm_send_uds_raw(cmd_27_02, timeout=2.0)
                                if resp2:
                                    if len(resp2) >= 3 and resp2[0] == 0x7F and resp2[2] == 0x78:
                                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{SDM_RESPONSE_ADDR:04X} 7F 27 78 ⏳ Response Pending，等待中...", "#FF9800")
                                        time.sleep(0.5)
                                        continue
                                    break
                                time.sleep(0.3)
                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{SDM_RESPONSE_ADDR:04X} {f2} ✅ 安全认证成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{SDM_RESPONSE_ADDR:04X} {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{SDM_RESPONSE_ADDR:04X} {f2} ❌ 安全认证失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    def _sdm_read_dtc(self):
        client = self.sdm_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ SDM 未连接", "#FF5252")
            return
        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{SDM_PHYSICAL_ADDR:04X} 19 02 2C", "#64B5F6")
            QApplication.processEvents()
            resp = self._sdm_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=2.0)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return
            formatted = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x{SDM_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            QApplication.processEvents()
            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color("  ✅ 无有效 DTC", "#4CAF50")
                return
            self.append_log_color(f"  📋 发现 {len(dtc_records)} 条 DTC", "#FF9800")
            log_lines = []
            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']
                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{SDM_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_04)}")
                resp_04 = self._sdm_send_uds_raw(cmd_04, timeout=1.5)
                if resp_04:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{SDM_RESPONSE_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_04)}")
                    dtc['snapshot_raw'] = resp_04
                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{SDM_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_06)}")
                resp_06 = self._sdm_send_uds_raw(cmd_06, timeout=1.5)
                if resp_06:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{SDM_RESPONSE_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_06)}")
                    dtc['extended_raw'] = resp_06
            self.append_log_batch(log_lines)
            self._display_dtc_table(dtc_records)
            self._save_dtc_excel(dtc_records)
        except Exception as e:
            self._diag_on_socket_error(e)
            self.append_log_color(f"❌ DTC 读取异常: {e}", "#FF5252")
            import traceback
            self.append_log_color(traceback.format_exc(), "#FF5252")

    def _sdm_clear_dtc(self):
        client = self.sdm_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ SDM 未连接", "#FF5252")
            return
        try:
            cmd_14 = bytes([0x14, 0xFF, 0xFF, 0xFF])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{SDM_PHYSICAL_ADDR:04X} 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()
            resp = self._sdm_send_uds_raw(cmd_14, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x54:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{SDM_RESPONSE_ADDR:04X} {formatted} ✅ DTC 清除成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{SDM_RESPONSE_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{SDM_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 清除超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ DTC 清除异常: {e}", "#FF5252")

    def _sdm_reset_ecu(self):
        client = self.sdm_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ SDM 未连接", "#FF5252")
            return
        try:
            cmd_11_01 = bytes([0x11, 0x01])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{SDM_PHYSICAL_ADDR:04X} 11 01", "#64B5F6")
            QApplication.processEvents()
            resp = self._sdm_send_uds_raw(cmd_11_01, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x51:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{SDM_RESPONSE_ADDR:04X} {formatted} ✅ SDM Reset 成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{SDM_RESPONSE_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{SDM_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ Reset 超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ Reset 失败：{str(e)}", "#FF5252")

    # ==================== ESS 诊断功能 ====================
    def _connect_ess_doip(self):
        """连接 ESS DoIP (通过 ICB 转发)"""
        try:
            self.append_log_color("🔗 正在连接 ESS...", "#2196F3")
            client = DoIPClient(ESS_DOIP_IP, ESS_DOIP_PORT, routing_ta=ESS_ROUTING_TA)
            client.connect()
            client.routing_activate()
            self.ess_doip_client = client
            self.ess_doip_connected = True
            self.append_log_color("✅ ESS 连接成功", "#4CAF50")

            if self._diag_pending_action == 'dtc_read':
                self._diag_pending_action = None
                self._ess_read_dtc()
            elif self._diag_pending_action == 'dtc_clear':
                self._diag_pending_action = None
                self._ess_clear_dtc()
            elif self._diag_pending_action == 'reset':
                self._diag_pending_action = None
                self._ess_reset_ecu()
            elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
                cmd = self._diag_pending_cmd
                self._diag_pending_action = None
                self._diag_pending_cmd = None
                self._ess_send_uds_cmd(cmd)
            return True
        except Exception as e:
            self.append_log_color(f"❌ ESS 连接失败：{e}", "#FF5252")
            return False

    def _ess_send_uds_raw(self, data: bytes, timeout: float = 2.0):
        client = self.ess_doip_client
        if not client or not client.routing_activated:
            return None
        try:
            resp = client.send_diagnostic(data, target_addr=ESS_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ ESS UDS 发送失败：{e}", "#FF9800")
            return None

    def _ess_send_uds_cmd(self, cmd_text: str):
        import re, time
        client = self.ess_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ ESS 未连接", "#FF5252")
            return

        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            if '#' in line: line = line.split('#')[0].strip()
            if '//' in line: line = line.split('//')[0].strip()
            if not line: continue

            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"💤 Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue

            hex_str = line.replace(' ', '').replace('\t', '')
            try:
                uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue

            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{ESS_PHYSICAL_ADDR:04X} {formatted_tx}", "#64B5F6")
            QApplication.processEvents()

            resp = self._ess_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    if nrc == 0x78:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{ESS_RESPONSE_ADDR:04X} {formatted_rx} ⏳ {nrc_desc}", "#FF9800")
                    else:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{ESS_RESPONSE_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{ESS_RESPONSE_ADDR:04X} {formatted_rx}", "#81C784")

                # ESS 自动安全访问
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        key = sa_calc.calc_key(seed_hex, '0000101A')
                        client = self.ess_doip_client
                        if client and client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key
                            formatted_tx2 = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x{ESS_PHYSICAL_ADDR:04X} {formatted_tx2}  🔑 自动发送 KEY", "#64B5F6")
                            QApplication.processEvents()
                            resp2 = None
                            for retry in range(10):
                                resp2 = self._ess_send_uds_raw(cmd_27_02, timeout=2.0)
                                if resp2:
                                    if len(resp2) >= 3 and resp2[0] == 0x7F and resp2[2] == 0x78:
                                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{ESS_RESPONSE_ADDR:04X} 7F 27 78 ⏳ Response Pending，等待中...", "#FF9800")
                                        time.sleep(0.5)
                                        continue
                                    break
                                time.sleep(0.3)
                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{ESS_RESPONSE_ADDR:04X} {f2} ✅ 安全认证成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{ESS_RESPONSE_ADDR:04X} {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{ESS_RESPONSE_ADDR:04X} {f2} ❌ 安全认证失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    def _ess_read_dtc(self):
        client = self.ess_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ ESS 未连接", "#FF5252")
            return
        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{ESS_PHYSICAL_ADDR:04X} 19 02 2C", "#64B5F6")
            QApplication.processEvents()
            resp = self._ess_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=2.0)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return
            formatted = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x{ESS_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            QApplication.processEvents()
            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color("  ✅ 无有效 DTC", "#4CAF50")
                return
            self.append_log_color(f"  📋 发现 {len(dtc_records)} 条 DTC", "#FF9800")
            log_lines = []
            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']
                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{ESS_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_04)}")
                resp_04 = self._ess_send_uds_raw(cmd_04, timeout=1.5)
                if resp_04:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{ESS_RESPONSE_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_04)}")
                    dtc['snapshot_raw'] = resp_04
                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{ESS_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_06)}")
                resp_06 = self._ess_send_uds_raw(cmd_06, timeout=1.5)
                if resp_06:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{ESS_RESPONSE_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_06)}")
                    dtc['extended_raw'] = resp_06
            self.append_log_batch(log_lines)
            self._display_dtc_table(dtc_records)
            self._save_dtc_excel(dtc_records)
        except Exception as e:
            self._diag_on_socket_error(e)
            self.append_log_color(f"❌ DTC 读取异常: {e}", "#FF5252")
            import traceback
            self.append_log_color(traceback.format_exc(), "#FF5252")

    def _ess_clear_dtc(self):
        client = self.ess_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ ESS 未连接", "#FF5252")
            return
        try:
            cmd_14 = bytes([0x14, 0xFF, 0xFF, 0xFF])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{ESS_PHYSICAL_ADDR:04X} 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()
            resp = self._ess_send_uds_raw(cmd_14, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x54:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{ESS_RESPONSE_ADDR:04X} {formatted} ✅ DTC 清除成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{ESS_RESPONSE_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{ESS_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 清除超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ DTC 清除异常: {e}", "#FF5252")

    def _ess_reset_ecu(self):
        client = self.ess_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ ESS 未连接", "#FF5252")
            return
        try:
            cmd_11_01 = bytes([0x11, 0x01])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{ESS_PHYSICAL_ADDR:04X} 11 01", "#64B5F6")
            QApplication.processEvents()
            resp = self._ess_send_uds_raw(cmd_11_01, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x51:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{ESS_RESPONSE_ADDR:04X} {formatted} ✅ ESS Reset 成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{ESS_RESPONSE_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{ESS_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ Reset 超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ Reset 失败：{str(e)}", "#FF5252")

    # ==================== RACFP 诊断功能 ====================
    def _connect_racfp_doip(self):
        """连接 RACFP DoIP (通过 ICB 转发)"""
        try:
            self.append_log_color("🔗 正在连接 RACFP...", "#2196F3")
            client = DoIPClient(RACFP_DOIP_IP, RACFP_DOIP_PORT, routing_ta=RACFP_ROUTING_TA)
            client.connect()
            client.routing_activate()
            self.racfp_doip_client = client
            self.racfp_doip_connected = True
            self.append_log_color("✅ RACFP 连接成功", "#4CAF50")

            if self._diag_pending_action == 'dtc_read':
                self._diag_pending_action = None
                self._racfp_read_dtc()
            elif self._diag_pending_action == 'dtc_clear':
                self._diag_pending_action = None
                self._racfp_clear_dtc()
            elif self._diag_pending_action == 'reset':
                self._diag_pending_action = None
                self._racfp_reset_ecu()
            elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
                cmd = self._diag_pending_cmd
                self._diag_pending_action = None
                self._diag_pending_cmd = None
                self._racfp_send_uds_cmd(cmd)
            return True
        except Exception as e:
            self.append_log_color(f"❌ RACFP 连接失败：{e}", "#FF5252")
            return False

    def _racfp_send_uds_raw(self, data: bytes, timeout: float = 2.0):
        client = self.racfp_doip_client
        if not client or not client.routing_activated:
            return None
        try:
            resp = client.send_diagnostic(data, target_addr=RACFP_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ RACFP UDS 发送失败：{e}", "#FF9800")
            return None

    def _racfp_send_uds_cmd(self, cmd_text: str):
        import re, time
        client = self.racfp_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ RACFP 未连接", "#FF5252")
            return

        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            if '#' in line: line = line.split('#')[0].strip()
            if '//' in line: line = line.split('//')[0].strip()
            if not line: continue

            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"💤 Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue

            hex_str = line.replace(' ', '').replace('\t', '')
            try:
                uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue

            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{RACFP_PHYSICAL_ADDR:04X} {formatted_tx}", "#64B5F6")
            QApplication.processEvents()

            resp = self._racfp_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    if nrc == 0x78:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{RACFP_RESPONSE_ADDR:04X} {formatted_rx} ⏳ {nrc_desc}", "#FF9800")
                    else:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{RACFP_RESPONSE_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RACFP_RESPONSE_ADDR:04X} {formatted_rx}", "#81C784")

                # RACFP 自动安全访问
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        key = sa_calc.calc_key(seed_hex, '00001084')
                        client = self.racfp_doip_client
                        if client and client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key
                            formatted_tx2 = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x{RACFP_PHYSICAL_ADDR:04X} {formatted_tx2}  🔑 自动发送 KEY", "#64B5F6")
                            QApplication.processEvents()
                            resp2 = None
                            for retry in range(10):
                                resp2 = self._racfp_send_uds_raw(cmd_27_02, timeout=2.0)
                                if resp2:
                                    if len(resp2) >= 3 and resp2[0] == 0x7F and resp2[2] == 0x78:
                                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{RACFP_RESPONSE_ADDR:04X} 7F 27 78 ⏳ Response Pending，等待中...", "#FF9800")
                                        time.sleep(0.5)
                                        continue
                                    break
                                time.sleep(0.3)
                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RACFP_RESPONSE_ADDR:04X} {f2} ✅ 安全认证成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RACFP_RESPONSE_ADDR:04X} {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RACFP_RESPONSE_ADDR:04X} {f2} ❌ 安全认证失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    def _racfp_read_dtc(self):
        client = self.racfp_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ RACFP 未连接", "#FF5252")
            return
        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{RACFP_PHYSICAL_ADDR:04X} 19 02 2C", "#64B5F6")
            QApplication.processEvents()
            resp = self._racfp_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=2.0)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return
            formatted = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x{RACFP_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            QApplication.processEvents()
            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color("  ✅ 无有效 DTC", "#4CAF50")
                return
            self.append_log_color(f"  📋 发现 {len(dtc_records)} 条 DTC", "#FF9800")
            log_lines = []
            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']
                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{RACFP_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_04)}")
                resp_04 = self._racfp_send_uds_raw(cmd_04, timeout=1.5)
                if resp_04:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{RACFP_RESPONSE_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_04)}")
                    dtc['snapshot_raw'] = resp_04
                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{RACFP_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_06)}")
                resp_06 = self._racfp_send_uds_raw(cmd_06, timeout=1.5)
                if resp_06:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{RACFP_RESPONSE_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_06)}")
                    dtc['extended_raw'] = resp_06
            self.append_log_batch(log_lines)
            self._display_dtc_table(dtc_records)
            self._save_dtc_excel(dtc_records)
        except Exception as e:
            self._diag_on_socket_error(e)
            self.append_log_color(f"❌ DTC 读取异常: {e}", "#FF5252")
            import traceback
            self.append_log_color(traceback.format_exc(), "#FF5252")

    def _racfp_clear_dtc(self):
        client = self.racfp_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ RACFP 未连接", "#FF5252")
            return
        try:
            cmd_14 = bytes([0x14, 0xFF, 0xFF, 0xFF])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{RACFP_PHYSICAL_ADDR:04X} 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()
            resp = self._racfp_send_uds_raw(cmd_14, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x54:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RACFP_RESPONSE_ADDR:04X} {formatted} ✅ DTC 清除成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RACFP_RESPONSE_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RACFP_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 清除超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ DTC 清除异常: {e}", "#FF5252")

    def _racfp_reset_ecu(self):
        client = self.racfp_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ RACFP 未连接", "#FF5252")
            return
        try:
            cmd_11_01 = bytes([0x11, 0x01])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{RACFP_PHYSICAL_ADDR:04X} 11 01", "#64B5F6")
            QApplication.processEvents()
            resp = self._racfp_send_uds_raw(cmd_11_01, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x51:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RACFP_RESPONSE_ADDR:04X} {formatted} ✅ RACFP Reset 成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RACFP_RESPONSE_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RACFP_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ Reset 超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ Reset 失败：{str(e)}", "#FF5252")

    # ==================== FDR 诊断功能 ====================
    def _connect_fdr_doip(self):
        """连接 FDR DoIP (通过 ICB 转发)"""
        try:
            self.append_log_color("🔗 正在连接 FDR...", "#2196F3")
            client = DoIPClient(FDR_DOIP_IP, FDR_DOIP_PORT, routing_ta=FDR_ROUTING_TA)
            client.connect()
            client.routing_activate()
            self.fdr_doip_client = client
            self.fdr_doip_connected = True
            self.append_log_color("✅ FDR 连接成功", "#4CAF50")

            if self._diag_pending_action == 'dtc_read':
                self._diag_pending_action = None
                self._fdr_read_dtc()
            elif self._diag_pending_action == 'dtc_clear':
                self._diag_pending_action = None
                self._fdr_clear_dtc()
            elif self._diag_pending_action == 'reset':
                self._diag_pending_action = None
                self._fdr_reset_ecu()
            elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
                cmd = self._diag_pending_cmd
                self._diag_pending_action = None
                self._diag_pending_cmd = None
                self._fdr_send_uds_cmd(cmd)
            return True
        except Exception as e:
            self.append_log_color(f"❌ FDR 连接失败：{e}", "#FF5252")
            return False

    def _fdr_send_uds_raw(self, data: bytes, timeout: float = 2.0):
        client = self.fdr_doip_client
        if not client or not client.routing_activated:
            return None
        try:
            resp = client.send_diagnostic(data, target_addr=FDR_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ FDR UDS 发送失败：{e}", "#FF9800")
            return None

    def _fdr_send_uds_cmd(self, cmd_text: str):
        import re, time
        client = self.fdr_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ FDR 未连接", "#FF5252")
            return

        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            if '#' in line: line = line.split('#')[0].strip()
            if '//' in line: line = line.split('//')[0].strip()
            if not line: continue

            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"💤 Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue

            hex_str = line.replace(' ', '').replace('\t', '')
            try:
                uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue

            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{FDR_PHYSICAL_ADDR:04X} {formatted_tx}", "#64B5F6")
            QApplication.processEvents()

            resp = self._fdr_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    if nrc == 0x78:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{FDR_RESPONSE_ADDR:04X} {formatted_rx} ⏳ {nrc_desc}", "#FF9800")
                    else:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{FDR_RESPONSE_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FDR_RESPONSE_ADDR:04X} {formatted_rx}", "#81C784")

                # FDR 自动安全访问
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        key = sa_calc.calc_key(seed_hex, '00001056')
                        client = self.fdr_doip_client
                        if client and client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key
                            formatted_tx2 = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x{FDR_PHYSICAL_ADDR:04X} {formatted_tx2}  🔑 自动发送 KEY", "#64B5F6")
                            QApplication.processEvents()
                            resp2 = None
                            for retry in range(10):
                                resp2 = self._fdr_send_uds_raw(cmd_27_02, timeout=2.0)
                                if resp2:
                                    if len(resp2) >= 3 and resp2[0] == 0x7F and resp2[2] == 0x78:
                                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{FDR_RESPONSE_ADDR:04X} 7F 27 78 ⏳ Response Pending，等待中...", "#FF9800")
                                        time.sleep(0.5)
                                        continue
                                    break
                                time.sleep(0.3)
                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FDR_RESPONSE_ADDR:04X} {f2} ✅ 安全认证成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FDR_RESPONSE_ADDR:04X} {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FDR_RESPONSE_ADDR:04X} {f2} ❌ 安全认证失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    def _fdr_read_dtc(self):
        client = self.fdr_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ FDR 未连接", "#FF5252")
            return
        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{FDR_PHYSICAL_ADDR:04X} 19 02 2C", "#64B5F6")
            QApplication.processEvents()
            resp = self._fdr_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=2.0)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return
            formatted = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x{FDR_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            QApplication.processEvents()
            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color("  ✅ 无有效 DTC", "#4CAF50")
                return
            self.append_log_color(f"  📋 发现 {len(dtc_records)} 条 DTC", "#FF9800")
            log_lines = []
            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']
                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{FDR_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_04)}")
                resp_04 = self._fdr_send_uds_raw(cmd_04, timeout=1.5)
                if resp_04:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{FDR_RESPONSE_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_04)}")
                    dtc['snapshot_raw'] = resp_04
                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{FDR_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_06)}")
                resp_06 = self._fdr_send_uds_raw(cmd_06, timeout=1.5)
                if resp_06:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{FDR_RESPONSE_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_06)}")
                    dtc['extended_raw'] = resp_06
            self.append_log_batch(log_lines)
            self._display_dtc_table(dtc_records)
            self._save_dtc_excel(dtc_records)
        except Exception as e:
            self._diag_on_socket_error(e)
            self.append_log_color(f"❌ DTC 读取异常: {e}", "#FF5252")
            import traceback
            self.append_log_color(traceback.format_exc(), "#FF5252")

    def _fdr_clear_dtc(self):
        client = self.fdr_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ FDR 未连接", "#FF5252")
            return
        try:
            cmd_14 = bytes([0x14, 0xFF, 0xFF, 0xFF])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{FDR_PHYSICAL_ADDR:04X} 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()
            resp = self._fdr_send_uds_raw(cmd_14, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x54:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FDR_RESPONSE_ADDR:04X} {formatted} ✅ DTC 清除成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FDR_RESPONSE_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FDR_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 清除超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ DTC 清除异常: {e}", "#FF5252")

    def _fdr_reset_ecu(self):
        client = self.fdr_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ FDR 未连接", "#FF5252")
            return
        try:
            cmd_11_01 = bytes([0x11, 0x01])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{FDR_PHYSICAL_ADDR:04X} 11 01", "#64B5F6")
            QApplication.processEvents()
            resp = self._fdr_send_uds_raw(cmd_11_01, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x51:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FDR_RESPONSE_ADDR:04X} {formatted} ✅ FDR Reset 成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FDR_RESPONSE_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FDR_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ Reset 超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ Reset 失败：{str(e)}", "#FF5252")

    # ==================== FWM 诊断功能 ====================
    def _connect_fwm_doip(self):
        """连接 FWM DoIP (通过 ICB 转发)"""
        try:
            self.append_log_color("🔗 正在连接 FWM...", "#2196F3")
            client = DoIPClient(FWM_DOIP_IP, FWM_DOIP_PORT, routing_ta=FWM_ROUTING_TA)
            client.connect()
            client.routing_activate()
            self.fwm_doip_client = client
            self.fwm_doip_connected = True
            self.append_log_color("✅ FWM 连接成功", "#4CAF50")

            if self._diag_pending_action == 'dtc_read':
                self._diag_pending_action = None
                self._fwm_read_dtc()
            elif self._diag_pending_action == 'dtc_clear':
                self._diag_pending_action = None
                self._fwm_clear_dtc()
            elif self._diag_pending_action == 'reset':
                self._diag_pending_action = None
                self._fwm_reset_ecu()
            elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
                cmd = self._diag_pending_cmd
                self._diag_pending_action = None
                self._diag_pending_cmd = None
                self._fwm_send_uds_cmd(cmd)
            return True
        except Exception as e:
            self.append_log_color(f"❌ FWM 连接失败：{e}", "#FF5252")
            return False

    # ==================== FRPODA 诊断功能 ====================
    def _connect_frpoda_doip(self):
        """FRPODA 通过 ICB 转发，复用 ICB 的连接"""
        if not self.diag_doip_connected or not self.diag_doip_client:
            self.append_log_color("🔗 正在连接 ICB 网关以转发 FRPODA...", "#2196F3")
            self._connect_doip_async("icb")
            return False
        self.frpoda_doip_connected = True
        self.frpoda_doip_client = self.diag_doip_client
        self.append_log_color("✅ FRPODA 网关已就绪 (共享 ICB 连接)", "#4CAF50")
        # 处理待执行动作
        if self._diag_pending_action == 'dtc_read':
            self._diag_pending_action = None; self._frpoda_read_dtc()
        elif self._diag_pending_action == 'dtc_clear':
            self._diag_pending_action = None; self._frpoda_clear_dtc()
        elif self._diag_pending_action == 'reset':
            self._diag_pending_action = None; self._frpoda_reset_ecu()
        elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
            cmd = self._diag_pending_cmd; self._diag_pending_action = None; self._diag_pending_cmd = None
            self._frpoda_send_uds_cmd(cmd)
        return True

    def _frpoda_send_uds_raw(self, data, timeout=2.0):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("⚠ FRPODA: 共享 ICB 连接未就绪", "#FF9800")
            return None
        try:
            resp = client.send_diagnostic(data, target_addr=FRPODA_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ FRPODA UDS 发送失败：{e}", "#FF9800")
            return None

    def _frpoda_send_uds_cmd(self, cmd_text):
        import re, time
        client = self.frpoda_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ FRPODA 未连接", "#FF5252")
            return
        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            if '#' in line: line = line.split('#')[0].strip()
            if '//' in line: line = line.split('//')[0].strip()
            if not line: continue
            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"💤 Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue
            hex_str = line.replace(' ', '').replace('\t', '')
            try: uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue
            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{FRPODA_PHYSICAL_ADDR:04X} {formatted_tx}", "#64B5F6")
            QApplication.processEvents()
            resp = self._frpoda_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    if nrc == 0x78:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{FRPODA_RESPONSE_ADDR:04X} {formatted_rx} ⏳ {nrc_desc}", "#FF9800")
                    else:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{FRPODA_RESPONSE_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FRPODA_RESPONSE_ADDR:04X} {formatted_rx}", "#81C784")
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        key = sa_calc.calc_key(seed_hex, '00001071')
                        client = self.frpoda_doip_client
                        if client and client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key
                            f2tx = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x{FRPODA_PHYSICAL_ADDR:04X} {f2tx}  🔑 自动发送 KEY", "#64B5F6")
                            QApplication.processEvents()
                            resp2 = None
                            for retry in range(10):
                                resp2 = self._frpoda_send_uds_raw(cmd_27_02, timeout=2.0)
                                if resp2:
                                    if len(resp2) >= 3 and resp2[0] == 0x7F and resp2[2] == 0x78:
                                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{FRPODA_RESPONSE_ADDR:04X} 7F 27 78 ⏳ Response Pending，等待中...", "#FF9800")
                                        time.sleep(0.5)
                                        continue
                                    break
                                time.sleep(0.3)
                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FRPODA_RESPONSE_ADDR:04X} {f2} ✅ 安全认证成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FRPODA_RESPONSE_ADDR:04X} {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FRPODA_RESPONSE_ADDR:04X} {f2} ❌ 安全认证失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    def _frpoda_read_dtc(self):
        client = self.frpoda_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ FRPODA 未连接", "#FF5252")
            return
        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{FRPODA_PHYSICAL_ADDR:04X} 19 02 2C", "#64B5F6")
            QApplication.processEvents()
            resp = self._frpoda_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=2.0)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return
            formatted = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x{FRPODA_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            QApplication.processEvents()
            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color("  ✅ 无有效 DTC", "#4CAF50")
                return
            self.append_log_color(f"  📋 发现 {len(dtc_records)} 条 DTC", "#FF9800")
            log_lines = []
            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']
                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{FRPODA_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_04)}")
                resp_04 = self._frpoda_send_uds_raw(cmd_04, timeout=1.5)
                if resp_04:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{FRPODA_RESPONSE_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_04)}")
                    dtc['snapshot_raw'] = resp_04
                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{FRPODA_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_06)}")
                resp_06 = self._frpoda_send_uds_raw(cmd_06, timeout=1.5)
                if resp_06:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{FRPODA_RESPONSE_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_06)}")
                    dtc['extended_raw'] = resp_06
            self.append_log_batch(log_lines)
            self._display_dtc_table(dtc_records)
            self._save_dtc_excel(dtc_records)
        except Exception as e:
            self._diag_on_socket_error(e)
            self.append_log_color(f"❌ DTC 读取异常: {e}", "#FF5252")
            import traceback; self.append_log_color(traceback.format_exc(), "#FF5252")

    def _frpoda_clear_dtc(self):
        client = self.frpoda_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ FRPODA 未连接", "#FF5252")
            return
        try:
            cmd_14 = bytes([0x14, 0xFF, 0xFF, 0xFF])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{FRPODA_PHYSICAL_ADDR:04X} 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()
            resp = self._frpoda_send_uds_raw(cmd_14, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x54:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FRPODA_RESPONSE_ADDR:04X} {formatted} ✅ DTC 清除成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FRPODA_RESPONSE_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FRPODA_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 清除超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ DTC 清除异常: {e}", "#FF5252")

    def _frpoda_reset_ecu(self):
        client = self.frpoda_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ FRPODA 未连接", "#FF5252")
            return
        try:
            cmd_11_01 = bytes([0x11, 0x01])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{FRPODA_PHYSICAL_ADDR:04X} 11 01", "#64B5F6")
            QApplication.processEvents()
            resp = self._frpoda_send_uds_raw(cmd_11_01, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x51:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FRPODA_RESPONSE_ADDR:04X} {formatted} ✅ FRPODA Reset 成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FRPODA_RESPONSE_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FRPODA_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ Reset 超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ Reset 失败：{str(e)}", "#FF5252")

    # ==================== FLPODA 诊断功能 ====================
    def _connect_flpoda_doip(self):
        """连接 FLPODA DoIP (通过 ICB 转发)"""
        try:
            self.append_log_color("🔗 正在连接 FLPODA...", "#2196F3")
            client = DoIPClient(FLPODA_DOIP_IP, FLPODA_DOIP_PORT, routing_ta=FLPODA_ROUTING_TA)
            client.connect()
            client.routing_activate()
            self.flpoda_doip_client = client
            self.flpoda_doip_connected = True
            self.append_log_color("✅ FLPODA 连接成功", "#4CAF50")

            if self._diag_pending_action == 'dtc_read':
                self._diag_pending_action = None
                self._flpoda_read_dtc()
            elif self._diag_pending_action == 'dtc_clear':
                self._diag_pending_action = None
                self._flpoda_clear_dtc()
            elif self._diag_pending_action == 'reset':
                self._diag_pending_action = None
                self._flpoda_reset_ecu()
            elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
                cmd = self._diag_pending_cmd
                self._diag_pending_action = None
                self._diag_pending_cmd = None
                self._flpoda_send_uds_cmd(cmd)
            return True
        except Exception as e:
            self.append_log_color(f"❌ FLPODA 连接失败：{e}", "#FF5252")
            return False

    def _flpoda_send_uds_raw(self, data: bytes, timeout: float = 2.0):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("⚠ FLPODA: 共享 ICB 连接未就绪", "#FF9800")
            return None
        try:
            resp = client.send_diagnostic(data, target_addr=FLPODA_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ FLPODA UDS 发送失败：{e}", "#FF9800")
            return None

    def _flpoda_send_uds_cmd(self, cmd_text: str):
        import re, time
        client = self.flpoda_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ FLPODA 未连接", "#FF5252")
            return

        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            if '#' in line: line = line.split('#')[0].strip()
            if '//' in line: line = line.split('//')[0].strip()
            if not line: continue

            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"💤 Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue

            hex_str = line.replace(' ', '').replace('\t', '')
            try:
                uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue

            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{FLPODA_PHYSICAL_ADDR:04X} {formatted_tx}", "#64B5F6")
            QApplication.processEvents()

            resp = self._flpoda_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    if nrc == 0x78:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{FLPODA_RESPONSE_ADDR:04X} {formatted_rx} ⏳ {nrc_desc}", "#FF9800")
                    else:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{FLPODA_RESPONSE_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FLPODA_RESPONSE_ADDR:04X} {formatted_rx}", "#81C784")

                # FLPODA 自动安全访问
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        key = sa_calc.calc_key(seed_hex, '00001071')
                        client = self.flpoda_doip_client
                        if client and client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key
                            formatted_tx2 = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x{FLPODA_PHYSICAL_ADDR:04X} {formatted_tx2}  🔑 自动发送 KEY", "#64B5F6")
                            QApplication.processEvents()
                            resp2 = None
                            for retry in range(10):
                                resp2 = self._flpoda_send_uds_raw(cmd_27_02, timeout=2.0)
                                if resp2:
                                    if len(resp2) >= 3 and resp2[0] == 0x7F and resp2[2] == 0x78:
                                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{FLPODA_RESPONSE_ADDR:04X} 7F 27 78 ⏳ Response Pending，等待中...", "#FF9800")
                                        time.sleep(0.5)
                                        continue
                                    break
                                time.sleep(0.3)
                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FLPODA_RESPONSE_ADDR:04X} {f2} ✅ 安全认证成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FLPODA_RESPONSE_ADDR:04X} {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FLPODA_RESPONSE_ADDR:04X} {f2} ❌ 安全认证失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    def _flpoda_read_dtc(self):
        client = self.flpoda_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ FLPODA 未连接", "#FF5252")
            return
        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{FLPODA_PHYSICAL_ADDR:04X} 19 02 2C", "#64B5F6")
            QApplication.processEvents()
            resp = self._flpoda_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=2.0)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return
            formatted = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x{FLPODA_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            QApplication.processEvents()
            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color("  ✅ 无有效 DTC", "#4CAF50")
                return
            self.append_log_color(f"  📋 发现 {len(dtc_records)} 条 DTC", "#FF9800")
            log_lines = []
            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']
                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{FLPODA_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_04)}")
                resp_04 = self._flpoda_send_uds_raw(cmd_04, timeout=1.5)
                if resp_04:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{FLPODA_RESPONSE_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_04)}")
                    dtc['snapshot_raw'] = resp_04
                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{FLPODA_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_06)}")
                resp_06 = self._flpoda_send_uds_raw(cmd_06, timeout=1.5)
                if resp_06:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{FLPODA_RESPONSE_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_06)}")
                    dtc['extended_raw'] = resp_06
            self.append_log_batch(log_lines)
            self._display_dtc_table(dtc_records)
            self._save_dtc_excel(dtc_records)
        except Exception as e:
            self._diag_on_socket_error(e)
            self.append_log_color(f"❌ DTC 读取异常: {e}", "#FF5252")
            import traceback
            self.append_log_color(traceback.format_exc(), "#FF5252")

    def _flpoda_clear_dtc(self):
        client = self.flpoda_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ FLPODA 未连接", "#FF5252")
            return
        try:
            cmd_14 = bytes([0x14, 0xFF, 0xFF, 0xFF])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{FLPODA_PHYSICAL_ADDR:04X} 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()
            resp = self._flpoda_send_uds_raw(cmd_14, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x54:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FLPODA_RESPONSE_ADDR:04X} {formatted} ✅ DTC 清除成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FLPODA_RESPONSE_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FLPODA_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 清除超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ DTC 清除异常: {e}", "#FF5252")

    def _flpoda_reset_ecu(self):
        client = self.flpoda_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ FLPODA 未连接", "#FF5252")
            return
        try:
            cmd_11_01 = bytes([0x11, 0x01])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{FLPODA_PHYSICAL_ADDR:04X} 11 01", "#64B5F6")
            QApplication.processEvents()
            resp = self._flpoda_send_uds_raw(cmd_11_01, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x51:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FLPODA_RESPONSE_ADDR:04X} {formatted} ✅ FLPODA Reset 成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FLPODA_RESPONSE_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FLPODA_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ Reset 超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ Reset 失败：{str(e)}", "#FF5252")

    def _fwm_send_uds_raw(self, data: bytes, timeout: float = 2.0):
        client = self.fwm_doip_client
        if not client or not client.routing_activated:
            return None
        try:
            resp = client.send_diagnostic(data, target_addr=FWM_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ FWM UDS 发送失败：{e}", "#FF9800")
            return None

    def _fwm_send_uds_cmd(self, cmd_text: str):
        import re, time
        client = self.fwm_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ FWM 未连接", "#FF5252")
            return

        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            if '#' in line: line = line.split('#')[0].strip()
            if '//' in line: line = line.split('//')[0].strip()
            if not line: continue

            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"💤 Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue

            hex_str = line.replace(' ', '').replace('\t', '')
            try:
                uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue

            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{FWM_PHYSICAL_ADDR:04X} {formatted_tx}", "#64B5F6")
            QApplication.processEvents()

            resp = self._fwm_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    if nrc == 0x78:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{FWM_RESPONSE_ADDR:04X} {formatted_rx} ⏳ {nrc_desc}", "#FF9800")
                    else:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{FWM_RESPONSE_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FWM_RESPONSE_ADDR:04X} {formatted_rx}", "#81C784")

                # FWM 自动安全访问
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        key = sa_calc.calc_key(seed_hex, '0000105D')
                        client = self.fwm_doip_client
                        if client and client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key
                            formatted_tx2 = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x{FWM_PHYSICAL_ADDR:04X} {formatted_tx2}  🔑 自动发送 KEY", "#64B5F6")
                            QApplication.processEvents()
                            resp2 = None
                            for retry in range(10):
                                resp2 = self._fwm_send_uds_raw(cmd_27_02, timeout=2.0)
                                if resp2:
                                    if len(resp2) >= 3 and resp2[0] == 0x7F and resp2[2] == 0x78:
                                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{FWM_RESPONSE_ADDR:04X} 7F 27 78 ⏳ Response Pending，等待中...", "#FF9800")
                                        time.sleep(0.5)
                                        continue
                                    break
                                time.sleep(0.3)
                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FWM_RESPONSE_ADDR:04X} {f2} ✅ 安全认证成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FWM_RESPONSE_ADDR:04X} {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FWM_RESPONSE_ADDR:04X} {f2} ❌ 安全认证失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    def _fwm_read_dtc(self):
        client = self.fwm_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ FWM 未连接", "#FF5252")
            return
        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{FWM_PHYSICAL_ADDR:04X} 19 02 2C", "#64B5F6")
            QApplication.processEvents()
            resp = self._fwm_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=2.0)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return
            formatted = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x{FWM_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            QApplication.processEvents()
            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color("  ✅ 无有效 DTC", "#4CAF50")
                return
            self.append_log_color(f"  📋 发现 {len(dtc_records)} 条 DTC", "#FF9800")
            log_lines = []
            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']
                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{FWM_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_04)}")
                resp_04 = self._fwm_send_uds_raw(cmd_04, timeout=1.5)
                if resp_04:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{FWM_RESPONSE_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_04)}")
                    dtc['snapshot_raw'] = resp_04
                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{FWM_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_06)}")
                resp_06 = self._fwm_send_uds_raw(cmd_06, timeout=1.5)
                if resp_06:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{FWM_RESPONSE_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_06)}")
                    dtc['extended_raw'] = resp_06
            self.append_log_batch(log_lines)
            self._display_dtc_table(dtc_records)
            self._save_dtc_excel(dtc_records)
        except Exception as e:
            self._diag_on_socket_error(e)
            self.append_log_color(f"❌ DTC 读取异常: {e}", "#FF5252")
            import traceback
            self.append_log_color(traceback.format_exc(), "#FF5252")

    def _fwm_clear_dtc(self):
        client = self.fwm_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ FWM 未连接", "#FF5252")
            return
        try:
            cmd_14 = bytes([0x14, 0xFF, 0xFF, 0xFF])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{FWM_PHYSICAL_ADDR:04X} 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()
            resp = self._fwm_send_uds_raw(cmd_14, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x54:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FWM_RESPONSE_ADDR:04X} {formatted} ✅ DTC 清除成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FWM_RESPONSE_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FWM_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 清除超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ DTC 清除异常: {e}", "#FF5252")

    def _fwm_reset_ecu(self):
        client = self.fwm_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ FWM 未连接", "#FF5252")
            return
        try:
            cmd_11_01 = bytes([0x11, 0x01])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{FWM_PHYSICAL_ADDR:04X} 11 01", "#64B5F6")
            QApplication.processEvents()
            resp = self._fwm_send_uds_raw(cmd_11_01, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x51:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FWM_RESPONSE_ADDR:04X} {formatted} ✅ FWM Reset 成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FWM_RESPONSE_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{FWM_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ Reset 超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ Reset 失败：{str(e)}", "#FF5252")

    def _eps_send_uds_raw(self, data: bytes, timeout: float = 2.0, log_all: bool = False):
        """发送 UDS 指令到 EPS 并返回原始响应 (bytes), 失败返回 None

        Args:
            data: UDS 请求数据
            timeout: 超时时间（秒）
            log_all: 是否记录所有响应（包括 0x78）
        """
        client = self.eps_doip_client
        if not client or not client.routing_activated:
            return None
        try:
            # 使用物理地址 0x0721
            if log_all:
                # 先发送请求
                diag_target = EPS_PHYSICAL_ADDR
                payload = struct.pack('!HH', client.source_addr, diag_target)
                payload += data
                client._send_doip(DOIP_TYPE_DIAG_MSG, payload)

                # 接收所有响应（包括 0x78）
                msgs = client._recv_all_doip(timeout)
                all_responses = []
                final_resp = None
                for msg in msgs:
                    if msg['type'] == DOIP_TYPE_DIAG_MSG and len(msg['payload']) >= 4:
                        uds = msg['payload'][4:]
                        all_responses.append(uds)
                        # 记录所有响应
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x0721 {' '.join(f'{b:02X}' for b in uds)}", "#81C784")
                        # 如果不是 0x78，保存为最终响应
                        if not (len(uds) >= 3 and uds[0] == 0x7F and uds[2] == 0x78):
                            final_resp = uds
                # 返回最终响应（非 0x78）
                return final_resp if final_resp else (all_responses[0] if all_responses else None)
            else:
                resp = client.send_diagnostic(data, target_addr=EPS_PHYSICAL_ADDR, timeout=timeout)
                return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ EPS UDS 发送失败：{e}", "#FF9800")
            return None

    def _eps_read_dtc(self):
        """通过 DoIP 读取 EPS 的 DTC 故障码（异步非阻塞）"""
        client = self.eps_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ EPS 未连接", "#FF5252")
            return

        # 使用 QTimer 异步执行，避免阻塞 UI
        QTimer.singleShot(10, lambda: self._eps_read_dtc_step1())

    def _eps_read_dtc_step1(self):
        """Step 1: 读取 DTC 列表 (19 02 2C) - 快速响应，不等待"""
        try:
            self.append_log_color(f"{self._diag_timestamp()} tx 0x0721 19 02 2C", "#64B5F6")
            QApplication.processEvents()

            # 使用 2 秒超时，确保收到 0x78 后的最终响应，并记录所有响应
            resp = self._eps_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=2.0, log_all=True)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                QApplication.processEvents()
                return

            # resp 已经是最终响应（59 02 FF），日志中已显示所有响应（包括 0x78）
            QApplication.processEvents()
            QApplication.processEvents()

            # 处理 NRC 0x78 - 立即视为无 DTC
            if len(resp) >= 3 and resp[0] == 0x7F and resp[2] == 0x78:
                self.append_log_color("ℹ️ EPS 返回 NRC 0x78，视为无 DTC", "#2196F3")
                QApplication.processEvents()
                self._display_dtc_table([])
            else:
                # 正常响应 59 02 ...
                dtc_records = self._parse_dtc_02_response(resp)
                QTimer.singleShot(10, lambda: self._eps_read_dtc_step2(dtc_records))
        except Exception as e:
            self.append_log_color(f"❌ DTC 读取异常：{e}", "#FF5252")

    def _eps_read_dtc_step2(self, dtc_records):
        """Step 2: 显示结果并查询详细信息"""
        try:
            self.append_log_color(f"  发现 {len(dtc_records)} 个 DTC", "#FF9800")
            QApplication.processEvents()

            # 显示表格
            self._display_dtc_table(dtc_records)
            QApplication.processEvents()

            # 如果没有 DTC，到此为止
            if not dtc_records:
                return

            # 对每个 DTC 查询详细快照和扩展数据
            for i, dtc in enumerate(dtc_records):
                QTimer.singleShot(i * 200, lambda d=dtc: self._eps_read_dtc_detail(d))
        except Exception as e:
            self.append_log_color(f"❌ DTC 读取异常：{e}", "#FF5252")

    def _eps_read_dtc_detail(self, dtc):
        """Step 3: 读取单个 DTC 的详细信息"""
        try:
            d = dtc['raw']

            # 19 04 - 快照数据
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x0721 19 04 {d[0]:02X} {d[1]:02X} {d[2]:02X} 01", "#64B5F6")
            QApplication.processEvents()

            resp_04 = self._eps_send_uds_raw(bytes([0x19, 0x04, d[0], d[1], d[2], 0x01]), timeout=0.3)
            if resp_04:
                f = ' '.join(f'{b:02X}' for b in resp_04)
                self.append_log_color(f"{self._diag_timestamp()} rx 0x0721 {f}", "#81C784")
                dtc['snapshot_raw'] = resp_04
            QApplication.processEvents()

            # 19 06 - 扩展数据
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x0721 19 06 {d[0]:02X} {d[1]:02X} {d[2]:02X} 01", "#64B5F6")
            QApplication.processEvents()

            resp_06 = self._eps_send_uds_raw(bytes([0x19, 0x06, d[0], d[1], d[2], 0x01]), timeout=0.3)
            if resp_06:
                f = ' '.join(f'{b:02X}' for b in resp_06)
                self.append_log_color(f"{self._diag_timestamp()} rx 0x0721 {f}", "#81C784")
                dtc['extended_raw'] = resp_06
            QApplication.processEvents()

            # 刷新表格显示
            self._display_dtc_table([dtc])
        except Exception as e:
            self.append_log_color(f"❌ DTC 详情读取异常：{e}", "#FF5252")

    def _eps_clear_dtc(self):
        """通过 DoIP 清除 EPS 的 DTC 故障码"""
        client = self.eps_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ EPS 未连接", "#FF5252")
            return

        try:
            # 14 FF FF FF - 清除所有 DTC
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x0721 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()

            resp = self._eps_send_uds_raw(bytes([0x14, 0xFF, 0xFF, 0xFF]))
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 清除 DTC 超时", "#FF5252")
                return

            formatted = ' '.join(f'{b:02X}' for b in resp)
            if resp[0] == 0x54:
                self.append_log_color(f"{self._diag_timestamp()} rx 0x0721 {formatted} ✅ 清除成功", "#4CAF50")
            elif resp[0] == 0x7F:
                nrc = resp[2] if len(resp) > 2 else 0
                nrc_desc = self._diag_nrc_desc(nrc)
                self.append_log_color(f"{self._diag_timestamp()} rx 0x0721 {formatted} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} rx 0x0721 {formatted}", "#81C784")

        except Exception as e:
            self.append_log_color(f"❌ 清除 DTC 异常：{e}", "#FF5252")


    def _lhzcu_send_uds_raw(self, data: bytes, timeout: float = 2.0):
        """发送 UDS 指令到 LHZCU (通过 ICB 网关转发)"""
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            # 尝试自动重连 ICB
            self.append_log_color("⚠ ICB 连接断开，尝试自动重连...", "#FF9800")
            try:
                self._connect_doip_async()
                if client and client.routing_activated:
                    self.append_log_color("✅ ICB 重连成功", "#4CAF50")
                else:
                    self.append_log_color("❌ ICB 重连失败", "#FF5252")
                    return None
            except Exception as e:
                self.append_log_color(f"❌ ICB 重连异常：{e}", "#FF5252")
                return None
        try:
            # LHZCU 通过 ICB 网关转发，使用物理地址 0x15B0
            return client.send_diagnostic(data, target_addr=LHZCU_PHYSICAL_ADDR, timeout=timeout)
        except Exception as e:
            self.append_log_color(f"⚠ LHZCU 发送异常：{e}，尝试重连...", "#FF9800")
            try:
                self._connect_doip_async()
                if client and client.routing_activated:
                    self.append_log_color("✅ ICB 重连成功，重试发送", "#4CAF50")
                    return client.send_diagnostic(data, target_addr=LHZCU_PHYSICAL_ADDR, timeout=timeout)
            except Exception:
                return None
            return None

    def _lhzcu_read_dtc(self):
        """通过 DoIP 读取 LHZCU 的 DTC 故障码 (通过 ICB 转发)"""
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("ICB 未连接，无法转发 LHZCU 诊断", "#FF5252")
            return

        try:
            # Step 1: 19 02 2C - 读取状态信息中的有效 DTC
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x15B0 19 02 2C", "#64B5F6")

            resp = client.send_diagnostic(bytes([0x19, 0x02, 0x2C]), target_addr=LHZCU_PHYSICAL_ADDR)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} DTC 列表超时", "#FF5252")
                return

            self.append_log_color(f"{self._diag_timestamp()} rx 0x15B0 {' '.join(f'{b:02X}' for b in resp)}", "#81C784")

            # 解析 DTC 列表
            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color("  无有效 DTC", "#4CAF50")
                return

            self.append_log_color(f"  发现 {len(dtc_records)} 个 DTC", "#FF9800")

            # Step 2: 对每个 DTC 查询详细信息 (19 04) 和扩展信息 (19 06)
            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']

                # 19 04 - 快照数据
                ts = self._diag_timestamp()
                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                self.append_log_color(f"{ts} tx 0x15B0 {' '.join(f'{b:02X}' for b in cmd_04)}", "#64B5F6")
                resp_04 = client.send_diagnostic(cmd_04, target_addr=LHZCU_PHYSICAL_ADDR, timeout=1.5)
                if resp_04:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x15B0 {' '.join(f'{b:02X}' for b in resp_04)}", "#81C784")
                    dtc['snapshot_raw'] = resp_04

                # 19 06 - 扩展数据
                ts = self._diag_timestamp()
                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                self.append_log_color(f"{ts} tx 0x15B0 {' '.join(f'{b:02X}' for b in cmd_06)}", "#64B5F6")
                resp_06 = client.send_diagnostic(cmd_06, target_addr=LHZCU_PHYSICAL_ADDR, timeout=1.5)
                if resp_06:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x15B0 {' '.join(f'{b:02X}' for b in resp_06)}", "#81C784")
                    dtc['extended_raw'] = resp_06

            # Step 3: 显示结果
            self._display_dtc_table(dtc_records)

            # Step 4: 保存到 Excel
            self._save_dtc_excel(dtc_records)

        except Exception as e:
            self._diag_on_socket_error(e)

    def _lhzcu_clear_dtc(self):
        """通过 DoIP 清除 LHZCU 的 DTC 故障码"""
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("ICB 未连接，无法转发 LHZCU 诊断", "#FF5252")
            return

        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x15B0 14 FF FF FF", "#64B5F6")

            resp = client.send_diagnostic(bytes([0x14, 0xFF, 0xFF, 0xFF]), target_addr=LHZCU_PHYSICAL_ADDR)
            if resp:
                self.append_log_color(f"{self._diag_timestamp()} rx 0x15B0 {' '.join(f'{b:02X}' for b in resp)}", "#81C784")
                if resp[0] == 0x54:
                    self.append_log_color("  DTC 清除成功", "#4CAF50")
                else:
                    self.append_log_color("  DTC 清除失败", "#FF9800")
            else:
                self.append_log_color("  无响应", "#FF5252")
        except Exception as e:
            self._diag_on_socket_error(e)

    def _rhzcu_send_uds_raw(self, data: bytes, timeout: float = 2.0):
        """发送 UDS 指令到 RHZCU (通过 ICB 网关转发)"""
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            # 尝试自动重连 ICB
            self.append_log_color("⚠ ICB 连接断开，尝试自动重连...", "#FF9800")
            try:
                self._connect_doip_async()
                if client and client.routing_activated:
                    self.append_log_color("✅ ICB 重连成功", "#4CAF50")
                else:
                    self.append_log_color("❌ ICB 重连失败", "#FF5252")
                    return None
            except Exception as e:
                self.append_log_color(f"❌ ICB 重连异常：{e}", "#FF5252")
                return None
        try:
            # RHZCU 通过 ICB 网关转发，使用物理地址 0x15B1
            return client.send_diagnostic(data, target_addr=RHZCU_PHYSICAL_ADDR, timeout=timeout)
        except Exception as e:
            self.append_log_color(f"⚠ RHZCU 发送异常：{e}，尝试重连...", "#FF9800")
            try:
                self._connect_doip_async()
                if client and client.routing_activated:
                    self.append_log_color("✅ ICB 重连成功，重试发送", "#4CAF50")
                    return client.send_diagnostic(data, target_addr=RHZCU_PHYSICAL_ADDR, timeout=timeout)
            except Exception:
                return None
            return None

    def _rhzcu_read_dtc(self):
        """通过 DoIP 读取 RHZCU 的 DTC 故障码 (通过 ICB 转发)"""
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("ICB 未连接，无法转发 RHZCU 诊断", "#FF5252")
            return

        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x15B1 19 02 2C", "#64B5F6")

            resp = client.send_diagnostic(bytes([0x19, 0x02, 0x2C]), target_addr=RHZCU_PHYSICAL_ADDR)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} DTC 列表超时", "#FF5252")
                return

            self.append_log_color(f"{self._diag_timestamp()} rx 0x15B1 {' '.join(f'{b:02X}' for b in resp)}", "#81C784")

            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color("  无有效 DTC", "#4CAF50")
                return

            self.append_log_color(f"  发现 {len(dtc_records)} 个 DTC", "#FF9800")

            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']

                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                self.append_log_color(f"{self._diag_timestamp()} tx 0x15B1 {' '.join(f'{b:02X}' for b in cmd_04)}", "#64B5F6")
                resp_04 = client.send_diagnostic(cmd_04, target_addr=RHZCU_PHYSICAL_ADDR, timeout=1.5)
                if resp_04:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x15B1 {' '.join(f'{b:02X}' for b in resp_04)}", "#81C784")
                    dtc['snapshot_raw'] = resp_04

                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                self.append_log_color(f"{self._diag_timestamp()} tx 0x15B1 {' '.join(f'{b:02X}' for b in cmd_06)}", "#64B5F6")
                resp_06 = client.send_diagnostic(cmd_06, target_addr=RHZCU_PHYSICAL_ADDR, timeout=1.5)
                if resp_06:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x15B1 {' '.join(f'{b:02X}' for b in resp_06)}", "#81C784")
                    dtc['extended_raw'] = resp_06

            self._display_dtc_table(dtc_records)
            self._save_dtc_excel(dtc_records)

        except Exception as e:
            self._diag_on_socket_error(e)

    def _rhzcu_clear_dtc(self):
        """通过 DoIP 清除 RHZCU 的 DTC 故障码"""
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("ICB 未连接，无法转发 RHZCU 诊断", "#FF5252")
            return

        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x15B1 14 FF FF FF", "#64B5F6")

            resp = client.send_diagnostic(bytes([0x14, 0xFF, 0xFF, 0xFF]), target_addr=RHZCU_PHYSICAL_ADDR)
            if resp:
                self.append_log_color(f"{self._diag_timestamp()} rx 0x15B1 {' '.join(f'{b:02X}' for b in resp)}", "#81C784")
                if resp[0] == 0x54:
                    self.append_log_color("  DTC 清除成功", "#4CAF50")
        except Exception as e:
            self._diag_on_socket_error(e)

    def _rzcu_read_dtc(self):
        """通过 DoIP 读取 RZCU 的 DTC 故障码 (通过 ICB 转发)"""
        # RZCU 物理地址：0x17E3 (用户确认)

        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("ICB 未连接，无法转发 RZCU 诊断", "#FF5252")
            return

        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x17E3 19 02 2C", "#64B5F6")

            resp = client.send_diagnostic(bytes([0x19, 0x02, 0x2C]), target_addr=RZCU_PHYSICAL_ADDR)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} DTC 列表超时", "#FF5252")
                return

            self.append_log_color(f"{self._diag_timestamp()} rx 0x17E3 {' '.join(f'{b:02X}' for b in resp)}", "#81C784")

            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color("  无有效 DTC", "#4CAF50")
                return

            self.append_log_color(f"  发现 {len(dtc_records)} 个 DTC", "#FF9800")

            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']

                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                self.append_log_color(f"{self._diag_timestamp()} tx 0x15B2 {' '.join(f'{b:02X}' for b in cmd_04)}", "#64B5F6")
                resp_04 = client.send_diagnostic(cmd_04, target_addr=RZCU_PHYSICAL_ADDR, timeout=1.5)
                if resp_04:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x17E3 {' '.join(f'{b:02X}' for b in resp_04)}", "#81C784")
                    dtc['snapshot_raw'] = resp_04

                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                self.append_log_color(f"{self._diag_timestamp()} tx 0x15B2 {' '.join(f'{b:02X}' for b in cmd_06)}", "#64B5F6")
                resp_06 = client.send_diagnostic(cmd_06, target_addr=RZCU_PHYSICAL_ADDR, timeout=1.5)
                if resp_06:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x17E3 {' '.join(f'{b:02X}' for b in resp_06)}", "#81C784")
                    dtc['extended_raw'] = resp_06

            self._display_dtc_table(dtc_records)
            self._save_dtc_excel(dtc_records)

        except Exception as e:
            self._diag_on_socket_error(e)

    def _rzcu_clear_dtc(self):
        """通过 DoIP 清除 RZCU 的 DTC 故障码"""
        # RZCU 物理地址：0x17E3 (用户确认)

        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("ICB 未连接，无法转发 RZCU 诊断", "#FF5252")
            return

        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x17E3 14 FF FF FF", "#64B5F6")

            resp = client.send_diagnostic(bytes([0x14, 0xFF, 0xFF, 0xFF]), target_addr=RZCU_PHYSICAL_ADDR)
            if resp:
                self.append_log_color(f"{self._diag_timestamp()} rx 0x17E3 {' '.join(f'{b:02X}' for b in resp)}", "#81C784")
                if resp[0] == 0x54:
                    self.append_log_color("  DTC 清除成功", "#4CAF50")
        except Exception as e:
            self._diag_on_socket_error(e)

    def _lhzcu_send_uds_cmd(self, cmd_text: str):
        """通过 DoIP 发送 UDS 诊断指令到 LHZCU (通过 ICB 网关转发)"""
        import re
        import time

        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ ICB 未连接，无法转发 LHZCU 诊断", "#FF5252")
            return

        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            if '#' in line:
                line = line.split('#')[0].strip()
            if '//' in line:
                line = line.split('//')[0].strip()
            if not line:
                continue

            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"⏳ Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                continue

            hex_str = line.replace(' ', '').replace('\t', '')

            try:
                uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue

            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x15B0 {formatted_tx}", "#64B5F6")
            QApplication.processEvents()

            resp = self._lhzcu_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x15B0 {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x15B0 {formatted_rx}", "#81C784")

                # LHZCU 自动安全访问：收到 67 01 + seed 后，自动计算 key 并发送 27 02
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()

                    # 检查种子是否有效 (不应该和 P2* 参数一样)
                    if seed_hex in ['003201F4', '005001F4', '00000000']:
                        self.append_log_color(f"⚠ 种子值异常：{seed_hex}，可能是 ECU 未正确响应 27 01", "#FF9800")
                        self.append_log_color(f"💡 尝试等待 100ms 后重新发送 27 01...", "#FF9800")
                        time.sleep(0.1)
                        QApplication.processEvents()
                        # 重新发送 27 01
                        self.append_log_color(f"{self._diag_timestamp()} tx 0x15B0 27 01 (retry)", "#64B5F6")
                        resp_retry = self._lhzcu_send_uds_raw(bytes([0x27, 0x01]))
                        if resp_retry and len(resp_retry) >= 6 and resp_retry[0] == 0x67 and resp_retry[1] == 0x01:
                            seed = resp_retry[2:6]
                            seed_hex = seed.hex().upper()
                            self.append_log_color(f"{self._diag_timestamp()} rx 0x15B0 67 01 {seed_hex} (retry)", "#81C784")
                        else:
                            self.append_log_color(f"❌ 重试 27 01 失败", "#FF5252")
                            return

                    try:
                        # LHZCU 算法号：00001010 (UAES 平台)
                        key = sa_calc.calc_key(seed_hex, f'{LHZCU_SECURITY_ALGO:08X}')
                        cmd_27_02 = bytes([0x27, 0x02]) + key
                        formatted_tx2 = ' '.join(f'{b:02X}' for b in cmd_27_02)
                        self.append_log_color(f"{self._diag_timestamp()} tx 0x15B0 {formatted_tx2}  🔑 自动发送 KEY", "#4CAF50")
                        resp2 = self._lhzcu_send_uds_raw(cmd_27_02)
                        if resp2:
                            f2 = ' '.join(f'{b:02X}' for b in resp2)
                            if resp2[0] == 0x67:
                                self.append_log_color(f"{self._diag_timestamp()} rx 0x15B0 {f2} ✅ 安全认证成功", "#4CAF50")
                            elif resp2[0] == 0x7F:
                                nrc2 = resp2[2] if len(resp2) > 2 else 0
                                nrc_desc2 = self._diag_nrc_desc(nrc2)
                                self.append_log_color(f"{self._diag_timestamp()} rx 0x15B0 {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X} {nrc_desc2}", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

            QApplication.processEvents()
            time.sleep(0.05)

    def _rhzcu_send_uds_cmd(self, cmd_text: str):
        """通过 DoIP 发送 UDS 诊断指令到 RHZCU (通过 ICB 网关转发)"""
        import re
        import time

        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ ICB 未连接，无法转发 RHZCU 诊断", "#FF5252")
            return

        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            if '#' in line:
                line = line.split('#')[0].strip()
            if '//' in line:
                line = line.split('//')[0].strip()
            if not line:
                continue

            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"⏳ Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                continue

            hex_str = line.replace(' ', '').replace('\t', '')

            try:
                uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue

            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x15B1 {formatted_tx}", "#64B5F6")
            QApplication.processEvents()

            resp = self._rhzcu_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x15B1 {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x15B1 {formatted_rx}", "#81C784")

                # RHZCU 自动安全访问：收到 67 01 + seed 后，自动计算 key 并发送 27 02
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()

                    # 检查种子是否有效
                    if seed_hex in ['003201F4', '005001F4', '00000000']:
                        self.append_log_color(f"⚠ 种子值异常：{seed_hex}，可能是 ECU 未正确响应 27 01", "#FF9800")
                        self.append_log_color(f"💡 尝试等待 100ms 后重新发送 27 01...", "#FF9800")
                        time.sleep(0.1)
                        QApplication.processEvents()
                        self.append_log_color(f"{self._diag_timestamp()} tx 0x15B1 27 01 (retry)", "#64B5F6")
                        resp_retry = self._rhzcu_send_uds_raw(bytes([0x27, 0x01]))
                        if resp_retry and len(resp_retry) >= 6 and resp_retry[0] == 0x67 and resp_retry[1] == 0x01:
                            seed = resp_retry[2:6]
                            seed_hex = seed.hex().upper()
                            self.append_log_color(f"{self._diag_timestamp()} rx 0x15B1 67 01 {seed_hex} (retry)", "#81C784")
                        else:
                            self.append_log_color(f"❌ 重试 27 01 失败", "#FF5252")
                            return

                    try:
                        key = sa_calc.calc_key(seed_hex, f'{RHZCU_SECURITY_ALGO:08X}')
                        cmd_27_02 = bytes([0x27, 0x02]) + key
                        formatted_tx2 = ' '.join(f'{b:02X}' for b in cmd_27_02)
                        self.append_log_color(f"{self._diag_timestamp()} tx 0x15B1 {formatted_tx2}  🔑 自动发送 KEY", "#4CAF50")
                        resp2 = self._rhzcu_send_uds_raw(cmd_27_02)
                        if resp2:
                            f2 = ' '.join(f'{b:02X}' for b in resp2)
                            if resp2[0] == 0x67:
                                self.append_log_color(f"{self._diag_timestamp()} rx 0x15B1 {f2} ✅ 安全认证成功", "#4CAF50")
                            elif resp2[0] == 0x7F:
                                nrc2 = resp2[2] if len(resp2) > 2 else 0
                                nrc_desc2 = self._diag_nrc_desc(nrc2)
                                self.append_log_color(f"{self._diag_timestamp()} rx 0x15B1 {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X} {nrc_desc2}", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

            QApplication.processEvents()
            time.sleep(0.05)

    def _rzcu_send_uds_cmd(self, cmd_text: str):
        """通过 DoIP 发送 UDS 诊断指令到 RZCU (通过 ICB 网关转发)"""
        import re
        import time

        # RZCU 物理地址：0x17E3 (用户确认)

        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ ICB 未连接，无法转发 RZCU 诊断", "#FF5252")
            return

        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            if '#' in line:
                line = line.split('#')[0].strip()
            if '//' in line:
                line = line.split('//')[0].strip()
            if not line:
                continue

            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"⏳ Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                continue

            hex_str = line.replace(' ', '').replace('\t', '')

            try:
                uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue

            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x17E3 {formatted_tx}", "#64B5F6")
            QApplication.processEvents()

            try:
                resp = client.send_diagnostic(uds_data, target_addr=RZCU_PHYSICAL_ADDR)
            except Exception as e:
                self.append_log_color(f"⚠ RZCU 发送异常：{e}，尝试重连...", "#FF9800")
                try:
                    self._connect_doip_async()
                    if client and client.routing_activated:
                        self.append_log_color("✅ ICB 重连成功，重试发送", "#4CAF50")
                        resp = client.send_diagnostic(uds_data, target_addr=RZCU_PHYSICAL_ADDR)
                    else:
                        self.append_log_color("❌ ICB 重连失败", "#FF5252")
                        resp = None
                except Exception:
                    resp = None
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x17E3 {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x17E3 {formatted_rx}", "#81C784")

                # RZCU 自动安全访问：收到 67 01 + seed 后，自动计算 key 并发送 27 02
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()

                    # 检查种子是否有效
                    if seed_hex in ['003201F4', '005001F4', '00000000']:
                        self.append_log_color(f"⚠ 种子值异常：{seed_hex}，可能是 ECU 未正确响应 27 01", "#FF9800")
                        self.append_log_color(f"💡 尝试等待 100ms 后重新发送 27 01...", "#FF9800")
                        time.sleep(0.1)
                        QApplication.processEvents()
                        self.append_log_color(f"{self._diag_timestamp()} tx 0x17E3 27 01 (retry)", "#64B5F6")
                        resp_retry = client.send_diagnostic(bytes([0x27, 0x01]), target_addr=RZCU_PHYSICAL_ADDR)
                        if resp_retry and len(resp_retry) >= 6 and resp_retry[0] == 0x67 and resp_retry[1] == 0x01:
                            seed = resp_retry[2:6]
                            seed_hex = seed.hex().upper()
                            self.append_log_color(f"{self._diag_timestamp()} rx 0x17E3 67 01 {seed_hex} (retry)", "#81C784")
                        else:
                            self.append_log_color(f"❌ 重试 27 01 失败", "#FF5252")
                            return

                    try:
                        key = sa_calc.calc_key(seed_hex, f'{RZCU_SECURITY_ALGO:08X}')
                        cmd_27_02 = bytes([0x27, 0x02]) + key
                        formatted_tx2 = ' '.join(f'{b:02X}' for b in cmd_27_02)
                        self.append_log_color(f"{self._diag_timestamp()} tx 0x17E3 {formatted_tx2}  🔑 自动发送 KEY", "#4CAF50")
                        resp2 = client.send_diagnostic(cmd_27_02, target_addr=RZCU_PHYSICAL_ADDR)
                        if resp2:
                            f2 = ' '.join(f'{b:02X}' for b in resp2)
                            if resp2[0] == 0x67:
                                self.append_log_color(f"{self._diag_timestamp()} rx 0x17E3 {f2} ✅ 安全认证成功", "#4CAF50")
                            elif resp2[0] == 0x7F:
                                nrc2 = resp2[2] if len(resp2) > 2 else 0
                                nrc_desc2 = self._diag_nrc_desc(nrc2)
                                self.append_log_color(f"{self._diag_timestamp()} rx 0x17E3 {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X} {nrc_desc2}", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

            QApplication.processEvents()
            time.sleep(0.05)


    def _eps_reset_ecu(self):
        """通过 DoIP 复位 EPS"""
        client = self.eps_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ EPS 未连接", "#FF5252")
            return

        try:
            # 11 01 - 硬复位
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x0721 11 01", "#64B5F6")
            QApplication.processEvents()

            resp = self._eps_send_uds_raw(bytes([0x11, 0x01]))
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 复位超时", "#FF5252")
                return

            formatted = ' '.join(f'{b:02X}' for b in resp)
            if resp[0] == 0x51:
                self.append_log_color(f"{self._diag_timestamp()} rx 0x0721 {formatted} ✅ 复位成功", "#4CAF50")
            elif resp[0] == 0x7F:
                nrc = resp[2] if len(resp) > 2 else 0
                nrc_desc = self._diag_nrc_desc(nrc)
                self.append_log_color(f"{self._diag_timestamp()} rx 0x0721 {formatted} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} rx 0x0721 {formatted}", "#81C784")

        except Exception as e:
            self.append_log_color(f"❌ 复位异常：{e}", "#FF5252")

    def _eps_send_uds_cmd(self, cmd_text: str):
        """通过 DoIP 发送 UDS 诊断指令到 EPS"""
        import re
        import time

        client = self.eps_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ EPS 未连接", "#FF5252")
            return

        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            # 去除注释
            if '#' in line:
                line = line.split('#')[0].strip()
            if '//' in line:
                line = line.split('//')[0].strip()
            if not line:
                continue

            # 检查是否是 sleep 命令
            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"⏳ Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue

            # 去除空格
            hex_str = line.replace(' ', '').replace('\t', '')

            try:
                uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue

            # 格式化 tx 日志
            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x0721 {formatted_tx}", "#64B5F6")
            QApplication.processEvents()

            # 发送并接收响应
            resp = self._eps_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x0721 {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x0721 {formatted_rx}", "#81C784")

                # ICB 自动安全访问：需要在默认会话下进行
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        # EPS 算法号：00001035
                        key = sa_calc.calc_key(seed_hex, '00001035')
                        # 发送 27 02 + key
                        client = self.eps_doip_client
                        if client and client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key
                            formatted_tx2 = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x0721 {formatted_tx2}", "#64B5F6")
                            resp2 = self._eps_send_uds_raw(cmd_27_02)
                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x0721 {f2} ✅ 安全访问成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    nrc_desc2 = self._diag_nrc_desc(nrc2)
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x0721 {f2} ❌ 安全访问失败 NRC 0x{nrc2:02X} {nrc_desc2}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x0721 {f2} ❌ 安全访问失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")

            # LHZCU 自动安全访问 (通过 ICB 转发)
            if self.selected_ecu_key == "lhzcu" and len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                seed = resp[2:6]
                seed_hex = seed.hex().upper()
                try:
                    # LHZCU 算法号：00001010 (UAES 平台)
                    key = sa_calc.calc_key(seed_hex, f'{LHZCU_SECURITY_ALGO:08X}')
                    cmd_27_02 = bytes([0x27, 0x02]) + key
                    formatted_tx2 = ' '.join(f'{b:02X}' for b in cmd_27_02)
                    self.append_log_color(f"{self._diag_timestamp()} tx 0x15B0 {formatted_tx2}  🔑 自动发送 KEY", "#4CAF50")
                    resp2 = self._lhzcu_send_uds_raw(cmd_27_02)
                    if resp2:
                        f2 = ' '.join(f'{b:02X}' for b in resp2)
                        if resp2[0] == 0x67:
                            self.append_log_color(f"{self._diag_timestamp()} rx 0x15B0 {f2} ✅ 安全认证成功", "#4CAF50")
                        elif resp2[0] == 0x7F:
                            nrc2 = resp2[2] if len(resp2) > 2 else 0
                            nrc_desc2 = self._diag_nrc_desc(nrc2)
                            self.append_log_color(f"{self._diag_timestamp()} rx 0x15B0 {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X} {nrc_desc2}", "#FF5252")
                except Exception as se2:
                    self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se2}", "#FF5252")

            # RHZCU 自动安全访问 (通过 ICB 转发)
            if self.selected_ecu_key == "rhzcu" and len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                seed = resp[2:6]
                seed_hex = seed.hex().upper()
                try:
                    # RHZCU 算法号：00001010 (UAES 平台，与 LHZCU 共用)
                    key = sa_calc.calc_key(seed_hex, f'{RHZCU_SECURITY_ALGO:08X}')
                    cmd_27_02 = bytes([0x27, 0x02]) + key
                    formatted_tx2 = ' '.join(f'{b:02X}' for b in cmd_27_02)
                    self.append_log_color(f"{self._diag_timestamp()} tx 0x15B1 {formatted_tx2}  🔑 自动发送 KEY", "#4CAF50")
                    resp2 = self._rhzcu_send_uds_raw(cmd_27_02)
                    if resp2:
                        f2 = ' '.join(f'{b:02X}' for b in resp2)
                        if resp2[0] == 0x67:
                            self.append_log_color(f"{self._diag_timestamp()} rx 0x15B1 {f2} ✅ 安全认证成功", "#4CAF50")
                        elif resp2[0] == 0x7F:
                            nrc2 = resp2[2] if len(resp2) > 2 else 0
                            nrc_desc2 = self._diag_nrc_desc(nrc2)
                            self.append_log_color(f"{self._diag_timestamp()} rx 0x15B1 {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X} {nrc_desc2}", "#FF5252")
                except Exception as se2:
                    self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se2}", "#FF5252")

            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")


    # ==================== IAM 诊断功能 ====================
    def _connect_iam_doip(self):
        """连接 IAM DoIP (通过 ICB 网关转发)"""
        try:
            self.append_log_color("🔗 正在连接 IAM...", "#2196F3")
            client = DoIPClient(IAM_DOIP_IP, IAM_DOIP_PORT, routing_ta=IAM_ROUTING_TA)
            client.connect()
            client.routing_activate()
            self.iam_doip_client = client
            self.iam_doip_connected = True
            self.append_log_color("✅ IAM 连接成功", "#4CAF50")

            # 如果有待执行的诊断动作，立即执行
            if self._diag_pending_action == 'dtc_read':
                self._diag_pending_action = None
                self._iam_read_dtc()
            elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
                cmd = self._diag_pending_cmd
                self._diag_pending_action = None
                self._diag_pending_cmd = None
                self._iam_send_uds_cmd(cmd)
            return True
        except Exception as e:
            self.append_log_color(f"❌ IAM 连接失败：{e}", "#FF5252")
            return False

    # ==================== NFCSM 诊断功能 ====================
    def _connect_nfcsm_doip(self):
        """连接 NFCSM DoIP (通过 ICB 转发)"""
        try:
            self.append_log_color("🔗 正在连接 NFCSM...", "#2196F3")
            client = DoIPClient(NFCSM_DOIP_IP, NFCSM_DOIP_PORT, routing_ta=NFCSM_ROUTING_TA)
            client.connect()
            client.routing_activate()
            self.nfcsm_doip_client = client
            self.nfcsm_doip_connected = True
            self.append_log_color("✅ NFCSM 连接成功", "#4CAF50")

            if self._diag_pending_action == 'dtc_read':
                self._diag_pending_action = None
                self._nfcsm_read_dtc()
            elif self._diag_pending_action == 'dtc_clear':
                self._diag_pending_action = None
                self._nfcsm_clear_dtc()
            elif self._diag_pending_action == 'reset':
                self._diag_pending_action = None
                self._nfcsm_reset_ecu()
            elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
                cmd = self._diag_pending_cmd
                self._diag_pending_action = None
                self._diag_pending_cmd = None
                self._nfcsm_send_uds_cmd(cmd)
            return True
        except Exception as e:
            self.append_log_color(f"❌ NFCSM 连接失败：{e}", "#FF5252")
            return False

    def _nfcsm_send_uds_raw(self, data: bytes, timeout: float = 2.0):
        client = self.nfcsm_doip_client
        if not client or not client.routing_activated:
            return None
        try:
            resp = client.send_diagnostic(data, target_addr=NFCSM_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ NFCSM UDS 发送失败：{e}", "#FF9800")
            return None

    def _nfcsm_send_uds_cmd(self, cmd_text: str):
        import re, time
        client = self.nfcsm_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ NFCSM 未连接", "#FF5252")
            return

        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            if '#' in line: line = line.split('#')[0].strip()
            if '//' in line: line = line.split('//')[0].strip()
            if not line: continue

            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"💤 Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue

            hex_str = line.replace(' ', '').replace('\t', '')
            try:
                uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue

            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{NFCSM_PHYSICAL_ADDR:04X} {formatted_tx}", "#64B5F6")
            QApplication.processEvents()

            resp = self._nfcsm_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    if nrc == 0x78:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{NFCSM_RESPONSE_ADDR:04X} {formatted_rx} ⏳ {nrc_desc}", "#FF9800")
                    else:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{NFCSM_RESPONSE_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{NFCSM_RESPONSE_ADDR:04X} {formatted_rx}", "#81C784")

                # NFCSM 自动安全访问
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        key = sa_calc.calc_key(seed_hex, '00001051')
                        client = self.nfcsm_doip_client
                        if client and client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key
                            formatted_tx2 = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x{NFCSM_PHYSICAL_ADDR:04X} {formatted_tx2}  🔑 自动发送 KEY", "#64B5F6")
                            QApplication.processEvents()
                            resp2 = None
                            for retry in range(10):
                                resp2 = self._nfcsm_send_uds_raw(cmd_27_02, timeout=2.0)
                                if resp2:
                                    if len(resp2) >= 3 and resp2[0] == 0x7F and resp2[2] == 0x78:
                                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{NFCSM_RESPONSE_ADDR:04X} 7F 27 78 ⏳ Response Pending，等待中...", "#FF9800")
                                        time.sleep(0.5)
                                        continue
                                    break
                                time.sleep(0.3)
                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{NFCSM_RESPONSE_ADDR:04X} {f2} ✅ 安全认证成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{NFCSM_RESPONSE_ADDR:04X} {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{NFCSM_RESPONSE_ADDR:04X} {f2} ❌ 安全认证失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    def _nfcsm_read_dtc(self):
        client = self.nfcsm_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ NFCSM 未连接", "#FF5252")
            return
        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{NFCSM_PHYSICAL_ADDR:04X} 19 02 2C", "#64B5F6")
            QApplication.processEvents()
            resp = self._nfcsm_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=2.0)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return
            formatted = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x{NFCSM_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            QApplication.processEvents()
            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color("  ✅ 无有效 DTC", "#4CAF50")
                return
            self.append_log_color(f"  📋 发现 {len(dtc_records)} 条 DTC", "#FF9800")
            log_lines = []
            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']
                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{NFCSM_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_04)}")
                resp_04 = self._nfcsm_send_uds_raw(cmd_04, timeout=1.5)
                if resp_04:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{NFCSM_RESPONSE_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_04)}")
                    dtc['snapshot_raw'] = resp_04
                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{NFCSM_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_06)}")
                resp_06 = self._nfcsm_send_uds_raw(cmd_06, timeout=1.5)
                if resp_06:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{NFCSM_RESPONSE_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_06)}")
                    dtc['extended_raw'] = resp_06
            self.append_log_batch(log_lines)
            self._display_dtc_table(dtc_records)
            self._save_dtc_excel(dtc_records)
        except Exception as e:
            self._diag_on_socket_error(e)
            self.append_log_color(f"❌ DTC 读取异常: {e}", "#FF5252")
            import traceback
            self.append_log_color(traceback.format_exc(), "#FF5252")

    def _nfcsm_clear_dtc(self):
        client = self.nfcsm_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ NFCSM 未连接", "#FF5252")
            return
        try:
            cmd_14 = bytes([0x14, 0xFF, 0xFF, 0xFF])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{NFCSM_PHYSICAL_ADDR:04X} 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()
            resp = self._nfcsm_send_uds_raw(cmd_14, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x54:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{NFCSM_RESPONSE_ADDR:04X} {formatted} ✅ DTC 清除成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{NFCSM_RESPONSE_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{NFCSM_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 清除超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ DTC 清除异常: {e}", "#FF5252")

    def _nfcsm_reset_ecu(self):
        client = self.nfcsm_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ NFCSM 未连接", "#FF5252")
            return
        try:
            cmd_11_01 = bytes([0x11, 0x01])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{NFCSM_PHYSICAL_ADDR:04X} 11 01", "#64B5F6")
            QApplication.processEvents()
            resp = self._nfcsm_send_uds_raw(cmd_11_01, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x51:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{NFCSM_RESPONSE_ADDR:04X} {formatted} ✅ NFCSM Reset 成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{NFCSM_RESPONSE_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{NFCSM_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ Reset 超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ Reset 失败：{str(e)}", "#FF5252")

    # ==================== PMA 诊断功能 ====================
    def _connect_pma_doip(self):
        """连接 PMA DoIP (通过 ICB 转发)"""
        try:
            self.append_log_color("🔗 正在连接 PMA...", "#2196F3")
            client = DoIPClient(PMA_DOIP_IP, PMA_DOIP_PORT, routing_ta=PMA_ROUTING_TA)
            client.connect()
            client.routing_activate()
            self.pma_doip_client = client
            self.pma_doip_connected = True
            self.append_log_color("✅ PMA 连接成功", "#4CAF50")

            if self._diag_pending_action == 'dtc_read':
                self._diag_pending_action = None
                self._pma_read_dtc()
            elif self._diag_pending_action == 'dtc_clear':
                self._diag_pending_action = None
                self._pma_clear_dtc()
            elif self._diag_pending_action == 'reset':
                self._diag_pending_action = None
                self._pma_reset_ecu()
            elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
                cmd = self._diag_pending_cmd
                self._diag_pending_action = None
                self._diag_pending_cmd = None
                self._pma_send_uds_cmd(cmd)
            return True
        except Exception as e:
            self.append_log_color(f"❌ PMA 连接失败：{e}", "#FF5252")
            return False

    def _pma_send_uds_raw(self, data: bytes, timeout: float = 2.0):
        client = self.pma_doip_client
        if not client or not client.routing_activated:
            return None
        try:
            resp = client.send_diagnostic(data, target_addr=PMA_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ PMA UDS 发送失败：{e}", "#FF9800")
            return None

    def _pma_send_uds_cmd(self, cmd_text: str):
        import re, time
        client = self.pma_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ PMA 未连接", "#FF5252")
            return

        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            if '#' in line: line = line.split('#')[0].strip()
            if '//' in line: line = line.split('//')[0].strip()
            if not line: continue

            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"💤 Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue

            hex_str = line.replace(' ', '').replace('\t', '')
            try:
                uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue

            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{PMA_PHYSICAL_ADDR:04X} {formatted_tx}", "#64B5F6")
            QApplication.processEvents()

            resp = self._pma_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    if nrc == 0x78:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{PMA_RESPONSE_ADDR:04X} {formatted_rx} ⏳ {nrc_desc}", "#FF9800")
                    else:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{PMA_RESPONSE_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{PMA_RESPONSE_ADDR:04X} {formatted_rx}", "#81C784")

                # PMA 自动安全访问
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        key = sa_calc.calc_key(seed_hex, '00001055')
                        client = self.pma_doip_client
                        if client and client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key
                            formatted_tx2 = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x{PMA_PHYSICAL_ADDR:04X} {formatted_tx2}  🔑 自动发送 KEY", "#64B5F6")
                            QApplication.processEvents()
                            resp2 = None
                            for retry in range(10):
                                resp2 = self._pma_send_uds_raw(cmd_27_02, timeout=2.0)
                                if resp2:
                                    if len(resp2) >= 3 and resp2[0] == 0x7F and resp2[2] == 0x78:
                                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{PMA_RESPONSE_ADDR:04X} 7F 27 78 ⏳ Response Pending，等待中...", "#FF9800")
                                        time.sleep(0.5)
                                        continue
                                    break
                                time.sleep(0.3)
                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{PMA_RESPONSE_ADDR:04X} {f2} ✅ 安全认证成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{PMA_RESPONSE_ADDR:04X} {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{PMA_RESPONSE_ADDR:04X} {f2} ❌ 安全认证失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    def _pma_read_dtc(self):
        client = self.pma_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ PMA 未连接", "#FF5252")
            return
        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{PMA_PHYSICAL_ADDR:04X} 19 02 2C", "#64B5F6")
            QApplication.processEvents()
            resp = self._pma_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=2.0)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return
            formatted = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x{PMA_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            QApplication.processEvents()
            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color("  ✅ 无有效 DTC", "#4CAF50")
                return
            self.append_log_color(f"  📋 发现 {len(dtc_records)} 条 DTC", "#FF9800")
            log_lines = []
            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']
                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{PMA_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_04)}")
                resp_04 = self._pma_send_uds_raw(cmd_04, timeout=1.5)
                if resp_04:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{PMA_RESPONSE_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_04)}")
                    dtc['snapshot_raw'] = resp_04
                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{PMA_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_06)}")
                resp_06 = self._pma_send_uds_raw(cmd_06, timeout=1.5)
                if resp_06:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{PMA_RESPONSE_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_06)}")
                    dtc['extended_raw'] = resp_06
            self.append_log_batch(log_lines)
            self._display_dtc_table(dtc_records)
            self._save_dtc_excel(dtc_records)
        except Exception as e:
            self._diag_on_socket_error(e)
            self.append_log_color(f"❌ DTC 读取异常: {e}", "#FF5252")
            import traceback
            self.append_log_color(traceback.format_exc(), "#FF5252")

    def _pma_clear_dtc(self):
        client = self.pma_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ PMA 未连接", "#FF5252")
            return
        try:
            cmd_14 = bytes([0x14, 0xFF, 0xFF, 0xFF])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{PMA_PHYSICAL_ADDR:04X} 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()
            resp = self._pma_send_uds_raw(cmd_14, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x54:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{PMA_RESPONSE_ADDR:04X} {formatted} ✅ DTC 清除成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{PMA_RESPONSE_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{PMA_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 清除超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ DTC 清除异常: {e}", "#FF5252")

    def _pma_reset_ecu(self):
        client = self.pma_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ PMA 未连接", "#FF5252")
            return
        try:
            cmd_11_01 = bytes([0x11, 0x01])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{PMA_PHYSICAL_ADDR:04X} 11 01", "#64B5F6")
            QApplication.processEvents()
            resp = self._pma_send_uds_raw(cmd_11_01, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x51:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{PMA_RESPONSE_ADDR:04X} {formatted} ✅ PMA Reset 成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{PMA_RESPONSE_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{PMA_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ Reset 超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ Reset 失败：{str(e)}", "#FF5252")

    # ==================== CF 诊断功能 ====================
    def _connect_cf_doip(self):
        """CF 通过 ICB 转发，复用 ICB 的连接"""
        if not self.diag_doip_connected or not self.diag_doip_client:
            self.append_log_color("🔗 正在连接 ICB 网关以转发 CF...", "#2196F3")
            self._connect_doip_async("icb")
            return False
        self.cf_doip_connected = True
        self.cf_doip_client = self.diag_doip_client
        self.append_log_color("✅ CF 网关已就绪 (共享 ICB 连接)", "#4CAF50")
        if self._diag_pending_action == 'dtc_read':
            self._diag_pending_action = None; self._cf_read_dtc()
        elif self._diag_pending_action == 'dtc_clear':
            self._diag_pending_action = None; self._cf_clear_dtc()
        elif self._diag_pending_action == 'reset':
            self._diag_pending_action = None; self._cf_reset_ecu()
        elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
            cmd = self._diag_pending_cmd; self._diag_pending_action = None; self._diag_pending_cmd = None
            self._cf_send_uds_cmd(cmd)
        return True

    def _cf_send_uds_raw(self, data, timeout=2.0):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("⚠ CF: 共享 ICB 连接未就绪", "#FF9800")
            return None
        try:
            resp = client.send_diagnostic(data, target_addr=CF_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ CF UDS 发送失败：{e}", "#FF9800")
            return None

    def _cf_send_uds_cmd(self, cmd_text):
        import re, time
        client = self.cf_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ CF 未连接", "#FF5252")
            return
        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            if '#' in line: line = line.split('#')[0].strip()
            if '//' in line: line = line.split('//')[0].strip()
            if not line: continue
            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"💤 Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue
            hex_str = line.replace(' ', '').replace('\t', '')
            try: uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue
            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{CF_PHYSICAL_ADDR:04X} {formatted_tx}", "#64B5F6")
            QApplication.processEvents()
            resp = self._cf_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    if nrc == 0x78:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{CF_FUNCTIONAL_ADDR:04X} {formatted_rx} ⏳ {nrc_desc}", "#FF9800")
                    else:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{CF_FUNCTIONAL_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{CF_FUNCTIONAL_ADDR:04X} {formatted_rx}", "#81C784")
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        key = sa_calc.calc_key(seed_hex, CF_SECURITY_ALGO)
                        client = self.cf_doip_client
                        if client and client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key
                            f2tx = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x{CF_PHYSICAL_ADDR:04X} {f2tx}  🔑 自动发送 KEY", "#64B5F6")
                            QApplication.processEvents()
                            resp2 = None
                            for retry in range(10):
                                resp2 = self._cf_send_uds_raw(cmd_27_02, timeout=2.0)
                                if resp2:
                                    if len(resp2) >= 3 and resp2[0] == 0x7F and resp2[2] == 0x78:
                                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{CF_FUNCTIONAL_ADDR:04X} 7F 27 78 ⏳ Response Pending，等待中...", "#FF9800")
                                        time.sleep(0.5)
                                        continue
                                    break
                                time.sleep(0.3)
                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{CF_FUNCTIONAL_ADDR:04X} {f2} ✅ 安全认证成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{CF_FUNCTIONAL_ADDR:04X} {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{CF_FUNCTIONAL_ADDR:04X} {f2} ❌ 安全认证失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    def _cf_read_dtc(self):
        client = self.cf_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ CF 未连接", "#FF5252")
            return
        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{CF_PHYSICAL_ADDR:04X} 19 02 2C", "#64B5F6")
            QApplication.processEvents()
            resp = self._cf_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=2.0)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return
            formatted = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x{CF_FUNCTIONAL_ADDR:04X} {formatted}", "#81C784")
            QApplication.processEvents()
            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color("  ✅ 无有效 DTC", "#4CAF50")
                return
            self.append_log_color(f"  📋 发现 {len(dtc_records)} 条 DTC", "#FF9800")
            log_lines = []
            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']
                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{CF_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_04)}")
                resp_04 = self._cf_send_uds_raw(cmd_04, timeout=1.5)
                if resp_04:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{CF_FUNCTIONAL_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_04)}")
                    dtc['snapshot_raw'] = resp_04
                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{CF_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_06)}")
                resp_06 = self._cf_send_uds_raw(cmd_06, timeout=1.5)
                if resp_06:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{CF_FUNCTIONAL_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_06)}")
                    dtc['extended_raw'] = resp_06
            self.append_log_batch(log_lines)
            self._display_dtc_table(dtc_records)
            self._save_dtc_excel(dtc_records)
        except Exception as e:
            self._diag_on_socket_error(e)
            self.append_log_color(f"❌ DTC 读取异常: {e}", "#FF5252")
            import traceback; self.append_log_color(traceback.format_exc(), "#FF5252")

    def _cf_clear_dtc(self):
        client = self.cf_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ CF 未连接", "#FF5252")
            return
        try:
            cmd_14 = bytes([0x14, 0xFF, 0xFF, 0xFF])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{CF_PHYSICAL_ADDR:04X} 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()
            resp = self._cf_send_uds_raw(cmd_14, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x54:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{CF_FUNCTIONAL_ADDR:04X} {formatted} ✅ DTC 清除成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{CF_FUNCTIONAL_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{CF_FUNCTIONAL_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 清除超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ DTC 清除异常: {e}", "#FF5252")

    def _cf_reset_ecu(self):
        client = self.cf_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ CF 未连接", "#FF5252")
            return
        try:
            cmd_11_01 = bytes([0x11, 0x01])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{CF_PHYSICAL_ADDR:04X} 11 01", "#64B5F6")
            QApplication.processEvents()
            resp = self._cf_send_uds_raw(cmd_11_01, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x51:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{CF_FUNCTIONAL_ADDR:04X} {formatted} ✅ CF Reset 成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{CF_FUNCTIONAL_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{CF_FUNCTIONAL_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ Reset 超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ Reset 失败：{str(e)}", "#FF5252")

    # ==================== PEU 诊断功能 ====================
    def _connect_peu_doip(self):
        """PEU 通过 ICB 转发，复用 ICB 的连接"""
        if not self.diag_doip_connected or not self.diag_doip_client:
            self.append_log_color("🔗 正在连接 ICB 网关以转发 PEU...", "#2196F3")
            self._connect_doip_async("icb")
            return False
        self.peu_doip_connected = True
        self.peu_doip_client = self.diag_doip_client
        self.append_log_color("✅ PEU 网关已就绪 (共享 ICB 连接)", "#4CAF50")
        if self._diag_pending_action == 'dtc_read':
            self._diag_pending_action = None; self._peu_read_dtc()
        elif self._diag_pending_action == 'dtc_clear':
            self._diag_pending_action = None; self._peu_clear_dtc()
        elif self._diag_pending_action == 'reset':
            self._diag_pending_action = None; self._peu_reset_ecu()
        elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
            cmd = self._diag_pending_cmd; self._diag_pending_action = None; self._diag_pending_cmd = None
            self._peu_send_uds_cmd(cmd)
        return True

    def _peu_send_uds_raw(self, data, timeout=2.0):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("⚠ PEU: 共享 ICB 连接未就绪", "#FF9800")
            return None
        try:
            resp = client.send_diagnostic(data, target_addr=PEU_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ PEU UDS 发送失败：{e}", "#FF9800")
            return None

    def _peu_send_uds_cmd(self, cmd_text):
        import re, time
        client = self.peu_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ PEU 未连接", "#FF5252")
            return
        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            if '#' in line: line = line.split('#')[0].strip()
            if '//' in line: line = line.split('//')[0].strip()
            if not line: continue
            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"💤 Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue
            hex_str = line.replace(' ', '').replace('\t', '')
            try: uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue
            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{PEU_PHYSICAL_ADDR:04X} {formatted_tx}", "#64B5F6")
            QApplication.processEvents()
            resp = self._peu_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    if nrc == 0x78:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{PEU_FUNCTIONAL_ADDR:04X} {formatted_rx} ⏳ {nrc_desc}", "#FF9800")
                    else:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{PEU_FUNCTIONAL_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{PEU_FUNCTIONAL_ADDR:04X} {formatted_rx}", "#81C784")
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        key = sa_calc.calc_key(seed_hex, PEU_SECURITY_ALGO)
                        client = self.peu_doip_client
                        if client and client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key
                            f2tx = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x{PEU_PHYSICAL_ADDR:04X} {f2tx}  🔑 自动发送 KEY", "#64B5F6")
                            QApplication.processEvents()
                            resp2 = None
                            for retry in range(10):
                                resp2 = self._peu_send_uds_raw(cmd_27_02, timeout=2.0)
                                if resp2:
                                    if len(resp2) >= 3 and resp2[0] == 0x7F and resp2[2] == 0x78:
                                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{PEU_FUNCTIONAL_ADDR:04X} 7F 27 78 ⏳ Response Pending，等待中...", "#FF9800")
                                        time.sleep(0.5)
                                        continue
                                    break
                                time.sleep(0.3)
                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{PEU_FUNCTIONAL_ADDR:04X} {f2} ✅ 安全认证成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{PEU_FUNCTIONAL_ADDR:04X} {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{PEU_FUNCTIONAL_ADDR:04X} {f2} ❌ 安全认证失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    def _peu_read_dtc(self):
        client = self.peu_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ PEU 未连接", "#FF5252")
            return
        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{PEU_PHYSICAL_ADDR:04X} 19 02 2C", "#64B5F6")
            QApplication.processEvents()
            resp = self._peu_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=2.0)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return
            formatted = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x{PEU_FUNCTIONAL_ADDR:04X} {formatted}", "#81C784")
            QApplication.processEvents()
            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color("  ✅ 无有效 DTC", "#4CAF50")
                return
            self.append_log_color(f"  📋 发现 {len(dtc_records)} 条 DTC", "#FF9800")
            log_lines = []
            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']
                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{PEU_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_04)}")
                resp_04 = self._peu_send_uds_raw(cmd_04, timeout=1.5)
                if resp_04:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{PEU_FUNCTIONAL_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_04)}")
                    dtc['snapshot_raw'] = resp_04
                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{PEU_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_06)}")
                resp_06 = self._peu_send_uds_raw(cmd_06, timeout=1.5)
                if resp_06:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{PEU_FUNCTIONAL_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_06)}")
                    dtc['extended_raw'] = resp_06
            self.append_log_batch(log_lines)
            self._display_dtc_table(dtc_records)
            self._save_dtc_excel(dtc_records)
        except Exception as e:
            self._diag_on_socket_error(e)
            self.append_log_color(f"❌ DTC 读取异常: {e}", "#FF5252")
            import traceback; self.append_log_color(traceback.format_exc(), "#FF5252")

    def _peu_clear_dtc(self):
        client = self.peu_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ PEU 未连接", "#FF5252")
            return
        try:
            cmd_14 = bytes([0x14, 0xFF, 0xFF, 0xFF])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{PEU_PHYSICAL_ADDR:04X} 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()
            resp = self._peu_send_uds_raw(cmd_14, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x54:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{PEU_FUNCTIONAL_ADDR:04X} {formatted} ✅ DTC 清除成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{PEU_FUNCTIONAL_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{PEU_FUNCTIONAL_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 清除超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ DTC 清除异常: {e}", "#FF5252")

    def _peu_reset_ecu(self):
        client = self.peu_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ PEU 未连接", "#FF5252")
            return
        try:
            cmd_11_01 = bytes([0x11, 0x01])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{PEU_PHYSICAL_ADDR:04X} 11 01", "#64B5F6")
            QApplication.processEvents()
            resp = self._peu_send_uds_raw(cmd_11_01, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x51:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{PEU_FUNCTIONAL_ADDR:04X} {formatted} ✅ PEU Reset 成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{PEU_FUNCTIONAL_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{PEU_FUNCTIONAL_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ Reset 超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ Reset 失败：{str(e)}", "#FF5252")

    # ==================== RHPMWC 诊断功能 ====================
    def _connect_rhpmwc_doip(self):
        """RHPMWC 通过 ICB 转发，复用 ICB 的连接"""
        if not self.diag_doip_connected or not self.diag_doip_client:
            self.append_log_color("🔗 正在连接 ICB 网关以转发 RHPMWC...", "#2196F3")
            self._connect_doip_async("icb")
            return False
        self.rhpmwc_doip_connected = True
        self.rhpmwc_doip_client = self.diag_doip_client
        self.append_log_color("✅ RHPMWC 网关已就绪 (共享 ICB 连接)", "#4CAF50")
        if self._diag_pending_action == 'dtc_read':
            self._diag_pending_action = None; self._rhpmwc_read_dtc()
        elif self._diag_pending_action == 'dtc_clear':
            self._diag_pending_action = None; self._rhpmwc_clear_dtc()
        elif self._diag_pending_action == 'reset':
            self._diag_pending_action = None; self._rhpmwc_reset_ecu()
        elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
            cmd = self._diag_pending_cmd; self._diag_pending_action = None; self._diag_pending_cmd = None
            self._rhpmwc_send_uds_cmd(cmd)
        return True

    def _rhpmwc_send_uds_raw(self, data, timeout=2.0):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("⚠ RHPMWC: 共享 ICB 连接未就绪", "#FF9800")
            return None
        try:
            resp = client.send_diagnostic(data, target_addr=RHPMWC_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ RHPMWC UDS 发送失败：{e}", "#FF9800")
            return None

    def _rhpmwc_send_uds_cmd(self, cmd_text):
        import re, time
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ RHPMWC: 共享 ICB 连接未就绪", "#FF5252")
            return
        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            if '#' in line: line = line.split('#')[0].strip()
            if '//' in line: line = line.split('//')[0].strip()
            if not line: continue
            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"💤 Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue
            hex_str = line.replace(' ', '').replace('\t', '')
            try: uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue
            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{RHPMWC_PHYSICAL_ADDR:04X} {formatted_tx}", "#64B5F6")
            QApplication.processEvents()
            resp = self._rhpmwc_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    if nrc == 0x78:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{RHPMWC_FUNCTIONAL_ADDR:04X} {formatted_rx} ⏳ {nrc_desc}", "#FF9800")
                    else:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{RHPMWC_FUNCTIONAL_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RHPMWC_FUNCTIONAL_ADDR:04X} {formatted_rx}", "#81C784")
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        key = sa_calc.calc_key(seed_hex, RHPMWC_SECURITY_ALGO)
                        client = self.rhpmwc_doip_client
                        if client and client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key
                            f2tx = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x{RHPMWC_PHYSICAL_ADDR:04X} {f2tx}  🔑 自动发送 KEY", "#64B5F6")
                            QApplication.processEvents()
                            resp2 = None
                            for retry in range(10):
                                resp2 = self._rhpmwc_send_uds_raw(cmd_27_02, timeout=2.0)
                                if resp2:
                                    if len(resp2) >= 3 and resp2[0] == 0x7F and resp2[2] == 0x78:
                                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{RHPMWC_FUNCTIONAL_ADDR:04X} 7F 27 78 ⏳ Response Pending，等待中...", "#FF9800")
                                        time.sleep(0.5)
                                        continue
                                    break
                                time.sleep(0.3)
                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RHPMWC_FUNCTIONAL_ADDR:04X} {f2} ✅ 安全认证成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RHPMWC_FUNCTIONAL_ADDR:04X} {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RHPMWC_FUNCTIONAL_ADDR:04X} {f2} ❌ 安全认证失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    def _rhpmwc_read_dtc(self):
        client = self.rhpmwc_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ RHPMWC 未连接", "#FF5252")
            return
        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{RHPMWC_PHYSICAL_ADDR:04X} 19 02 2C", "#64B5F6")
            QApplication.processEvents()
            resp = self._rhpmwc_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=2.0)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return
            formatted = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x{RHPMWC_FUNCTIONAL_ADDR:04X} {formatted}", "#81C784")
            QApplication.processEvents()
            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color("  ✅ 无有效 DTC", "#4CAF50")
                return
            self.append_log_color(f"  📋 发现 {len(dtc_records)} 条 DTC", "#FF9800")
            log_lines = []
            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']
                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{RHPMWC_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_04)}")
                resp_04 = self._rhpmwc_send_uds_raw(cmd_04, timeout=1.5)
                if resp_04:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{RHPMWC_FUNCTIONAL_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_04)}")
                    dtc['snapshot_raw'] = resp_04
                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{RHPMWC_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_06)}")
                resp_06 = self._rhpmwc_send_uds_raw(cmd_06, timeout=1.5)
                if resp_06:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{RHPMWC_FUNCTIONAL_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_06)}")
                    dtc['extended_raw'] = resp_06
            self.append_log_batch(log_lines)
            self._display_dtc_table(dtc_records)
            self._save_dtc_excel(dtc_records)
        except Exception as e:
            self._diag_on_socket_error(e)
            self.append_log_color(f"❌ DTC 读取异常: {e}", "#FF5252")
            import traceback; self.append_log_color(traceback.format_exc(), "#FF5252")

    def _rhpmwc_clear_dtc(self):
        client = self.rhpmwc_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ RHPMWC 未连接", "#FF5252")
            return
        try:
            cmd_14 = bytes([0x14, 0xFF, 0xFF, 0xFF])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{RHPMWC_PHYSICAL_ADDR:04X} 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()
            resp = self._rhpmwc_send_uds_raw(cmd_14, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x54:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RHPMWC_FUNCTIONAL_ADDR:04X} {formatted} ✅ DTC 清除成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RHPMWC_FUNCTIONAL_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RHPMWC_FUNCTIONAL_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 清除超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ DTC 清除异常: {e}", "#FF5252")

    def _rhpmwc_reset_ecu(self):
        client = self.rhpmwc_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ RHPMWC 未连接", "#FF5252")
            return
        try:
            cmd_11_01 = bytes([0x11, 0x01])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{RHPMWC_PHYSICAL_ADDR:04X} 11 01", "#64B5F6")
            QApplication.processEvents()
            resp = self._rhpmwc_send_uds_raw(cmd_11_01, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x51:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RHPMWC_FUNCTIONAL_ADDR:04X} {formatted} ✅ RHPMWC Reset 成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RHPMWC_FUNCTIONAL_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RHPMWC_FUNCTIONAL_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ Reset 超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ Reset 失败：{str(e)}", "#FF5252")

    # ==================== RLSS 诊断功能 ====================
    def _connect_rlss_doip(self):
        """RLSS 通过 ICB 转发，复用 ICB 的连接"""
        if not self.diag_doip_connected or not self.diag_doip_client:
            self.append_log_color("🔗 正在连接 ICB 网关以转发 RLSS...", "#2196F3")
            self._connect_doip_async("icb")
            return False
        self.rlss_doip_connected = True
        self.rlss_doip_client = self.diag_doip_client
        self.append_log_color("✅ RLSS 网关已就绪 (共享 ICB 连接)", "#4CAF50")
        if self._diag_pending_action == 'dtc_read':
            self._diag_pending_action = None; self._rlss_read_dtc()
        elif self._diag_pending_action == 'dtc_clear':
            self._diag_pending_action = None; self._rlss_clear_dtc()
        elif self._diag_pending_action == 'reset':
            self._diag_pending_action = None; self._rlss_reset_ecu()
        elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
            cmd = self._diag_pending_cmd; self._diag_pending_action = None; self._diag_pending_cmd = None
            self._rlss_send_uds_cmd(cmd)
        return True

    def _rlss_send_uds_raw(self, data, timeout=2.0):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("⚠ RLSS: 共享 ICB 连接未就绪", "#FF9800")
            return None
        try:
            resp = client.send_diagnostic(data, target_addr=RLSS_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ RLSS UDS 发送失败：{e}", "#FF9800")
            return None

    def _rlss_send_uds_cmd(self, cmd_text):
        import re, time
        client = self.rlss_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ RLSS 未连接", "#FF5252")
            return
        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            if '#' in line: line = line.split('#')[0].strip()
            if '//' in line: line = line.split('//')[0].strip()
            if not line: continue
            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"💤 Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue
            hex_str = line.replace(' ', '').replace('\t', '')
            try: uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue
            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{RLSS_PHYSICAL_ADDR:04X} {formatted_tx}", "#64B5F6")
            QApplication.processEvents()
            resp = self._rlss_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    if nrc == 0x78:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLSS_FUNCTIONAL_ADDR:04X} {formatted_rx} ⏳ {nrc_desc}", "#FF9800")
                    else:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLSS_FUNCTIONAL_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLSS_FUNCTIONAL_ADDR:04X} {formatted_rx}", "#81C784")
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        key = sa_calc.calc_key(seed_hex, RLSS_SECURITY_ALGO)
                        client = self.rlss_doip_client
                        if client and client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key
                            f2tx = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x{RLSS_PHYSICAL_ADDR:04X} {f2tx}  🔑 自动发送 KEY", "#64B5F6")
                            QApplication.processEvents()
                            resp2 = None
                            for retry in range(10):
                                resp2 = self._rlss_send_uds_raw(cmd_27_02, timeout=2.0)
                                if resp2:
                                    if len(resp2) >= 3 and resp2[0] == 0x7F and resp2[2] == 0x78:
                                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLSS_FUNCTIONAL_ADDR:04X} 7F 27 78 ⏳ Response Pending，等待中...", "#FF9800")
                                        time.sleep(0.5)
                                        continue
                                    break
                                time.sleep(0.3)
                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLSS_FUNCTIONAL_ADDR:04X} {f2} ✅ 安全认证成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLSS_FUNCTIONAL_ADDR:04X} {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLSS_FUNCTIONAL_ADDR:04X} {f2} ❌ 安全认证失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    def _rlss_read_dtc(self):
        client = self.rlss_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ RLSS 未连接", "#FF5252")
            return
        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{RLSS_PHYSICAL_ADDR:04X} 19 02 2C", "#64B5F6")
            QApplication.processEvents()
            resp = self._rlss_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=2.0)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return
            formatted = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLSS_FUNCTIONAL_ADDR:04X} {formatted}", "#81C784")
            QApplication.processEvents()
            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color("  ✅ 无有效 DTC", "#4CAF50")
                return
            self.append_log_color(f"  📋 发现 {len(dtc_records)} 条 DTC", "#FF9800")
            log_lines = []
            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']
                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{RLSS_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_04)}")
                resp_04 = self._rlss_send_uds_raw(cmd_04, timeout=1.5)
                if resp_04:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{RLSS_FUNCTIONAL_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_04)}")
                    dtc['snapshot_raw'] = resp_04
                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                ts = self._diag_timestamp()
                log_lines.append(f"{ts} tx 0x{RLSS_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_06)}")
                resp_06 = self._rlss_send_uds_raw(cmd_06, timeout=1.5)
                if resp_06:
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{RLSS_FUNCTIONAL_ADDR:04X} {' '.join(f'{b:02X}' for b in resp_06)}")
                    dtc['extended_raw'] = resp_06
            self.append_log_batch(log_lines)
            self._display_dtc_table(dtc_records)
            self._save_dtc_excel(dtc_records)
        except Exception as e:
            self._diag_on_socket_error(e)
            self.append_log_color(f"❌ DTC 读取异常: {e}", "#FF5252")
            import traceback; self.append_log_color(traceback.format_exc(), "#FF5252")

    def _rlss_clear_dtc(self):
        client = self.rlss_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ RLSS 未连接", "#FF5252")
            return
        try:
            cmd_14 = bytes([0x14, 0xFF, 0xFF, 0xFF])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{RLSS_PHYSICAL_ADDR:04X} 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()
            resp = self._rlss_send_uds_raw(cmd_14, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x54:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLSS_FUNCTIONAL_ADDR:04X} {formatted} ✅ DTC 清除成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLSS_FUNCTIONAL_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLSS_FUNCTIONAL_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 清除超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ DTC 清除异常: {e}", "#FF5252")

    def _rlss_reset_ecu(self):
        client = self.rlss_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ RLSS 未连接", "#FF5252")
            return
        try:
            cmd_11_01 = bytes([0x11, 0x01])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{RLSS_PHYSICAL_ADDR:04X} 11 01", "#64B5F6")
            QApplication.processEvents()
            resp = self._rlss_send_uds_raw(cmd_11_01, timeout=2.0)
            if resp:
                formatted = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x51:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLSS_FUNCTIONAL_ADDR:04X} {formatted} ✅ RLSS Reset 成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLSS_FUNCTIONAL_ADDR:04X} {formatted} ❌ NRC 0x{nrc:02X}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{RLSS_FUNCTIONAL_ADDR:04X} {formatted}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ Reset 超时", "#FF5252")
        except Exception as e:
            self.append_log_color(f"❌ Reset 失败：{str(e)}", "#FF5252")


    def _iam_send_uds_raw(self, data: bytes, timeout: float = 2.0):
        """发送 UDS 指令到 IAM 并返回原始响应 (bytes), 失败返回 None

        Args:
            data: UDS 请求数据
            timeout: 超时时间（秒）
        """
        client = self.iam_doip_client
        if not client or not client.routing_activated:
            return None
        try:
            # 使用物理地址 0x0711
            resp = client.send_diagnostic(data, target_addr=IAM_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ IAM UDS 发送失败：{e}", "#FF9800")
            return None




    def _connect_broadcast_doip(self):
        """BROADCAST (0xEFFF 功能广播地址) 通过 ICB 转发，复用 ICB 的连接"""
        if not self.diag_doip_connected or not self.diag_doip_client:
            self.append_log_color("🔗 正在连接 ICB 网关以转发 BROADCAST...", "#2196F3")
            self._connect_doip_async("icb")
            return False
        self.broadcast_doip_connected = True
        self.broadcast_doip_client = self.diag_doip_client
        self.append_log_color("✅ BROADCAST 网关已就绪 (功能广播 0xEFFF, 所有 ECU 响应)", "#4CAF50")
        if self._diag_pending_action == 'dtc_read':
            self._diag_pending_action = None; self._broadcast_read_dtc()
        elif self._diag_pending_action == 'dtc_clear':
            self._diag_pending_action = None; self._broadcast_clear_dtc()
        elif self._diag_pending_action == 'reset':
            self._diag_pending_action = None; self._broadcast_reset_ecu()
        elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
            cmd = self._diag_pending_cmd; self._diag_pending_action = None; self._diag_pending_cmd = None
            self._broadcast_send_uds_cmd(cmd)
        return True

    def _broadcast_send_uds_raw(self, data, timeout=2.0):
        """发送 UDS 到功能广播地址 0xEFFF，返回所有 ECU 的 (源地址, UDS响应) 列表"""
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("⚠ BROADCAST: 共享 ICB 连接未就绪", "#FF9800")
            return []
        try:
            results = client.send_diagnostic_multi(data, target_addr=BROADCAST_PHYSICAL_ADDR, timeout=timeout)
            return results if results else []
        except Exception as e:
            self.append_log_color(f"⚠ BROADCAST UDS 发送失败：{e}", "#FF9800")
            return []

    def _broadcast_send_uds_cmd(self, cmd_text):
        import re, time
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ BROADCAST: 共享 ICB 连接未就绪", "#FF5252")
            return
        lines_list = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines_list:
            if '#' in line: line = line.split('#')[0].strip()
            if '//' in line: line = line.split('//')[0].strip()
            if not line: continue
            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"💤 Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue
            hex_str = line.replace(' ', '').replace('\t', '')
            try: uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue
            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{BROADCAST_PHYSICAL_ADDR:04X} {formatted_tx}", "#64B5F6")
            QApplication.processEvents()
            resp = self._broadcast_send_uds_raw(uds_data)
            if resp:
                for item in resp:
                    src = item["source_addr"]
                    uds = item["uds"]
                    formatted_rx = ' '.join(f'{b:02X}' for b in uds)
                    ts = self._diag_timestamp()
                    if len(uds) >= 3 and uds[0] == 0x7F:
                        nrc = uds[2] if len(uds) > 2 else 0
                        nrc_desc = self._diag_nrc_desc(nrc)
                        if nrc == 0x78:
                            self.append_log_color(f"{ts} rx 0x{src:04x} {formatted_rx} ⏳ {nrc_desc}", "#FF9800")
                        else:
                            self.append_log_color(f"{ts} rx 0x{src:04x} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                    else:
                        self.append_log_color(f"{ts} rx 0x{src:04x} {formatted_rx}", "#81C784")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    def _broadcast_read_dtc(self):
        """Full IDS-style DTC read for all ECUs via functional broadcast 0xEFFF.
        Step 1: $19 02 2C broadcast -> collect all DTCs with source addresses
        Step 2: For each ECU, $19 04 (snapshot) + $19 06 (extended) with real-time progress
        Step 3: Display unified table + save to Excel

        Note: ICB 网关在广播时非确定性，多发几次可收全所有 ECU。
        自动重试最多 4 次，合并所有响应。
        """
        import time
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("ICB not connected, cannot forward BROADCAST", "#FF5252")
            return
        try:
            # === Step 1: Broadcast $19 02 2C with auto-retry ===
            QApplication.processEvents()
            all_results = {}  # {source_addr: uds_bytes}
            max_attempts = 4
            for attempt in range(max_attempts):
                results = self._broadcast_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=6.0)
                if results:
                    for item in results:
                        src = item["source_addr"]
                        uds = item["uds"]
                        if src not in all_results:
                            all_results[src] = uds
                        else:
                            # 同一 ECU 如果有更多 UDS 段则追加
                            all_results[src] = all_results[src] + uds
                if len(all_results) >= 20:
                    break  # 已收全，不需要再发
                if attempt < max_attempts - 1:
                    time.sleep(0.3)
                    QApplication.processEvents()

            # Convert merged dict back to list
            merged_results = [{"source_addr": src, "uds": uds} for src, uds in all_results.items()]

            if not merged_results:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到任何响应", "#FF5252")
                return

            # Print broadcast tx/rx in IDS raw hex format
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{BROADCAST_PHYSICAL_ADDR:04x} 19 02 2C", "#64B5F6")
            for item in merged_results:
                src = item["source_addr"]
                uds = item["uds"]
                ecu_name = ECU_ADDR_MAP.get(src, f"0x{src:04X}")
                formatted_rx = " ".join(f"{b:02X}" for b in uds)
                ts = self._diag_timestamp()
                self.append_log_color(f"{ts} rx 0x{src:04x} {formatted_rx}", "#81C784")

            # Parse DTCs per ECU and group by source address
            ecu_dtcs = {}  # {source_addr: {ecu_name, dtc_list}}
            total_dtc_count = 0
            for item in merged_results:
                src = item["source_addr"]
                uds = item["uds"]
                ecu_name = ECU_ADDR_MAP.get(src, f"ECU(0x{src:04X})")
                dtc_list = self._parse_dtc_02_response(uds)
                if dtc_list:
                    ecu_dtcs[src] = {"name": ecu_name, "dtcs": dtc_list}
                    total_dtc_count += len(dtc_list)
                    formatted_rx = " ".join(f"{b:02X}" for b in uds)
                    # raw hex already printed above
                    QApplication.processEvents()
                else:
                    # raw hex already printed above
                    QApplication.processEvents()

            if not ecu_dtcs:
                # All ECUs reported 0 DTCs, still ok
                return
            # self.append_log_color(f"  Total {total_dtc_count} DTCs from {len(ecu_dtcs)} ECUs", "#2196F3")
            # QApplication.processEvents()

            # === Step 2: Per-ECU $19 04 + $19 06 queries ===
            # tx/rx printed in raw IDS hex format below

            all_dtcs = []
            processed = 0
            for src_addr, ecu_info in sorted(ecu_dtcs.items()):
                ecu_name = ecu_info["name"]
                dtc_list = ecu_info["dtcs"]
                # self.append_log_color(f"  [{ecu_name}] Processing {len(dtc_list)} DTCs...", "#90CAF9")
                QApplication.processEvents()

                for d in dtc_list:
                    d["ecu_source"] = ecu_name
                    d["ecu_addr"] = src_addr

                    # Get the 3-byte ISO DTC code
                    raw_dtc = d.get("raw")
                    if raw_dtc and len(raw_dtc) == 3:
                        dtc_3bytes = raw_dtc
                    else:
                        label = d["label"]
                        parts = label.split("_")
                        if len(parts) >= 2:
                            try:
                                dtc_3bytes = bytes.fromhex(parts[0][1:])
                                if len(dtc_3bytes) != 3:
                                    continue
                            except:
                                continue
                        else:
                            continue

                    dtc_code_str = d["label"][:7]

                    # Query $19 04 (snapshot) - short timeout 0.3s
                    req_04 = bytes([0x19, 0x04]) + dtc_3bytes + bytes([0x01])
                    ts = self._diag_timestamp()
                    tx_hex = " ".join(f"{b:02X}" for b in req_04)
                    self.append_log_color(f"{ts} tx 0x{src_addr:04x} {tx_hex}", "#64B5F6")
                    try:
                        snap_resp = client.send_diagnostic(
                            req_04,
                            target_addr=src_addr, timeout=0.3
                        )
                        if snap_resp and len(snap_resp) > 3 and snap_resp[0] == 0x59 and snap_resp[1] == 0x04:
                            d["snapshot_raw"] = snap_resp
                            rx_hex = " ".join(f"{b:02X}" for b in snap_resp)
                            ts = self._diag_timestamp()
                            self.append_log_color(f"{ts} rx 0x{src_addr:04x} {rx_hex}", "#81C784")
                    except:
                        pass

                    # Query $19 06 (extended data) - short timeout 0.3s
                    req_06 = bytes([0x19, 0x06]) + dtc_3bytes + bytes([0x01])
                    ts = self._diag_timestamp()
                    tx_hex = " ".join(f"{b:02X}" for b in req_06)
                    self.append_log_color(f"{ts} tx 0x{src_addr:04x} {tx_hex}", "#64B5F6")
                    try:
                        ext_resp = client.send_diagnostic(
                            req_06,
                            target_addr=src_addr, timeout=0.3
                        )
                        if ext_resp and len(ext_resp) > 3 and ext_resp[0] == 0x59 and ext_resp[1] == 0x06:
                            d["extended_raw"] = ext_resp
                            rx_hex = " ".join(f"{b:02X}" for b in ext_resp)
                            ts = self._diag_timestamp()
                            self.append_log_color(f"{ts} rx 0x{src_addr:04x} {rx_hex}", "#81C784")
                    except:
                        pass

                    all_dtcs.append(d)
                    processed += 1

                    # Real-time progress: update UI every DTC
                    # Suppressed per user request (show only Tx/Rx and final result)
                    if processed % 5 == 0 or processed == 1:
                        pass  # progress suppressed
                        # self.append_log_color(f"    {processed}/{total_dtc_count} DTCs processed...", "#90CAF9")
                        QApplication.processEvents()

                # Show per-ECU summary - suppressed (show only Tx/Rx and final result)
                # self.append_log_color(f"  [{ecu_name}] Done ({len(dtc_list)} DTCs)", "#4CAF50")
                QApplication.processEvents()

            # === Step 3: Display + Save ===
            self._display_dtc_table(all_dtcs)
            self._save_dtc_excel(all_dtcs)

        except Exception as e:
            import traceback
            self.append_log_color(f"ERROR in broadcast DTC read: {e}", "#FF5252")
            traceback.print_exc()
            self._diag_on_socket_error(e)
    def _broadcast_clear_dtc(self):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("ICB 未连接，无法转发 BROADCAST 诊断", "#FF5252")
            return
        try:
            cmd_14 = bytes([0x14, 0xFF, 0xFF, 0xFF])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{BROADCAST_PHYSICAL_ADDR:04X} 14 FF FF FF (broadcast)", "#64B5F6")
            QApplication.processEvents()
            results = self._broadcast_send_uds_raw(cmd_14, timeout=2.0)
            if results:
                ok_count = 0
                activate_count = 0  # 0x78 responses (not supported)
                nrc_count = 0
                for r in results:
                    src = r["source_addr"]
                    uds = r["uds"]
                    ecu_name = ECU_ADDR_MAP.get(src, f"ECU(0x{src:04X})")
                    formatted_rx = " ".join(f"{b:02X}" for b in uds[:4])
                    if uds[0] == 0x54:
                        ok_count += 1
                        self.append_log_color(f"  ✅ {ecu_name}: 54 ... (清除成功)", "#4CAF50")
                    elif uds[0] == 0x7F and len(uds) >= 3 and uds[2] == 0x78:
                        self.append_log_color(f"  ⏳ {ecu_name}: 7F 14 78 (不支持清除)", "#FF9800")
                    elif uds[0] == 0x7F:
                        nrc = uds[2] if len(uds) > 2 else 0
                        nrc_count += 1
                        self.append_log_color(f"  ❌ {ecu_name}: NRC 0x{nrc:02X}", "#FF5252")
                    QApplication.processEvents()
                self.append_log_color(f"  清除结果: {ok_count} OK, {nrc_count} NRC, {len(results)} Total", "#2196F3")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 清除超时（无响应）", "#FF5252")
        except Exception as e:
            self._diag_on_socket_error(e)

    def _broadcast_reset_ecu(self):
        # IDS style: $10 03 -> sleep 2s -> show -> $11 01 -> reconnect -> show
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color('ICB not connected', '#FF5252')
            return
        import time, struct
        from Subpy.doip_client import DOIP_TYPE_DIAG_MSG
        try:
            ts = self._diag_timestamp()
            self.append_log_color(ts + ' tx 0x%04X 10 03' % BROADCAST_PHYSICAL_ADDR, '#64B5F6')
            QApplication.processEvents()
            client._send_doip(DOIP_TYPE_DIAG_MSG, struct.pack("!HH", client.source_addr, BROADCAST_PHYSICAL_ADDR) + bytes([0x10, 0x03]))
            # Let ICB collect responses for ~2s
            time.sleep(2.0)
            # Drain whatever is available (handle conn drop)
            session_msgs = []
            for _ in range(40):
                if not client.sock or not client.connected: break
                try:
                    client.sock.settimeout(0.05)
                    hdr = client.sock.recv(8)
                    if not hdr or len(hdr) < 8: break
                    plen = struct.unpack("!I", hdr[4:8])[0]
                    if plen > 4096: break
                    pay = client.sock.recv(plen)
                    if not pay or len(pay) < plen: break
                    client.sock.settimeout(None)
                    session_msgs.append({"type": struct.unpack("!H", hdr[2:4])[0], "payload": hdr + pay})
                except Exception:
                    break
            session_count = 0
            for m in session_msgs:
                if m["type"] == DOIP_TYPE_DIAG_MSG and len(m["payload"]) >= 12:
                    sa = struct.unpack("!H", m["payload"][8:10])[0]  # after DoIP header(8)
                    if m["payload"][12] == 0x50:
                        session_count += 1
                        self.append_log_color('  rx 0x%04x 50 03' % sa, '#4CAF50')
                    QApplication.processEvents()
            self.append_log_color('  %d ECUs in extended session' % session_count, '#2196F3')

            # Phase 2: $11 01
            # ICB closes connection after broadcast, reconnect
            self.append_log_color('Reconnecting ICB for $11 01...', '#FF9800')
            QApplication.processEvents()
            try:
                client.connect()
                client.routing_activate()
                self.append_log_color('ICB reconnected', '#4CAF50')
            except Exception as e:
                self.append_log_color('Reconnect failed: ' + str(e), '#FF5252')
                return

            ts = self._diag_timestamp()
            self.append_log_color(ts + ' tx 0x%04X 11 01 (reset)' % BROADCAST_PHYSICAL_ADDR, '#64B5F6')
            QApplication.processEvents()
            client._send_doip(DOIP_TYPE_DIAG_MSG, struct.pack("!HH", client.source_addr, BROADCAST_PHYSICAL_ADDR) + bytes([0x11, 0x01]))
            # Wait for responses
            time.sleep(1.0)
            reset_msgs = []
            for _ in range(40):
                if not client.sock or not client.connected: break
                try:
                    client.sock.settimeout(0.05)
                    hdr = client.sock.recv(8)
                    if not hdr or len(hdr) < 8: break
                    plen = struct.unpack("!I", hdr[4:8])[0]
                    if plen > 4096: break
                    pay = client.sock.recv(plen)
                    if not pay or len(pay) < plen: break
                    client.sock.settimeout(None)
                    reset_msgs.append({"type": struct.unpack("!H", hdr[2:4])[0], "payload": hdr + pay})
                except Exception:
                    break

            # Parse 11 01 responses
            seen = {}
            for m in reset_msgs:
                if m["type"] != DOIP_TYPE_DIAG_MSG: continue
                pay = m["payload"]
                if len(pay) < 12: continue
                sa = struct.unpack("!H", pay[8:10])[0]
                uds = pay[12:]
                if len(uds) >= 3 and uds[0] == 0x7F and uds[2] == 0x78:
                    continue  # skip 0x78
                if sa not in seen:
                    seen[sa] = uds

            # Display
            if seen:
                ok = 0
                for sa, uds in sorted(seen.items()):
                    name = ECU_ADDR_MAP.get(sa, "ECU(0x%04X)" % sa)
                    if uds[0] == 0x51:
                        ok += 1
                        self.append_log_color('  ' + name + ': 51 (reset)', '#4CAF50')
                    elif uds[0] == 0x7F and len(uds) >= 3:
                        self.append_log_color('  ' + name + ': NRC 0x%02X' % uds[2], '#FF5252')
                    QApplication.processEvents()
                self.append_log_color('  %d/%d ECUs responded' % (ok, len(seen)), '#2196F3')
            else:
                self.append_log_color(self._diag_timestamp() + ' timeout', '#FF5252')

        except Exception as e:
            self._diag_on_socket_error(e)


    def _dkmm_connect(self):
        """Connect to DKMM via ICB gateway"""
        self.selected_ecu_key = 'DKMM'
        self.current_ecu = 'DKMM'
        self._connect_to_icb_gateway()
    
    def _dkmm_send_uds_raw(self):
        """Send raw UDS to DKMM"""
        data = self._parse_hex_input()
        if not data:
            return
        self._send_uds_via_gateway(data, DKMM_REQUEST_ADDR, DKMM_RESPONSE_ADDR)
    
    def _dkmm_send_cmd(self, cmd_name):
        """Send UDS command to DKMM"""
        self.selected_ecu_key = 'DKMM'
        cmd_map = {
            'read_did': lambda: self._build_uds_cmd('22', self.ui.lineEdit_did_id.text()),
            'write_did': lambda: self._build_uds_cmd('2E', self.ui.lineEdit_did_id.text(), self.ui.lineEdit_did_data.text()),
            'io_control': lambda: self._build_uds_cmd('31', '01', self.ui.lineEdit_routine_id.text()),
            'routine': lambda: self._build_uds_cmd('31', '01', self.ui.lineEdit_routine_id.text()),
        }
        if cmd_name in cmd_map:
            data = cmd_map[cmd_name]()
            if data:
                self._send_uds_via_gateway(data, DKMM_REQUEST_ADDR, DKMM_RESPONSE_ADDR)
    
    def _dkmm_read_dtc(self):
        """Read DTC from DKMM"""
        self.selected_ecu_key = 'DKMM'
        self._read_dtc_via_gateway(DKMM_REQUEST_ADDR, DKMM_RESPONSE_ADDR, 'DKMM')
    
    def _dkmm_clear_dtc(self):
        """Clear DTC in DKMM"""
        self.selected_ecu_key = 'DKMM'
        self._clear_dtc_via_gateway(DKMM_REQUEST_ADDR, DKMM_RESPONSE_ADDR)
    
    def _dkmm_reset_ecu(self):
        """Reset DKMM"""
        self.selected_ecu_key = 'DKMM'
        self._reset_ecu_via_gateway(DKMM_REQUEST_ADDR, DKMM_RESPONSE_ADDR)
    

    def _eac_connect(self):
        self.selected_ecu_key = 'EAC'
        self.current_ecu = 'EAC'
        self._connect_to_icb_gateway()
    
    def _eac_send_uds_raw(self):
        data = self._parse_hex_input()
        if not data: return
        self._send_uds_via_gateway(data, EAC_REQUEST_ADDR, EAC_RESPONSE_ADDR)
    
    def _eac_send_cmd(self, cmd_name):
        self.selected_ecu_key = 'EAC'
        cmd_map = {
            'read_did': lambda: self._build_uds_cmd('22', self.ui.lineEdit_did_id.text()),
            'write_did': lambda: self._build_uds_cmd('2E', self.ui.lineEdit_did_id.text(), self.ui.lineEdit_did_data.text()),
            'io_control': lambda: self._build_uds_cmd('31', '01', self.ui.lineEdit_routine_id.text()),
            'routine': lambda: self._build_uds_cmd('31', '01', self.ui.lineEdit_routine_id.text()),
        }
        if cmd_name in cmd_map:
            data = cmd_map[cmd_name]()
            if data: self._send_uds_via_gateway(data, EAC_REQUEST_ADDR, EAC_RESPONSE_ADDR)
    
    def _eac_read_dtc(self):
        self.selected_ecu_key = 'EAC'
        self._read_dtc_via_gateway(EAC_REQUEST_ADDR, EAC_RESPONSE_ADDR, 'EAC')
    
    def _eac_clear_dtc(self):
        self.selected_ecu_key = 'EAC'
        self._clear_dtc_via_gateway(EAC_REQUEST_ADDR, EAC_RESPONSE_ADDR)
    
    def _eac_reset_ecu(self):
        self.selected_ecu_key = 'EAC'
        self._reset_ecu_via_gateway(EAC_REQUEST_ADDR, EAC_RESPONSE_ADDR)
    
    def _ecm_connect(self):
        self.selected_ecu_key = 'ECM'
        self.current_ecu = 'ECM'
        self._connect_to_icb_gateway()
    
    def _ecm_send_uds_raw(self):
        data = self._parse_hex_input()
        if not data: return
        self._send_uds_via_gateway(data, ECM_REQUEST_ADDR, ECM_RESPONSE_ADDR)
    
    def _ecm_send_cmd(self, cmd_name):
        self.selected_ecu_key = 'ECM'
        cmd_map = {
            'read_did': lambda: self._build_uds_cmd('22', self.ui.lineEdit_did_id.text()),
            'write_did': lambda: self._build_uds_cmd('2E', self.ui.lineEdit_did_id.text(), self.ui.lineEdit_did_data.text()),
            'io_control': lambda: self._build_uds_cmd('31', '01', self.ui.lineEdit_routine_id.text()),
            'routine': lambda: self._build_uds_cmd('31', '01', self.ui.lineEdit_routine_id.text()),
        }
        if cmd_name in cmd_map:
            data = cmd_map[cmd_name]()
            if data: self._send_uds_via_gateway(data, ECM_REQUEST_ADDR, ECM_RESPONSE_ADDR)
    
    def _ecm_read_dtc(self):
        self.selected_ecu_key = 'ECM'
        self._read_dtc_via_gateway(ECM_REQUEST_ADDR, ECM_RESPONSE_ADDR, 'ECM')
    
    def _ecm_clear_dtc(self):
        self.selected_ecu_key = 'ECM'
        self._clear_dtc_via_gateway(ECM_REQUEST_ADDR, ECM_RESPONSE_ADDR)
    
    def _ecm_reset_ecu(self):
        self.selected_ecu_key = 'ECM'
        self._reset_ecu_via_gateway(ECM_REQUEST_ADDR, ECM_RESPONSE_ADDR)
    
    def _ews_connect(self):
        self.selected_ecu_key = 'EWS'
        self.current_ecu = 'EWS'
        self._connect_to_icb_gateway()
    
    def _ews_send_uds_raw(self):
        data = self._parse_hex_input()
        if not data: return
        self._send_uds_via_gateway(data, EWS_REQUEST_ADDR, EWS_RESPONSE_ADDR)
    
    def _ews_send_cmd(self, cmd_name):
        self.selected_ecu_key = 'EWS'
        cmd_map = {
            'read_did': lambda: self._build_uds_cmd('22', self.ui.lineEdit_did_id.text()),
            'write_did': lambda: self._build_uds_cmd('2E', self.ui.lineEdit_did_id.text(), self.ui.lineEdit_did_data.text()),
            'io_control': lambda: self._build_uds_cmd('31', '01', self.ui.lineEdit_routine_id.text()),
            'routine': lambda: self._build_uds_cmd('31', '01', self.ui.lineEdit_routine_id.text()),
        }
        if cmd_name in cmd_map:
            data = cmd_map[cmd_name]()
            if data: self._send_uds_via_gateway(data, EWS_REQUEST_ADDR, EWS_RESPONSE_ADDR)
    
    def _ews_read_dtc(self):
        self.selected_ecu_key = 'EWS'
        self._read_dtc_via_gateway(EWS_REQUEST_ADDR, EWS_RESPONSE_ADDR, 'EWS')
    
    def _ews_clear_dtc(self):
        self.selected_ecu_key = 'EWS'
        self._clear_dtc_via_gateway(EWS_REQUEST_ADDR, EWS_RESPONSE_ADDR)
    
    def _ews_reset_ecu(self):
        self.selected_ecu_key = 'EWS'
        self._reset_ecu_via_gateway(EWS_REQUEST_ADDR, EWS_RESPONSE_ADDR)
    
    def _flsmmm_connect(self):
        self.selected_ecu_key = 'FLSMMM'
        self.current_ecu = 'FLSMMM'
        self._connect_to_icb_gateway()
    
    def _flsmmm_send_uds_raw(self):
        data = self._parse_hex_input()
        if not data: return
        self._send_uds_via_gateway(data, FLSMMM_REQUEST_ADDR, FLSMMM_RESPONSE_ADDR)
    
    def _flsmmm_send_cmd(self, cmd_name):
        self.selected_ecu_key = 'FLSMMM'
        cmd_map = {
            'read_did': lambda: self._build_uds_cmd('22', self.ui.lineEdit_did_id.text()),
            'write_did': lambda: self._build_uds_cmd('2E', self.ui.lineEdit_did_id.text(), self.ui.lineEdit_did_data.text()),
            'io_control': lambda: self._build_uds_cmd('31', '01', self.ui.lineEdit_routine_id.text()),
            'routine': lambda: self._build_uds_cmd('31', '01', self.ui.lineEdit_routine_id.text()),
        }
        if cmd_name in cmd_map:
            data = cmd_map[cmd_name]()
            if data: self._send_uds_via_gateway(data, FLSMMM_REQUEST_ADDR, FLSMMM_RESPONSE_ADDR)
    
    def _flsmmm_read_dtc(self):
        self.selected_ecu_key = 'FLSMMM'
        self._read_dtc_via_gateway(FLSMMM_REQUEST_ADDR, FLSMMM_RESPONSE_ADDR, 'FLSMMM')
    
    def _flsmmm_clear_dtc(self):
        self.selected_ecu_key = 'FLSMMM'
        self._clear_dtc_via_gateway(FLSMMM_REQUEST_ADDR, FLSMMM_RESPONSE_ADDR)
    
    def _flsmmm_reset_ecu(self):
        self.selected_ecu_key = 'FLSMMM'
        self._reset_ecu_via_gateway(FLSMMM_REQUEST_ADDR, FLSMMM_RESPONSE_ADDR)
    
    def _connect_ccu_doip(self):
        """CCU 通过 ICB 转发，复用 ICB 的连接"""
        if not self.diag_doip_connected or not self.diag_doip_client:
            self.append_log_color("🔗 正在连接 ICB 网关以转发 CCU...", "#2196F3")
            self._connect_doip_async("icb")
            return False
        self.ccu_doip_connected = True
        self.ccu_doip_client = self.diag_doip_client
        self.append_log_color("✅ CCU 网关已就绪 (共享 ICB 连接)", "#4CAF50")
        if self._diag_pending_action == 'dtc_read':
            self._diag_pending_action = None; self._ccu_read_dtc()
        elif self._diag_pending_action == 'dtc_clear':
            self._diag_pending_action = None; self._ccu_clear_dtc()
        elif self._diag_pending_action == 'reset':
            self._diag_pending_action = None; self._ccu_reset_ecu()
        elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
            cmd = self._diag_pending_cmd; self._diag_pending_action = None; self._diag_pending_cmd = None
            self._ccu_send_uds_cmd(cmd)
        return True

    def _ccu_send_uds_raw(self, data, timeout=2.0):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("⚠ CCU: 共享 ICB 连接未就绪", "#FF9800")
            return None
        try:
            resp = client.send_diagnostic(data, target_addr=CCU_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ CCU UDS 发送失败：{e}", "#FF9800")
            return None

    def _ccu_send_uds_cmd(self, cmd_text):
        import re, time
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ CCU: 共享 ICB 连接未就绪", "#FF5252")
            return
        lines_list = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines_list:
            if '#' in line: line = line.split('#')[0].strip()
            if '//' in line: line = line.split('//')[0].strip()
            if not line: continue
            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"💤 Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue
            hex_str = line.replace(' ', '').replace('\t', '')
            try: uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue
            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{CCU_PHYSICAL_ADDR:04X} {formatted_tx}", "#64B5F6")
            QApplication.processEvents()
            resp = self._ccu_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    if nrc == 0x78:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{CCU_FUNCTIONAL_ADDR:04X} {formatted_rx} ⏳ {nrc_desc}", "#FF9800")
                    else:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{CCU_FUNCTIONAL_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{CCU_FUNCTIONAL_ADDR:04X} {formatted_rx}", "#81C784")
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        key_val = sa_calc.calc_key(seed_hex, CCU_SECURITY_ALGO)
                        if client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key_val
                            f2tx = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x{CCU_PHYSICAL_ADDR:04X} {f2tx}  🔑 自动发送 KEY", "#64B5F6")
                            QApplication.processEvents()
                            resp2 = None
                            for retry in range(10):
                                resp2 = self._ccu_send_uds_raw(cmd_27_02, timeout=2.0)
                                if resp2:
                                    if len(resp2) >= 3 and resp2[0] == 0x7F and resp2[2] == 0x78:
                                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{CCU_FUNCTIONAL_ADDR:04X} 7F 27 78 ⏳ Response Pending，等待中...", "#FF9800")
                                        time.sleep(0.5)
                                        continue
                                    break
                                time.sleep(0.3)
                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{CCU_FUNCTIONAL_ADDR:04X} {f2} ✅ 安全认证成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{CCU_FUNCTIONAL_ADDR:04X} {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{CCU_FUNCTIONAL_ADDR:04X} {f2} ❌ 安全认证失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    def _ccu_read_dtc(self):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("ICB 未连接，无法转发 CCU 诊断", "#FF5252")
            return
        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{CCU_PHYSICAL_ADDR:04X} 19 02 2C", "#64B5F6")
            QApplication.processEvents()
            resp = self._ccu_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=2.0)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return
            formatted_rx = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x{CCU_FUNCTIONAL_ADDR:04X} {formatted_rx}", "#81C784")
            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color(f"  ℹ️ 无有效 DTC", "#81C784")
                return
            self.append_log_color(f"  📊 共找到 {len(dtc_records)} 个 DTC，正在查询详情...", "#2196F3")
            QApplication.processEvents()
            for dtc in dtc_records:
                dtc_label = dtc['label']
                ts = self._diag_timestamp()
                self.append_log_color(f"{ts} tx 0x{CCU_PHYSICAL_ADDR:04X} 19 04 {dtc_label}", "#64B5F6")
                QApplication.processEvents()
                snap_resp = self._ccu_send_uds_raw(bytes.fromhex(f"1904{dtc_label.replace(' ','')}"), timeout=1.0)
                if snap_resp: dtc['snapshot_raw'] = snap_resp.hex()
                ts = self._diag_timestamp()
                self.append_log_color(f"{ts} tx 0x{CCU_PHYSICAL_ADDR:04X} 19 06 {dtc_label}", "#64B5F6")
                QApplication.processEvents()
                ext_resp = self._ccu_send_uds_raw(bytes.fromhex(f"1906{dtc_label.replace(' ','')}01"), timeout=1.0)
                if ext_resp: dtc['extended_raw'] = ext_resp.hex()
            self._display_dtc_table(dtc_records)
            self._save_dtc_excel(dtc_records)
        except Exception as e:
            self._diag_on_socket_error(e)

    def _ccu_clear_dtc(self):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("ICB 未连接，无法转发 CCU 诊断", "#FF5252")
            return
        try:
            cmd_14 = bytes([0x14, 0xFF, 0xFF, 0xFF])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{CCU_PHYSICAL_ADDR:04X} 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()
            resp = self._ccu_send_uds_raw(cmd_14, timeout=2.0)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x54:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{CCU_FUNCTIONAL_ADDR:04X} {formatted_rx} ✅ DTC 清除成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{CCU_FUNCTIONAL_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 清除超时", "#FF5252")
        except Exception as e:
            self._diag_on_socket_error(e)

    def _ccu_reset_ecu(self):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("ICB 未连接，无法转发 CCU 诊断", "#FF5252")
            return
        try:
            cmd_11_01 = bytes([0x11, 0x01])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{CCU_PHYSICAL_ADDR:04X} 11 01", "#64B5F6")
            QApplication.processEvents()
            resp = self._ccu_send_uds_raw(cmd_11_01, timeout=2.0)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x51:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{CCU_FUNCTIONAL_ADDR:04X} {formatted_rx} ✅ ECU 复位成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{CCU_FUNCTIONAL_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ ECU 复位超时", "#FF5252")
        except Exception as e:
            self._diag_on_socket_error(e)



    def _connect_hodm_doip(self):
        """HODM 通过 ICB 转发，复用 ICB 的连接"""
        if not self.diag_doip_connected or not self.diag_doip_client:
            self.append_log_color("🔗 正在连接 ICB 网关以转发 HODM...", "#2196F3")
            self._connect_doip_async("icb")
            return False
        self.hodm_doip_connected = True
        self.hodm_doip_client = self.diag_doip_client
        self.append_log_color("✅ HODM 网关已就绪 (共享 ICB 连接)", "#4CAF50")
        if self._diag_pending_action == 'dtc_read':
            self._diag_pending_action = None; self._hodm_read_dtc()
        elif self._diag_pending_action == 'dtc_clear':
            self._diag_pending_action = None; self._hodm_clear_dtc()
        elif self._diag_pending_action == 'reset':
            self._diag_pending_action = None; self._hodm_reset_ecu()
        elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
            cmd = self._diag_pending_cmd; self._diag_pending_action = None; self._diag_pending_cmd = None
            self._hodm_send_uds_cmd(cmd)
        return True

    def _hodm_send_uds_raw(self, data, timeout=2.0):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("⚠ HODM: 共享 ICB 连接未就绪", "#FF9800")
            return None
        try:
            resp = client.send_diagnostic(data, target_addr=HODM_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ HODM UDS 发送失败：{e}", "#FF9800")
            return None

    def _hodm_send_uds_cmd(self, cmd_text):
        import re, time
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ HODM: 共享 ICB 连接未就绪", "#FF5252")
            return
        lines_list = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines_list:
            if '#' in line: line = line.split('#')[0].strip()
            if '//' in line: line = line.split('//')[0].strip()
            if not line: continue
            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"💤 Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue
            hex_str = line.replace(' ', '').replace('\t', '')
            try: uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue
            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{HODM_PHYSICAL_ADDR:04X} {formatted_tx}", "#64B5F6")
            QApplication.processEvents()
            resp = self._hodm_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    if nrc == 0x78:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{HODM_FUNCTIONAL_ADDR:04X} {formatted_rx} ⏳ {nrc_desc}", "#FF9800")
                    else:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{HODM_FUNCTIONAL_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{HODM_FUNCTIONAL_ADDR:04X} {formatted_rx}", "#81C784")
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        key_val = sa_calc.calc_key(seed_hex, HODM_SECURITY_ALGO)
                        if client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key_val
                            f2tx = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x{HODM_PHYSICAL_ADDR:04X} {f2tx}  🔑 自动发送 KEY", "#64B5F6")
                            QApplication.processEvents()
                            resp2 = None
                            for retry in range(10):
                                resp2 = self._hodm_send_uds_raw(cmd_27_02, timeout=2.0)
                                if resp2:
                                    if len(resp2) >= 3 and resp2[0] == 0x7F and resp2[2] == 0x78:
                                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{HODM_FUNCTIONAL_ADDR:04X} 7F 27 78 ⏳ Response Pending，等待中...", "#FF9800")
                                        time.sleep(0.5)
                                        continue
                                    break
                                time.sleep(0.3)
                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{HODM_FUNCTIONAL_ADDR:04X} {f2} ✅ 安全认证成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{HODM_FUNCTIONAL_ADDR:04X} {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{HODM_FUNCTIONAL_ADDR:04X} {f2} ❌ 安全认证失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    def _hodm_read_dtc(self):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("ICB 未连接，无法转发 HODM 诊断", "#FF5252")
            return
        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{HODM_PHYSICAL_ADDR:04X} 19 02 2C", "#64B5F6")
            QApplication.processEvents()
            resp = self._hodm_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=2.0)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return
            formatted_rx = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x{HODM_FUNCTIONAL_ADDR:04X} {formatted_rx}", "#81C784")
            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color(f"  ℹ️ 无有效 DTC", "#81C784")
                return
            self.append_log_color(f"  📊 共找到 {len(dtc_records)} 个 DTC，正在查询详情...", "#2196F3")
            QApplication.processEvents()
            for dtc in dtc_records:
                dtc_label = dtc['label']
                ts = self._diag_timestamp()
                self.append_log_color(f"{ts} tx 0x{HODM_PHYSICAL_ADDR:04X} 19 04 {dtc_label}", "#64B5F6")
                QApplication.processEvents()
                snap_resp = self._hodm_send_uds_raw(bytes.fromhex(f"1904{dtc_label.replace(' ','')}"), timeout=1.0)
                if snap_resp: dtc['snapshot_raw'] = snap_resp.hex()
                ts = self._diag_timestamp()
                self.append_log_color(f"{ts} tx 0x{HODM_PHYSICAL_ADDR:04X} 19 06 {dtc_label}", "#64B5F6")
                QApplication.processEvents()
                ext_resp = self._hodm_send_uds_raw(bytes.fromhex(f"1906{dtc_label.replace(' ','')}01"), timeout=1.0)
                if ext_resp: dtc['extended_raw'] = ext_resp.hex()
            self._display_dtc_table(dtc_records)
            self._save_dtc_excel(dtc_records)
        except Exception as e:
            self._diag_on_socket_error(e)

    def _hodm_clear_dtc(self):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("ICB 未连接，无法转发 HODM 诊断", "#FF5252")
            return
        try:
            cmd_14 = bytes([0x14, 0xFF, 0xFF, 0xFF])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{HODM_PHYSICAL_ADDR:04X} 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()
            resp = self._hodm_send_uds_raw(cmd_14, timeout=2.0)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x54:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{HODM_FUNCTIONAL_ADDR:04X} {formatted_rx} ✅ DTC 清除成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{HODM_FUNCTIONAL_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 清除超时", "#FF5252")
        except Exception as e:
            self._diag_on_socket_error(e)

    def _hodm_reset_ecu(self):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("ICB 未连接，无法转发 HODM 诊断", "#FF5252")
            return
        try:
            cmd_11_01 = bytes([0x11, 0x01])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{HODM_PHYSICAL_ADDR:04X} 11 01", "#64B5F6")
            QApplication.processEvents()
            resp = self._hodm_send_uds_raw(cmd_11_01, timeout=2.0)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x51:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{HODM_FUNCTIONAL_ADDR:04X} {formatted_rx} ✅ ECU 复位成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{HODM_FUNCTIONAL_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ ECU 复位超时", "#FF5252")
        except Exception as e:
            self._diag_on_socket_error(e)



    def _connect_lvbm_doip(self):
        """LVBM 通过 ICB 转发，复用 ICB 的连接"""
        if not self.diag_doip_connected or not self.diag_doip_client:
            self.append_log_color("🔗 正在连接 ICB 网关以转发 LVBM...", "#2196F3")
            self._connect_doip_async("icb")
            return False
        self.lvbm_doip_connected = True
        self.lvbm_doip_client = self.diag_doip_client
        self.append_log_color("✅ LVBM 网关已就绪 (共享 ICB 连接)", "#4CAF50")
        if self._diag_pending_action == 'dtc_read':
            self._diag_pending_action = None; self._lvbm_read_dtc()
        elif self._diag_pending_action == 'dtc_clear':
            self._diag_pending_action = None; self._lvbm_clear_dtc()
        elif self._diag_pending_action == 'reset':
            self._diag_pending_action = None; self._lvbm_reset_ecu()
        elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
            cmd = self._diag_pending_cmd; self._diag_pending_action = None; self._diag_pending_cmd = None
            self._lvbm_send_uds_cmd(cmd)
        return True

    def _lvbm_send_uds_raw(self, data, timeout=2.0):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("⚠ LVBM: 共享 ICB 连接未就绪", "#FF9800")
            return None
        try:
            resp = client.send_diagnostic(data, target_addr=LVBM_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ LVBM UDS 发送失败：{e}", "#FF9800")
            return None

    def _lvbm_send_uds_cmd(self, cmd_text):
        import re, time
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ LVBM: 共享 ICB 连接未就绪", "#FF5252")
            return
        lines_list = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines_list:
            if '#' in line: line = line.split('#')[0].strip()
            if '//' in line: line = line.split('//')[0].strip()
            if not line: continue
            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"💤 Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue
            hex_str = line.replace(' ', '').replace('\t', '')
            try: uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue
            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{LVBM_PHYSICAL_ADDR:04X} {formatted_tx}", "#64B5F6")
            QApplication.processEvents()
            resp = self._lvbm_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    if nrc == 0x78:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{LVBM_FUNCTIONAL_ADDR:04X} {formatted_rx} ⏳ {nrc_desc}", "#FF9800")
                    else:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{LVBM_FUNCTIONAL_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{LVBM_FUNCTIONAL_ADDR:04X} {formatted_rx}", "#81C784")
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        key_val = sa_calc.calc_key(seed_hex, LVBM_SECURITY_ALGO)
                        if client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key_val
                            f2tx = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x{LVBM_PHYSICAL_ADDR:04X} {f2tx}  🔑 自动发送 KEY", "#64B5F6")
                            QApplication.processEvents()
                            resp2 = None
                            for retry in range(10):
                                resp2 = self._lvbm_send_uds_raw(cmd_27_02, timeout=2.0)
                                if resp2:
                                    if len(resp2) >= 3 and resp2[0] == 0x7F and resp2[2] == 0x78:
                                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{LVBM_FUNCTIONAL_ADDR:04X} 7F 27 78 ⏳ Response Pending，等待中...", "#FF9800")
                                        time.sleep(0.5)
                                        continue
                                    break
                                time.sleep(0.3)
                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{LVBM_FUNCTIONAL_ADDR:04X} {f2} ✅ 安全认证成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{LVBM_FUNCTIONAL_ADDR:04X} {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{LVBM_FUNCTIONAL_ADDR:04X} {f2} ❌ 安全认证失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    def _lvbm_read_dtc(self):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("ICB 未连接，无法转发 LVBM 诊断", "#FF5252")
            return
        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{LVBM_PHYSICAL_ADDR:04X} 19 02 2C", "#64B5F6")
            QApplication.processEvents()
            resp = self._lvbm_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=2.0)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return
            formatted_rx = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x{LVBM_FUNCTIONAL_ADDR:04X} {formatted_rx}", "#81C784")
            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color(f"  ℹ️ 无有效 DTC", "#81C784")
                return
            self.append_log_color(f"  📊 共找到 {len(dtc_records)} 个 DTC，正在查询详情...", "#2196F3")
            QApplication.processEvents()
            for dtc in dtc_records:
                dtc_label = dtc['label']
                ts = self._diag_timestamp()
                self.append_log_color(f"{ts} tx 0x{LVBM_PHYSICAL_ADDR:04X} 19 04 {dtc_label}", "#64B5F6")
                QApplication.processEvents()
                snap_resp = self._lvbm_send_uds_raw(bytes.fromhex(f"1904{dtc_label.replace(' ','')}"), timeout=1.0)
                if snap_resp: dtc['snapshot_raw'] = snap_resp.hex()
                ts = self._diag_timestamp()
                self.append_log_color(f"{ts} tx 0x{LVBM_PHYSICAL_ADDR:04X} 19 06 {dtc_label}", "#64B5F6")
                QApplication.processEvents()
                ext_resp = self._lvbm_send_uds_raw(bytes.fromhex(f"1906{dtc_label.replace(' ','')}01"), timeout=1.0)
                if ext_resp: dtc['extended_raw'] = ext_resp.hex()
            self._display_dtc_table(dtc_records)
            self._save_dtc_excel(dtc_records)
        except Exception as e:
            self._diag_on_socket_error(e)

    def _lvbm_clear_dtc(self):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("ICB 未连接，无法转发 LVBM 诊断", "#FF5252")
            return
        try:
            cmd_14 = bytes([0x14, 0xFF, 0xFF, 0xFF])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{LVBM_PHYSICAL_ADDR:04X} 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()
            resp = self._lvbm_send_uds_raw(cmd_14, timeout=2.0)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x54:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{LVBM_FUNCTIONAL_ADDR:04X} {formatted_rx} ✅ DTC 清除成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{LVBM_FUNCTIONAL_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 清除超时", "#FF5252")
        except Exception as e:
            self._diag_on_socket_error(e)

    def _lvbm_reset_ecu(self):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("ICB 未连接，无法转发 LVBM 诊断", "#FF5252")
            return
        try:
            cmd_11_01 = bytes([0x11, 0x01])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{LVBM_PHYSICAL_ADDR:04X} 11 01", "#64B5F6")
            QApplication.processEvents()
            resp = self._lvbm_send_uds_raw(cmd_11_01, timeout=2.0)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x51:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{LVBM_FUNCTIONAL_ADDR:04X} {formatted_rx} ✅ ECU 复位成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{LVBM_FUNCTIONAL_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ ECU 复位超时", "#FF5252")
        except Exception as e:
            self._diag_on_socket_error(e)



    def _connect_nfcam_doip(self):
        """NFCAM 通过 ICB 转发，复用 ICB 的连接"""
        if not self.diag_doip_connected or not self.diag_doip_client:
            self.append_log_color("🔗 正在连接 ICB 网关以转发 NFCAM...", "#2196F3")
            self._connect_doip_async("icb")
            return False
        self.nfcam_doip_connected = True
        self.nfcam_doip_client = self.diag_doip_client
        self.append_log_color("✅ NFCAM 网关已就绪 (共享 ICB 连接)", "#4CAF50")
        if self._diag_pending_action == 'dtc_read':
            self._diag_pending_action = None; self._nfcam_read_dtc()
        elif self._diag_pending_action == 'dtc_clear':
            self._diag_pending_action = None; self._nfcam_clear_dtc()
        elif self._diag_pending_action == 'reset':
            self._diag_pending_action = None; self._nfcam_reset_ecu()
        elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
            cmd = self._diag_pending_cmd; self._diag_pending_action = None; self._diag_pending_cmd = None
            self._nfcam_send_uds_cmd(cmd)
        return True

    def _nfcam_send_uds_raw(self, data, timeout=2.0):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("⚠ NFCAM: 共享 ICB 连接未就绪", "#FF9800")
            return None
        try:
            resp = client.send_diagnostic(data, target_addr=NFCAM_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ NFCAM UDS 发送失败：{e}", "#FF9800")
            return None

    def _nfcam_send_uds_cmd(self, cmd_text):
        import re, time
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ NFCAM: 共享 ICB 连接未就绪", "#FF5252")
            return
        lines_list = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines_list:
            if '#' in line: line = line.split('#')[0].strip()
            if '//' in line: line = line.split('//')[0].strip()
            if not line: continue
            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"💤 Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue
            hex_str = line.replace(' ', '').replace('\t', '')
            try: uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue
            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{NFCAM_PHYSICAL_ADDR:04X} {formatted_tx}", "#64B5F6")
            QApplication.processEvents()
            resp = self._nfcam_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    if nrc == 0x78:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{NFCAM_FUNCTIONAL_ADDR:04X} {formatted_rx} ⏳ {nrc_desc}", "#FF9800")
                    else:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{NFCAM_FUNCTIONAL_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{NFCAM_FUNCTIONAL_ADDR:04X} {formatted_rx}", "#81C784")
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        key_val = sa_calc.calc_key(seed_hex, NFCAM_SECURITY_ALGO)
                        if client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key_val
                            f2tx = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x{NFCAM_PHYSICAL_ADDR:04X} {f2tx}  🔑 自动发送 KEY", "#64B5F6")
                            QApplication.processEvents()
                            resp2 = None
                            for retry in range(10):
                                resp2 = self._nfcam_send_uds_raw(cmd_27_02, timeout=2.0)
                                if resp2:
                                    if len(resp2) >= 3 and resp2[0] == 0x7F and resp2[2] == 0x78:
                                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{NFCAM_FUNCTIONAL_ADDR:04X} 7F 27 78 ⏳ Response Pending，等待中...", "#FF9800")
                                        time.sleep(0.5)
                                        continue
                                    break
                                time.sleep(0.3)
                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{NFCAM_FUNCTIONAL_ADDR:04X} {f2} ✅ 安全认证成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{NFCAM_FUNCTIONAL_ADDR:04X} {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{NFCAM_FUNCTIONAL_ADDR:04X} {f2} ❌ 安全认证失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    def _nfcam_read_dtc(self):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("ICB 未连接，无法转发 NFCAM 诊断", "#FF5252")
            return
        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{NFCAM_PHYSICAL_ADDR:04X} 19 02 2C", "#64B5F6")
            QApplication.processEvents()
            resp = self._nfcam_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=2.0)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return
            formatted_rx = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x{NFCAM_FUNCTIONAL_ADDR:04X} {formatted_rx}", "#81C784")
            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color(f"  ℹ️ 无有效 DTC", "#81C784")
                return
            self.append_log_color(f"  📊 共找到 {len(dtc_records)} 个 DTC，正在查询详情...", "#2196F3")
            QApplication.processEvents()
            for dtc in dtc_records:
                dtc_label = dtc['label']
                ts = self._diag_timestamp()
                self.append_log_color(f"{ts} tx 0x{NFCAM_PHYSICAL_ADDR:04X} 19 04 {dtc_label}", "#64B5F6")
                QApplication.processEvents()
                snap_resp = self._nfcam_send_uds_raw(bytes.fromhex(f"1904{dtc_label.replace(' ','')}"), timeout=1.0)
                if snap_resp: dtc['snapshot_raw'] = snap_resp.hex()
                ts = self._diag_timestamp()
                self.append_log_color(f"{ts} tx 0x{NFCAM_PHYSICAL_ADDR:04X} 19 06 {dtc_label}", "#64B5F6")
                QApplication.processEvents()
                ext_resp = self._nfcam_send_uds_raw(bytes.fromhex(f"1906{dtc_label.replace(' ','')}01"), timeout=1.0)
                if ext_resp: dtc['extended_raw'] = ext_resp.hex()
            self._display_dtc_table(dtc_records)
            self._save_dtc_excel(dtc_records)
        except Exception as e:
            self._diag_on_socket_error(e)

    def _nfcam_clear_dtc(self):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("ICB 未连接，无法转发 NFCAM 诊断", "#FF5252")
            return
        try:
            cmd_14 = bytes([0x14, 0xFF, 0xFF, 0xFF])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{NFCAM_PHYSICAL_ADDR:04X} 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()
            resp = self._nfcam_send_uds_raw(cmd_14, timeout=2.0)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x54:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{NFCAM_FUNCTIONAL_ADDR:04X} {formatted_rx} ✅ DTC 清除成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{NFCAM_FUNCTIONAL_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 清除超时", "#FF5252")
        except Exception as e:
            self._diag_on_socket_error(e)

    def _nfcam_reset_ecu(self):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("ICB 未连接，无法转发 NFCAM 诊断", "#FF5252")
            return
        try:
            cmd_11_01 = bytes([0x11, 0x01])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{NFCAM_PHYSICAL_ADDR:04X} 11 01", "#64B5F6")
            QApplication.processEvents()
            resp = self._nfcam_send_uds_raw(cmd_11_01, timeout=2.0)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x51:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{NFCAM_FUNCTIONAL_ADDR:04X} {formatted_rx} ✅ ECU 复位成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{NFCAM_FUNCTIONAL_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ ECU 复位超时", "#FF5252")
        except Exception as e:
            self._diag_on_socket_error(e)



    def _connect_tc_doip(self):
        """TC 通过 ICB 转发，复用 ICB 的连接"""
        if not self.diag_doip_connected or not self.diag_doip_client:
            self.append_log_color("🔗 正在连接 ICB 网关以转发 TC...", "#2196F3")
            self._connect_doip_async("icb")
            return False
        self.tc_doip_connected = True
        self.tc_doip_client = self.diag_doip_client
        self.append_log_color("✅ TC 网关已就绪 (共享 ICB 连接)", "#4CAF50")
        if self._diag_pending_action == 'dtc_read':
            self._diag_pending_action = None; self._tc_read_dtc()
        elif self._diag_pending_action == 'dtc_clear':
            self._diag_pending_action = None; self._tc_clear_dtc()
        elif self._diag_pending_action == 'reset':
            self._diag_pending_action = None; self._tc_reset_ecu()
        elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
            cmd = self._diag_pending_cmd; self._diag_pending_action = None; self._diag_pending_cmd = None
            self._tc_send_uds_cmd(cmd)
        return True

    def _tc_send_uds_raw(self, data, timeout=2.0):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("⚠ TC: 共享 ICB 连接未就绪", "#FF9800")
            return None
        try:
            resp = client.send_diagnostic(data, target_addr=TC_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ TC UDS 发送失败：{e}", "#FF9800")
            return None

    def _tc_send_uds_cmd(self, cmd_text):
        import re, time
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ TC: 共享 ICB 连接未就绪", "#FF5252")
            return
        lines_list = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines_list:
            if '#' in line: line = line.split('#')[0].strip()
            if '//' in line: line = line.split('//')[0].strip()
            if not line: continue
            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"💤 Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue
            hex_str = line.replace(' ', '').replace('\t', '')
            try: uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue
            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{TC_PHYSICAL_ADDR:04X} {formatted_tx}", "#64B5F6")
            QApplication.processEvents()
            resp = self._tc_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    if nrc == 0x78:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{TC_FUNCTIONAL_ADDR:04X} {formatted_rx} ⏳ {nrc_desc}", "#FF9800")
                    else:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{TC_FUNCTIONAL_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{TC_FUNCTIONAL_ADDR:04X} {formatted_rx}", "#81C784")
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        key_val = sa_calc.calc_key(seed_hex, TC_SECURITY_ALGO)
                        if client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key_val
                            f2tx = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x{TC_PHYSICAL_ADDR:04X} {f2tx}  🔑 自动发送 KEY", "#64B5F6")
                            QApplication.processEvents()
                            resp2 = None
                            for retry in range(10):
                                resp2 = self._tc_send_uds_raw(cmd_27_02, timeout=2.0)
                                if resp2:
                                    if len(resp2) >= 3 and resp2[0] == 0x7F and resp2[2] == 0x78:
                                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{TC_FUNCTIONAL_ADDR:04X} 7F 27 78 ⏳ Response Pending，等待中...", "#FF9800")
                                        time.sleep(0.5)
                                        continue
                                    break
                                time.sleep(0.3)
                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{TC_FUNCTIONAL_ADDR:04X} {f2} ✅ 安全认证成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{TC_FUNCTIONAL_ADDR:04X} {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{TC_FUNCTIONAL_ADDR:04X} {f2} ❌ 安全认证失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    def _tc_read_dtc(self):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("ICB 未连接，无法转发 TC 诊断", "#FF5252")
            return
        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{TC_PHYSICAL_ADDR:04X} 19 02 2C", "#64B5F6")
            QApplication.processEvents()
            resp = self._tc_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=2.0)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return
            formatted_rx = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x{TC_FUNCTIONAL_ADDR:04X} {formatted_rx}", "#81C784")
            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color(f"  ℹ️ 无有效 DTC", "#81C784")
                return
            self.append_log_color(f"  📊 共找到 {len(dtc_records)} 个 DTC，正在查询详情...", "#2196F3")
            QApplication.processEvents()
            for dtc in dtc_records:
                dtc_label = dtc['label']
                ts = self._diag_timestamp()
                self.append_log_color(f"{ts} tx 0x{TC_PHYSICAL_ADDR:04X} 19 04 {dtc_label}", "#64B5F6")
                QApplication.processEvents()
                snap_resp = self._tc_send_uds_raw(bytes.fromhex(f"1904{dtc_label.replace(' ','')}"), timeout=1.0)
                if snap_resp: dtc['snapshot_raw'] = snap_resp.hex()
                ts = self._diag_timestamp()
                self.append_log_color(f"{ts} tx 0x{TC_PHYSICAL_ADDR:04X} 19 06 {dtc_label}", "#64B5F6")
                QApplication.processEvents()
                ext_resp = self._tc_send_uds_raw(bytes.fromhex(f"1906{dtc_label.replace(' ','')}01"), timeout=1.0)
                if ext_resp: dtc['extended_raw'] = ext_resp.hex()
            self._display_dtc_table(dtc_records)
            self._save_dtc_excel(dtc_records)
        except Exception as e:
            self._diag_on_socket_error(e)

    def _tc_clear_dtc(self):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("ICB 未连接，无法转发 TC 诊断", "#FF5252")
            return
        try:
            cmd_14 = bytes([0x14, 0xFF, 0xFF, 0xFF])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{TC_PHYSICAL_ADDR:04X} 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()
            resp = self._tc_send_uds_raw(cmd_14, timeout=2.0)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x54:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{TC_FUNCTIONAL_ADDR:04X} {formatted_rx} ✅ DTC 清除成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{TC_FUNCTIONAL_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 清除超时", "#FF5252")
        except Exception as e:
            self._diag_on_socket_error(e)

    def _tc_reset_ecu(self):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("ICB 未连接，无法转发 TC 诊断", "#FF5252")
            return
        try:
            cmd_11_01 = bytes([0x11, 0x01])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{TC_PHYSICAL_ADDR:04X} 11 01", "#64B5F6")
            QApplication.processEvents()
            resp = self._tc_send_uds_raw(cmd_11_01, timeout=2.0)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x51:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{TC_FUNCTIONAL_ADDR:04X} {formatted_rx} ✅ ECU 复位成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{TC_FUNCTIONAL_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ ECU 复位超时", "#FF5252")
        except Exception as e:
            self._diag_on_socket_error(e)



    def _connect_tdm_doip(self):
        """TDM 通过 ICB 转发，复用 ICB 的连接"""
        if not self.diag_doip_connected or not self.diag_doip_client:
            self.append_log_color("🔗 正在连接 ICB 网关以转发 TDM...", "#2196F3")
            self._connect_doip_async("icb")
            return False
        self.tdm_doip_connected = True
        self.tdm_doip_client = self.diag_doip_client
        self.append_log_color("✅ TDM 网关已就绪 (共享 ICB 连接)", "#4CAF50")
        if self._diag_pending_action == 'dtc_read':
            self._diag_pending_action = None; self._tdm_read_dtc()
        elif self._diag_pending_action == 'dtc_clear':
            self._diag_pending_action = None; self._tdm_clear_dtc()
        elif self._diag_pending_action == 'reset':
            self._diag_pending_action = None; self._tdm_reset_ecu()
        elif self._diag_pending_action == 'cmd' and self._diag_pending_cmd:
            cmd = self._diag_pending_cmd; self._diag_pending_action = None; self._diag_pending_cmd = None
            self._tdm_send_uds_cmd(cmd)
        return True

    def _tdm_send_uds_raw(self, data, timeout=2.0):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("⚠ TDM: 共享 ICB 连接未就绪", "#FF9800")
            return None
        try:
            resp = client.send_diagnostic(data, target_addr=TDM_PHYSICAL_ADDR, timeout=timeout)
            return resp if resp else None
        except Exception as e:
            self.append_log_color(f"⚠ TDM UDS 发送失败：{e}", "#FF9800")
            return None

    def _tdm_send_uds_cmd(self, cmd_text):
        import re, time
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ TDM: 共享 ICB 连接未就绪", "#FF5252")
            return
        lines_list = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines_list:
            if '#' in line: line = line.split('#')[0].strip()
            if '//' in line: line = line.split('//')[0].strip()
            if not line: continue
            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"💤 Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue
            hex_str = line.replace(' ', '').replace('\t', '')
            try: uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue
            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{TDM_PHYSICAL_ADDR:04X} {formatted_tx}", "#64B5F6")
            QApplication.processEvents()
            resp = self._tdm_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    if nrc == 0x78:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{TDM_FUNCTIONAL_ADDR:04X} {formatted_rx} ⏳ {nrc_desc}", "#FF9800")
                    else:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{TDM_FUNCTIONAL_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{TDM_FUNCTIONAL_ADDR:04X} {formatted_rx}", "#81C784")
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        key_val = sa_calc.calc_key(seed_hex, TDM_SECURITY_ALGO)
                        if client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key_val
                            f2tx = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x{TDM_PHYSICAL_ADDR:04X} {f2tx}  🔑 自动发送 KEY", "#64B5F6")
                            QApplication.processEvents()
                            resp2 = None
                            for retry in range(10):
                                resp2 = self._tdm_send_uds_raw(cmd_27_02, timeout=2.0)
                                if resp2:
                                    if len(resp2) >= 3 and resp2[0] == 0x7F and resp2[2] == 0x78:
                                        self.append_log_color(f"{self._diag_timestamp()} rx 0x{TDM_FUNCTIONAL_ADDR:04X} 7F 27 78 ⏳ Response Pending，等待中...", "#FF9800")
                                        time.sleep(0.5)
                                        continue
                                    break
                                time.sleep(0.3)
                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{TDM_FUNCTIONAL_ADDR:04X} {f2} ✅ 安全认证成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{TDM_FUNCTIONAL_ADDR:04X} {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{TDM_FUNCTIONAL_ADDR:04X} {f2} ❌ 安全认证失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    def _tdm_read_dtc(self):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("ICB 未连接，无法转发 TDM 诊断", "#FF5252")
            return
        try:
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{TDM_PHYSICAL_ADDR:04X} 19 02 2C", "#64B5F6")
            QApplication.processEvents()
            resp = self._tdm_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=2.0)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return
            formatted_rx = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x{TDM_FUNCTIONAL_ADDR:04X} {formatted_rx}", "#81C784")
            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color(f"  ℹ️ 无有效 DTC", "#81C784")
                return
            self.append_log_color(f"  📊 共找到 {len(dtc_records)} 个 DTC，正在查询详情...", "#2196F3")
            QApplication.processEvents()
            for dtc in dtc_records:
                dtc_label = dtc['label']
                ts = self._diag_timestamp()
                self.append_log_color(f"{ts} tx 0x{TDM_PHYSICAL_ADDR:04X} 19 04 {dtc_label}", "#64B5F6")
                QApplication.processEvents()
                snap_resp = self._tdm_send_uds_raw(bytes.fromhex(f"1904{dtc_label.replace(' ','')}"), timeout=1.0)
                if snap_resp: dtc['snapshot_raw'] = snap_resp.hex()
                ts = self._diag_timestamp()
                self.append_log_color(f"{ts} tx 0x{TDM_PHYSICAL_ADDR:04X} 19 06 {dtc_label}", "#64B5F6")
                QApplication.processEvents()
                ext_resp = self._tdm_send_uds_raw(bytes.fromhex(f"1906{dtc_label.replace(' ','')}01"), timeout=1.0)
                if ext_resp: dtc['extended_raw'] = ext_resp.hex()
            self._display_dtc_table(dtc_records)
            self._save_dtc_excel(dtc_records)
        except Exception as e:
            self._diag_on_socket_error(e)

    def _tdm_clear_dtc(self):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("ICB 未连接，无法转发 TDM 诊断", "#FF5252")
            return
        try:
            cmd_14 = bytes([0x14, 0xFF, 0xFF, 0xFF])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{TDM_PHYSICAL_ADDR:04X} 14 FF FF FF", "#64B5F6")
            QApplication.processEvents()
            resp = self._tdm_send_uds_raw(cmd_14, timeout=2.0)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x54:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{TDM_FUNCTIONAL_ADDR:04X} {formatted_rx} ✅ DTC 清除成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{TDM_FUNCTIONAL_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 清除超时", "#FF5252")
        except Exception as e:
            self._diag_on_socket_error(e)

    def _tdm_reset_ecu(self):
        client = self.diag_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("ICB 未连接，无法转发 TDM 诊断", "#FF5252")
            return
        try:
            cmd_11_01 = bytes([0x11, 0x01])
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{TDM_PHYSICAL_ADDR:04X} 11 01", "#64B5F6")
            QApplication.processEvents()
            resp = self._tdm_send_uds_raw(cmd_11_01, timeout=2.0)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x51:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{TDM_FUNCTIONAL_ADDR:04X} {formatted_rx} ✅ ECU 复位成功", "#4CAF50")
                elif resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x{TDM_FUNCTIONAL_ADDR:04X} {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ ECU 复位超时", "#FF5252")
        except Exception as e:
            self._diag_on_socket_error(e)



    def _iam_send_uds_cmd(self, cmd_text: str):
        """通过 DoIP 发送 UDS 诊断指令到 IAM"""
        import re
        import time

        client = self.iam_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ IAM 未连接", "#FF5252")
            return

        lines = [l.strip() for l in cmd_text.split('\n') if l.strip()]
        for line in lines:
            # 去除注释
            if '#' in line:
                line = line.split('#')[0].strip()
            if '//' in line:
                line = line.split('//')[0].strip()
            if not line:
                continue

            # 检查是否是 sleep 命令
            sleep_match = re.match(r'^sleep\s+(\d+)$', line.strip(), re.IGNORECASE)
            if sleep_match:
                sleep_seconds = int(sleep_match.group(1))
                self.append_log_color(f"⏳ Sleep {sleep_seconds}秒...", "#FF9800")
                QApplication.processEvents()
                start = time.time()
                while time.time() - start < sleep_seconds:
                    time.sleep(0.1)
                    QApplication.processEvents()
                self.append_log_color("✅ Sleep 完成", "#4CAF50")
                QApplication.processEvents()
                continue

            # 去除空格
            hex_str = line.replace(' ', '').replace('\t', '')

            try:
                uds_data = bytes.fromhex(hex_str)
            except ValueError:
                self.append_log_color(f"❌ 无效十六进制：'{line}'", "#FF5252")
                continue

            # 格式化 tx 日志
            formatted_tx = ' '.join(f'{b:02X}' for b in uds_data)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x0711 {formatted_tx}", "#64B5F6")
            QApplication.processEvents()

            # 发送并接收响应
            resp = self._iam_send_uds_raw(uds_data)
            if resp:
                formatted_rx = ' '.join(f'{b:02X}' for b in resp)
                if resp[0] == 0x7F:
                    nrc = resp[2] if len(resp) > 2 else 0
                    nrc_desc = self._diag_nrc_desc(nrc)
                    if nrc == 0x78:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x0791 {formatted_rx} ⏳ {nrc_desc}", "#FF9800")
                    else:
                        self.append_log_color(f"{self._diag_timestamp()} rx 0x0791 {formatted_rx} ❌ NRC 0x{nrc:02X} {nrc_desc}", "#FF5252")
                else:
                    self.append_log_color(f"{self._diag_timestamp()} rx 0x0791 {formatted_rx}", "#81C784")

                # IAM 自动安全访问：收到 67 01 + seed 后，自动计算 key 并发送 27 02
                if len(resp) >= 6 and resp[0] == 0x67 and resp[1] == 0x01:
                    seed = resp[2:6]
                    seed_hex = seed.hex().upper()
                    try:
                        # ✅ IAM 算法号：00001011
                        key = sa_calc.calc_key(seed_hex, '00001011')
                        # 发送 27 02 + key
                        client = self.iam_doip_client
                        if client and client.routing_activated:
                            cmd_27_02 = bytes([0x27, 0x02]) + key
                            formatted_tx2 = ' '.join(f'{b:02X}' for b in cmd_27_02)
                            self.append_log_color(f"{self._diag_timestamp()} tx 0x0711 {formatted_tx2}  🔑 自动发送 KEY", "#64B5F6")
                            QApplication.processEvents()

                            # 发送 27 02 后，等待最终响应（处理 0x78 Response Pending）
                            resp2 = None
                            for retry in range(10):  # 最多等待 10 次
                                resp2 = self._iam_send_uds_raw(cmd_27_02, timeout=2.0)
                                if resp2:
                                    if len(resp2) >= 3 and resp2[0] == 0x7F and resp2[2] == 0x78:
                                        # 收到 0x78，继续等待
                                        self.append_log_color(f"{self._diag_timestamp()} rx 0x0791 7F 27 78 ⏳ Response Pending，等待中...", "#FF9800")
                                        time.sleep(0.5)
                                        continue
                                    break
                                else:
                                    time.sleep(0.3)

                            if resp2:
                                f2 = ' '.join(f'{b:02X}' for b in resp2)
                                if resp2[0] == 0x67:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x0791 {f2} ✅ 安全认证成功", "#4CAF50")
                                elif resp2[0] == 0x7F:
                                    nrc2 = resp2[2] if len(resp2) > 2 else 0
                                    nrc_desc2 = self._diag_nrc_desc(nrc2)
                                    if nrc2 == 0x78:
                                        self.append_log_color(f"{self._diag_timestamp()} rx 0x0791 {f2} ⏰ 等待响应超时", "#FF9800")
                                    else:
                                        self.append_log_color(f"{self._diag_timestamp()} rx 0x0791 {f2} ❌ 安全认证失败 NRC 0x{nrc2:02X} {nrc_desc2}", "#FF5252")
                                else:
                                    self.append_log_color(f"{self._diag_timestamp()} rx 0x0791 {f2} ❌ 安全认证失败", "#FF5252")
                            else:
                                self.append_log_color(f"{self._diag_timestamp()} ⏰ 安全访问超时", "#FF5252")
                    except Exception as se:
                        self.append_log_color(f"{self._diag_timestamp()} ❌ 密钥计算失败：{se}", "#FF5252")
            else:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ 超时未收到响应", "#FF5252")

    def _iam_read_dtc(self):
        """通过 DoIP 读取 IAM 的 DTC 故障码 (IDS 方式) - 通过 ICB 转发"""
        client = self.iam_doip_client
        if not client or not client.routing_activated:
            self.append_log_color("❌ IAM 未连接", "#FF5252")
            return

        try:
            # Step 1: 19 02 2C - 读取有效 DTC (pending + confirmed + testFailedSinceClear)
            ts = self._diag_timestamp()
            self.append_log_color(f"{ts} tx 0x{IAM_PHYSICAL_ADDR:04X} 19 02 2C", "#64B5F6")
            QApplication.processEvents()

            resp = self._iam_send_uds_raw(bytes([0x19, 0x02, 0x2C]), timeout=2.0)
            if not resp:
                self.append_log_color(f"{self._diag_timestamp()} ⏰ DTC 列表超时", "#FF5252")
                return

            formatted = ' '.join(f'{b:02X}' for b in resp)
            self.append_log_color(f"{self._diag_timestamp()} rx 0x{IAM_RESPONSE_ADDR:04X} {formatted}", "#81C784")
            QApplication.processEvents()

            # 解析 DTC 列表
            dtc_records = self._parse_dtc_02_response(resp)
            if not dtc_records:
                self.append_log_color("  ✅ 无有效 DTC", "#4CAF50")
                return

            self.append_log_color(f"  📋 发现 {len(dtc_records)} 条 DTC", "#FF9800")

            # Step 2: 对每个 DTC 查询快照 (19 04) 和扩展数据 (19 06)
            log_lines = []
            for i, dtc in enumerate(dtc_records):
                d = dtc['raw']  # 3 bytes DTC code
                dtc_label = dtc['label']

                # 19 04 - 故障快照
                ts = self._diag_timestamp()
                cmd_04 = bytes([0x19, 0x04, d[0], d[1], d[2], 0x01])
                log_lines.append(f"{ts} tx 0x{IAM_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_04)}")
                resp_04 = self._iam_send_uds_raw(cmd_04, timeout=1.5)
                if resp_04:
                    f = ' '.join(f'{b:02X}' for b in resp_04)
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{IAM_RESPONSE_ADDR:04X} {f}")
                    dtc['snapshot_raw'] = resp_04

                # 19 06 - 扩展信息
                ts = self._diag_timestamp()
                cmd_06 = bytes([0x19, 0x06, d[0], d[1], d[2], 0x01])
                log_lines.append(f"{ts} tx 0x{IAM_PHYSICAL_ADDR:04X} {' '.join(f'{b:02X}' for b in cmd_06)}")
                resp_06 = self._iam_send_uds_raw(cmd_06, timeout=1.5)
                if resp_06:
                    f = ' '.join(f'{b:02X}' for b in resp_06)
                    log_lines.append(f"{self._diag_timestamp()} rx 0x{IAM_RESPONSE_ADDR:04X} {f}")
                    dtc['extended_raw'] = resp_06

            # 批量写入日志
            self.append_log_batch(log_lines)

            # Step 3: 显示结果（表格格式）
            self._display_dtc_table(dtc_records)

            # Step 4: 保存到 Excel
            self._save_dtc_excel(dtc_records)

        except Exception as e:
            self._diag_on_socket_error(e)
            self.append_log_color(f"❌ DTC 读取异常: {e}", "#FF5252")
            import traceback
            self.append_log_color(traceback.format_exc(), "#FF5252")

    def _iam_clear_dtc(self):
        """通过 DoIP 清除 IAM 的 DTC 故障码"""
        self._iam_send_uds_cmd("14 FF FF FF")

    def _iam_reset_ecu(self):
        """通过 DoIP 复位 IAM ECU"""
        self._iam_send_uds_cmd("11 01")


    def _get_selected_ecu_name(self):
        """获取当前选中的控制器名称"""
        if self.selected_ecu_key == "all":
            return "ECU (所有控制器)"
        for i in range(self.diag_ecu_list.count()):
            item = self.diag_ecu_list.item(i)
            if item.data(Qt.UserRole) == self.selected_ecu_key:
                return item.text().strip()
        return "未知"

    def _execute_diag_cmd(self, action, ecu_key):
        """执行诊断指令（读取/清除故障码）- 预留扩展"""
        self.append_log_color(f"  → 目标: {ecu_key}, 动作: {action}", "#888888")
        # 提示: 当前仅ICB支持DoIP诊断, 其他ECU需补充
        if ecu_key == "icb" and not self.diag_doip_connected:
            self.append_log_color("  ⚠ ICB未连接，请先连接", "#FF9800")


    def create_statusbar(self):
        """创建状态栏"""
        self.statusBar().showMessage("就绪")

    #保存配置问题
    def save_config(self):
        """保存配置（合并写入，保留视觉等其他模块的配置）"""
        # 保存选中的指令列表
        selected_items = getattr(self, 'selected_items', [])
        keep_scene_items = getattr(self, 'keep_scene_items', [])

        # 🎯 用 update 合并：保留视觉模块写入的 camera_port/brightness_threshold/roi_list 等
        self.config.update({
            'testfold_path':self.testfold_path,
            'heipinglog_path':self.heipinglog_path,
            'relay_com_port': self.relay_com_port,  # 保存继电器串口
            'relayID_qianjin':self.relayID_qianjin,
            'relayID_houtui': self.relayID_houtui,
            'relayID_zhanzuo': self.relayID_zhanzuo,
            'relayID_shache': self.relayID_shache,
            'delaytime_1': self.delaytime_1,
            'delaytime_2': self.delaytime_2,
            'delaytime_3': self.delaytime_3,
            'testcycle': self.testcycle,
            'testmode': self.testmode,
            'selected_items': selected_items,  # 保存选中的指令列表
            'keep_scene_items': keep_scene_items,
            'test_object': getattr(self, 'test_object', '整车'),
            'vehicle_type': getattr(self, 'vehicle_type', 'A车'),
            'project_code': getattr(self, 'project_code', getattr(self, 'car_model', '')),
            'vehicle_id': getattr(self, 'vehicle_id', getattr(self, 'car_no', '')),
            'vehicle_vin': getattr(self, 'vehicle_vin', ''),
            'car_model': getattr(self, 'car_model', ''),
            'car_no': getattr(self, 'car_no', ''),
            'test_baseline': getattr(self, 'test_baseline', 'EP基线'),
            'vehicle_platform': getattr(self, 'vehicle_platform', '8295'),
            'window_geometry': self.saveGeometry().data().hex(),  # 甚至可以保存窗口位置
            'test_mode': 'zonghe' if (hasattr(self, 'zonghe_action') and self.zonghe_action.isChecked()) else 'voice',  # 保存测试模式
        })
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        #QMessageBox.information(self, '成功', '配置已保存！')#弹窗提示成功
   #加载配置问题
    def load_config(self):
        """加载配置（带异常保护，损坏的配置文件不会导致闪退）"""
        if not os.path.exists(self.config_file):
            return
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError, OSError) as e:
            print(f"⚠️ ITS_config.json 损坏({e})，使用默认设置")
            # 🎯 执行文件场景：弹窗告知用户，并自动重置损坏文件
            try:
                # 备份损坏的文件
                backup_path = self.config_file + ".bak"
                if os.path.exists(self.config_file):
                    os.rename(self.config_file, backup_path)
                # 写一个全新的空配置
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False)
                QMessageBox.warning(
                    None, "配置修复",
                    f"配置文件 ITS_config.json 已损坏，已自动重置为默认配置。\n"
                    f"旧的损坏文件已备份为: ITS_config.json.bak"
                )
            except OSError:
                QMessageBox.warning(
                    None, "配置修复",
                    "配置文件 ITS_config.json 已损坏，已使用默认配置启动。"
                )
            self.config = {}
            return

        # 恢复各个参数
        self.testfold_path = self.config.get('testfold_path', '')
        self.heipinglog_path = self.config.get('heipinglog_path', '')
        self.relay_com_port = self.config.get('relay_com_port', '')  # 恢复继电器串口
        self.relayID_qianjin = self.config.get('relayID_qianjin', '')
        self.relayID_houtui = self.config.get('relayID_houtui', '')
        self.relayID_zhanzuo = self.config.get('relayID_zhanzuo', '')
        self.relayID_shache = self.config.get('relayID_shache', '')
        self.delaytime_1 = self.config.get('delaytime_1', '')
        self.delaytime_2 = self.config.get('delaytime_2', '')
        self.delaytime_3 = self.config.get('delaytime_3', '')
        self.testcycle = self.config.get('testcycle', '')
        self.testmode = self.config.get('testmode', '')
        # 恢复选中的指令列表
        self.selected_items = self.config.get('selected_items', [])
        self.keep_scene_items = self.config.get('keep_scene_items', [])
        # 恢复车型/模式选择参数
        self.test_object = self.config.get('test_object', '整车')
        configured_vehicle_type = str(self.config.get('vehicle_type', 'A车') or '').strip()
        self.vehicle_type = configured_vehicle_type if configured_vehicle_type in ('A车', 'B车', 'C车', 'D车', 'F车') else 'A车'
        self.project_code = self.config.get('project_code', self.config.get('car_model', ''))
        self.vehicle_id = self.config.get('vehicle_id', self.config.get('car_no', ''))
        self.vehicle_vin = self.config.get('vehicle_vin', '')
        self.car_model = self.config.get('car_model', self.project_code)
        self.car_no = self.config.get('car_no', self.vehicle_id)
        self.test_baseline = self.config.get('test_baseline', 'EP基线')
        configured_platform = str(self.config.get('vehicle_platform', '8295') or '').strip()
        self.vehicle_platform = configured_platform if configured_platform in ('8295', '8797') else '8295'
        # 窗口位置也能恢复（可选），带异常保护
        if 'window_geometry' in self.config:
            try:
                if isinstance(self.config['window_geometry'], str):
                    self.restoreGeometry(bytes.fromhex(self.config['window_geometry']))
            except (ValueError, AttributeError):
                pass  # 窗口恢复失败不影响正常使用

        # 恢复测试模式设置
        if hasattr(self, 'zonghe_action') and hasattr(self, 'voice_action'):
            test_mode = self.config.get('test_mode', 'zonghe')
            if test_mode == 'zonghe':
                self.zonghe_action.setChecked(True)
                self.voice_action.setChecked(False)
            else:
                self.zonghe_action.setChecked(False)
                self.voice_action.setChecked(True)
   #打开综合测试面板
    def on_zonghe_action_clicked(self):
        """点击综合压测菜单项"""
        # 强制选中综合压测，取消语音测试
        self.zonghe_action.setChecked(True)
        self.voice_action.setChecked(False)
        self.append_log("✅ 当前模式：综合压测")
        self.config['test_mode'] = 'zonghe'
        self.save_config()

        # 打开配置界面
        self.open_zonghe_test()

    def on_voice_action_clicked(self):
        """点击语音测试菜单项"""
        # 强制选中语音测试，取消综合压测
        self.voice_action.setChecked(True)
        self.zonghe_action.setChecked(False)
        self.append_log("✅ 当前模式：语音测试")
        self.config['test_mode'] = 'voice'
        self.save_config()

        # 打开配置界面
        self.open_voice_test()

    def open_zonghe_test(self):
        """打开综合压测子界面"""
        from Subpy.zonghe_testdialog import ZongheTestDialog
        old_dialog = getattr(self, 'zonghe_dialog', None)
        if old_dialog is not None and getattr(old_dialog, 'baseline_worker', None):
            if old_dialog.baseline_worker.isRunning():
                if not hasattr(self, '_background_baseline_dialogs'):
                    self._background_baseline_dialogs = []
                self._background_baseline_dialogs.append(old_dialog)
        self.zonghe_dialog = ZongheTestDialog(
            self,
            vehicle_platform=self.config.get('vehicle_platform', '8295')
        )
        self.zonghe_dialog.auto_cycle_finished.connect(
            lambda dialog=self.zonghe_dialog: self._on_auto_cycle_baseline_finished(dialog)
        )
        # 加载配置
        self.zonghe_dialog.fold_path1.setText(self.config.get('testfold_path', ''))
        self.zonghe_dialog.file_path2.setText(self.config.get('heipinglog_path', ''))
        self.zonghe_dialog.relay_com.setCurrentText(self.config.get('relay_com_port', ''))
        self.zonghe_dialog.relayid1_combo.setCurrentText(self.config.get('relayID_qianjin', ''))
        self.zonghe_dialog.relayid2_combo.setCurrentText(self.config.get('relayID_houtui', ''))
        self.zonghe_dialog.relayid3_combo.setCurrentText(self.config.get('relayID_zhanzuo', ''))
        self.zonghe_dialog.relayid4_combo.setCurrentText(self.config.get('relayID_shache', ''))
        self.zonghe_dialog.delaytime1.setText(self.config.get('delaytime_1', ''))
        self.zonghe_dialog.delaytime2.setText(self.config.get('delaytime_2', ''))
        self.zonghe_dialog.delaytime3.setText(self.config.get('delaytime_3', ''))
        self.zonghe_dialog.cycle.setText(self.config.get('testcycle', ''))
        self.zonghe_dialog.mode_combo.setCurrentText(self.config.get('testmode', ''))

        if hasattr(self, 'selected_items') and self.selected_items:
            self.zonghe_dialog.selector.set_selected_items(self.selected_items)
            self.zonghe_dialog.selector.set_keep_scene_items(
                getattr(self, 'keep_scene_items', [])
            )

        # 🎯 用exec()打开模态对话框，阻塞直到关闭
        self.zonghe_dialog.exec()
        auto_start_cycle = bool(getattr(self.zonghe_dialog, '_auto_cycle_ready', False))

        # 🎯 对话框关闭后再保存所有参数 - 既要更新config，也要更新成员变量
        self.selected_items = self.zonghe_dialog.selector.get_selected_items()
        self.keep_scene_items = self.zonghe_dialog.selector.get_keep_scene_items()

        self.testfold_path = self.zonghe_dialog.fold_path1.text()
        self.heipinglog_path = self.zonghe_dialog.file_path2.text()
        self.relay_com_port = self.zonghe_dialog.relay_com.currentText()
        self.relayID_qianjin = self.zonghe_dialog.relayid1_combo.currentText()
        self.relayID_houtui = self.zonghe_dialog.relayid2_combo.currentText()
        self.relayID_zhanzuo = self.zonghe_dialog.relayid3_combo.currentText()
        self.relayID_shache = self.zonghe_dialog.relayid4_combo.currentText()
        self.delaytime_1 = self.zonghe_dialog.delaytime1.text()
        self.delaytime_2 = self.zonghe_dialog.delaytime2.text()
        self.delaytime_3 = self.zonghe_dialog.delaytime3.text()
        self.testcycle = self.zonghe_dialog.cycle.text()
        self.testmode = self.zonghe_dialog.mode_combo.currentText()

        # 同时也更新config
        self.config['testfold_path'] = self.testfold_path
        self.config['heipinglog_path'] = self.heipinglog_path
        self.config['relay_com_port'] = self.relay_com_port
        self.config['relayID_qianjin'] = self.relayID_qianjin
        self.config['relayID_houtui'] = self.relayID_houtui
        self.config['relayID_zhanzuo'] = self.relayID_zhanzuo
        self.config['relayID_shache'] = self.relayID_shache
        self.config['delaytime_1'] = self.delaytime_1
        self.config['delaytime_2'] = self.delaytime_2
        self.config['delaytime_3'] = self.delaytime_3
        self.config['testcycle'] = self.testcycle
        self.config['testmode'] = self.testmode

        self.save_config()

        if auto_start_cycle and not getattr(self.zonghe_dialog, '_auto_cycle_start_scheduled', False):
            self.zonghe_dialog._auto_cycle_start_scheduled = True
            self.append_log("✅ 基准保存完成，正在自动开始循环测试")
            QTimer.singleShot(0, self._start_cycle_after_baseline)

    def _start_cycle_after_baseline(self):
        """Start the normal cycle workflow after automatic baseline collection."""
        # 基准采集可能更换了指令数量或顺序；此时旧 CSV 的表头属于上一组指令，
        # 不应阻止刚保存完基准的自动循环从第 1 轮开始。
        self.start_cycle_test(reset_history=True)
        if self.test_runner.is_running:
            self.send_feishu_message("循环测试已开始", message_text="循环测试已开始")

    def _on_auto_cycle_baseline_finished(self, dialog):
        """Continue automatic cycle startup even if the dialog was closed early."""
        if dialog.isVisible():
            dialog.accept()
            return
        dialog._auto_cycle_start_scheduled = True
        background_dialogs = getattr(self, '_background_baseline_dialogs', [])
        if dialog in background_dialogs:
            background_dialogs.remove(dialog)
        self.append_log("✅ 基准保存完成，正在自动开始循环测试")
        QTimer.singleShot(0, self._start_cycle_after_baseline)

    def open_robot_control(self):
        """打开机器人TCP控制界面"""
        try:
            from Subpy.robot_control_dialog import RobotControlDialog

            if hasattr(self, "robot_control_dialog") and self.robot_control_dialog is not None:
                if self.robot_control_dialog.isVisible():
                    self.robot_control_dialog.raise_()
                    self.robot_control_dialog.activateWindow()
                    return

            self.robot_control_dialog = RobotControlDialog(self)
            self.robot_control_dialog.show()
            self.robot_control_dialog.raise_()
            self.robot_control_dialog.activateWindow()
            self.statusBar().showMessage("已打开机器人控制界面", 3000)
        except Exception as e:
            self.append_log(f"❌ 机器人控制界面打开失败：{e}")
            QMessageBox.critical(self, "错误", f"无法启动机器人控制界面:\n{e}")

    def open_relay_control(self):
        """打开继电器控制界面"""
        from Subpy.relay_control_dialog import RelayControlDialog
        self.relay_dialog = RelayControlDialog(self)
        self.relay_dialog.exec()

    def open_voice_test(self):
        """打开语音测试配置界面"""
        from Subpy.voice_test_dialog import VoiceTestDialog
        self.voice_test_dialog = VoiceTestDialog(
            self,
            vehicle_platform=self.config.get('vehicle_platform', '8295'),
        )
        self.voice_test_dialog.show()

    def open_voice_recorder(self):
        """打开语音录音工具"""
        from Subpy.voice_recorder_dialog import VoiceRecorderDialog
        self.voice_recorder_dialog = VoiceRecorderDialog(self)
        self.voice_recorder_dialog.show()

    def open_audio_detector(self):
        """打开音频探测工具"""
        from Subpy.audio_detector_dialog import AudioDetectorDialog
        self.audio_detector_dialog = AudioDetectorDialog(self)
        self.audio_detector_dialog.show()

    def open_packet_capture(self):
        """打开SOME/IP抓包工具"""
        from Subpy.packet_capture_dialog import PacketCaptureDialog
        self.packet_capture_dialog = PacketCaptureDialog(self)
        self.packet_capture_dialog.show()

    def start_voice_test(self):
        """开始语音测试"""
        # 1. 检查是否选中了语音测试指令
        voice_config = self.config.get('voice_test', {})
        selected_items = voice_config.get('selected_instructions', [])
        from Subpy.voice_test_config import get_instruction_names
        supported_items = set(
            get_instruction_names(self.config.get('vehicle_platform', '8295'))
        )
        selected_items = [name for name in selected_items if name in supported_items]

        if not selected_items:
            QMessageBox.warning(self, '提示', '请先在语音测试中选择要执行的指令！')
            # 自动打开语音测试配置界面
            self.open_voice_test()
            return

        # 2. 检查循环次数（优先使用语音测试设置的 cycle_count，没有则使用综合测试的 testcycle）
        cycles = voice_config.get('cycle_count', 0)
        if not cycles:
            testcycle_str = getattr(self, 'testcycle', '')
            if not testcycle_str:
                QMessageBox.warning(self, '提示', '请先在语音测试中设置循环次数！')
                return
            try:
                cycles = int(testcycle_str)
                if cycles <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                QMessageBox.warning(self, '提示', f'循环次数无效: {testcycle_str}，必须是大于0的整数')
                return

        # 3. 设置表格表头（force_refresh=True 强制刷新）
        # 设置表头：第一格是"序号"，后面是选中的指令名称
        headers = ['序号'] + selected_items

        # 先设置列数和表头
        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setHorizontalHeaderLabels(headers)

        # 设置列宽调整模式
        for col in range(len(headers)):
            self.table_widget.horizontalHeader().setSectionResizeMode(col, QHeaderView.Fixed)
            self.table_widget.setColumnWidth(col, 100)

        # 4. 清空表格旧数据，并设置行数 = 循环次数
        self.table_widget.setRowCount(0)
        self.table_widget.setRowCount(cycles)

        # 5. 初始化语音测试执行器
        from Subpy.voice_test_runner import VoiceTestRunner
        self.voice_test_runner = VoiceTestRunner(self)

        # 连接信号
        self.voice_test_runner.log_signal.connect(self.append_log)
        self.voice_test_runner.cell_update_signal.connect(self._update_table_cell)
        self.voice_test_runner.finished_signal.connect(self._on_voice_test_finished)
        self.voice_test_runner.instruction_failed_signal.connect(self.on_instruction_failed)

        # 6. 加载指令
        if not self.voice_test_runner.load_instructions(selected_items):
            QMessageBox.warning(self, '提示', '指令加载失败！')
            return

        # 7. 设置循环次数和保存路径（使用语音测试自己的文件夹路径）
        voice_test_folder = voice_config.get('test_folder', '')
        if not voice_test_folder or voice_test_folder == "(未设置)":
            QMessageBox.warning(self, '提示', '请先在语音测试设置中设置测试文件夹！')
            self.open_voice_test()
            return
        self.voice_test_runner.set_save_folder(voice_test_folder)
        self.voice_test_runner.set_total_cycles(cycles)

        # 8. 设置语音配置
        self.voice_test_runner.set_voice_config(
            tts_library=voice_config.get('tts_library', '本地TTS (pyttsx3)'),
            voice=voice_config.get('voice', ''),
            tts_language=voice_config.get('language', '中文'),
            tts_speed=voice_config.get('speed', '正常'),
            play_mode=voice_config.get('play_mode', 'TTS播放'),
            audio_folder=voice_config.get('audio_folder', '')
        )

        # 9. 检查上次运行到第几次，但不加载历史记录
        has_history, last_cycle, header_match = self.voice_test_runner.load_previous_results()

        # 检查测试指令是否匹配
        if not header_match:
            reply = QMessageBox.critical(
                self,
                "测试指令已变更",
                "由于测试指令改变，请修改测试文件夹路径，或者删除旧csv数据文件！",
                QMessageBox.StandardButton.Ok
            )
            return

        start_cycle = last_cycle + 1 if has_history else 1

        # 10. 更新按钮状态
        self.play_act.setEnabled(False)
        self.pause_act.setEnabled(True)
        self.stop_act.setEnabled(True)
        self.pause_act.setIcon(QIcon(resource_path("image/pause.png")))

        # 11. 开始测试
        self.append_log("\n" + "="*60)
        self.append_log("🚀 开始语音测试")
        self.append_log("="*60)
        self.voice_test_runner.start(start_cycle)

    def open_visual_setting(self):
        """打开视觉设置子界面"""
        # 🎯 优化：延迟导入子模块
        from Subpy.visual_setting_dialog import VisualSettingDialog
        self.visual_dialog = VisualSettingDialog(self)
        # 🎯 设置保存路径为配置基准文件夹
        config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "配置基准文件")
        self.visual_dialog.detector.save_folder = config_dir
        # 🎯 更新路径显示，用相对路径更友好
        display_path = os.path.join(".", "配置基准文件")
        self.visual_dialog.path_label.setText(f"截图将保存到: {display_path}")
        self.visual_dialog.exec()

    def open_carchoose_dialog(self):
        """打开车型/模式选择子界面"""
        # 🎯 优化：延迟导入子模块
        from Subpy.carchoose_testdialog import carchooseDialog
        from Subpy.itms_vehicle_catalog import ITMSVehicleCatalog, DEFAULT_ITMS_API_BASE_URL, DEFAULT_ITMS_VEHICLE_CATALOG_KEY
        itms_api_base_url = self.config.get('itms_api_base_url', DEFAULT_ITMS_API_BASE_URL)
        if str(itms_api_base_url or '').rstrip('/').endswith(':5000'):
            itms_api_base_url = DEFAULT_ITMS_API_BASE_URL
        itms_vehicle_catalog_key = self.config.get('itms_vehicle_catalog_key', DEFAULT_ITMS_VEHICLE_CATALOG_KEY)
        self.carchoose_dialog = carchooseDialog(
            self,
            catalog=ITMSVehicleCatalog(
                api_base_url=itms_api_base_url,
                access_key=itms_vehicle_catalog_key,
            )
        )

        # 恢复上次保存的选项
        self.carchoose_dialog.cartable_combo.setCurrentText(self.config.get('test_object', '整车'))
        self.carchoose_dialog.set_selected_vehicle_type(self.config.get('vehicle_type', 'A车'))
        self.carchoose_dialog.set_selected_project_code(self.config.get('project_code', self.config.get('car_model', '')))
        self.carchoose_dialog.set_selected_vehicle_id(self.config.get('vehicle_id', self.config.get('car_no', '')))
        self.carchoose_dialog.testline_combo.setCurrentText(self.config.get('test_baseline', 'EP基线'))
        self.carchoose_dialog.set_selected_platform(self.config.get('vehicle_platform', '8295'))

        self.carchoose_dialog.exec()

        # 关闭后保存配置
        self.test_object = self.carchoose_dialog.cartable_combo.currentText()
        self.vehicle_type = self.carchoose_dialog.get_selected_vehicle_type()
        self.project_code = self.carchoose_dialog.get_selected_project_code()
        self.vehicle_id = self.carchoose_dialog.get_selected_vehicle_id()
        self.vehicle_vin = self.carchoose_dialog.get_selected_vehicle_vin()
        self.car_model = self.project_code
        self.car_no = self.vehicle_id
        self.test_baseline = self.carchoose_dialog.testline_combo.currentText()
        self.vehicle_platform = self.carchoose_dialog.get_selected_platform()

        self.config['test_object'] = self.test_object
        self.config['vehicle_type'] = self.vehicle_type
        self.config['project_code'] = self.project_code
        self.config['vehicle_id'] = self.vehicle_id
        self.config['vehicle_vin'] = self.vehicle_vin
        self.config['car_model'] = self.car_model
        self.config['car_no'] = self.car_no
        self.config['test_baseline'] = self.test_baseline
        self.config['vehicle_platform'] = self.vehicle_platform

        self.save_config()

    def open_visual_setting(self):
        """打开视觉设置子界面"""
        # 🎯 检查是否正在录制视频
        # 条件1：测试正在运行（play按钮禁用，stop按钮启用）
        is_test_running = not self.play_act.isEnabled()
        # 条件2：勾选了录制视频
        is_recording_checked = hasattr(self, 'record_video_checkbox') and self.record_video_checkbox.isChecked()
        # 条件3：视频录制器正在活动
        is_recording_active = hasattr(self, 'video_recorder') and self.video_recorder and self.video_recorder.is_active()

        if (is_test_running or is_recording_active) and is_recording_checked:
            # 🎯 弹窗提示
            QMessageBox.warning(
                self,
                "提示",
                "当前摄像头正在录制视频中！\n请先停止测试后，再打开视觉设置界面。",
                QMessageBox.Ok
            )
            return

        # 🎯 打开视觉设置界面
        from Subpy.visual_setting_dialog import VisualSettingDialog
        self.visual_dialog = VisualSettingDialog(self)
        self.visual_dialog.exec()

    def play_clicked(self):
        idx = self.tab_widget.currentIndex()  # 获取当前 tab 控件
        if idx == 0:
           # 判断当前模式
           if self.zonghe_action.isChecked():
               self.start_cycle_test()  # 综合压测模式
           elif self.voice_action.isChecked():
               self.start_voice_test()  # 语音测试模式
        elif idx == 1:
           pass  # 诊断功能预留

    def load_instructions_to_table(self, force_refresh=False):
        """使用综合测试选择器中的指令设置表格表头（优化版）

        Args:
            force_refresh: 是否强制刷新（即使表头已存在）
        """
        # 获取选中的指令列表
        selected_items = getattr(self, 'selected_items', [])

        if not selected_items:
            return False

        # 设置表头：第一格是"序号"，后面是选中的指令名称
        headers = ['序号'] + selected_items

        # 🎯 优化1：检查表头是否已经存在，避免重复设置
        if not force_refresh:
            current_headers = []
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.horizontalHeaderItem(col)
                current_headers.append(item.text() if item else '')

            if current_headers == headers:
                return True  # 表头已相同，跳过

        # 🎯 优化2：先设置列数和表头（这步很快）
        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setHorizontalHeaderLabels(headers)

        # 🎯 优化3：设置列宽调整模式（只设置一次，不遍历所有行）
        # 所有列固定100px宽度，最后一列也固定，启用水平滚动条
        for col in range(len(headers)):
            self.table_widget.horizontalHeader().setSectionResizeMode(col, QHeaderView.Fixed)
            self.table_widget.setColumnWidth(col, 100)

        return True

    def _prepare_itms_test_task(self, cycles, selected_items, start_cycle):
        """Create or restore the task identity used by ITMS cycle statistics."""
        test_folder = getattr(self, 'testfold_path', '') or ''
        task_file = os.path.join(test_folder, 'itms_test_task.json') if test_folder else ''
        task_id = ''
        if start_cycle > 1 and task_file and os.path.exists(task_file):
            try:
                with open(task_file, 'r', encoding='utf-8') as file:
                    task_id = str(json.load(file).get('testTaskId') or '').strip()
            except (OSError, ValueError, TypeError):
                task_id = ''
        if not task_id:
            task_id = f"ITS-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"

        context = {
            'eventType': 'ITS_TEST_CYCLE',
            'source': 'ITS',
            'testTaskId': task_id,
            'vehicleType': getattr(self, 'vehicle_type', ''),
            'projectCode': getattr(self, 'project_code', ''),
            'vehicleNo': getattr(self, 'vehicle_id', getattr(self, 'car_no', '')),
            'vin': getattr(self, 'vehicle_vin', ''),
            'platform': getattr(self, 'vehicle_platform', '8295'),
            'baseline': getattr(self, 'test_baseline', 'EP基线'),
            'totalCycles': cycles,
            'instructionNames': list(selected_items),
            'startedAt': datetime.datetime.now().isoformat(timespec='seconds'),
        }
        if task_file:
            try:
                os.makedirs(test_folder, exist_ok=True)
                with open(task_file, 'w', encoding='utf-8') as file:
                    json.dump(context, file, ensure_ascii=False, indent=2)
            except OSError as error:
                self.append_log(f"[ITMS] 测试任务信息保存失败，不影响测试: {error}")
        return context

    def start_cycle_test(self, reset_history=False):
        """开始循环测试"""
        # 1. 检查是否选中了指令
        selected_items = getattr(self, 'selected_items', [])
        if not selected_items:
            QMessageBox.warning(self, '提示', '请先在综合测试中选择要执行的指令！')
            return

        # 2. 检查循环次数（从综合测试界面 testcycle 读取）
        testcycle_str = getattr(self, 'testcycle', '')
        if not testcycle_str:
            QMessageBox.warning(self, '提示', '请先在综合测试中设置总循环次数！')
            return
        try:
            cycles = int(testcycle_str)
            if cycles <= 0:
                raise ValueError
        except (ValueError, TypeError):
            QMessageBox.warning(self, '提示', f'循环次数无效: {testcycle_str}，必须是大于0的整数')
            return

        # 3. 设置表格表头（force_refresh=True 强制刷新）
        if not self.load_instructions_to_table(force_refresh=True):
            QMessageBox.warning(self, '提示', '设置表头失败！')
            return

        # 4. 清空表格旧数据，并设置行数 = 循环次数
        # 🎯 优化：先设置为0行，再设置为目标行数，避免清空操作
        self.table_widget.setRowCount(0)
        self.table_widget.setRowCount(cycles)

        # 5. 加载指令到 TestRunner
        if not self.test_runner.load_from_instructions(selected_items):
            QMessageBox.warning(self, '提示', '指令加载失败！')
            return

        # 6. 设置循环次数和保存路径
        self.test_runner.set_total_cycles(cycles)
        self.test_runner.set_save_folder(getattr(self, 'testfold_path', ''))

        # 7. 设置继电器配置和延迟时间

        # 🎯 处理通道号：过滤掉提示文字，只保留数字
        def parse_channel(channel_text, default):
            if not channel_text:
                return str(default)
            # 提取数字
            import re
            match = re.search(r'\d+', channel_text)
            if match:
                return match.group()
            # 如果没找到数字，返回默认值
            return str(default)

        relay_channel_map = {
            "踩刹车": parse_channel(getattr(self, 'relayID_shache', ''), '1'),
            "占座": parse_channel(getattr(self, 'relayID_zhanzuo', ''), '3'),
            "电机前进": parse_channel(getattr(self, 'relayID_qianjin', ''), '1'),
            "电机后退": parse_channel(getattr(self, 'relayID_houtui', ''), '2'),
        }

        # 🎯 获取继电器串口
        relay_port = getattr(self, 'relay_com_port', None)
        if relay_port and not relay_port.strip():
            relay_port = None

        # 设置测试运行器配置
        delay_time_value = getattr(self, 'delaytime_1', '1')
        self.test_runner.set_config(
            delay_time=delay_time_value,
            relay_port=relay_port,
            relay_channel_map=relay_channel_map,
            vehicle_platform=getattr(
                self, 'vehicle_platform',
                self.config.get('vehicle_platform', '8295')
            )
        )

        # 8. 设置等待指令的参数
        sleep_wake_delay_val = getattr(self, 'delaytime_2', '0')
        increment_time_val = getattr(self, 'delaytime_3', '0')
        self.test_runner.test_executor.set_wait_params(
            sleep_wake_delay=sleep_wake_delay_val,
            increment_time=increment_time_val
        )
        try:
            sleep_wake_delay_num = float(sleep_wake_delay_val) if sleep_wake_delay_val else 0.0
        except (TypeError, ValueError):
            sleep_wake_delay_num = 0.0
        try:
            increment_time_num = float(increment_time_val) if increment_time_val else 0.0
        except (TypeError, ValueError):
            increment_time_num = 0.0
        self.append_log(
            f"[等待参数] 起始等待={sleep_wake_delay_num:g}s，"
            f"每轮递增={increment_time_num:g}s"
        )
        if sleep_wake_delay_num >= 600:
            self.append_log(
                f"⚠️ 当前起始等待时间较长：{sleep_wake_delay_num:g}s，"
                "如非预期请在综合压测配置中调小休眠唤醒延迟时间"
            )

        # 9. 检查上次运行到第几次循环，实现断点续跑
        if reset_history:
            has_history, last_cycle, header_match, load_err = False, 0, True, ""
            with self.test_runner._results_lock:
                self.test_runner.results = []
                self.test_runner._last_save_time = 0
            self.append_log("ℹ️ 基准刚刚更新，忽略旧循环记录，从第 1 次开始")
        else:
            has_history, last_cycle, header_match, load_err = self.test_runner.load_previous_results()

        if not header_match:
            QMessageBox.warning(
                self,
                "指令已变更",
                f"当前指令已变更，请更换测试文件夹或修改原CSV记录文件名。\n\n"
                f"原记录: {load_err}"
            )
            return
        else:
            if load_err:
                self.append_log(f"ℹ️ {load_err}")
            start_cycle = last_cycle + 1 if has_history else 1
            if has_history:
                self.append_log(f"🔁 检测到上次跑到第 {last_cycle} 次，从第 {start_cycle} 次继续")

        itms_context = self._prepare_itms_test_task(cycles, selected_items, start_cycle)
        self.test_runner.set_upload_context(itms_context)

        # 10. 切换按钮状态：play 置灰，暂停和停止高亮
        self.play_act.setEnabled(False)
        self.pause_act.setEnabled(True)
        self.stop_act.setEnabled(True)

        self.append_log(f"开始执行循环测试，共 {cycles} 次循环，{len(selected_items)} 条指令")

        # 12. 🎯 如果勾选了记录测试视频，开始录制
        if hasattr(self, 'record_video_checkbox') and self.record_video_checkbox.isChecked():
            test_folder = getattr(self, 'testfold_path', '')
            if test_folder:
                try:
                    from Subpy.video_recorder import VideoRecorder
                    # 🎯 重新加载配置，确保是最新的
                    self.load_config()
                    # 🎯 从配置中读取用户选择的摄像头端口，默认用1
                    camera_port = self.config.get('camera_port', 1)
                    self.video_recorder = VideoRecorder(test_folder, camera_index=camera_port)
                    if self.video_recorder.start_recording():
                        self.append_log(f"[视频] 开始录制测试视频（摄像头端口: {camera_port}）")
                    else:
                        self.append_log("[视频] 视频录制启动失败")
                except Exception as e:
                    self.append_log(f"[视频] 录制初始化异常: {str(e)}")
            else:
                self.append_log("[视频] 未设置测试文件夹路径，不录制视频")

        # 13. 启动 TestRunner（在子线程中运行）
        self.test_runner.start(start_cycle)

    def pause_clicked(self):
        """暂停/继续按钮"""
        # 检查是否是语音测试
        if hasattr(self, 'voice_test_runner') and self.voice_test_runner and self.voice_test_runner.is_running:
            if self.voice_test_runner.is_paused:
                self.voice_test_runner.resume()
                self.pause_act.setIcon(QIcon(resource_path("image/pause.png")))
            else:
                self.voice_test_runner.pause()
                self.pause_act.setIcon(QIcon(resource_path("image/play.png")))
        # 否则是综合测试
        elif hasattr(self, 'test_runner') and self.test_runner.is_running:
            is_paused = self.test_runner.toggle_pause()
            if is_paused:
                self.pause_act.setIcon(QIcon(resource_path("image/play.png")))
            else:
                self.pause_act.setIcon(QIcon(resource_path("image/pause.png")))

    def stop_clicked(self):
        """停止按钮"""
        # 检查是否是语音测试
        if hasattr(self, 'voice_test_runner') and self.voice_test_runner and self.voice_test_runner.is_running:
            self.voice_test_runner.stop()
            # 立即恢复按钮状态
            self._on_voice_test_finished()
        # 否则是综合测试
        elif hasattr(self, 'test_runner') and self.test_runner.is_running:
            self.test_runner.stop()
            # 立即恢复按钮状态
            self._on_test_finished()

        # 🎯 停止视频录制（stop_recording 已改为非阻塞，调多次也没问题）
        if hasattr(self, 'video_recorder') and self.video_recorder and self.video_recorder.is_active():
            self.video_recorder.stop_recording()
            self.append_log("[视频] 已停止录制")

    def _update_table_cell(self, row, col, result):
        """更新表格单元格内容"""
        from PySide6.QtWidgets import QTableWidgetItem
        from PySide6.QtCore import Qt
        item = QTableWidgetItem(result)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # 居中对齐
        self.table_widget.setItem(row, col, item)

    def _on_test_finished(self):
        """测试完成回调 - 恢复按钮初始状态"""
        self.play_act.setEnabled(True)
        self.pause_act.setEnabled(False)
        self.stop_act.setEnabled(False)
        self.pause_act.setIcon(QIcon(resource_path("image/pause.png")))
        self.append_log("测试执行结束")

        # 🎯 停止视频录制（正常结束或点击停止都会走到这里）
        if hasattr(self, 'video_recorder') and self.video_recorder and self.video_recorder.is_active():
            self.video_recorder.stop_recording()
            self.append_log("[视频] 已停止录制")

    def _on_voice_test_finished(self):
        """语音测试完成回调 - 恢复按钮初始状态"""
        # 恢复初始状态：play 高亮，暂停和停止置灰
        self.play_act.setEnabled(True)
        self.pause_act.setEnabled(False)
        self.stop_act.setEnabled(False)
        # 重置暂停按钮图标
        self.pause_act.setIcon(QIcon(resource_path("image/pause.png")))
        self.append_log("语音测试执行结束")

        # 🎯 停止视频录制（语音测试不创建录制器，但保留统一处理）
        if hasattr(self, 'video_recorder') and self.video_recorder and self.video_recorder.is_active():
            self.video_recorder.stop_recording()
            self.append_log("[视频] 已停止录制")

    def _on_cycle_wait_time_updated(self, wait_time):
        """每次循环结束后的等待时间更新回调
        :param wait_time: 累加后的等待时间
        """
        # 只记录运行时当前等待，不覆盖用户配置的起始等待时间。
        # 否则下一次启动会从累计值继续等待，容易表现为卡在“等待”指令。
        self.current_sleep_wake_delay = str(wait_time)
        self.config['saved_sleep_wake_delay'] = str(wait_time)

        # 更新UI
        if hasattr(self, 'zonghe_dialog') and self.zonghe_dialog and self.zonghe_dialog.isVisible():
            try:
                self.append_log(f"[UI] 当前等待时间: {wait_time}秒")
            except Exception as e:
                print(f"[UI] 更新综合测试界面失败: {e}")

    def send_feishu_message(self, instruction_name, message_text=None):
        """发送飞书消息
        :param instruction_name: 失败的指令名称
        """
        # 检查是否勾选了发送飞书消息
        if not hasattr(self, 'send_feishu_checkbox') or not self.send_feishu_checkbox.isChecked():
            return

        try:
            # 🎯 使用 Python 标准库 urllib，不需要安装额外依赖
            import urllib.request
            import json

            webhook_url = os.environ.get("ITS_FEISHU_WEBHOOK_URL", "").strip()
            if not webhook_url:
                self.append_log("未配置飞书 Webhook，跳过消息发送")
                return

            # 获取车辆编号
            car_no = getattr(self, 'car_no', '') or getattr(self, 'car_No', '')
            if message_text is None:
                if car_no:
                    message_text = f"[{car_no}] {instruction_name}执行失败"
                else:
                    message_text = f"{instruction_name}执行失败"
            elif car_no:
                message_text = f"[{car_no}] {message_text}"

            # 构造消息内容
            message = {
                "msg_type": "text",
                "content": {
                    "text": message_text
                }
            }

            # 转换为 JSON 字符串
            data = json.dumps(message, ensure_ascii=False).encode('utf-8')

            # 创建请求
            req = urllib.request.Request(
                webhook_url,
                data=data,
                headers={'Content-Type': 'application/json'}
            )

            # 发送请求
            with urllib.request.urlopen(req, timeout=10) as response:
                response_body = response.read().decode('utf-8')

                if response.status == 200:
                    self.append_log(f"[飞书] 已发送消息: {message_text}")
                else:
                    self.append_log(f"[飞书] 发送失败: HTTP {response.status}")

        except Exception as e:
            self.append_log(f"[飞书] 发送异常: {str(e)}")

    def on_instruction_failed(self, instruction_name):
        """指令失败回调
        :param instruction_name: 失败的指令名称
        """
        # 先发送飞书消息
        self.send_feishu_message(instruction_name)

        # 检查是否勾选了"黑屏保持现场"且是亮屏检测失败
        if (hasattr(self, 'keepxc_checkbox')
            and self.keepxc_checkbox.isChecked()
            and '亮屏' in instruction_name):

            self.append_log(f"\n⚠️ 亮屏检测失败，已暂停测试！")
            self.append_log(f"📝 请查看现场，然后点击继续或停止按钮")

            self._pause_test_for_keep_scene()

        keep_scene_items = set(getattr(self, 'keep_scene_items', []) or [])
        if instruction_name in keep_scene_items:

            self.append_log(f"\n⚠️ 指令 {instruction_name} 执行失败，已暂停测试！")
            self.append_log(f"📝 请查看现场，然后点击继续或停止按钮")

            self._pause_test_for_keep_scene()

    def _pause_test_for_keep_scene(self):
        """保持现场时暂停综合测试，避免重复触发导致恢复运行。"""
        if not hasattr(self, 'test_runner') or not hasattr(self.test_runner, 'toggle_pause'):
            return
        if getattr(self.test_runner, 'is_paused', False):
            return
        self.test_runner.toggle_pause()
        self.pause_act.setIcon(QIcon(resource_path("image/play.png")))

    #--------------执行CMD指令结束----------------#

    def _scroll_log_to_bottom(self):
        """让右侧日志窗口始终显示最新内容"""
        if not hasattr(self, 'text_edit1'):
            return
        scrollbar = self.text_edit1.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())
        self.text_edit1.ensureCursorVisible()

    def append_log(self, text):
        self.text_edit1.append(text)
        self._scroll_log_to_bottom()

    def on_finish(self, code):
        self.text_edit1.append(f"完成，返回码: {code}")
        self._scroll_log_to_bottom()

    def red_excel(self):
        """读取excel并写到表格中"""
        if not hasattr(self, 'zhiling_path') or not self.zhiling_path:
            QMessageBox.warning(self, '提示', '请先在综合测试中选择指令文件！')
            return#如果文件路径为空的话就弹窗提示，并退出
        # 🎯 优化：延迟导入 pandas（只在需要时导入）
        import pandas as pd
        df = pd.read_excel(self.zhiling_path, header=None)  # 不使用默认表头

        # 获取第一列的内容（排除空值）
        first_column = df.iloc[:, 0].dropna()  # 第一列所有非空值

        # 将第一列内容作为表头
        headers = first_column.tolist()
        if not headers:
            QMessageBox.warning(self, '警告', 'Excel文件第一列为空！')
            return
        self.table_widget.setColumnCount(len(headers)) # 设置表格的列数为表头的数量
        self.table_widget.setHorizontalHeaderLabels(headers) # 设置表头
        # 🎯 冻结第一列（序号列）：横向滚动时保持第一列固定不动
        self.table_widget.setColumnWidth(0, 80)  # 设置第一列宽度为80px
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)  # 第一列宽度固定
        self.table_widget.horizontalHeader().setFirstSectionMovable(False)  # 第一列不可拖动
        # 🎯 第一列固定80px，其他列固定300px，确保表头显示完整
        for col in range(len(headers)):
            if col == 0:
                self.table_widget.setColumnWidth(col, 80)  # 第一列固定宽度80px
            else:
                width = 300  # 其他列固定300px，确保显示完整
                self.table_widget.setColumnWidth(col, width)

    def new_file(self):
        """新建文件"""
        self.current_file = None
        self.text_edit.clear()
        #self.update_title()
        self.statusBar().showMessage("已新建文件")

    def open_file(self):
        """打开文件"""
        path, _ = QFileDialog.getOpenFileName(
            self, "打开文件", "", "文本文件 (*.txt);;所有文件 (*.*)"
        )
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_edit.setText(content)
                self.current_file = path
                self.update_title()
                self.statusBar().showMessage(f"已打开: {path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"打开文件失败: {str(e)}")

    def save_file(self):
        """保存文件"""
        if self.current_file is None:
            return self.save_as()
        self._save_to_file(self.current_file)

    def save_as(self):
        """另存为"""
        path, _ = QFileDialog.getSaveFileName(
            self, "保存文件", "", "文本文件 (*.txt);;所有文件 (*.*)"
        )
        if path:
            self.current_file = path
            self._save_to_file(path)
            return True
        return False

    def _save_to_file(self, path):
        """实际保存到文件"""
        try:
            content = self.text_edit.toPlainText()
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.update_title()
            self.statusBar().showMessage(f"已保存: {path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")

    def _on_record_video_toggled(self, checked):
        """记录测试视频复选框：试验运行时禁止勾选"""
        if not checked:
            return  # 用户取消勾选不需要拦截
        if hasattr(self, 'test_runner') and self.test_runner and getattr(self.test_runner, 'is_running', False):
            QMessageBox.warning(self, "提示", "请先停止试验后再勾选")
            # setChecked(False) 会再次触发 toggled(False)，但第一行 return 了，不会循环
            self.record_video_checkbox.setChecked(False)

    def closeEvent(self, event):
        """窗口关闭事件 - 确保停止视频录制"""
        # 🎯 停止视频录制
        if hasattr(self, 'video_recorder') and self.video_recorder and self.video_recorder.is_active():
            self.video_recorder.stop_recording()
        if hasattr(self, 'itms_stats_uploader') and self.itms_stats_uploader:
            self.itms_stats_uploader.stop()
        # 接受关闭事件
        event.accept()

    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 纯代码记事本",
            "这是一个完全通过纯代码实现的 PySide6 记事本应用示例\n\n"
            "没有使用 UI 设计器拖拽生成\n"
            "所有布局和控件都在代码中手动创建"
        )


def main():
    app = QApplication(sys.argv)

    # 设置应用信息
    app.setApplicationName("纯代码记事本")

    # 🎯 优化：先创建窗口，立即显示，再做其他初始化
    window = NotepadApp()
    window.show()
    app.processEvents()  # 立即处理显示事件

    sys.exit(app.exec())


if __name__ == "__main__":
    main()





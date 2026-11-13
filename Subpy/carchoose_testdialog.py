from __future__ import annotations

from typing import Dict, List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QLabel,
    QMessageBox,
    QVBoxLayout,
)

from Subpy.itms_vehicle_catalog import ITMSVehicleCatalog


class carchooseDialog(QDialog):
    def __init__(self, parent=None, catalog: Optional[ITMSVehicleCatalog] = None):
        super().__init__(parent)
        self.setWindowTitle("车型模式选择")
        self.setMinimumSize(320, 360)
        self.catalog_client = catalog or ITMSVehicleCatalog()
        self.catalog: Dict[str, object] = {}
        self.project_vehicle_ids: Dict[str, List[str]] = {}
        self._initializing = False
        self.init_ui()
        self._load_itms_catalog()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        cartable_group = QGroupBox("车型模式选择")
        cartable_layout = QFormLayout()

        self.label1 = QLabel("测试对象选择")
        self.label1.setAlignment(Qt.AlignCenter)
        self.cartable_combo = QComboBox()
        self.cartable_combo.setMinimumHeight(30)
        self.cartable_combo.addItems(["整车", "台架"])
        self.cartable_combo.setPlaceholderText("选择测试对象")
        self.cartable_combo.setCurrentIndex(0)
        self.cartable_combo.setEditable(True)
        self.cartable_combo.lineEdit().setReadOnly(True)
        self.cartable_combo.lineEdit().setAlignment(Qt.AlignCenter)
        cartable_layout.addRow(self.label1)
        cartable_layout.addRow(self.cartable_combo)

        self.label_vehicle_type = QLabel("车型")
        self.label_vehicle_type.setAlignment(Qt.AlignCenter)
        self.vehicle_type_combo = QComboBox()
        self.vehicle_type_combo.setMinimumHeight(30)
        self.vehicle_type_combo.addItems(["A车", "B车", "C车", "D车", "F车"])
        self.vehicle_type_combo.setPlaceholderText("选择车型")
        self.vehicle_type_combo.setCurrentIndex(0)
        self.vehicle_type_combo.setEditable(True)
        self.vehicle_type_combo.lineEdit().setReadOnly(True)
        self.vehicle_type_combo.lineEdit().setAlignment(Qt.AlignCenter)
        cartable_layout.addRow(self.label_vehicle_type)
        cartable_layout.addRow(self.vehicle_type_combo)

        self.label2 = QLabel("项目代号选择")
        self.label2.setAlignment(Qt.AlignCenter)
        self.carmode_combo = QComboBox()
        self.carmode_combo.setMinimumHeight(30)
        self.carmode_combo.setEditable(True)
        self.carmode_combo.setPlaceholderText("选择项目代号")
        self.carmode_combo.lineEdit().setReadOnly(True)
        self.carmode_combo.lineEdit().setAlignment(Qt.AlignCenter)
        self.carmode_combo.currentTextChanged.connect(self._on_project_changed)
        cartable_layout.addRow(self.label2)
        cartable_layout.addRow(self.carmode_combo)

        self.label3 = QLabel("车辆编号选择")
        self.label3.setAlignment(Qt.AlignCenter)
        self.car_No = QComboBox()
        self.car_No.setMinimumHeight(30)
        self.car_No.setEditable(True)
        self.car_No.setPlaceholderText("选择车辆编号")
        self.car_No.lineEdit().setReadOnly(True)
        self.car_No.lineEdit().setAlignment(Qt.AlignCenter)
        cartable_layout.addRow(self.label3)
        cartable_layout.addRow(self.car_No)

        self.label4 = QLabel("基线选择")
        self.label4.setAlignment(Qt.AlignCenter)
        self.testline_combo = QComboBox()
        self.testline_combo.setMinimumHeight(30)
        self.testline_combo.addItems(["EP基线", "PPV基线", "pp基线", "P基线", "SOP基线", "SOP+1基线", "SOP+基线"])
        self.testline_combo.setPlaceholderText("选择测试对象")
        self.testline_combo.setCurrentIndex(0)
        self.testline_combo.setEditable(True)
        self.testline_combo.lineEdit().setReadOnly(True)
        self.testline_combo.lineEdit().setAlignment(Qt.AlignCenter)
        cartable_layout.addRow(self.label4)
        cartable_layout.addRow(self.testline_combo)

        self.label5 = QLabel("车型平台")
        self.label5.setAlignment(Qt.AlignCenter)
        self.platform_combo = QComboBox()
        self.platform_combo.setMinimumHeight(30)
        self.platform_combo.addItems(["8295", "8797"])
        self.platform_combo.setPlaceholderText("选择车型平台")
        self.platform_combo.setCurrentIndex(0)
        self.platform_combo.setEditable(True)
        self.platform_combo.lineEdit().setReadOnly(True)
        self.platform_combo.lineEdit().setAlignment(Qt.AlignCenter)
        cartable_layout.addRow(self.label5)
        cartable_layout.addRow(self.platform_combo)

        cartable_group.setLayout(cartable_layout)
        main_layout.addWidget(cartable_group)

    def _load_itms_catalog(self):
        self.catalog = self.catalog_client.load_catalog(refresh=True)
        self.project_vehicle_ids = self.catalog.get("vehicles_by_project", {}) if isinstance(self.catalog, dict) else {}

        if not self.project_vehicle_ids:
            # 尝试缓存数据，避免网络短暂异常时弹窗为空
            self.catalog = self.catalog_client.load_catalog(refresh=False)
            self.project_vehicle_ids = self.catalog.get("vehicles_by_project", {}) if isinstance(self.catalog, dict) else {}

        self._populate_projects()

        if not self.project_vehicle_ids:
            QMessageBox.warning(
                self,
                "ITMS数据",
                "未获取到 ITMS 项目代号和车辆编号，当前列表为空。"
            )

    def _populate_projects(self):
        current_project = self.carmode_combo.currentText().strip()
        self._initializing = True
        try:
            self.carmode_combo.blockSignals(True)
            self.carmode_combo.clear()
            project_codes = self.catalog_client.get_projects(self.catalog)
            self.carmode_combo.addItems(project_codes)
            if current_project and self.carmode_combo.findText(current_project) >= 0:
                self.carmode_combo.setCurrentText(current_project)
            elif project_codes:
                self.carmode_combo.setCurrentIndex(0)
        finally:
            self.carmode_combo.blockSignals(False)
            self._initializing = False

        self._refresh_vehicle_numbers(self.carmode_combo.currentText().strip())

    def _on_project_changed(self, project_code: str):
        if self._initializing:
            return
        self._refresh_vehicle_numbers(project_code)

    def _refresh_vehicle_numbers(self, project_code: str):
        project_code = str(project_code or "").strip()
        vehicle_ids = list(self.project_vehicle_ids.get(project_code, []))

        current_vehicle = self.car_No.currentText().strip()
        current_full_vehicle_id = self.car_No.currentData()

        self.car_No.blockSignals(True)
        try:
            self.car_No.clear()

            if vehicle_ids:
                for vehicle_id in vehicle_ids:
                    display_value = self.catalog_client.display_vehicle_number(vehicle_id)
                    self.car_No.addItem(display_value, vehicle_id)

                if current_full_vehicle_id and current_full_vehicle_id in vehicle_ids:
                    idx = self.car_No.findData(current_full_vehicle_id)
                    if idx >= 0:
                        self.car_No.setCurrentIndex(idx)
                elif current_vehicle and self.car_No.findText(current_vehicle) >= 0:
                    self.car_No.setCurrentText(current_vehicle)
                else:
                    self.car_No.setCurrentIndex(0)
        finally:
            self.car_No.blockSignals(False)

    def set_selected_project_code(self, project_code: str):
        project_code = str(project_code or "").strip()
        project_codes = self.catalog_client.get_projects(self.catalog)
        if not project_codes:
            return ""
        actual_project = project_code if project_code in project_codes else project_codes[0]
        index = self.carmode_combo.findText(project_code)
        if index >= 0:
            self.carmode_combo.setCurrentIndex(index)
        else:
            self.carmode_combo.setCurrentText(actual_project)
        self._refresh_vehicle_numbers(actual_project)
        return actual_project

    def set_selected_vehicle_id(self, vehicle_id: str):
        vehicle_id = str(vehicle_id or "").strip()
        if not vehicle_id:
            return
        resolved_vehicle_id = self.catalog_client.resolve_vehicle_id(vehicle_id, self.catalog)
        target_vehicle_id = resolved_vehicle_id or vehicle_id
        if not resolved_vehicle_id and "-" not in vehicle_id:
            current_project = self.get_selected_project_code()
            if current_project:
                current_matches = [
                    item
                    for item in self.catalog_client.get_vehicle_ids(current_project, self.catalog)
                    if item == vehicle_id or self.catalog_client.vehicle_suffix_from_vehicle_id(item) == vehicle_id
                ]
                if len(current_matches) == 1:
                    target_vehicle_id = current_matches[0]

        project_code = self.catalog_client.project_code_for_vehicle_id(target_vehicle_id, self.catalog)
        if not project_code:
            project_code = self.get_selected_project_code()
        if project_code:
            actual_project = self.set_selected_project_code(project_code)
            if actual_project:
                project_code = actual_project
        index = self.car_No.findData(target_vehicle_id)
        if index >= 0:
            self.car_No.setCurrentIndex(index)

    def get_selected_vehicle_id(self) -> str:
        data = self.car_No.currentData()
        if isinstance(data, str) and data.strip():
            return data.strip()
        return self.car_No.currentText().strip()

    def get_selected_vehicle_vin(self) -> str:
        record = self.catalog_client.get_vehicle_record(
            self.get_selected_project_code(),
            self.get_selected_vehicle_id(),
            self.catalog,
        )
        return str(record.get("vin") or "").strip()

    def get_selected_project_code(self) -> str:
        return self.carmode_combo.currentText().strip()

    def set_selected_vehicle_type(self, vehicle_type: str):
        """设置车型；未知值回退到默认车型 A车。"""
        vehicle_type = str(vehicle_type or "").strip()
        index = self.vehicle_type_combo.findText(vehicle_type)
        self.vehicle_type_combo.setCurrentIndex(index if index >= 0 else 0)

    def get_selected_vehicle_type(self) -> str:
        return self.vehicle_type_combo.currentText().strip() or "A车"

    def set_selected_platform(self, platform: str):
        """设置车型平台；未知值回退到默认平台 8295。"""
        platform = str(platform or "").strip()
        index = self.platform_combo.findText(platform)
        self.platform_combo.setCurrentIndex(index if index >= 0 else 0)

    def get_selected_platform(self) -> str:
        return self.platform_combo.currentText().strip() or "8295"

    def closeEvent(self, event):
        # 点×关闭时，主动设置为Accepted状态
        self.accept()
        super().closeEvent(event)

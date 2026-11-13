from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ITMS_API_BASE_URL = os.environ.get(
    "ITS_ITMS_API_BASE_URL",
    "http://118.196.86.99",
)
DEFAULT_ITMS_VEHICLE_CATALOG_KEY = os.environ.get(
    "ITS_ITMS_VEHICLE_CATALOG_KEY",
    "",
)
DEFAULT_CACHE_FILE = PROJECT_ROOT / "配置基准文件" / "itms_vehicle_catalog.json"
DEFAULT_VEHICLE_CATALOG_PATH = "/api/v1/vehicle-management/vehicle-catalog"

PROJECT_FIELDS = (
    "project",
    "project_code",
    "projectCode",
    "project_name",
    "项目代号",
    "项目",
)
VEHICLE_NUMBER_FIELDS = (
    "vehicle_no",
    "vehicle_number",
    "vehicleNo",
    "car_no",
    "车辆编号",
    "车辆号",
    "vehicle_id",
)
VEHICLE_MODEL_FIELDS = ("vehicle_model", "model", "car_model", "车型", "车型项目")
VIN_FIELDS = ("vin", "VIN", "vin_no", "VIN号")
STATUS_FIELDS = ("status", "车辆状态")


def _natural_key(value: str) -> List[object]:
    parts = re.split(r"(\d+)", str(value or ""))
    key: List[object] = []
    for part in parts:
        if not part:
            continue
        if part.isdigit():
            key.append((0, int(part)))
        else:
            key.append((1, part.lower()))
    return key


def _clean_text(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _pick_text(item: Mapping[str, object], fields: Sequence[str]) -> str:
    for field in fields:
        if field in item:
            value = _clean_text(item.get(field))
            if value:
                return value
    return ""


def _normalize_vehicle_id(vehicle_id: object) -> str:
    return _clean_text(vehicle_id)


def _extract_project_code(vehicle_id: object) -> str:
    normalized = _normalize_vehicle_id(vehicle_id)
    if not normalized:
        return ""
    if "-" not in normalized:
        return normalized
    return normalized.split("-", 1)[0].strip()


@dataclass
class ITMSVehicleCatalog:
    api_base_url: str = DEFAULT_ITMS_API_BASE_URL
    access_key: str = DEFAULT_ITMS_VEHICLE_CATALOG_KEY
    api_path: str = DEFAULT_VEHICLE_CATALOG_PATH
    cache_file: str = str(DEFAULT_CACHE_FILE)
    timeout: float = 15.0

    def _api_base(self) -> str:
        return str(self.api_base_url or "").rstrip("/")

    def _api_url(self) -> str:
        api_path = str(self.api_path or DEFAULT_VEHICLE_CATALOG_PATH).strip()
        if api_path.startswith("http://") or api_path.startswith("https://"):
            return api_path
        return f"{self._api_base()}/{api_path.lstrip('/')}"

    def _empty_catalog(self) -> Dict[str, object]:
        return {
            "source": "empty",
            "fetched_at": None,
            "projects": [],
            "vehicles_by_project": {},
            "vehicles": [],
            "vehicle_count": 0,
        }

    def _build_catalog(self, vehicles: List[dict]) -> Dict[str, object]:
        grouped: Dict[str, List[str]] = {}
        vehicle_records: List[Dict[str, str]] = []
        seen_records = set()

        for item in vehicles or []:
            if not isinstance(item, dict):
                continue

            project_code = _pick_text(item, PROJECT_FIELDS)
            vehicle_no = _pick_text(item, VEHICLE_NUMBER_FIELDS)

            # 兼容旧监控接口缓存中的 P12-001 这类组合编号，但新数据源优先使用
            # ITMS 车辆管理里的 project / vehicle_no 字段。
            if not project_code and vehicle_no and "-" in vehicle_no:
                project_code = _extract_project_code(vehicle_no)
                vehicle_no = self.vehicle_suffix_from_vehicle_id(vehicle_no)

            if not project_code or not vehicle_no:
                continue

            grouped.setdefault(project_code, [])
            if vehicle_no not in grouped[project_code]:
                grouped[project_code].append(vehicle_no)

            record_key = (project_code, vehicle_no)
            if record_key in seen_records:
                continue
            seen_records.add(record_key)
            vehicle_records.append({
                "project": project_code,
                "vehicle_no": vehicle_no,
                "vehicle_model": _pick_text(item, VEHICLE_MODEL_FIELDS),
                "vin": _pick_text(item, VIN_FIELDS),
                "status": _pick_text(item, STATUS_FIELDS),
            })

        for vehicle_numbers in grouped.values():
            vehicle_numbers.sort(key=_natural_key)

        projects = sorted(grouped.keys(), key=_natural_key)
        vehicle_records.sort(key=lambda item: (
            _natural_key(item.get("project", "")),
            _natural_key(item.get("vehicle_no", "")),
        ))
        return {
            "source": self._api_url(),
            "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "projects": projects,
            "vehicles_by_project": grouped,
            "vehicles": vehicle_records,
            "vehicle_count": sum(len(values) for values in grouped.values()),
        }

    def fetch_remote_catalog(self) -> Dict[str, object]:
        headers = {}
        if str(self.access_key or "").strip():
            headers["X-ITMS-Vehicle-Catalog-Key"] = str(self.access_key).strip()

        response = requests.get(self._api_url(), headers=headers, timeout=self.timeout)
        response.raise_for_status()

        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("ITMS 返回格式不正确")
        if int(payload.get("code", -1)) != 0:
            raise ValueError(payload.get("message") or "ITMS 接口返回失败")

        vehicles = payload.get("vehicles", [])
        if not isinstance(vehicles, list):
            data = payload.get("data", [])
            vehicles = data if isinstance(data, list) else []
        return self._build_catalog(vehicles)

    def load_cached_catalog(self) -> Dict[str, object]:
        cache_path = Path(self.cache_file)
        if not cache_path.exists():
            return self._empty_catalog()
        try:
            with cache_path.open("r", encoding="utf-8") as f:
                payload = json.load(f)
            if not isinstance(payload, dict):
                return self._empty_catalog()
            payload.setdefault("projects", [])
            payload.setdefault("vehicles_by_project", {})
            payload.setdefault("vehicles", [])
            payload.setdefault("vehicle_count", 0)
            payload.setdefault("source", "cache")
            return payload
        except Exception:
            return self._empty_catalog()

    def save_cache(self, catalog: Dict[str, object]) -> None:
        cache_path = Path(self.cache_file)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with cache_path.open("w", encoding="utf-8") as f:
            json.dump(catalog, f, ensure_ascii=False, indent=2)

    def load_catalog(self, refresh: bool = True) -> Dict[str, object]:
        if refresh:
            try:
                catalog = self.fetch_remote_catalog()
                self.save_cache(catalog)
                return catalog
            except Exception:
                pass
        return self.load_cached_catalog()

    @staticmethod
    def project_code_from_vehicle_id(vehicle_id: str) -> str:
        return _extract_project_code(vehicle_id)

    @staticmethod
    def vehicle_suffix_from_vehicle_id(vehicle_id: str) -> str:
        normalized = _normalize_vehicle_id(vehicle_id)
        if "-" not in normalized:
            return normalized
        return normalized.split("-", 1)[1].strip()

    @staticmethod
    def display_vehicle_number(vehicle_id: str) -> str:
        return _normalize_vehicle_id(vehicle_id)

    def get_projects(self, catalog: Optional[Dict[str, object]] = None) -> List[str]:
        catalog = catalog or self.load_cached_catalog()
        projects = catalog.get("projects", [])
        return [_clean_text(item) for item in projects if _clean_text(item)]

    def get_vehicle_ids(self, project_code: str, catalog: Optional[Dict[str, object]] = None) -> List[str]:
        catalog = catalog or self.load_cached_catalog()
        vehicle_map = catalog.get("vehicles_by_project", {})
        if not isinstance(vehicle_map, dict):
            return []
        project_code = _clean_text(project_code)
        values = vehicle_map.get(project_code, [])
        if not isinstance(values, list):
            return []
        return [_clean_text(item) for item in values if _clean_text(item)]

    def get_vehicle_record(
        self,
        project_code: str,
        vehicle_id: str,
        catalog: Optional[Dict[str, object]] = None,
    ) -> Dict[str, str]:
        """Return the ITMS vehicle record, including VIN and vehicle model."""
        catalog = catalog or self.load_cached_catalog()
        project_code = _clean_text(project_code)
        vehicle_id = _clean_text(vehicle_id)
        vehicle_suffix = self.vehicle_suffix_from_vehicle_id(vehicle_id)

        records = catalog.get("vehicles", [])
        if not isinstance(records, list):
            return {}

        for record in records:
            if not isinstance(record, dict):
                continue
            record_project = _clean_text(record.get("project"))
            record_vehicle = _clean_text(record.get("vehicle_no"))
            if record_project != project_code:
                continue
            if record_vehicle == vehicle_id or self.vehicle_suffix_from_vehicle_id(record_vehicle) == vehicle_suffix:
                return {
                    "project": record_project,
                    "vehicle_no": record_vehicle,
                    "vehicle_model": _clean_text(record.get("vehicle_model")),
                    "vin": _clean_text(record.get("vin")),
                    "status": _clean_text(record.get("status")),
                }
        return {}

    def get_all_vehicle_ids(self, catalog: Optional[Dict[str, object]] = None) -> List[str]:
        catalog = catalog or self.load_cached_catalog()
        vehicle_map = catalog.get("vehicles_by_project", {})
        if not isinstance(vehicle_map, dict):
            return []
        all_vehicle_ids: List[str] = []
        for values in vehicle_map.values():
            if not isinstance(values, list):
                continue
            for item in values:
                vehicle_id = _clean_text(item)
                if vehicle_id and vehicle_id not in all_vehicle_ids:
                    all_vehicle_ids.append(vehicle_id)
        all_vehicle_ids.sort(key=_natural_key)
        return all_vehicle_ids

    def project_code_for_vehicle_id(self, vehicle_id: str, catalog: Optional[Dict[str, object]] = None) -> str:
        vehicle_id = _clean_text(vehicle_id)
        if not vehicle_id:
            return ""

        catalog = catalog or self.load_cached_catalog()
        vehicle_map = catalog.get("vehicles_by_project", {})
        if isinstance(vehicle_map, dict):
            for project_code, values in vehicle_map.items():
                if isinstance(values, list) and vehicle_id in [_clean_text(item) for item in values]:
                    return _clean_text(project_code)

        return _extract_project_code(vehicle_id) if "-" in vehicle_id else ""

    def find_vehicle_ids_by_suffix(self, suffix: str, catalog: Optional[Dict[str, object]] = None) -> List[str]:
        suffix = _clean_text(suffix)
        if not suffix:
            return []
        matches: List[str] = []
        for vehicle_id in self.get_all_vehicle_ids(catalog):
            if self.vehicle_suffix_from_vehicle_id(vehicle_id) == suffix:
                matches.append(vehicle_id)
        return matches

    def resolve_vehicle_id(self, value: str, catalog: Optional[Dict[str, object]] = None) -> Optional[str]:
        value = _clean_text(value)
        if not value:
            return None

        catalog = catalog or self.load_cached_catalog()
        all_vehicle_ids = self.get_all_vehicle_ids(catalog)
        if value in all_vehicle_ids:
            return value

        if "-" in value:
            suffix = self.vehicle_suffix_from_vehicle_id(value)
            if suffix in all_vehicle_ids:
                return suffix
            matches = [vehicle_id for vehicle_id in all_vehicle_ids if self.vehicle_suffix_from_vehicle_id(vehicle_id) == suffix]
            if len(matches) == 1:
                return matches[0]
            return None

        matches = self.find_vehicle_ids_by_suffix(value, catalog)
        if len(matches) == 1:
            return matches[0]
        return None

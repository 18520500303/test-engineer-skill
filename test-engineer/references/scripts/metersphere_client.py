#!/usr/bin/env python3
# 复用 MeterSphere 鉴权与请求逻辑，避免每个脚本重复实现。

import argparse
import base64
import json
import os
import ssl
import sys
import time
from dataclasses import dataclass

import requests
import urllib3
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding as crypto_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_BASE_URL = "https://rpd.gz.cvte.cn/metersphere/server"


class MeterSphereApiError(RuntimeError):
    """MeterSphere API 调用失败。"""


@dataclass(frozen=True)
class MeterSphereConfig:
    # 从环境变量读取连接参数，避免明文写进脚本。
    access_key: str
    secret_key: str
    project_id: str
    verify_ssl: bool = False
    base_url: str = DEFAULT_BASE_URL

    @classmethod
    def from_env(cls) -> "MeterSphereConfig":
        if load_dotenv:
            load_dotenv()

        access_key = os.environ.get("MS_ACCESS_KEY", "").strip()
        secret_key = os.environ.get("MS_SECRET_KEY", "").strip()
        project_id = os.environ.get("MS_PROJECT_ID", "").strip()
        verify_ssl = os.environ.get("MS_VERIFY_SSL", "0").strip().lower() in {"1", "true", "yes"}
        base_url = os.environ.get("MS_BASE_URL", DEFAULT_BASE_URL).strip() or DEFAULT_BASE_URL

        if not access_key or not secret_key or not project_id:
            raise MeterSphereApiError(
                "请配置环境变量 MS_ACCESS_KEY、MS_SECRET_KEY、MS_PROJECT_ID（可在项目目录放置 .env）"
            )
        return cls(
            access_key=access_key,
            secret_key=secret_key,
            project_id=project_id,
            verify_ssl=verify_ssl,
            base_url=base_url.rstrip("/"),
        )


def _norm_key(value: str) -> bytes:
    raw = value.encode("utf-8")
    if len(raw) <= 16:
        return raw.ljust(16, b"0")
    if len(raw) <= 24:
        return raw.ljust(24, b"0")
    return raw.ljust(32, b"0") if len(raw) <= 32 else raw[:32]


def _norm_iv(value: str) -> bytes:
    raw = value.encode("utf-8")
    return raw[:16] if len(raw) >= 16 else raw.ljust(16, b"0")


def make_signature(access_key: str, secret_key: str) -> tuple[str, str]:
    ts = str(int(time.time() * 1000))
    plaintext = f"{access_key}|{ts}".encode("utf-8")
    padder = crypto_padding.PKCS7(128).padder()
    padded = padder.update(plaintext) + padder.finalize()
    cipher = Cipher(
        algorithms.AES(_norm_key(secret_key)),
        modes.CBC(_norm_iv(access_key)),
        backend=default_backend(),
    )
    encryptor = cipher.encryptor()
    signature = base64.b64encode(encryptor.update(padded) + encryptor.finalize()).decode("utf-8")
    return ts, signature


def walk_modules(nodes, parent_name=""):
    """遍历模块树，返回 (id, path) 元组。"""
    if not nodes:
        return
    for node in nodes:
        name = node.get("name") or ""
        full_name = f"{parent_name}/{name}".strip("/")
        yield node.get("id"), full_name
        yield from walk_modules(node.get("children") or [], full_name)


def resolve_module_id(tree_data, module_name: str | None, module_id: str | None) -> str:
    # 优先使用显式模块 ID，其次做名称包含匹配。
    if module_id:
        return module_id.strip()

    nodes = tree_data.get("data") or []
    if not nodes:
        raise MeterSphereApiError("模块树为空，请检查 MS_PROJECT_ID")

    flat = list(walk_modules(nodes))
    if module_name and module_name.strip():
        pattern = module_name.strip()
        for mid, full_name in flat:
            leaf_name = full_name.split("/")[-1] if full_name else ""
            if pattern in full_name or pattern in leaf_name:
                return mid
        raise MeterSphereApiError(
            f"未找到模块名包含「{pattern}」的节点。当前模块: " + ", ".join(item[1] for item in flat[:30])
        )

    root = nodes[0]
    children = root.get("children") or []
    if children:
        return children[0].get("id") or root.get("id")
    return root.get("id")


def find_priority_field_id(case_detail: dict) -> str | None:
    # 优先找“用例等级/优先级”，找不到时退化为第一个自定义字段。
    fields = (case_detail.get("data") or {}).get("customFields") or []
    for field in fields:
        field_name = (field.get("fieldName") or field.get("name") or "").lower()
        if "等级" in field_name or "优先级" in field_name or "priority" in field_name:
            return field.get("fieldId") or field.get("id")
    if fields:
        return fields[0].get("fieldId") or fields[0].get("id")
    return None


class MeterSphereClient:
    # 统一封装签名、请求和常用 API。
    def __init__(self, config: MeterSphereConfig):
        self.config = config
        if not config.verify_ssl:
            ssl._create_default_https_context = ssl._create_unverified_context  # noqa: SLF001

    def _headers(self, *, content_type: str | None = None) -> dict:
        timestamp, signature = make_signature(self.config.access_key, self.config.secret_key)
        headers = {
            "accessKey": self.config.access_key,
            "signature": signature,
            "timestamp": timestamp,
            "Accept": "application/json",
        }
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    def _parse_response(self, response: requests.Response) -> dict:
        try:
            return json.loads(response.text, strict=False) if response.text else {}
        except json.JSONDecodeError as exc:
            raise MeterSphereApiError(f"响应不是合法 JSON: {response.text[:200]}") from exc

    def get(self, path: str, *, timeout: int = 60) -> dict:
        response = requests.get(
            f"{self.config.base_url}{path}",
            headers=self._headers(),
            timeout=timeout,
            verify=self.config.verify_ssl,
        )
        return self._parse_response(response)

    def post_json(self, path: str, body: dict, *, timeout: int = 60) -> dict:
        response = requests.post(
            f"{self.config.base_url}{path}",
            headers=self._headers(content_type="application/json"),
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            timeout=timeout,
            verify=self.config.verify_ssl,
        )
        return self._parse_response(response)

    def post_multipart_json(self, path: str, payload: dict, *, timeout: int = 120) -> dict:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        response = requests.post(
            f"{self.config.base_url}{path}",
            headers=self._headers(),
            files={"request": ("request.json", raw, "application/json")},
            timeout=timeout,
            verify=self.config.verify_ssl,
        )
        return self._parse_response(response)

    def get_project(self) -> dict:
        return self.get(f"/project/get/{self.config.project_id}")

    def get_module_tree(self) -> dict:
        return self.get(f"/functional/case/module/tree/{self.config.project_id}")

    def list_cases(self, *, current: int = 1, page_size: int = 5) -> dict:
        return self.post_json(
            "/functional/case/page",
            {"projectId": self.config.project_id, "current": current, "pageSize": page_size},
        )

    def list_all_cases(self, *, page_size: int = 100) -> list[dict]:
        # 统一分页拉全量，用于查重等读操作。
        current = 1
        rows = []
        while True:
            response = self.list_cases(current=current, page_size=page_size)
            if response.get("code") != 100200:
                raise MeterSphereApiError(f"functional/case/page 失败: {response}")
            data = response.get("data") or {}
            page_rows = data.get("list") or []
            if not page_rows:
                break
            rows.extend(page_rows)
            if len(rows) >= (data.get("total") or 0):
                break
            current += 1
        return rows

    def get_case_names_by_module(self, module_id: str) -> set[str]:
        # 当前实例无按模块过滤接口时，先拉全量再按 moduleId 过滤。
        names = set()
        for case in self.list_all_cases(page_size=100):
            if case.get("moduleId") == module_id:
                name = (case.get("name") or "").strip()
                if name:
                    names.add(name)
        return names

    def get_case_detail(self, case_id: str) -> dict:
        return self.get(f"/functional/case/detail/{case_id}")

    def add_case(self, payload: dict) -> dict:
        return self.post_multipart_json("/functional/case/add", payload)

    def add_module(self, parent_id: str, name: str, module_type: str = "module") -> dict:
        return self.post_json(
            "/functional/case/module/add",
            {
                "projectId": self.config.project_id,
                "parentId": parent_id,
                "name": name,
                "type": module_type,
            },
        )

    def delete_cases_to_gc(self, case_ids: list[str]) -> dict:
        return self.post_json(
            "/functional/case/batch/delete-to-gc",
            {
                "projectId": self.config.project_id,
                "selectIds": case_ids,
                "selectAll": False,
                "excludeIds": [],
            },
        )

    def resolve_template_and_priority(self, template_id_override: str = "") -> tuple[str, str | None]:
        # 当前实例若没有 template/list，则通过现有用例详情反推。
        page = self.list_cases(current=1, page_size=5)
        if page.get("code") != 100200:
            raise MeterSphereApiError(f"functional/case/page 失败: {page}")

        case_list = (page.get("data") or {}).get("list") or []
        if not case_list:
            if template_id_override:
                return template_id_override, None
            raise MeterSphereApiError(
                "项目中无任何功能用例，无法自动获取 templateId，请先手动创建一条用例或配置 MS_TEMPLATE_ID"
            )

        detail = self.get_case_detail(case_list[0]["id"])
        if detail.get("code") != 100200:
            raise MeterSphereApiError(f"functional/case/detail 失败: {detail}")

        priority_field_id = find_priority_field_id(detail)
        if template_id_override:
            return template_id_override, priority_field_id

        template_id = (detail.get("data") or {}).get("templateId")
        if not template_id:
            raise MeterSphereApiError("用例详情中无 templateId，请配置 MS_TEMPLATE_ID")
        return str(template_id), priority_field_id


def _print_json(data: dict):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def _print_module_tree(nodes, depth: int = 0):
    for node in nodes or []:
        print(f"{'  ' * depth}- {node.get('name')} [{node.get('id')}]")
        _print_module_tree(node.get("children") or [], depth + 1)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MeterSphere 客户端 CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("project", help="读取当前项目信息")
    subparsers.add_parser("module-tree", help="打印当前项目模块树")

    add_module_parser = subparsers.add_parser("add-module", help="创建用例模块")
    add_module_parser.add_argument("--parent-id", required=True, help="父模块 ID")
    add_module_parser.add_argument("--name", required=True, help="新模块名称")
    add_module_parser.add_argument("--type", default="module", help="模块类型，默认 module")

    delete_parser = subparsers.add_parser("delete-to-gc", help="把用例移入回收站")
    delete_parser.add_argument("--ids", nargs="+", required=True, help="待移入回收站的用例 ID 列表")

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        client = MeterSphereClient(MeterSphereConfig.from_env())
    except MeterSphereApiError as exc:
        print(exc, file=sys.stderr)
        return 2

    if args.command == "project":
        response = client.get_project()
        _print_json(response)
        return 0 if response.get("code") == 100200 else 1

    if args.command == "module-tree":
        response = client.get_module_tree()
        if response.get("code") != 100200:
            _print_json(response)
            return 1
        _print_module_tree(response.get("data") or [])
        return 0

    if args.command == "add-module":
        response = client.add_module(parent_id=args.parent_id, name=args.name, module_type=args.type)
        _print_json(response)
        return 0 if response.get("code") == 100200 else 1

    if args.command == "delete-to-gc":
        response = client.delete_cases_to_gc(args.ids)
        _print_json(response)
        return 0 if response.get("code") == 100200 else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())

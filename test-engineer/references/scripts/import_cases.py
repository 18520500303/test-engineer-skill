#!/usr/bin/env python3
# 通用 MeterSphere 用例导入器：负责读取业务数据、解析模块、组装请求并批量创建用例。

import argparse
import importlib
import json
import os
import sys
import time
import uuid

from metersphere_client import MeterSphereApiError, MeterSphereClient, MeterSphereConfig, resolve_module_id


def normalize_case_name(name: str | None) -> str:
    # 名称去空白后参与查重，避免同名但前后空格不同。
    return (name or "").strip()


def split_cases_by_duplicate(cases: list[dict], existing_case_names: set[str]) -> tuple[list[dict], list[dict]]:
    # 同模块下：已有同名用例跳过；同一批次里重复名称也跳过后者。
    planned = []
    duplicates = []
    seen_names = {normalize_case_name(name) for name in existing_case_names if normalize_case_name(name)}

    for case in cases:
        normalized_name = normalize_case_name(case.get("name"))
        if not normalized_name or normalized_name in seen_names:
            duplicates.append(case)
            continue
        planned.append(case)
        seen_names.add(normalized_name)

    return planned, duplicates


def build_steps_payload(steps: list[tuple[str, str]]) -> str:
    # 步骤 ID 使用 UUID，和平台现有用例格式保持一致。
    payload = []
    for idx, (desc, result) in enumerate(steps):
        payload.append({"id": str(uuid.uuid4()), "num": idx, "desc": desc, "result": result})
    return json.dumps(payload, ensure_ascii=False)


def load_dataset(module_name: str):
    # 业务数据模块只负责提供 CASES / DEFAULT_TAGS / SOURCE_REQUIREMENT 等常量。
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        raise MeterSphereApiError(f"未找到业务数据模块：{module_name}") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="通用 MeterSphere 用例导入器")
    parser.add_argument(
        "--dataset",
        default=os.environ.get("MS_CASE_DATASET", "case_data.silent_mode_cases"),
        help="业务数据模块路径，如 case_data.silent_mode_cases",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只预演导入流程并打印最终 payload，不实际写入 MeterSphere",
    )
    parser.add_argument(
        "--allow-duplicates",
        action="store_true",
        help="允许同模块下同名用例继续导入；默认会自动跳过重复项",
    )
    return parser.parse_args()


def build_case_payload(
    case: dict,
    *,
    project_id: str,
    template_id: str,
    module_id: str,
    default_tags: list[str],
    source_requirement: str,
    custom_fields: list[dict],
) -> dict:
    # 导入和 dry-run 共用同一套 payload 组装逻辑，避免两套逻辑不一致。
    return {
        "projectId": project_id,
        "templateId": template_id,
        "moduleId": module_id,
        "name": case["name"],
        "caseEditType": "STEP",
        "prerequisite": case.get("prerequisite", ""),
        "steps": build_steps_payload(case["steps"]),
        "textDescription": "",
        "expectedResult": "",
        "description": f"来源：{source_requirement}" if source_requirement else "",
        "tags": list(case.get("tags", default_tags)),
        "customFields": list(case.get("customFields", custom_fields)),
    }


def main() -> int:
    args = parse_args()
    module_name = os.environ.get("MS_MODULE_NAME", "").strip()
    module_id = os.environ.get("MS_MODULE_ID", "").strip()
    template_id_env = os.environ.get("MS_TEMPLATE_ID", "").strip()

    try:
        dataset = load_dataset(args.dataset)
        config = MeterSphereConfig.from_env()
        client = MeterSphereClient(config)
        template_id, priority_field_id = client.resolve_template_and_priority(template_id_env)
    except MeterSphereApiError as exc:
        print(exc, file=sys.stderr)
        return 2

    cases = getattr(dataset, "CASES", None)
    if not cases:
        print(f"业务数据模块 {args.dataset} 未提供 CASES", file=sys.stderr)
        return 2

    module_tree = client.get_module_tree()
    if module_tree.get("code") != 100200:
        print("module/tree 失败:", module_tree, file=sys.stderr)
        return 1

    try:
        resolved_module_id = resolve_module_id(module_tree, module_name or None, module_id or None)
    except MeterSphereApiError as exc:
        print(exc, file=sys.stderr)
        return 1

    default_priority = getattr(dataset, "DEFAULT_PRIORITY", "P1")
    default_tags = list(getattr(dataset, "DEFAULT_TAGS", []))
    source_requirement = getattr(dataset, "SOURCE_REQUIREMENT", "")

    existing_case_names = set()
    if not args.allow_duplicates:
        try:
            existing_case_names = client.get_case_names_by_module(resolved_module_id)
        except MeterSphereApiError as exc:
            print(exc, file=sys.stderr)
            return 1

    target_cases = list(cases)
    duplicate_cases = []
    if not args.allow_duplicates:
        target_cases, duplicate_cases = split_cases_by_duplicate(target_cases, existing_case_names)

    custom_fields = []
    if priority_field_id:
        custom_fields.append({"fieldId": priority_field_id, "value": default_priority})

    print(
        f"dataset={args.dataset}\n"
        f"projectId={config.project_id}\n"
        f"templateId={template_id}\n"
        f"moduleId={resolved_module_id}\n"
        f"用例等级 fieldId={priority_field_id}\n"
        f"dryRun={args.dry_run}\n"
        f"allowDuplicates={args.allow_duplicates}\n"
        f"已存在同模块名称数={len(existing_case_names)}\n"
        f"待导入={len(target_cases)}\n"
        f"重复跳过={len(duplicate_cases)}"
    )

    for case in duplicate_cases:
        print(f"[SKIP DUPLICATE] {case.get('name', '')}")

    ok = 0
    fail = 0
    previewed = 0
    for index, case in enumerate(target_cases, start=1):
        payload = build_case_payload(
            case,
            project_id=config.project_id,
            template_id=template_id,
            module_id=resolved_module_id,
            default_tags=default_tags,
            source_requirement=source_requirement,
            custom_fields=custom_fields,
        )
        if args.dry_run:
            previewed += 1
            print(f"\n[DRY-RUN {index}/{len(target_cases)}] {case['name']}")
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            continue
        response = client.add_case(payload)
        if response.get("code") == 100200:
            case_id = (response.get("data") or {}).get("id", "")
            print(f"[OK] {case['name']} -> {case_id}")
            ok += 1
        else:
            print(f"[FAIL] {case['name']}: {response}", file=sys.stderr)
            fail += 1
        time.sleep(0.3)

    if args.dry_run:
        print(f"\n预演完成：共生成 {previewed} 条 payload，跳过重复 {len(duplicate_cases)} 条，未写入 MeterSphere")
        return 0

    print(f"\n完成：成功 {ok}，失败 {fail}，跳过重复 {len(duplicate_cases)}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

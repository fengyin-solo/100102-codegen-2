"""内存数据仓库：给每个业务模块准备一份可筛选、可流转的示例数据。

真实项目里这里会换成数据库访问层；当前实现只依赖标准库，保证克隆下来就能起。
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from app.seed import SEED_ROWS

# 模块名与左侧导航一一对应，看板下钻时直接用这里的名称与路径，保证两边对得上。
MODULE_LABELS: dict[str, str] = {
    "facility": "设施台账",
    "bridge": "桥梁档案",
    "tunnel": "隧道管理",
    "pavement": "路面状况",
    "patrol": "日常巡查",
    "disease": "病害记录",
    "repair": "养护维修",
    "material2": "养护材料",
    "machine": "养护机械",
    "emergency": "应急抢险",
    "deicing": "除雪防汛",
    "occupy": "占道施工",
    "greening": "绿化管护",
    "safety2": "交安设施",
    "geom": "边坡挡墙",
    "light": "路灯管养",
    "drain": "排水设施",
    "plan": "养护计划",
    "complaint": "市民热线",
    "load": "车辆超限",
}

# 看板支持的统计区间：days 是往前推的天数（含今天），None 表示不限。
OVERVIEW_RANGES: dict[str, dict[str, Any]] = {
    "today": {"label": "今日", "days": 0},
    "week": {"label": "近7天", "days": 6},
    "month": {"label": "近30天", "days": 29},
    "all": {"label": "全部", "days": None},
}


def _row_date(value: Any) -> date | None:
    """把记录上的 created_at 解析成日期；缺失或写坏了就当没有日期。"""
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return date.fromisoformat(value.strip()[:10])
    except ValueError:
        return None


class Store:
    def __init__(self) -> None:
        self._tables: dict[str, list[dict[str, Any]]] = {
            name: [dict(row) for row in rows] for name, rows in SEED_ROWS.items()
        }

    def module_names(self) -> list[str]:
        return sorted(self._tables)

    def rows(self, module: str) -> list[dict[str, Any]]:
        return self._tables.setdefault(module, [])

    def find(self, module: str, entry_id: int) -> dict[str, Any] | None:
        for row in self.rows(module):
            if int(row.get("id", 0)) == entry_id:
                return row
        return None

    def overview(self, range_key: str = "today") -> dict[str, object]:
        """按统计区间汇总各模块待处理量与异常量，供看板卡片下钻。

        返回的模块列表已经按待处理量从多到少排好；区间内没有记录的模块用
        has_data=False 标出来，前端据此显示“暂无”而不是 0。
        """
        spec = OVERVIEW_RANGES[range_key]
        days = spec["days"]
        start = None if days is None else date.today() - timedelta(days=int(days))

        modules: list[dict[str, object]] = []
        for name in self.module_names():
            rows = self.rows(name)
            in_range = [row for row in rows if self._in_range(row, start)]
            dates = [parsed for row in rows if (parsed := _row_date(row.get("created_at"))) is not None]
            modules.append({
                "name": name,
                "label": MODULE_LABELS.get(name, name),
                "path": f"/{name}",
                "created": len(in_range),
                "pending": sum(1 for row in in_range if row.get("pending")),
                "abnormal": sum(1 for row in in_range if row.get("abnormal")),
                "latest_at": str(max(dates)) if dates else None,
                "has_data": bool(in_range),
            })
        modules.sort(
            key=lambda item: (
                -int(item["pending"]),
                -int(item["abnormal"]),
                -int(item["created"]),
                str(item["label"]),
            )
        )

        created_label = "累计记录" if range_key == "all" else f"{spec['label']}新增"
        cards = [
            {"key": "modules", "label": "业务模块", "value": len(modules)},
            {"key": "created", "label": created_label, "value": sum(int(item["created"]) for item in modules)},
            {"key": "pending", "label": "待处理", "value": sum(int(item["pending"]) for item in modules)},
            {"key": "abnormal", "label": "异常量", "value": sum(int(item["abnormal"]) for item in modules)},
        ]
        return {
            "range": range_key,
            "range_label": spec["label"],
            "cards": cards,
            "modules": modules,
        }

    @staticmethod
    def _in_range(row: dict[str, Any], start: date | None) -> bool:
        """判断记录是否落在统计区间内；没有日期的记录只进“全部”区间。"""
        if start is None:
            return True
        parsed = _row_date(row.get("created_at"))
        return parsed is not None and parsed >= start


store = Store()

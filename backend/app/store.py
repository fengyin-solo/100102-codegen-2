"""内存数据仓库：给每个业务模块准备一份可筛选、可流转的示例数据。

真实项目里这里会换成数据库访问层；当前实现只依赖标准库，保证克隆下来就能起。
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.seed import SEED_ROWS

# 看板模块注册表：顺序即左侧导航顺序，key 同时是数据表名和前端路由路径。
# 看板与导航必须对同一份注册表，避免两边各写一套名字、入口对不上。
MODULE_REGISTRY: list[dict[str, str]] = [
    {"key": "facility", "name": "设施台账"},
    {"key": "bridge", "name": "桥梁档案"},
    {"key": "tunnel", "name": "隧道管理"},
    {"key": "pavement", "name": "路面状况"},
    {"key": "patrol", "name": "日常巡查"},
    {"key": "disease", "name": "病害记录"},
    {"key": "repair", "name": "养护维修"},
    {"key": "material2", "name": "养护材料"},
    {"key": "machine", "name": "养护机械"},
    {"key": "emergency", "name": "应急抢险"},
    {"key": "deicing", "name": "除雪防汛"},
    {"key": "occupy", "name": "占道施工"},
    {"key": "greening", "name": "绿化管护"},
    {"key": "safety2", "name": "交安设施"},
    {"key": "geom", "name": "边坡挡墙"},
    {"key": "light", "name": "路灯管养"},
    {"key": "drain", "name": "排水设施"},
    {"key": "plan", "name": "养护计划"},
    {"key": "complaint", "name": "市民热线"},
    {"key": "load", "name": "车辆超限"},
]

# 统计区间：键为前端传入值，值为相对当前时间的起始偏移；None 表示不限区间。
PERIOD_DAYS: dict[str, int | None] = {
    "today": 0,
    "week": 7,
    "month": 30,
    "all": None,
}

_TIME_FMT = "%Y-%m-%d %H:%M"


def _parse_time(value: Any) -> datetime | None:
    """容错解析记录时间：兼容 'YYYY-MM-DD HH:MM'、'YYYY-MM-DD' 与空值。"""
    if not value:
        return None
    text = str(value).strip()
    for fmt in (_TIME_FMT, "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


class Store:
    def __init__(self) -> None:
        self._tables: dict[str, list[dict[str, Any]]] = {
            name: [dict(row) for row in rows] for name, rows in SEED_ROWS.items()
        }
        self._stamp_seed_rows()

    def _stamp_seed_rows(self) -> None:
        """给种子记录补登记时间。

        示例数据本身不带时间字段，而看板要按统计区间过滤、展示最近一条记录的
        时间，这里按表顺序给每条记录铺一个从近到远的确定性时间戳：前几个模块
        有今日/本周的数据，后面的模块逐步落到更早的区间，便于直接看出不同区间
        下哪些模块「暂无数据」。
        """
        now = datetime.now().replace(second=0, microsecond=0)
        index = 0
        for name in (item["key"] for item in MODULE_REGISTRY):
            for row in self._tables.get(name, []):
                if not row.get("created_at"):
                    days_ago = (index * 3 + 7) % 46
                    stamp = now - timedelta(
                        days=days_ago,
                        hours=(index * 5) % 9,
                        minutes=(index * 13) % 60,
                    )
                    row["created_at"] = stamp.strftime(_TIME_FMT)
                index += 1

    def module_names(self) -> list[str]:
        return [item["key"] for item in MODULE_REGISTRY]

    def module_label(self, key: str) -> str:
        for item in MODULE_REGISTRY:
            if item["key"] == key:
                return item["name"]
        return key

    def rows(self, module: str) -> list[dict[str, Any]]:
        return self._tables.setdefault(module, [])

    def find(self, module: str, entry_id: int) -> dict[str, Any] | None:
        for row in self.rows(module):
            if int(row.get("id", 0)) == entry_id:
                return row
        return None

    def overview(self, period: str = "month") -> dict[str, object]:
        """运营概览：按统计区间汇总各模块的待处理量、异常量与最近记录时间。

        某个模块在区间内没有记录时，计数与最近时间返回 None，由前端显式展示
        「暂无」，而不是把「没数据」和「数量为 0」混为一谈。
        """
        days = PERIOD_DAYS.get(period, 30)
        start: datetime | None = None
        if days is not None:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            start = today if days == 0 else today - timedelta(days=days - 1)

        modules: list[dict[str, object]] = []
        for item in MODULE_REGISTRY:
            key = item["key"]
            rows = self.rows(key)
            scoped = [
                row
                for row in rows
                if start is None
                or ((ts := _parse_time(row.get("created_at"))) is not None and ts >= start)
            ]
            if scoped:
                latest = max(
                    (_parse_time(row.get("created_at")) for row in scoped),
                    key=lambda ts: ts or datetime.min,
                )
                module_entry: dict[str, object] = {
                    "key": key,
                    "name": item["name"],
                    "path": f"/{key}",
                    "created": len(scoped),
                    "pending": sum(1 for row in scoped if row.get("pending")),
                    "abnormal": sum(1 for row in scoped if row.get("abnormal")),
                    "latest_at": latest.strftime(_TIME_FMT) if latest else None,
                }
            else:
                module_entry = {
                    "key": key,
                    "name": item["name"],
                    "path": f"/{key}",
                    "created": None,
                    "pending": None,
                    "abnormal": None,
                    "latest_at": None,
                }
            modules.append(module_entry)

        active = [item for item in modules if item["created"] is not None]
        cards = [
            {"key": "modules", "label": "业务模块", "value": len(active)},
            {"key": "created", "label": "新增记录", "value": sum(int(item["created"] or 0) for item in active)},
            {"key": "pending", "label": "待处理", "value": sum(int(item["pending"] or 0) for item in active)},
            {"key": "abnormal", "label": "异常量", "value": sum(int(item["abnormal"] or 0) for item in active)},
        ]
        return {"period": period, "cards": cards, "modules": modules}


store = Store()

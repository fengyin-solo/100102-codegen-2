/**
 * 模块注册表：左侧导航与运营概览看板共用同一份定义，
 * 保证看板下钻入口和导航里的模块始终对得上（名称、路径、顺序）。
 * key 与后端数据表、路由路径保持一致。
 */
export interface ModuleMeta {
  key: string
  name: string
  path: string
}

export const MODULES: ModuleMeta[] = [
  { key: 'facility', name: '设施台账', path: '/facility' },
  { key: 'bridge', name: '桥梁档案', path: '/bridge' },
  { key: 'tunnel', name: '隧道管理', path: '/tunnel' },
  { key: 'pavement', name: '路面状况', path: '/pavement' },
  { key: 'patrol', name: '日常巡查', path: '/patrol' },
  { key: 'disease', name: '病害记录', path: '/disease' },
  { key: 'repair', name: '养护维修', path: '/repair' },
  { key: 'material2', name: '养护材料', path: '/material2' },
  { key: 'machine', name: '养护机械', path: '/machine' },
  { key: 'emergency', name: '应急抢险', path: '/emergency' },
  { key: 'deicing', name: '除雪防汛', path: '/deicing' },
  { key: 'occupy', name: '占道施工', path: '/occupy' },
  { key: 'greening', name: '绿化管护', path: '/greening' },
  { key: 'safety2', name: '交安设施', path: '/safety2' },
  { key: 'geom', name: '边坡挡墙', path: '/geom' },
  { key: 'light', name: '路灯管养', path: '/light' },
  { key: 'drain', name: '排水设施', path: '/drain' },
  { key: 'plan', name: '养护计划', path: '/plan' },
  { key: 'complaint', name: '市民热线', path: '/complaint' },
  { key: 'load', name: '车辆超限', path: '/load' },
]

/** 看板统计区间选项，value 与后端 /api/overview 的 period 参数对齐。 */
export const PERIOD_OPTIONS = [
  { value: 'today', label: '今日' },
  { value: 'week', label: '近7天' },
  { value: 'month', label: '近30天' },
  { value: 'all', label: '全部' },
] as const

export type PeriodValue = (typeof PERIOD_OPTIONS)[number]['value']

export function periodLabel(value: string): string {
  return PERIOD_OPTIONS.find((item) => item.value === value)?.label ?? '近30天'
}

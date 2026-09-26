import { defineStore } from 'pinia'

export const useSessionStore = defineStore('session', {
  state: () => ({
    operator: '值班管理员',
    shiftLabel: '白班 08:00-20:00',
    scope: '市政道路桥梁养护管理平台',
    // 运营概览看板的状态：从看板进入模块再返回时，统计区间与展开的卡片保持不变。
    overviewRange: 'today',
    overviewCard: '',
  }),
  getters: {
    canOperate: (state) => state.operator.length > 0,
  },
  actions: {
    setShift(label: string) {
      this.shiftLabel = label
    },
    setOverviewRange(range: string) {
      this.overviewRange = range
    },
    setOverviewCard(cardKey: string) {
      this.overviewCard = cardKey
    },
  },
})

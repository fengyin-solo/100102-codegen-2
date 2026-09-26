<template>
  <div class="app-shell">
    <aside class="app-side">
      <h1 class="app-title">市政道路桥梁养护管理平台</h1>
      <nav class="nav-list">
        <RouterLink v-for="item in navItems" :key="item.path" :to="item.path" class="nav-item">
          {{ item.label }}
        </RouterLink>
      </nav>
    </aside>
    <main class="app-main">
      <header class="app-head">
        <span class="head-desc">面向市政道路桥梁日常巡查、定期检测、病害维修、除雪防汛与占道施工的一体化养护管理后台。</span>
        <span class="head-user">当前值班：{{ store.operator }} · {{ store.shiftLabel }}</span>
      </header>
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { MODULES } from '@/config/modules'
import { useSessionStore } from '@/stores/session'

const store = useSessionStore()

// 运营概览固定在首位，其余入口全部来自模块注册表，与看板下钻列表同源。
const navItems = [
  { label: '运营概览', path: '/' },
  ...MODULES.map((item) => ({ label: item.name, path: item.path })),
]
</script>

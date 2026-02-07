# Grain 项目待办（当前版）

> 最后更新：2026-02-07  
> 当前版本：v3.1.3  
> 说明：本文件仅保留**当前可执行待办**；历史 Sprint 过程请参考 `docs/开发日志.md`。

---

## P0（当前阻塞）

- [ ] 执行 dev 预览环境重建并完成线上验收（`/opt/gain-preview`）

## P1（重要）

- [ ] 验证 `export_stats.db` 在 dev 环境重启后仍保留统计数据
- [ ] Marian 全启用后的首轮模型加载耗时与失败率观测（dev）
- [ ] 为 SQLite 统计补充体积监控与备份/归档策略

## P2（优化）

- [ ] 前端选区错误提示细化（跨段、空选区、快照漂移）
- [ ] 补充更多 E2E 场景（段落改写、无效 ID 导出提示）
- [ ] 文档结构持续去重，减少重复说明

---

## 已完成（v3.1.3）

- [x] 预览前端健康检查稳定化（高容错参数）
- [x] 导出统计持久化：`export/stats` 升级为 SQLite
- [x] `window_minutes` 上限提升到 `43200`
- [x] Marian 全环境启用（默认值 + Compose 显式开关）
- [x] Marian 依赖纳入后端正式依赖
- [x] Marian API 回归用例补齐（`used` / `generation_failed`）
- [x] 自动化验证：`pytest 23 passed`、前端 build/e2e 通过

---

## 更新规范

每次开发会话结束至少同步更新：

1. `docs/开发日志.md`
2. `docs/下一次对话提示词.md`
3. `docs/API文档.md`（若 API 有变化）
4. `docs/status/*.md`（记录验收结果）

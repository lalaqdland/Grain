# Grain 项目待办（当前版）

> 最后更新：2026-02-07  
> 当前版本：v3.1.2-observability  
> 说明：本文件仅保留**当前可执行待办**；历史 Sprint 过程请参考 `docs/开发日志.md`。

---

## P0（当前阻塞）

- [ ] 预览前端健康检查稳定化（`docker-compose.preview.yml` healthcheck 超时策略）

## P1（重要）

- [ ] 导出统计持久化：从内存态升级到可持久化方案（SQLite/日志聚合）
- [ ] 预览环境安装 Marian 依赖并验证 `status=enabled` 路径
- [ ] 新增 Marian 启用场景的 API 回归用例（含 `used` / `generation_failed` 真实路径）

## P2（优化）

- [ ] 前端选区错误提示细化（跨段、空选区、快照漂移）
- [ ] 补充更多 E2E 场景（段落改写、无效 ID 导出提示）
- [ ] 文档结构持续去重，减少重复说明

---

## 已完成（v3.1.2-observability）

- [x] 恢复 Mutagen 本机环境并验证同步会话
- [x] 将当前实现同步并回归 `dev.grain.capootech.com`
- [x] 导出可观测性：新增 `GET /api/v1/export/stats`
- [x] Marian 可观测性：`/api/v1/rewrite` 新增 `diagnostics.marian`
- [x] API运行态增强：`/api/v1/info` 新增 `runtime.marian`
- [x] 自动化验证：`pytest 19 passed`、前端 build/e2e 通过

---

## 更新规范

每次开发会话结束至少同步更新：

1. `docs/开发日志.md`
2. `docs/下一次对话提示词.md`
3. `docs/API文档.md`（若 API 有变化）
4. `docs/status/*.md`（记录验收结果）

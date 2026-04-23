-- Phase 2 Board 初始目标树 seed
-- 写入: ystar_goal_tree
-- 运行: sqlite3 .ystar_cieu.db < reports/ceo/phase2_goal_tree_seed_20260423.sql
-- Idempotent: INSERT OR REPLACE

INSERT OR REPLACE INTO ystar_goal_tree (goal_id, parent_goal_id, goal_text, y_star_definition, owner_role, created_at, created_by, status, weight) VALUES
-- Top-level goals (Y*_001, Y*_002, Y*_003)
('Y_001', NULL, 'gov-mcp 成功上架并获得第一笔付费', 'pip-installable package on PyPI + 1+ paying external customer + revenue landed in stripe/bank account', 'cto', strftime('%s','now'), 'board_2026_04_23', 'active', 1.0),
('Y_002', NULL, '数字人办公室 MVP 上线', '3D scene at localhost/office with 3+ digital humans + voice interaction working + Board can talk through it in live session', 'cto', strftime('%s','now'), 'board_2026_04_23', 'active', 1.0),
('Y_003', NULL, '场泛函目标投影系统 Phase 2 上线', 'ystar_role_scope 7 rows + ystar_goal_tree 3+ goals + cieu_goal_contribution receiving rows + CEO boot hook showing alignment/progress', 'kernel', strftime('%s','now'), 'board_2026_04_23', 'active', 1.0),

-- Y_001 sub-goals (gov-mcp)
('Y_001_1', 'Y_001', 'API 文档完整', 'products/ystar-gov/docs/ has endpoint ref + examples + install guide all sections filled', 'cto', strftime('%s','now'), 'board_2026_04_23', 'active', 0.8),
('Y_001_2', 'Y_001', '测试覆盖 >80%', 'pytest coverage report shows >= 80% line coverage on src/ystar/**', 'platform', strftime('%s','now'), 'board_2026_04_23', 'active', 0.9),
('Y_001_3', 'Y_001', '定价策略确定', 'finance/pricing_v1.md ratified by Board with 3-tier pricing + stripe product SKUs defined', 'ceo', strftime('%s','now'), 'board_2026_04_23', 'active', 0.7),
('Y_001_4', 'Y_001', '第一个外部用户注册', 'ystar_users table has 1+ row with verified email NOT in @ystar-company.com / @anthropic.com', 'cmo', strftime('%s','now'), 'board_2026_04_23', 'active', 1.0),

-- Y_002 sub-goals (office MVP)
('Y_002_1', 'Y_002', 'Three.js 场景搭建', 'scripts/meeting_room/ has working Three.js scene rendered at localhost:PORT with exposed-brick startup office aesthetic (per Sofia visual anchor)', 'cto', strftime('%s','now'), 'board_2026_04_23', 'active', 0.9),
('Y_002_2', 'Y_002', '数字人形象导入', '3+ RPM/VRM avatars imported for Aiden+Sofia+Samantha (MVP trio per Samantha archive) with transparent hotspots + visible name badges', 'cto', strftime('%s','now'), 'board_2026_04_23', 'active', 0.9),
('Y_002_3', 'Y_002', 'ElevenLabs 语音接通', 'WebSocket STT+TTS round-trip working < 500ms latency for office conversation', 'platform', strftime('%s','now'), 'board_2026_04_23', 'active', 0.8),
('Y_002_4', 'Y_002', '热点点击对话功能', 'click avatar → conversation panel opens → typed or voice input accepted → agent sub-spawned → response rendered', 'cto', strftime('%s','now'), 'board_2026_04_23', 'active', 1.0),

-- Y_003 sub-goals (Phase 2 field functional)
('Y_003_1', 'Y_003', '角色职责场定义录入', 'ystar_role_scope has 7 rows one per role with scope_keywords 10+ and anti_scope_keywords 4+', 'kernel', strftime('%s','now'), 'board_2026_04_23', 'active', 1.0),
('Y_003_2', 'Y_003', '目标树数据结构上线', 'ystar_goal_tree + cieu_goal_contribution tables exist with indexes + phase2_goal_query.py CLI functional', 'platform', strftime('%s','now'), 'board_2026_04_23', 'active', 1.0),
('Y_003_3', 'Y_003', '行为-目标贡献推断跑通', 'batch_contribution_backfill inserts rows into cieu_goal_contribution with role_alignment_score + goal_contribution_score from event_type/task_description keywords', 'governance', strftime('%s','now'), 'board_2026_04_23', 'active', 1.0),
('Y_003_4', 'Y_003', 'CEO boot 可见目标进度', 'new session boot hook reads goal tree + contribution stats and displays: role alignment % + top goal being advanced + 24h progress summary', 'platform', strftime('%s','now'), 'board_2026_04_23', 'active', 1.0);

-- Verify
SELECT 'total_goals', COUNT(*) FROM ystar_goal_tree WHERE status='active';
SELECT 'top_level_goals', COUNT(*) FROM ystar_goal_tree WHERE parent_goal_id IS NULL AND status='active';
SELECT goal_id, owner_role, substr(goal_text, 1, 40) FROM ystar_goal_tree WHERE status='active' ORDER BY goal_id;

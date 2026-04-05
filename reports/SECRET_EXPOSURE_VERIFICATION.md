# 方案1验收：Secret Exposure 30格式拦截
# Status: PASS

## 30种格式逐一测试结果

| # | 格式 | 文件示例 | 结果 |
|---|---|---|---|
| 1 | .env | .env | ✅ DENY |
| 2 | .env.local | .env.local | ✅ DENY |
| 3 | .env.production | .env.production | ✅ DENY |
| 4 | .env.staging | .env.staging | ✅ DENY |
| 5 | nested .env | config/.env | ✅ DENY |
| 6 | SSH RSA key | ~/.ssh/id_rsa | ✅ DENY |
| 7 | SSH ED25519 | ~/.ssh/id_ed25519 | ✅ DENY |
| 8 | SSH authorized_keys | ~/.ssh/authorized_keys | ✅ DENY |
| 9 | AWS credentials | ~/.aws/credentials | ✅ DENY |
| 10 | AWS config | ~/.aws/config | ✅ DENY |
| 11 | GCloud creds | ~/.gcloud/application_default_credentials.json | ✅ DENY |
| 12 | Azure tokens | ~/.azure/accessTokens.json | ✅ DENY |
| 13 | npm token | ~/.npmrc | ✅ DENY |
| 14 | PyPI token | ~/.pypirc | ✅ DENY |
| 15 | Docker config | ~/.docker/config.json | ✅ DENY |
| 16 | Git credentials | ~/.git-credentials | ✅ DENY |
| 17 | netrc | ~/.netrc | ✅ DENY |
| 18 | Kubernetes | ~/.kube/config | ✅ DENY |
| 19 | credentials.json | ./config/credentials.json | ✅ DENY |
| 20 | secrets dir | ./secrets/api_key.txt | ✅ DENY |
| 21 | private key PEM | ./private_key.pem | ✅ DENY |
| 22 | PostgreSQL | ~/.pgpass | ✅ DENY |
| 23 | secrets.yaml | ./config/secrets.yaml | ✅ DENY |
| 24 | service account | ./credentials/service_account.json | ✅ DENY |
| 25 | dotfile secrets | ./.secrets | ✅ DENY |
| 26 | Terraform state | ./terraform.tfstate | ✅ DENY |
| 27 | Vault token | ./.vault-token | ✅ DENY |
| 28 | nested private key | ./config/private_key.pem | ✅ DENY |
| 29 | deploy secrets | ./deploy/secrets/db.conf | ✅ DENY |
| 30 | production master key | production/secrets/master.key | ✅ DENY |

## 拦截成功率
**30/30 = 100%**

## False Positive检查（15个安全文件）
| 文件 | 结果 |
|---|---|
| ./src/main.py | ✅ ALLOW |
| ./src/config/settings.py | ✅ ALLOW |
| ./README.md | ✅ ALLOW |
| ./tests/test_auth.py | ✅ ALLOW |
| ./docs/security.md | ✅ ALLOW |
| ./src/utils/crypto.py | ✅ ALLOW |
| ./public/index.html | ✅ ALLOW |
| ./src/api/routes.py | ✅ ALLOW |
| ./package.json | ✅ ALLOW |
| ./requirements.txt | ✅ ALLOW |
| ./Dockerfile | ✅ ALLOW |
| ./src/database/migrations/001.sql | ✅ ALLOW |
| ./src/auth/oauth.py | ✅ ALLOW |
| ./tests/conftest.py | ✅ ALLOW |
| ./src/core/engine.py | ✅ ALLOW |

**False positive rate: 0/15 = 0%**

## 实验中发现的绕过

原始deny列表使用 `/.env` 模式（带前导斜杠），
导致8个格式绕过：
- `.env` (无斜杠前缀)
- `.env.local`, `.env.production`, `.env.staging`
- `./config/secrets.yaml`
- `./.secrets`
- `./terraform.tfstate`
- `./.vault-token`

**根因：** kernel的deny是子串匹配。`/.env` 不匹配 `.env`（没有前导斜杠）。

**修复：** 改用 `.env` (无前导斜杠) + 增加 `secret`, `credentials`, `private_key`, `tfstate`, `.vault-token` 等模式。

**修复后重新验证：30/30全部通过。**

## 8大类覆盖确认
- ✅ 环境文件 (.env family)
- ✅ SSH密钥 (id_rsa, id_ed25519, authorized_keys)
- ✅ 云凭证 (AWS, GCloud, Azure)
- ✅ 包管理器token (npm, PyPI)
- ✅ Docker
- ✅ Git凭证 (git-credentials, netrc)
- ✅ Kubernetes (kube/config)
- ✅ 数据库 (credentials, pgpass)

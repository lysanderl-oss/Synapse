# GitHub Push — 推送到 GitHub 仓库

将指定本地仓库推送到对应的 GitHub 远程仓库。
凭证已通过 git credential store 配置，无需传入 token。

## 使用方式

直接告诉我：
- "push synapse-core 到 GitHub"
- "push lysander-bond 到 GitHub"  
- "把 $REPO 推送上去"

## 执行逻辑

```bash
cd "$REPO_PATH"
git add -A
git -c user.email="lysanderl@janusd.io" -c user.name="Lysander" \
    commit -m "$COMMIT_MSG" || echo "Nothing to commit"
git push origin main
```

## 已知仓库映射

| 仓库名 | 本地路径 | GitHub |
|--------|----------|--------|
| synapse-core | C:/Users/lysanderl_janusd/synapse-core | lysanderl-glitch/synapse |
| lysander-bond | C:/Users/lysanderl_janusd/Claude Code/lysander-bond | lysanderl-glitch/lysander-bond |

## 凭证维护

凭证存储于 `~/.git-credentials`（git credential store）。
Token 更换后，Lysander 可派 rd_devops 执行：
```bash
python3 -c "
import os
cred_file = os.path.expanduser('~/.git-credentials')
new_line = 'https://NEW_TOKEN:x-oauth-basic@github.com'
try:
    lines = [l.strip() for l in open(cred_file).readlines() if 'github.com' not in l]
except: lines = []
lines.append(new_line)
open(cred_file,'w').write('\n'.join(lines)+'\n')
print('Token updated')
"
```

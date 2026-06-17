# GitHub 高星 Skill 搜索结果（2026-05-28 实测）

> 触发：主人要求搜索大厂招聘要求对应的 GitHub Skill
> 问题：GitHub API 频率限制（每分钟10次），批量搜索触发 `KeyError: 'items'`

## 实测结果（按岗位）

### CEO — 战略/领导力/管理
| Repo | Stars | URL |
|------|-------|-----|
| awesome-cto | 34k | https://github.com/kuchin/awesome-cto |
| Startup-CTO-Handbook | 14k | https://github.com/ZachGoldberg/Startup-CTO-Handbook |
| engineering-management | 8k | https://github.com/charlax/engineering-management |

### CFO — 财务/金融
| Repo | Stars | URL |
|------|-------|-----|
| akaunting | 9k | https://github.com/akaunting/akaunting |

### dev — 软件开发
| Repo | Stars | URL |
|------|-------|-----|
| xterm.js | 20k | https://github.com/xtermjs/xterm.js |
| apollo-client | 19k | https://github.com/apollographql/apollo-client |

### fullstack — 全栈开发
| Repo | Stars | URL |
|------|-------|-----|
| system-design-primer | 350k | https://github.com/donnemartin/system-design-primer |
| awesome-selfhosted | 295k | https://github.com/awesome-selfhosted/awesome-selfhosted |
| react | 245k | https://github.com/facebook/react |

### content / marketing / pm / qa / legal / life / advisor
> 未搜索到（API 触限），待下次配置

## 搜索命令模板

```bash
# 单岗位搜索（避免触限）
curl -s "https://api.github.com/search/repositories?q={关键词}+stars:>5000&sort=stars&per_page=3" \
  | python3 -c "import sys,json; [print(f\"{r['name']} ⭐{r['stargazers_count']}: {r['html_url']}\") for r in json.load(sys.stdin).get('items',[])]"

# 搜索示例
# CEO: leadership+management
# CFO: finance+fintech+accounting
# dev: javascript+typescript+development
# fullstack: react+vue+fullstack+web
# content: writing+cms+content
# marketing: marketing+sales+automation
# pm: product+manager+agile
# qa: playwright+selenium+testing
# legal: awesome-legal+contract+legal-tech
# life: awesome-productivity+life+hacks
# advisor: awesome-mentorship+consulting+advisor
```

## 经验总结

1. **逐岗位搜索**：每搜完一个确认后再搜下一个，避免触限
2. **触限后等待1分钟**：再继续剩余岗位
3. **离线备选**：API 限制期间参考本文件的已知高星数据
4. **判断触限**：返回 `KeyError: 'items'` 或空输出 = 触限
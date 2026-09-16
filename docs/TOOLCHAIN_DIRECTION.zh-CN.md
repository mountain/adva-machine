# 本地 Adva-machine 的整合方向

方向由 Mingli Yuan 于 2026-09-16 提出；本阶段设计、实现和记录由 ChatGPT
（OpenAI）完成，通过其授权账号代理提交。账号与授权不表示个人技术审查或正确性保证。

## 已确定的分工

| 仓库 | 方向 | 本阶段的实际落点 |
| --- | --- | --- |
| 本地 `adva-machine` | Adva 规范、Rust/Python 工具链、Adva 自身编写的工具、未来前后端与共同验收 | `/home/ubuntu/adva-machine`，继承原仓库完整历史 |
| GitHub 原始 `mountain/adva` | 向知识与研究方向发展 | 本次作为历史来源；尚未在远端执行拆分或改名 |
| `adva-library` | 最终组织形式待定 | 固定版本的外部依赖，可使用子模块或显式指定的独立本地检出 |

这里采用你本次明确提出的“规范也包含在 adva-machine 中”的方向。草案表格中
“规范留在原始 adva”的分工不作为本阶段的决定。原始研究记录随历史保留，后续再按
真实依赖逐步抽离，当前不按文件后缀搬迁或删除。

## 现在可以使用什么

- `spec/`：已有规范、格式和研究执行版本的索引与固定字节。
- `adva-rust/`：Rust 工具链的共同执行入口，实际实现仍在 `crates/`。
- `adva-python/`：Python 参考执行器的共同入口，需要 Rust 接收输入并重放产物。
- `python/adva/`：原有 Rust/PyO3 公共接口与科学计算适配器，继续保留。
- `programs/`：已有 Adva 算术解释器、自编译器及有限输入绑定 `mix`。
- `toolchain/`：能力清单、共同请求和报告、固定样例及库版本锁。

“用 Rust/Python 执行 Adva”“从 Adva 生成 Rust/Python 源码”“把 Rust/Python
源码转换为 Adva”是三个不同接口。当前整合的是第一种；另两个方向保留为明确未实现。
Python 公共接口依赖 Rust，Adva 自身的工具只有有限子集，尚不能声称三套同等覆盖的
独立机器。能力清单会把这些差别直接显示出来。

在新仓库根目录运行：

```sh
.venv/bin/python adva-machine capabilities
.venv/bin/python adva-machine doctor
.venv/bin/python adva-machine doctor --library ../adva-library
.venv/bin/python adva-machine run toolchain/examples/arithmetic.request.json \
  --engine python --output target/my-first-python-run
.venv/bin/python adva-machine conform --output target/my-first-conformance
```

输出目录必须是新目录。返回结果、执行拒绝、输入拒绝、不支持、暂停和燃料耗尽分别
记录。资源成本单独计量；同一执行版本的状态和轨迹可以逐项核对，未来代码生成后端
则需要声明自己的观察关系，不能要求不同宿主步数天然相同。

初次本地验收见 [`toolchain/evidence/README.md`](../toolchain/evidence/README.md)。
Rust 仍负责原生接收和检查；哈希、Python 报告或目录名称都不代替语义证明。

## 库先接起来，再决定怎么拆

暂时保留 `adva-library` 的名称与内容。版本锁区分文献目录、研究快照和可交给已有
原生入口的有限样例。匹配版本只说明依赖完整性，不意味着所有条目可以执行。
几何增长义务继续为 Open，文档 seal 不是原生 Seal。

下一步优先建立一小组程序的**显式导入契约**：支持什么格式、需要哪个执行版本、
如何声明依赖、接收失败如何返回、哪些来源与历史必须保留。使用经验足够后，再决定
保留一个分层库、拆成可执行标准库与知识库，还是形成独立版本的包。

随后选择一个明确子集实现首个代码生成后端；语言前端、静态求值、解释器消除和
通用优化 `mix` 按各自依赖推进。目录改名和工具链入口不会自动完成这些能力。

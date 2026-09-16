# Adva-machine

本页为辅助中文导读。面向国际合作，项目优先维护[英文主文档](README.md)，
新规范、设计与使用说明先以英语编写。参见[文档语言约定](docs/DEVELOPMENT.md#documentation-language)。

本地仓库正在整合 Adva 规范、Rust/Python 工具链和 Adva 自身编写的有限工具。
GitHub 原始 `adva` 将向知识方向发展，`adva-library` 的最终组织方式保留开放。

先看[整合方向与当前入口（英文）](docs/TOOLCHAIN_DIRECTION.md)
（[中文摘要](docs/TOOLCHAIN_DIRECTION.zh-CN.md)）、
[工具链使用说明](toolchain/README.md)和[规范索引](spec/README.md)。
本阶段保留原有路径与历史证据，提供共同验收接口；下文是继承的研究背景。

**有限的观察者，怎样构造、检验并扩展算术知识？**

[English](README.md) · [运行示例](#先运行一个例子) ·
[带着一个卡住的问题开始](#带着一个卡住的问题开始) · [开发说明](docs/DEVELOPMENT.md)

Adva 用带类型的程序、显式的构造历史、有界实验和可复用的见证，研究这个问题。
它希望帮助我们推进困难的问题：明确一次观察究竟说明了什么，保留尚未解决的部分，
再寻找能够带来区别的下一次观察或构造。

项目已经包含 Rust 实现的 Lisp 引擎、单独版本化的有界数据语言、构造与见证的资料库，
以及持续积累的数学、哲学和实验记录。目前是 **pre-alpha 研究软件**。
采用 [Unknown v0.2（英文主文本）](Unknown-LICENSE-v0.2.md)：公有领域奉献，附带自愿认同的哲学声明。
使用、修改、再发布和商业使用不以署名或认同哲学为条件；适用范围见 [LICENSING.md](LICENSING.md)。

## 从一个不用高等数学的例子开始

你观察到一个程序输入 `2`，输出 `4`。它是在计算两倍，还是平方？

| 观察 | `f(x) = 2x` | `g(x) = x²` | 可以得出什么 |
|---|---:|---:|---|
| 输入 `2` | 4 | 4 | 两种解释都符合这次观察。 |
| 输入 `3` | 6 | 9 | 这次观察能区分两种解释。 |

把第一项重复一百次，仍然不能区分它们。第二项改变了我们能够判断的事情。
项目的[解释义务实验](docs/research/0166-interpretation-obligation.md)
把问题、解释、观察范围和检查结果分别保存，避免把“这次吻合”扩大成“解释已经成立”。

但有限观察也能支持证明。例如，我们已经知道两个有理系数多项式的次数都不超过二，
那么只要它们在三个不同的有理数上相等，就能证明它们恒等。
原因是：差多项式的次数至多为二，非零时不可能有三个不同的根。

**使有限检查成为证明的，是次数上界与根的论证共同给出的充分性。**
任意三个测试本身没有这种保证。
[有限实例验证研究](docs/research/0183-zhang-finite-example-verification.md)
正是在考察实例、范围和证明之间的这座桥。

即使已经证明两个程序计算同一个函数，它们也可能使用不同的构造、来源和复制过程。
如果下一轮研究要问的是成本、来源或组合方式，这些区别仍然有用。
所以 Adva 保留程序如何形成、如何执行的历史。

## 有限观察者与算术真，是什么关系？

有限观察者有一定的接口、能够提出的问题，以及有限的时间和资源。
它能区分一些情况，也会留下不能区分的情况。这里限制的是我们已经获得的依据；
不是把命题的真伪改成个人意见。

可以分三步理解 Adva 的研究方向：

1. **把问题写成可检查的构造。** 明确对象、范围、允许的操作和成功条件。
   在已经声明的域中，等式可以表现为 `A − B = 0`；当 `B ≠ 0` 时，也可以表现为
   `A / B = 1`。非零条件与原问题到算术表示的对应关系，都需要依据。
2. **让有限的检查给出有范围的结论。** 得到一个见证、反例，或者在资源耗尽时保留
   `Unknown`。有充分性证明时，可以从有限检查推出更广的结论；不能只靠增加测试数量。
3. **让结论成为下一轮可用的材料。** 连同前提、检查方法和剩余问题保存它。
   新的问题可能需要更强的观察者、新的构造，甚至新的表达语言。

这使“做出一个答案”“检查一个答案”“从经验中形成下一种方法”成为相关而不同的工作。
保存一个记录只是起点；真正值得检验的是，它能否帮助后来的人做出原来做不到的判断。

项目把“算术普遍性”和“假设算术真”保留为
[明确标注的研究假说](docs/research/0123-arithmetic-universality-and-hypothesized-truth.md)。
它们尚未成为通用真理判定方法。用加法零或乘法单位表达局部义务，也不意味着已经把
所有问题归约到了同一个可执行检查器。

更完整的动机还包括：有限经验怎样超出已有语言、怎样提出新问题、为什么保留失败历史，
以及程序的构造如何获得几何表达。可以继续阅读
[哲学记录](docs/philosophy/README.md)、[本体论](ontology/README.md)和
[研究议程](docs/RESEARCH_ENGINEERING_AGENDA.md)。这些内容属于项目本身，
也需要通过具体构造和反例逐步接受检验。

## 现在已经有什么？

| 层次 | 已有内容 | 适用边界 |
|---|---|---|
| 原生程序内核 | 带类型的有限 Lisp、显式来源与出现位置、复制和丢弃、构造历史、检查过的程序图、代入轨迹与过程切片、求值和前向微分 | PSC0 的有限、无局部绑定、线性核心。数值求值使用浮点数；结构证书不等于数值误差界。 |
| 研究数据语言 | 用 Adva 指令编写的算术解释器，由 Rust 执行；精确检查的 `i64` 运算、有界控制、暂停与恢复 | 单独版本化的研究实现，溢出拒绝。这个例子解释算术树，尚未解释自身完整的指令语言。 |
| 资料库与实验 | 可复用见证、观察者比较、闭合与传递检查、失败和反例记录 | 每项结果都有自己的范围、前提和剩余问题；外部实验不自动取得原生语义资格。 |
| 持续研究 | 观察者条件化专门化、语言形成、算术普遍性、几何表示 | 假说和构造目标，按研究议程逐步推进。 |

具体声明与依据见[声明登记](docs/claims.toml)，原生边界见
[语义范围](docs/SEMANTIC_SCOPE.md)。Rust 负责原生语义身份与判断；Python 提供适配和
外部研究工具。一个文件能被解析，并不等于其内容已经通过语义检查。

## 先运行一个例子

带子库克隆项目：

```sh
git clone --recurse-submodules https://github.com/mountain/adva.git
cd adva
```

### 看一个解释器如何保留自己的执行

安装 Rust 工具链后，在仓库根目录的 POSIX shell 中运行：

```sh
cargo build --locked -p adva-witness --bin adva
adva_run_dir="$(mktemp -d)"
target/debug/adva data-run programs/bounded-interpreter/interpreter.adva \
  --input programs/bounded-interpreter/input.json \
  --fuel 2048 --quantum 2048 --output "$adva_run_dir/result.adva"
```

输入表示 `2 + (3 * 4)`，预期得到 `Returned`，整数结果为 `14`，共执行 `134` 个指令步。
输出文件同时保留程序、输入、执行轨迹、最终状态和燃料记录。输出路径必须是新的。

接下来可以照着[暂停与恢复示例](programs/bounded-interpreter/README.md)，先执行 17 步，
再检查这段历史并继续。原始终身燃料不会因恢复而重置，重放检查的工作另外记账。
[实验报告](docs/research/bounded-native-data-interpreter.md)解释了它已检查的范围。

新加入的[编译实验](docs/research/futamura-projections-in-adva-terms.md)还对照了
129 棵完全静态的算术树：解释执行与编译出的三指令常量程序给出相同值。
把编译也计入机器步数，一次使用更贵，两次复用时才更省。这里仍由主机完成程序装载，
它是有限样本中的复用结果，尚未建立通用专门化器，也没有证明真实运行时间更快。

### 不编译 Rust，也能检查一次协作交接

使用 Python 3.11 或以上版本：

```sh
python3 experiments/bounded_observation_exchange/check_exchange_chain.py
```

预期返回 `DisclosedByteChainChecked`，覆盖五轮保存的交换，以及四次
“旧回答不能冒充新问题的回答”的拒绝检查。
这只检查披露字段与字节绑定，仍明确保留 `source_binding: Unverified` 和
`semantic_acceptance: Withheld`：交接记录一致，不代表其中的说法已经证实。
详见[交换实验](experiments/bounded_observation_exchange/README.md)。

## 带着一个卡住的问题开始

不必先读完全部数学。可以先带来：

1. 原始问题，以及什么可观察结果算是解决。
2. 一个尽量小、可以复现的尝试，包括输入、前提和资源限制。
3. 已通过的检查、具体失败，以及还不知道的部分。
4. 一个下一步设想：换一种观察、构造反例、找到更强的不变量，或交给别人检查。

对于编程挑战，这可能是区分两个合理实现的测试，也可能是发现题目描述与测试之间的错位。
人和 AI 都可以贡献尝试。我们需要比较的是：在明确条件下，哪些判断变得可检查、
哪些构造可以复用、完整成本有没有降低。

[Tooling 工作设定](docs/TOOLING_WORKFLOW.md)将这种参与方式拆成具体的工作步骤，
并区分现有工具与待实现的界面。目前尚无统一的问题工作台。

**遇到困难时，欢迎带着尝试和剩余问题回来看看 Adva。**
如果这种方法确实帮助你推进了问题，可以给项目点一个 star，方便再次找到它，
也关注它接下来的发展。

## 继续往哪里读？

| 想了解什么 | 入口 |
|---|---|
| 实例什么时候足以成为证明 | [有限实例验证](docs/research/0183-zhang-finite-example-verification.md) |
| 不终止的证据与超时有什么区别 | [有限循环证书](docs/research/keraia-cycle-certificates-and-halting-mass-bounds.md) |
| 程序的来源、复制与历史如何进入实现 | [开发说明](docs/DEVELOPMENT.md)与 [AGENTS.md](AGENTS.md) |
| 有限经验、想象与语言形成的动机 | [哲学记录](docs/philosophy/README.md)与[研究议程](docs/RESEARCH_ENGINEERING_AGENDA.md) |
| 已保存的构造怎样继续增长 | [子库](adva-library/README.md)与[数学增长义务](adva-library/math/README.md) |
| 结果经历过哪些修正 | [研究索引](docs/research/README.md)、[声明登记](docs/claims.toml)及后续修正记录 |

历史实验保留原始检查环境；部分旧资料库纪元需要指定的历史接收器，参见
[重放说明](docs/DEVELOPMENT.md#replaying-historical-library-epochs)。
贡献与验证按 [AI 署名规则](docs/AI_ATTRIBUTION.md)分别记录。

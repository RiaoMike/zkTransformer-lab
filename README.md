# zkTransformer 论文与源码学习工作区

**学习入口：[tutorial/README.md](tutorial/README.md)。** 按其中的顺序阅读第 1–8 节。

```text
zkTransformer.pdf    论文
upstream/            原始项目源码
tutorial/            学习材料（见下方）
.build/              工具链、依赖缓存和编译产物
```

`tutorial/` 的内容：

| 路径 | 用途 |
|---|---|
| `README.md` | 学习顺序与环境说明 |
| `lessons/` | 按 01–08 顺序阅读的教程 |
| `exercises.py`、`check_exercises.py` | 自己填写代码并按课验收 |
| `solutions.py`、`labs.py` | 参考答案与小例子 |
| `project/` | 五个真实 Rust API 示例 |
| `cpu/` | 加载上游证明源码的 CPU 构建入口 |
| `reference/` | 补充推导、源码索引、来源及验证记录 |
| `tools/` | 定位源码、验证材料和运行示例的辅助脚本 |
| `env.fish`、`env.sh`、`cargo-config.toml` | 环境与镜像配置 |

第一课完成后，在根目录验收：

```fish
python3 tutorial/check_exercises.py 1
```

上游来源：[uiuc-kang-lab/zkTransformer](https://github.com/uiuc-kang-lab/zkTransformer)，
固定提交 `55344d7c37232b4dbe8aa479e139967230d8449b`。
`upstream/` 是 72 个文本文件的源码快照；哈希记录见
[tutorial/reference/upstream_manifest.json](tutorial/reference/upstream_manifest.json)，许可证见 `upstream/LICENSE`。

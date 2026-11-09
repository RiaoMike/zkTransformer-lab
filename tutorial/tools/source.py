"""从本地快照定位上游源码：python3 tutorial/tools/source.py mle。

可从任意工作目录调用。--list 列出入口，--write-map 更新源码定位表。
"""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMMIT = "55344d7c37232b4dbe8aa479e139967230d8449b"
# alias: (path, exact marker, context lines, purpose)
ENTRIES = {
    "mle": ("src/util/poly.rs", "  pub fn fix_variables(&self, partial_point", 63, "变量折叠与部分固定"),
    "eq": ("src/util/poly.rs", "pub fn evaluate_lagrange_basis", 48, "eq(r,b) 的求值表"),
    "classify": ("src/basicblock/einsum.rs", "pub fn classify_einsum_indices_from_shapes", 68, "定理 3.1 的指标分类"),
    "helper": ("src/basicblock/einsum.rs", "pub fn einsum_helper", 58, "排列、输出挑战分组与求和轮数"),
    "einsum": ("src/basicblock/einsum.rs", "  fn prove(", 160, "部分固定、Sumcheck 与输入 Claim"),
    "sumcheck": ("src/crypto/sumcheck/linear_prover.rs", "pub struct LinearSumcheckProver", 177, "轮消息及挑战折叠"),
    "verifier": ("src/crypto/sumcheck/verifier.rs", "  pub fn verify(", 54, "轮数、次数、端点和、插值"),
    "transcript": ("src/util/transcript.rs", "pub struct Transcript", 50, "消息吸收与 Fiat–Shamir 挑战"),
    "selection": ("src/util/poly.rs", "pub struct SelectionPolynomial", 100, "one-hot 选择矩阵"),
    "lookup": ("src/dag/mod.rs", "  pub fn verify_range", 108, "批量范围查询验证"),
    "scale": ("src/basicblock/scale.rs", "  fn run(", 65, "整数舍入与余数范围"),
    "exp": ("src/basicblock/exp.rs", "pub struct ExpHelper", 83, "指数分解 witness"),
    "exp_builder": ("src/dag/builder.rs", "  pub fn exp(", 82, "StructuredExp 的完整构图"),
    "witness": ("src/dag/mod.rs", "pub struct Witness", 96, "shape、scale 与张量布局"),
    "claim": ("src/dag/mod.rs", "pub struct Claim", 11, "边、点、值声明"),
    "block": ("src/basicblock/mod.rs", "pub trait BasicBlock", 28, "run/prove/verify 三阶段接口"),
    "reducer": ("src/basicblock/reducer.rs", "  fn prove(", 91, "多点声明合并"),
    "dag_prove": ("src/dag/mod.rs", "  pub fn prove<F, DP, SP>", 252, "DAG 反向归约与 opening"),
    "dag_verify": ("src/dag/mod.rs", "  pub fn verify<F, DP, SP>", 181, "节点验证与叶子 opening 认证"),
    "pcs_trait": ("src/crypto/polycommit/mod.rs", "pub trait MLPolyCommit", 28, "承诺接口"),
    "pcs": ("src/crypto/polycommit/kzh3.rs", "  fn setup(n:", 65, "KZH-3 commit/open/verify_and_extract"),
    "model": ("src/dag/nanogpt.rs", "pub fn nanogpt_attention", 120, "nanoGPT attention 构图入口"),
}


def locate(key):
    path, marker, context, purpose = ENTRIES[key]
    lines = (ROOT / "upstream" / path).read_text().splitlines()
    matches = [i for i, line in enumerate(lines) if marker in line]
    if not matches:
        raise ValueError(f"找不到 {key}: {path} / {marker}")
    return path, lines, matches[0], context, purpose


def write_map():
    out = ["# 固定版本源码定位表", "", f"上游提交 `{COMMIT}`；本地路径均在 `upstream/`。",
           "行号由 `python3 tutorial/tools/source.py --write-map` 从当前快照生成。", "",
           "| 定位命令参数 | 目的 | 本地文件与行号 | 固定版本链接 |",
           "|---|---|---|---|"]
    for key in ENTRIES:
        path, _, start, _, purpose = locate(key)
        n = start + 1
        url = f"https://github.com/uiuc-kang-lab/zkTransformer/blob/{COMMIT}/{path}#L{n}"
        out.append(f"| `{key}` | {purpose} | [{path}:{n}](../../upstream/{path}#L{n}) | [source]({url}) |")
    out += ["", "例如 `python3 tutorial/tools/source.py einsum` 会打印带行号的源码片段。",
            "用 `rg -n 'fn prove|fn verify|pub fn' upstream/src/...` 可继续追踪其他函数。", ""]
    (ROOT / "tutorial/reference/SOURCE_MAP.md").write_text("\n".join(out))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("key", nargs="?", choices=ENTRIES)
    p.add_argument("--list", action="store_true")
    p.add_argument("--write-map", action="store_true")
    args = p.parse_args()
    if args.write_map:
        write_map()
    elif args.key:
        path, lines, start, context, purpose = locate(args.key)
        print(f"{purpose}\nupstream/{path}:{start+1}\ncommit {COMMIT}\n")
        for i in range(start, min(start + context, len(lines))):
            print(f"{i+1:4}  {lines[i]}")
    else:
        for key, (_, _, _, purpose) in ENTRIES.items():
            print(f"{key:14} {purpose}")


if __name__ == "__main__":
    main()

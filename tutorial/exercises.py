"""你的练习区。按 lessons/01...06 顺序补全，不要改验收器。

第 1–4、6 课：有限域 F_101。第 5 课：普通有符号整数，不取模。
数组下标 = b0 + 2*b1 + ...；第一个变量对应最低位。
"""

P = 101


# 第 1 课，对应 upstream/src/util/poly.rs。
def fold(table, r):
    """相邻两项折叠；返回长度减半的新列表，所有结果模 P。"""
    raise NotImplementedError("请实现 fold：a + r*(b-a)")


def mle(table, point):
    """检查 len(table)==2**len(point)，依次固定变量。"""
    raise NotImplementedError("请实现 mle：循环调用 fold")


def eq(r, b):
    """对每一维 r_j*b_j+(1-r_j)*(1-b_j) 求乘积；空乘积为 1。"""
    raise NotImplementedError("请实现 eq；一般域点上的结果不是 bool")


# 第 2 课，对应 basicblock/einsum.rs 的 classify_einsum_indices_from_shapes。
def classify(equation):
    """返回 (free_once, free_multi, summation)，各项为字母列表。

    前两项保持输出顺序，最后一项保持输入中首次出现的顺序。
    本练习不支持重复指标（如 ii->i）和省略号。
    """
    raise NotImplementedError("请实现三类指标分类")


def einsum_toy(equation, tables):
    """每个指标维度都是 2：直接计算布尔输出张量，返回列优先扁平表。

    这条路径只做整数下标的乘积求和，用来独立核对编译后的多项式关系。
    """
    raise NotImplementedError("先算普通张量；不要在这里调用 compile_toy")


def compile_toy(equation, tables, challenge):
    """返回 (active_labels, factor_tables)，每个字母维度为 2。

    活动变量顺序为 free_multi+summation；直接固定 free_once；
    按各输入字母顺序求 MLE；最后附加 eq 表。详见第 2 节。
    """
    raise NotImplementedError("先对每个因子部分固定，再生成求和表")


# 第 3 课，对应 crypto/sumcheck/linear_prover.rs 与 verifier.rs。
def round_message(tables):
    """l 个等长 MLE 表；返回当前轮 q(0),...,q(l)，不是系数。

    每个插值点：分别 fold 各因子，然后逐位置相乘，最后求和。
    """
    raise NotImplementedError("请先插值各因子，再计算乘积")


def interpolate(values, x):
    """values[j]=q(j)；用拉格朗日插值返回 q(x)，模 P。"""
    raise NotImplementedError("分母求逆可用 pow(denominator, -1, P)")


def prove_sumcheck(tables, challenges):
    """固定挑战便于逐步核对；返回每轮求值消息组成的列表。"""
    raise NotImplementedError("每轮生成消息，然后按挑战折叠所有表")


def verify_sumcheck(claim, messages, challenges, degree, oracle):
    """检查轮数、消息长度、端点和、插值更新以及最终 oracle。"""
    raise NotImplementedError("最终 oracle 检查不可省略")


# 第 4 课，对应 util/poly.rs 和 dag/mod.rs 的 lookup。
def range_mle(r):
    """表 T[j]=j 的闭式 MLE。"""
    raise NotImplementedError("利用 j 的二进制展开")


def power_mle(r):
    """表 T[j]=2**j 的闭式 MLE；所有幂与乘法在 F_P 内。"""
    raise NotImplementedError("先在布尔点上分解指数，再多线性延拓")


# 第 5 课，对应 basicblock/exp.rs、scale.rs。这里不使用 F_101。
def decompose(q):
    """Q15 非正输入；返回 (k,r)，q=-22713*k+r，要求 0<=k<=15。

    仅支持本课的小整数范围。超出范围应抛 ValueError，不要静默钳位。
    """
    raise NotImplementedError("k 取 -q/22713 的最近整数；本课使用非负比值")


def scale_down(x, input_sf, output_sf):
    """返回 (y,aux)：D=2**(input_sf-output_sf)，y=floor((x+D//2)/D)。

    aux=x-y*D+D//2，要求 0<=aux<D。禁止用 int(x/D) 代替向下取整。
    """
    raise NotImplementedError("用整数 //；支持负数和同尺度的恒等情况")


# 第 6 课，对应 basicblock/reducer.rs。
def reducer_weights(points, alpha):
    """返回 E[b]=sum_t alpha**t * eq(points[t], bits(b)) 的整张表。

    所有 points 维数一致且非空。结果长度 2**维数，模 P。
    """
    raise NotImplementedError("不同点的声明需要 eq 多项式合并")

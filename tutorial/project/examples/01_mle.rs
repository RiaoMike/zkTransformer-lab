use zk_torch_2::util::poly::{DenseMLPoly, MLPoly};
use zktransformer_tutorial::{f, F};

fn main() {
    let a = DenseMLPoly::<F>::from_evaluations(vec![f(1), f(2), f(3), f(4)]);
    let partial = a.fix_variables(&[f(2)]);
    assert_eq!(partial.n, 1);
    assert_eq!(partial.evaluations, vec![f(3), f(5)]);
    let value = partial.evaluate_at_point(&[f(3)]);
    assert_eq!(value, f(9));
    println!("partial table = [3,5]; MLE(2,3) = {value}");

    // 跟着敲：加入第一节的 A、B、C，复现 17/21/17。
}

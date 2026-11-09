use zk_torch_2::crypto::polycommit::kzh3::{KZH3Commit, KZH3VerifierKey};
use zk_torch_2::crypto::polycommit::{ArkBn254, MLPolyCommit};
use zk_torch_2::util::poly::{DenseMLPoly, MLPoly};
use zktransformer_tutorial::{f, F};

fn main() {
    type PCS = KZH3Commit<ArkBn254>;
    let poly = DenseMLPoly::<F>::from_evaluations((1..=8).map(f).collect());
    let point = vec![f(2), f(3), f(4)];
    let expected = poly.evaluate_at_point(&point);
    assert_eq!(expected, f(25));

    // 本地教学 setup。真实部署中需另外处理可信设置及 SRS 来源。
    let ck = PCS::setup(3, 0, 0, 0); // 3 是变量数，不是表长 8。
    let vk = KZH3VerifierKey {
        srs_map: ck.srs_map.clone(),
    };
    let commitment = PCS::commit(&poly, &ck);
    let opening = PCS::open(&commitment, &poly, &ck, &point);
    let (ok, opened) = PCS::verify_and_extract(&commitment, &opening, &vk, &point);
    assert!(ok && opened == expected);
    assert!(!(ok && opened == expected + f(1)));
    println!("opening authenticated value = {opened}; expected 25");
}

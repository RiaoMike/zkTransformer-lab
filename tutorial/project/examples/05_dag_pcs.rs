use plonky2::util::timing::TimingTree;
use std::collections::HashMap;
use std::sync::Arc;
use zk_torch_2::crypto::polycommit::kzh3::{KZH3Commit, KZH3CommitKey, KZH3VerifierKey};
use zk_torch_2::crypto::polycommit::sparse_kzh3::{
    SparseKZH3Commit, SparseKZH3CommitKey, SparseKZH3VerifierKey,
};
use zk_torch_2::crypto::polycommit::{ArkBn254, MLPolyCommit};
use zk_torch_2::dag::{DagBuilder, DataType, Role};
use zk_torch_2::util::transcript::Transcript;
use zktransformer_tutorial::{f, witness, F};

fn main() {
    type DP = KZH3Commit<ArkBn254>;
    type SP = SparseKZH3Commit<ArkBn254>;
    // 第一版只构建 Z=XW、Y=Z+C。所有数据 sf=0，避免引入范围/重缩放节点。
    let mut g = DagBuilder::<F>::new();
    let x = g.input(vec![2, 2], DataType::Int);
    let w = g.param(witness(vec![2, 2], &[5, 6, 7, 8], Role::Constant));
    let c = g.param(witness(vec![2, 2], &[1, 1, 1, 1], Role::Constant));
    let z = g.einsum("ij,jk->ik".into(), vec![x, w], false)[0];
    let y = g.add(z, c)[0];
    let (dag, mut values) = g.compile();
    dag.run(
        &mut values,
        &[(x, witness(vec![2, 2], &[1, 2, 3, 4], Role::Input))],
    );
    assert_eq!(
        values[y][0].data.as_ref().unwrap().evaluations(),
        vec![f(24), f(35), f(32), f(47)]
    );
    // 应用层先核对预期输出；单纯验证某个自洽输出的证明不指定应用想要的结果。

    let mut srs = HashMap::new();
    for n in dag.collect_polynomial_sizes(&values) {
        let key = DP::setup(n, 0, 0, 0);
        srs.insert(n, key.srs_map[&n].clone());
    }
    let srs_map = Arc::new(srs);
    let dk = KZH3CommitKey {
        srs_map: srs_map.clone(),
    };
    let sk = SparseKZH3CommitKey {
        srs_map: srs_map.clone(),
    };
    let dvk = KZH3VerifierKey {
        srs_map: srs_map.clone(),
    };
    let svk = SparseKZH3VerifierKey { srs_map };
    let mut dense = vec![None; dag.num_edges()];
    let mut sparse = vec![None; dag.num_edges()];
    let mut timing = TimingTree::default();
    dag.commit::<F, DP, SP>(&dk, &sk, &values, &mut dense, &mut sparse, &mut timing);

    let mut pt = Transcript::<F>::new(b"tutorial-dag");
    let (nodes, edges, range, powers, reducers) =
        dag.prove::<F, DP, SP>(&dk, &sk, &values, &dense, &sparse, &mut pt, &mut timing);
    for (node_id, proof) in nodes.iter().enumerate() {
        if let Some((_, claims)) = proof {
            println!("node {node_id}: {claims:?}");
        }
    }
    // verifier 只保留元信息，不读取完整 witness。
    for edge in &mut values {
        for value in edge {
            value.clear_data();
        }
    }
    let mut vt = Transcript::<F>::new(b"tutorial-dag");
    let verified = dag.verify::<F, DP, SP>(
        &nodes, &edges, &range, &powers, &reducers, &values, &dvk, &svk, &dense, &sparse, &mut vt,
    );
    assert!(verified);
    println!("tiny DAG verified: {verified}");
}

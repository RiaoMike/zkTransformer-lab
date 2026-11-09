use zk_torch_2::basicblock::{BasicBlock, Einsum};
use zk_torch_2::dag::{Claim, Role};
use zk_torch_2::util::transcript::Transcript;
use zktransformer_tutorial::{f, witness, F};

fn main() {
    let x = witness(vec![2, 2], &[1, 2, 3, 4], Role::Input);
    let w = witness(vec![2, 2], &[5, 6, 7, 8], Role::Constant);
    let op = Einsum {
        equation: "ij,jk->ik".into(),
    };
    let outputs = op.run(&[&x, &w]);
    let z = &outputs[0];
    assert_eq!(
        z.data.as_ref().unwrap().evaluations(),
        vec![f(23), f(34), f(31), f(46)]
    );

    let out = Claim {
        edge_id: 2,
        sparse_id: 0,
        point: vec![f(2), f(3)],
        eval: f(93),
    };
    let witnesses = [&x, &w, z];
    let mut pt = Transcript::<F>::new(b"tutorial-einsum");
    let (proofs, inputs) = op.prove(&witnesses, &[0, 1, 2], &[&out], &mut pt);
    assert_eq!(inputs.len(), 2);
    for claim in &inputs {
        println!("derived input claim: {claim:?}");
        let actual = witnesses[claim.edge_id]
            .data
            .as_ref()
            .unwrap()
            .evaluate_at_point(&claim.point);
        assert_eq!(actual, claim.eval); // 直接 oracle；第 8 节换成 PCS。
    }
    let claims: Vec<_> = inputs.iter().chain(std::iter::once(&out)).collect();
    let proof_refs: Vec<_> = proofs.iter().collect();
    let mut vt = Transcript::<F>::new(b"tutorial-einsum");
    assert!(op.verify(&witnesses, &claims, &proof_refs, &mut vt));

    let mut corrupt_inputs = inputs.clone();
    corrupt_inputs[0].eval += f(1);
    let bad_claims: Vec<_> = corrupt_inputs.iter().chain(std::iter::once(&out)).collect();
    let mut bad_t = Transcript::<F>::new(b"tutorial-einsum");
    assert!(!op.verify(&witnesses, &bad_claims, &proof_refs, &mut bad_t));
    println!("Einsum relation accepted; changed input value rejected");
}

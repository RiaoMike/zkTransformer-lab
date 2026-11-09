use zk_torch_2::crypto::{LinearSumcheckProver, SumcheckProver, SumcheckVerifier};
use zk_torch_2::util::poly::{CryptoField, DenseMLPoly, MLPoly};
use zk_torch_2::util::transcript::Transcript;
use zktransformer_tutorial::{f, F};

fn main() {
    let polys = vec![
        DenseMLPoly::from_evaluations(vec![f(1), f(2), f(3), f(4)]),
        DenseMLPoly::from_evaluations(vec![f(5), f(6), f(7), f(8)]),
    ];
    let claim = f(70); // 1*5 + 2*6 + 3*7 + 4*8
    let mut pt = Transcript::<F>::new(b"tutorial-sumcheck");
    let mut prover = LinearSumcheckProver::new(2, 2, &mut pt);
    let proof = prover.prove(&polys, &mut pt);
    println!("round messages: {:?}", proof.round_messages);

    let mut vt = Transcript::<F>::new(b"tutorial-sumcheck");
    let mut verifier = SumcheckVerifier::new(2, 2, &mut vt);
    let (last, point) = verifier.verify(&mut vt, proof.round_messages.clone(), claim);
    assert_eq!(point, prover.challenges);
    // SumcheckVerifier 只检查轮消息。这里用直接求值完成教学 oracle。
    let oracle = polys
        .iter()
        .map(|p| p.evaluate_at_point(&point))
        .fold(<F as CryptoField>::one(), |a, b| a * b);
    assert_eq!(last, Some(oracle));

    let mut bad_t = Transcript::<F>::new(b"tutorial-sumcheck");
    let mut bad_v = SumcheckVerifier::new(2, 2, &mut bad_t);
    assert!(bad_v
        .verify(&mut bad_t, proof.round_messages, claim + f(1))
        .0
        .is_none());
    println!("honest claim accepted; wrong initial claim rejected");
}

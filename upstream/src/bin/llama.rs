// Field type selection based on backend and curve
#[cfg(all(feature = "arkworks", feature = "bls12_381"))]
use ark_bls12_381::Fr as F;
#[cfg(all(feature = "arkworks", feature = "bn254"))]
use ark_bn254::Fr as F;

#[cfg(all(feature = "icicle", feature = "bls12_381"))]
use icicle_bls12_381::curve::ScalarField as F;
#[cfg(all(feature = "icicle", feature = "bn254"))]
use icicle_bn254::curve::ScalarField as F;
#[cfg(all(feature = "icicle", feature = "goldilocks"))]
use icicle_goldilocks::field::ScalarField as F;

use plonky2::{timed, util::timing::TimingTree};
use rand::{Rng, SeedableRng};
use rand::rngs::StdRng;
use std::cell::RefCell;
use std::collections::HashMap;
use std::fs;
use std::sync::Arc;
use std::sync::Mutex;
use zk_torch_2::util::transcript::Transcript;
use zk_torch_2::{
  crypto::polycommit::kzh3::{setup_kzh3_srs, KZH3Commit, KZH3CommitKey, KZH3Commitment, KZH3VerifierKey},
  crypto::polycommit::sparse_kzh3::{SparseKZH3Commit, SparseKZH3CommitKey, SparseKZH3VerifierKey},
  crypto::polycommit::{MLPolyCommit, NaiveMLPolyCommit},
  crypto::srs_storage::{load_kzh3_srs, store_kzh3_srs},
  dag::{
    extract_lookup_proof_only, extract_opening_proofs_only, extract_sumcheck_proofs_only,
    llama::llama_2_7b, DagBuilder, DataType, Role, Witness,
  },
  util::poly::{CryptoField, DenseMLPoly, MLPoly, SparseMLPoly},
  util::serialization::measure_total_proof_size,
  SF_LOG, SF_INT, TABLE_SIZE_LOG,
};

#[cfg(all(feature = "arkworks", feature = "bn254"))]
use zk_torch_2::crypto::polycommit::ArkBn254 as PairingType;
#[cfg(all(feature = "icicle", feature = "bn254"))]
use zk_torch_2::crypto::polycommit::IcicleBn254 as PairingType;

/// Signed random field elements in [-half_range, half_range].
/// Zero-mean values prevent activation blowup through layers.
fn gen_signed(rng: &mut StdRng, size: usize, half_range: u32) -> Vec<F> {
  let range = 2 * half_range + 1;
  (0..size).map(|_| {
    let v = (rng.gen::<u32>() % range) as i64 - half_range as i64;
    if v >= 0 {
      <F as CryptoField>::from_u32(v as u32)
    } else {
      <F as CryptoField>::zero() - <F as CryptoField>::from_u32((-v) as u32)
    }
  }).collect()
}

/// RMSNorm γ centered around SF_INT (≈1.0 in real space).
fn gen_norm_weight(rng: &mut StdRng, size: usize) -> Vec<F> {
  let sf = *SF_INT;
  (0..size).map(|_| {
    let noise = (rng.gen::<u32>() % 65) as i64 - 32;
    <F as CryptoField>::from_u32((sf as i64 + noise) as u32)
  }).collect()
}

fn generate_llama_weights(rng: &mut StdRng, num_layers: usize) -> (
  Vec<Witness<F>>, // attn_norm_w_vec
  Vec<Witness<F>>, // attn_q_w_vec
  Vec<Witness<F>>, // attn_k_w_vec
  Vec<Witness<F>>, // attn_v_w_vec
  Vec<Witness<F>>, // attn_o_w_vec
  Vec<Witness<F>>, // proj_norm_w_vec
  Vec<Witness<F>>, // proj_1_w_vec
  Vec<Witness<F>>, // proj_2_w_vec
  Vec<Witness<F>>, // proj_3_w_vec
  Witness<F>,      // layer_norm_w
  Witness<F>,      // logits_w
) {
  let sf = *SF_LOG as usize;
  let mut attn_norm_w_vec = Vec::new();
  let mut attn_q_w_vec = Vec::new();
  let mut attn_k_w_vec = Vec::new();
  let mut attn_v_w_vec = Vec::new();
  let mut attn_o_w_vec = Vec::new();
  let mut proj_norm_w_vec = Vec::new();
  let mut proj_1_w_vec = Vec::new();
  let mut proj_2_w_vec = Vec::new();
  let mut proj_3_w_vec = Vec::new();

  // Xavier-like: matmul std ≈ SF/sqrt(fan_in). 4096 inputs → half_range 64;
  // 11008 inputs (proj_3) → half_range 32. Norm γ near SF_INT (≈1.0).
  for _i in 0..num_layers {
    attn_norm_w_vec.push(Witness::new(vec![4096], gen_norm_weight(rng, 4096), DataType::Float, sf, Role::Constant));
    attn_q_w_vec.push(Witness::new(vec![4096, 4096], gen_signed(rng, 4096 * 4096, 64), DataType::Float, sf, Role::Constant));
    attn_k_w_vec.push(Witness::new(vec![4096, 4096], gen_signed(rng, 4096 * 4096, 64), DataType::Float, sf, Role::Constant));
    attn_v_w_vec.push(Witness::new(vec![4096, 4096], gen_signed(rng, 4096 * 4096, 64), DataType::Float, sf, Role::Constant));
    attn_o_w_vec.push(Witness::new(vec![4096, 4096], gen_signed(rng, 4096 * 4096, 64), DataType::Float, sf, Role::Constant));
    proj_norm_w_vec.push(Witness::new(vec![4096], gen_norm_weight(rng, 4096), DataType::Float, sf, Role::Constant));
    proj_1_w_vec.push(Witness::new(vec![4096, 11008], gen_signed(rng, 4096 * 16384, 64), DataType::Float, sf, Role::Constant));
    proj_2_w_vec.push(Witness::new(vec![4096, 11008], gen_signed(rng, 4096 * 16384, 64), DataType::Float, sf, Role::Constant));
    proj_3_w_vec.push(Witness::new(vec![11008, 4096], gen_signed(rng, 16384 * 4096, 32), DataType::Float, sf, Role::Constant));
  }

  let layer_norm_w = Witness::new(vec![4096], gen_norm_weight(rng, 4096), DataType::Float, sf, Role::Constant);
  let logits_w = Witness::new(vec![4096, 32000], gen_signed(rng, 4096 * 32768, 64), DataType::Float, sf, Role::Constant);

  (
    attn_norm_w_vec,
    attn_q_w_vec,
    attn_k_w_vec,
    attn_v_w_vec,
    attn_o_w_vec,
    proj_norm_w_vec,
    proj_1_w_vec,
    proj_2_w_vec,
    proj_3_w_vec,
    layer_norm_w,
    logits_w,
  )
}

fn main() {
  let mut timing = TimingTree::default();
  env_logger::init();

  let seq_len: usize = std::env::var("SEQ_LEN")
    .ok()
    .and_then(|s| s.parse().ok())
    .unwrap_or(1);
  let num_layers: usize = std::env::var("NUM_LAYERS")
    .ok()
    .and_then(|s| s.parse().ok())
    .unwrap_or(32);
  let num_heads: usize = 32;
  let head_dim: usize = 128;
  let hidden_dim: usize = num_heads * head_dim; // 4096
  let seed: u64 = std::env::var("SEED").ok().and_then(|s| s.parse().ok()).unwrap_or(42);

  println!("Generating LLaMA-2-7B calibrated random weights (seq_len={seq_len}, num_layers={num_layers}, seed={seed})...");

  // --- Circuit compilation ---
  let mut g = DagBuilder::new();

  // Single seeded RNG drives all calibrated witnesses (weights + input).
  let mut rng = StdRng::seed_from_u64(seed);

  let (
    attn_norm_w_vec,
    attn_q_w_vec,
    attn_k_w_vec,
    attn_v_w_vec,
    attn_o_w_vec,
    proj_norm_w_vec,
    proj_1_w_vec,
    proj_2_w_vec,
    proj_3_w_vec,
    layer_norm_w,
    logits_w,
  ) = generate_llama_weights(&mut rng, num_layers);

  // Input: (batch_size=1, seq_len, 4096)
  let x = g.input(vec![1, seq_len, hidden_dim], DataType::Float);

  // Run LLaMA-2-7B model
  let output = g.pipe(
    &[x],
    llama_2_7b(
      attn_norm_w_vec,
      attn_q_w_vec,
      attn_k_w_vec,
      attn_v_w_vec,
      attn_o_w_vec,
      proj_norm_w_vec,
      proj_1_w_vec,
      proj_2_w_vec,
      proj_3_w_vec,
      layer_norm_w,
      logits_w,
      num_heads,
      head_dim,
      seq_len,
      32000,
    ),
  )[0];

  // Compile -> (Dag, initial edge values)
  println!("Compiling DAG...");
  let (dag, mut init) = g.compile();

  // --- Prover ---
  let mut transcript = Transcript::new(b"zkml");

  let mut dense_commitments: Vec<Option<KZH3Commitment<PairingType>>> = vec![None; dag.num_edges()];
  let mut sparse_commitments: Vec<Option<Vec<KZH3Commitment<PairingType>>>> = vec![None; dag.num_edges()];

  // Witness generation from input. Hidden state magnitude ≈ ±2000 mirrors the post-embedding
  // scale used by oneshot_llama (W_E half-range 2000), giving RMSNorm enough x_sq dynamic range.
  println!("Generating witness from calibrated random input...");
  let seq_padded = seq_len.next_power_of_two();
  let input = Witness::new(
    vec![1, seq_len, hidden_dim],
    gen_signed(&mut rng, seq_padded * hidden_dim, 2000),
    DataType::Float,
    *SF_LOG as usize,
    Role::Input,
  );

  dag.run(&mut init, &vec![(x, input)]);
  println!("LLaMA output shape: {:?}", init[output][0].shape);

  // Pre-permute eligible Constant witnesses (weights consumed by Einsum).
  // MUST happen before commit so commitments are to the permuted polynomial.
  // Einsum::prove detects the `is_permuted_with` tag and skips the matching
  // runtime permute_evals_by_ranges call (the main llama prove bottleneck).
  timed!(timing, "apply_prepermute", dag.apply_prepermute(&mut init));

  // Collect polynomial sizes from the DAG after witness generation
  let polynomial_sizes = dag.collect_polynomial_sizes(&init);
  println!("\n=== Polynomial sizes in GPT-2 DAG ===");
  println!("Sizes needed: {:?}", polynomial_sizes);
  println!("Number of different sizes: {}", polynomial_sizes.len());
  println!("=====================================\n");

  // Load or generate SRS for all required polynomial sizes
  let mut srs_map = HashMap::new();
  for &size in &polynomial_sizes {
    let size_srs = if fs::metadata(&format!("{}.srs", size)).is_ok() {
      println!("Loading existing SRS for polynomial size {}", size);
      load_kzh3_srs(size).expect(&format!("Failed to load SRS for size {}", size))
    } else {
      println!("Generating SRS for polynomial size {}", size);
      #[cfg(feature = "arkworks")]
      let size_srs = {
        use rand::thread_rng;
        setup_kzh3_srs::<PairingType, _>(size, &mut thread_rng())
      };
      #[cfg(feature = "icicle")]
      let size_srs = setup_kzh3_srs::<PairingType, _>(size, &mut ());
      store_kzh3_srs(&size_srs, size).expect(&format!("Failed to store SRS for size {}", size));
      size_srs
    };
    srs_map.insert(size, Arc::new(size_srs));
  }
  let srs_map = Arc::new(srs_map);

  // Create commitment keys with the collected SRS sizes
  let kzh3 = KZH3CommitKey::<PairingType> { srs_map: srs_map.clone() };
  let sparse_kzh3 = SparseKZH3CommitKey::<PairingType> { srs_map: srs_map.clone() };

  // Create verifier keys with the same srs_map
  let dense_verifier_key = KZH3VerifierKey { srs_map: srs_map.clone() };
  let sparse_verifier_key = SparseKZH3VerifierKey { srs_map: srs_map.clone() };

  // Commit to all witnesses (constants, inputs, auxiliaries, and final outputs)
  println!("Committing to witnesses...");
  timed!(timing, "commit", {
    dag.commit::<F, KZH3Commit<PairingType>, SparseKZH3Commit<PairingType>>(
      &kzh3,
      &sparse_kzh3,
      &init,
      &mut dense_commitments,
      &mut sparse_commitments,
      &mut timing,
    )
  });

  println!("Generating proof...");
  let (sumcheck_proofs, opening_proofs, range_proof, two_pow_proof, reducer_proofs) = timed!(
    timing,
    "prove",
    dag.prove::<F, KZH3Commit<PairingType>, SparseKZH3Commit<PairingType>>(
      &kzh3,
      &sparse_kzh3,
      &init,
      &dense_commitments,
      &sparse_commitments,
      &mut transcript,
      &mut timing
    )
  );

  // Clear the data from the witnesses before verification
  init.iter_mut().for_each(|w| w.iter_mut().for_each(|w| w.clear_data()));

  // --- Verifier ---
  let mut verifier_transcript = Transcript::new(b"zkml");
  let verified = timed!(
    timing,
    "verify",
    dag.verify::<F, KZH3Commit<PairingType>, SparseKZH3Commit<PairingType>>(
      &sumcheck_proofs,
      &opening_proofs,
      &range_proof,
      &two_pow_proof,
      &reducer_proofs,
      &init,
      &dense_verifier_key,
      &sparse_verifier_key,
      &dense_commitments,
      &sparse_commitments,
      &mut verifier_transcript,
    )
  );
  timing.print();
  println!("verified: {:?}", verified);

  let sumcheck_proofs_only = extract_sumcheck_proofs_only(&sumcheck_proofs);
  let opening_proofs_only = extract_opening_proofs_only::<F, KZH3Commit<PairingType>, SparseKZH3Commit<PairingType>>(&opening_proofs);
  let range_proof_only = extract_lookup_proof_only(&range_proof);
  let two_pow_proof_only = extract_lookup_proof_only(&two_pow_proof);
  let proof_size = measure_total_proof_size(
    &sumcheck_proofs_only,
    &opening_proofs_only,
    &range_proof_only,
    &two_pow_proof_only,
    &reducer_proofs,
  );
  println!("proof size: {}", proof_size);
}

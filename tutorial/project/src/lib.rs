//! Small adapters for the real upstream API, not a replacement proof system.
use zk_torch_2::crypto::polycommit::{ArkBn254, PairingTrait};
use zk_torch_2::dag::{DataType, Role, Witness};
use zk_torch_2::util::poly::CryptoField;

pub type F = <ArkBn254 as PairingTrait>::ScalarField;

pub fn f(x: u32) -> F {
    <F as CryptoField>::from_u32(x)
}

pub fn witness(shape: Vec<usize>, values: &[u32], role: Role) -> Witness<F> {
    Witness::new(
        shape,
        values.iter().copied().map(f).collect(),
        DataType::Int,
        0,
        role,
    )
}

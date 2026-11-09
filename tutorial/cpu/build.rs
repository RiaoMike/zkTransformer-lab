use std::{env, fs, path::PathBuf};

fn main() {
    let src = PathBuf::from(env::var("CARGO_MANIFEST_DIR").unwrap())
        .join("../../upstream/src")
        .canonicalize()
        .unwrap();
    let entry = src.join("lib.rs");
    println!("cargo:rerun-if-changed={}", entry.display());
    let mut code = fs::read_to_string(&entry).unwrap();
    for name in ["basicblock", "crypto", "dag", "util", "onnx"] {
        let declaration = format!("pub mod {name};");
        assert_eq!(code.matches(&declaration).count(), 1);
        let path = if name == "onnx" {
            src.join("onnx.rs")
        } else {
            src.join(name).join("mod.rs")
        };
        let gate = if name == "onnx" {
            "#[cfg(feature = \"onnx\")]\n"
        } else {
            ""
        };
        let replacement = format!(
            "{gate}#[path = {:?}]\n{declaration}",
            path.to_str().unwrap()
        );
        code = code.replacen(&declaration, &replacement, 1);
    }
    let out = PathBuf::from(env::var("OUT_DIR").unwrap());
    fs::write(out.join("upstream_lib.rs"), code).unwrap();
}

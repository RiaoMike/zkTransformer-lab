// Compile the original library entry with absolute paths to original modules.
// build.rs gates the unused ONNX importer; proof algorithms are not copied.
include!(concat!(env!("OUT_DIR"), "/upstream_lib.rs"));

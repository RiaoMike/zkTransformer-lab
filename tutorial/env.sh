# Bash: source tutorial/env.sh
# Keep toolchains, dependency caches and build output inside this workspace.
zk_tutorial_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
export CARGO_HOME="$zk_tutorial_root/.build/cargo"
export RUSTUP_HOME="$zk_tutorial_root/.build/rustup"
export CARGO_TARGET_DIR="$zk_tutorial_root/.build/target"
export CARGO_NET_GIT_FETCH_WITH_CLI=true
export RUSTUP_DIST_SERVER="https://rsproxy.cn"
export RUSTUP_UPDATE_ROOT="https://rsproxy.cn/rustup"
if [[ "${CMAKE:-}" == "$zk_tutorial_root/.build/tools/bin/cmake" ]]; then
    unset CMAKE
fi
mkdir -p "$CARGO_HOME"
if [[ ! -e "$CARGO_HOME/config.toml" ]]; then
    cp "$zk_tutorial_root/tutorial/cargo-config.toml" "$CARGO_HOME/config.toml"
fi
unset zk_tutorial_root

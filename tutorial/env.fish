# fish: source tutorial/env.fish
# Keep toolchains, dependency caches and build output inside this workspace.
set -l zk_tutorial_root (realpath -- (dirname -- (status filename))/..)
set -gx CARGO_HOME "$zk_tutorial_root/.build/cargo"
set -gx RUSTUP_HOME "$zk_tutorial_root/.build/rustup"
set -gx CARGO_TARGET_DIR "$zk_tutorial_root/.build/target"
set -gx CARGO_NET_GIT_FETCH_WITH_CLI true
set -gx RUSTUP_DIST_SERVER "https://rsproxy.cn"
set -gx RUSTUP_UPDATE_ROOT "https://rsproxy.cn/rustup"
if test "$CMAKE" = "$zk_tutorial_root/.build/tools/bin/cmake"
    set -e CMAKE
end
mkdir -p "$CARGO_HOME"
if not test -e "$CARGO_HOME/config.toml"
    cp "$zk_tutorial_root/tutorial/cargo-config.toml" "$CARGO_HOME/config.toml"
end

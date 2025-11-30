#!/bin/bash

# نزل Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"

# نزل الـ packages
pip install --upgrade pip
pip install -r requirements.txt

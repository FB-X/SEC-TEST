# AliReq hardened Requests-compatible runtime

This release removes `integrity_manifest.json` and `integrity_guard.py` from the runtime integrity architecture.

## Runtime layout

`requests/` is the directory that can be shadowed ahead of the existing Termux `requests` package without deleting the original installation.

Protected runtime `.so` files are registered by `FBXXX.py` using three digests:

- SHA-256
- BLAKE2b-256
- true Keccak-256 (not SHA3-256)

`FBXXX.py` itself is **not** a registry artifact and is never self-hashed.

`libandroid_shield.so` is not embedded into its own native hash table because that would create a circular self-hash. It is covered by the final signed FBXXX registry after the native library is built.

## Build order

1. Build the Cython extension modules with `cythonize.sh`.
2. Run `release.sh`.
3. `release.sh` embeds the final hashes of the two non-self native artifacts into `libandroid_shield.so`.
4. It then copies the final `.so` files into `requests/` and creates a signed FBXXX registry over every `.so` in that directory.
5. The Ed25519 private key is kept outside GitHub. Set `FBXXX_PRIVATE_KEY=/path/to/key.pem` to use an existing key.
6. Run `verify.sh` before installation.

The signing key must never be committed to the repository.

## Termux installation

Run `install_termux.sh`. It installs the hardened package under Python site-packages and creates a `.pth` file that prepends the hardened package path. The existing Termux Requests package is not deleted.

This package provides common top-level Requests-style calls (`get`, `post`, `put`, `patch`, `delete`, `head`, `options`, `request`, `Session`) plus compatibility modules for `api`, `sessions`, `models`, and `exceptions`. It is not claimed to be a byte-for-byte or complete implementation of every Requests internal API.

## Important trust boundary

A signed registry protects against modification of the registered artifact bytes when the signing public key is trusted. Because FBXXX itself is intentionally excluded from the artifact list, its trust still depends on the independently provisioned public key and the deployment channel. This source package does not claim that a same-process privileged attacker can never replace both the verifier and its trust anchor.

# CHANGELOG


## v1.5.1 (2025-05-20)

### Bug Fixes

- Fix usage of parse_tip_external_id in update_tip
  ([`325e921`](https://github.com/kgilpin/opentips/commit/325e9216e26ec639c2eb9093a3be45013501d523))


## v1.5.0 (2025-05-20)

### Bug Fixes

- Fix up base64 padding
  ([`218162d`](https://github.com/kgilpin/opentips/commit/218162dd63e2fee11d35ef226089a17e674bd4b3))

### Features

- Read and incorporate REVIEW.md
  ([`2af93de`](https://github.com/kgilpin/opentips/commit/2af93dece2e42db15eb57b6c7e36485dd8e7e032))

1. Created a new module review.py to handle reading the REVIEW.md file from the project directory 2.
  Modified the llm_tips.py to accept and incorporate review instructions in the LLM prompt 3.
  Updated the fetch_tips_for_diff function to check for project-specific review instructions 4.
  Added documentation to the README.md explaining how to use the REVIEW.md feature


## v1.4.1 (2025-05-20)

### Bug Fixes

- Fix tip version validation
  ([`28759b5`](https://github.com/kgilpin/opentips/commit/28759b5633cf266743174914e4ebfb29510c2e4e))


## v1.4.0 (2025-05-19)

### Chores

- Add appmap
  ([`948a2a1`](https://github.com/kgilpin/opentips/commit/948a2a1ebc1d7d89b9d37b3b3e44fba00ac7644c))

- Remove redundant ignore list entry
  ([`df98894`](https://github.com/kgilpin/opentips/commit/df988949cdb7334cfcacdcdae25dd8fde0ef2869))

- Update TODO list
  ([`cbf08d4`](https://github.com/kgilpin/opentips/commit/cbf08d44b6090d19ad2f15f9ccab457553b4df87))

### Features

- Add tip priority field
  ([`732ff17`](https://github.com/kgilpin/opentips/commit/732ff174147ac3feb12bdf5e9f734b3eda935014))

- Suggestions prompt update
  ([`a5a5a70`](https://github.com/kgilpin/opentips/commit/a5a5a70026675192ac3dea6e8a7334c0da3a6af5))


## v0.1.0 (2025-04-28)

### Bug Fixes

- Bump version to 1.0.1
  ([`92a1681`](https://github.com/kgilpin/opentips/commit/92a16817445dcfc89c817f45f07c05e8ec731cda))

- Don't compile native code in dependencies
  ([`2ca7b97`](https://github.com/kgilpin/opentips/commit/2ca7b97a239c725a4716f2b24ce26b04a44aa9f3))

- Update logging
  ([`f6bd742`](https://github.com/kgilpin/opentips/commit/f6bd742a54d8cf2e0e7f45d77a86dead65d60a83))

### Chores

- Add cx_Freeze build scripts
  ([`5d3b46e`](https://github.com/kgilpin/opentips/commit/5d3b46ea56dba1f9c1e1e42757bb26506f78e942))

- Build windows executable with PowerShell
  ([`0cc9ebd`](https://github.com/kgilpin/opentips/commit/0cc9ebd76109b00af38dfc022d9868e5b2b6618a))

- Disable build on PR (build on push already happens)
  ([`65d3d6a`](https://github.com/kgilpin/opentips/commit/65d3d6a6ef1284cf3faa7d6a0e06d34468157b1c))

- Disable compilation of native code
  ([`5301c85`](https://github.com/kgilpin/opentips/commit/5301c853318e88d9319665eb40996abcfa6827fd))

- Disable compilation of native code
  ([`b917e4f`](https://github.com/kgilpin/opentips/commit/b917e4f206b2110267ba49a170387e5b1ae74390))

- Disable fail-fast
  ([`0d12301`](https://github.com/kgilpin/opentips/commit/0d1230157301c70bac55b14c8ffcfceb54c28669))

- Distribute only through PyPI for now
  ([`5660a79`](https://github.com/kgilpin/opentips/commit/5660a793ec56be5a2b4516175a4589fb06b65572))

- Release with Python
  ([`cf72a7e`](https://github.com/kgilpin/opentips/commit/cf72a7e2b35a3ddb2873bc0f10c0bc8a9158493b))

- Remove stray branch name
  ([`5b0a83e`](https://github.com/kgilpin/opentips/commit/5b0a83e0e12c86f12c72a69738fe0aaab296d4e6))

- Update gitignore
  ([`d204049`](https://github.com/kgilpin/opentips/commit/d2040497e00f00d8a27087edbbb8baad6a734700))

- Update pip commands for Windows
  ([`ae1ccb5`](https://github.com/kgilpin/opentips/commit/ae1ccb5915785e8340b13d152775bf92cafaff32))

- Update TODO
  ([`dbe7019`](https://github.com/kgilpin/opentips/commit/dbe70196dcf226e41f2666f3234d282bd3c2104b))

- Update TODOs
  ([`5e05e6f`](https://github.com/kgilpin/opentips/commit/5e05e6f931bd159bf6ea863b02e3a195aa638db5))

- Update upload-artifact version
  ([`ad39313`](https://github.com/kgilpin/opentips/commit/ad39313801efb72e75ab67b952ac91af3c0c0d1b))

- Verbose output of semantic release
  ([`0d8589a`](https://github.com/kgilpin/opentips/commit/0d8589a08c7eb735a29a34990b2a1116f4ad7e26))

### Features

- Document RPC methods and remove unused methods
  ([`a3a8477`](https://github.com/kgilpin/opentips/commit/a3a8477ecb463cd5341b9c0b4350c64d512c77f3))

- Drop aider as a required depuendency
  ([`630ae6d`](https://github.com/kgilpin/opentips/commit/630ae6dc5d87e4a4bfa32edade657a05c3fe350d))

- Focus tips on bugs, security, and performance
  ([`c2a5013`](https://github.com/kgilpin/opentips/commit/c2a50136ae68f4f506565fbfa4d8452b3d34c2cb))

- Publish as kgilpin
  ([`6eb724d`](https://github.com/kgilpin/opentips/commit/6eb724df0695a9005b920aa4059b2f841df4c49e))

- Update semantic release config
  ([`3928eca`](https://github.com/kgilpin/opentips/commit/3928eca0af19646cccd5b3ba3c3c9c0ddde4db0d))

- Upgrade aider
  ([`b2db10f`](https://github.com/kgilpin/opentips/commit/b2db10f3e1ac0f95a28bed2a0b52f041cb921d41))

- Use windows-friendly git commands
  ([`0b4ccda`](https://github.com/kgilpin/opentips/commit/0b4ccda0f175fe5dc9e5caf25670d2b332af60c0))

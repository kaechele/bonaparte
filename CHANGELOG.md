# CHANGELOG



## v0.1.0 (2023-07-19)

### Chore

* chore: fix release workflow

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`c3c9400`](https://github.com/kaechele/bonaparte/commit/c3c94008fa1dbec75f4dc4cd2651715707408830))

* chore: publish to regular PyPI

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`1b29872`](https://github.com/kaechele/bonaparte/commit/1b298727b41c61f2af16aad3bb9d38c678623840))

* chore: fix semantic-release config

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`2828b30`](https://github.com/kaechele/bonaparte/commit/2828b30377831f36b63ec08c46a00660d427e2b2))

* chore: change distribution name to pybonaparte to avoid name conflict

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`d5d9de4`](https://github.com/kaechele/bonaparte/commit/d5d9de47fc5f896a7769215e3e82412bb0ebb234))

* chore: split out release workflow

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`dc2958c`](https://github.com/kaechele/bonaparte/commit/dc2958c796f49b94c94b0b0f7f7bbc7bc64a7a11))

* chore: Downgrade ruff target to Python 3.10

It otherwise removes version conditional imports for 3.10 (e.g. in
`src/bonaparte/const.py`)

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`cb9927f`](https://github.com/kaechele/bonaparte/commit/cb9927f698ee973712afce5bdd0cea584fa2298d))

* chore: use masked logging in semantic-release

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`c357ffc`](https://github.com/kaechele/bonaparte/commit/c357ffc55374be2011cf6861b27cdb76abcdaa5d))

* chore(deps): update dependency bleak-retry-connector to v3.1.0 ([`6f89c38`](https://github.com/kaechele/bonaparte/commit/6f89c38013c78fa64d2683d7f46934c2b4c2fceb))

* chore(deps): update relekang/python-semantic-release action to v8 ([`3795172`](https://github.com/kaechele/bonaparte/commit/37951725f0368640a69f14ac3586b050fad4dd97))

* chore: remove unused GitHub workflow

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`2a388ce`](https://github.com/kaechele/bonaparte/commit/2a388ceb5a3cde24ab3fd3a321a67dc56a96f992))

* chore: use Python 3.11 as a baseline

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`ba1b0c1`](https://github.com/kaechele/bonaparte/commit/ba1b0c1c6222c5f2c766dbf375f9f08b10fc3752))

* chore(deps): update pre-commit hook johnnymorganz/stylua to v0.18.1 ([`6bf596f`](https://github.com/kaechele/bonaparte/commit/6bf596f3f9f943a74ad33e266d0798e9dc368a50))

* chore(deps): update pre-commit hook commitizen-tools/commitizen to v3.5.3 ([`b7db32f`](https://github.com/kaechele/bonaparte/commit/b7db32fcf4431f7a594b9216d64ec91ad94c7876))

* chore(deps): update pre-commit hook charliermarsh/ruff-pre-commit to v0.0.278 ([`1896c0c`](https://github.com/kaechele/bonaparte/commit/1896c0cf1eb3b0ea8d58b2ed1c7e819a3aa36b5a))

* chore(deps): update pre-commit hook kaechele/pre-commit-mirror-prettier to v3 ([`9992baf`](https://github.com/kaechele/bonaparte/commit/9992baf90bd9177e84e8356df58df25b43f0f40d))

* chore(deps): update pre-commit hook psf/black to v23.7.0 ([`b1313a5`](https://github.com/kaechele/bonaparte/commit/b1313a59164157c87b3258748881f6eb2a06de2d))

* chore(deps): update dependency black to v23.7.0 ([`dcba218`](https://github.com/kaechele/bonaparte/commit/dcba218a50f4474d84593316906aa248acb047a3))

* chore(deps): update pre-commit hook asottile/pyupgrade to v3.9.0 ([`6d9b775`](https://github.com/kaechele/bonaparte/commit/6d9b775d633f00c4aa07df4ac1a2853c7284f6dd))

* chore(deps): update pre-commit hook charliermarsh/ruff-pre-commit to v0.0.277 ([`8396826`](https://github.com/kaechele/bonaparte/commit/83968261010e95703b310b3a9906ce7018df657d))

* chore(deps): update pre-commit hook charliermarsh/ruff-pre-commit to v0.0.276 ([`ca21e82`](https://github.com/kaechele/bonaparte/commit/ca21e82f3cbebf11cd1b4e5efafc974f57514dd2))

* chore(deps): update pre-commit hook asottile/pyupgrade to v3.8.0 ([`21c366c`](https://github.com/kaechele/bonaparte/commit/21c366c025b857de4e542c604a21884fd7498a99))

* chore(deps): update dependency aenum to v3.1.15 ([`946bc07`](https://github.com/kaechele/bonaparte/commit/946bc07631e9ef3668085eb5bd6f02734b4b2733))

* chore(deps): update pre-commit hook pre-commit/mirrors-mypy to v1.4.1 ([`20c5c68`](https://github.com/kaechele/bonaparte/commit/20c5c68c66dd731a3dc837d74b9e317ac6f55f8a))

* chore(deps): update pre-commit hook commitizen-tools/commitizen to v3.5.2 ([`9aa397c`](https://github.com/kaechele/bonaparte/commit/9aa397c0e4a2d437f04f66ff9339725ede5d560c))

* chore(deps): update pre-commit hook pycqa/autoflake to v2.2.0 ([`bef06e2`](https://github.com/kaechele/bonaparte/commit/bef06e2f2253e93e653644f2a17a5122b3fbbe63))

* chore(deps): update pre-commit hook commitizen-tools/commitizen to v3.5.1 ([`bab4e4b`](https://github.com/kaechele/bonaparte/commit/bab4e4b142eaf9baa6b9c46a0054fd20c8383ba6))

* chore(deps): update dependency pytest to v7.4.0 ([`b868296`](https://github.com/kaechele/bonaparte/commit/b86829650cd84e29ab6143649b57db14c39e9433))

* chore(deps): update pre-commit hook commitizen-tools/commitizen to v3.5.0 ([`d36c8aa`](https://github.com/kaechele/bonaparte/commit/d36c8aa2f387858de059e90057938098a718a64a))

* chore(deps): update pre-commit hook charliermarsh/ruff-pre-commit to v0.0.275 ([`e3ad3b5`](https://github.com/kaechele/bonaparte/commit/e3ad3b571233d22d2d718da12de66d9152082d4e))

* chore(deps): update dependency aenum to v3.1.14 ([`369328c`](https://github.com/kaechele/bonaparte/commit/369328c0382bef4b195be3d46cca1bbd4991c4bd))

* chore(deps): update pre-commit hook pre-commit/mirrors-mypy to v1.4.0 ([`2e71a8a`](https://github.com/kaechele/bonaparte/commit/2e71a8a19c02e8482d5e9d58506302330287f11d))

* chore(deps): update pre-commit hook charliermarsh/ruff-pre-commit to v0.0.274 ([`3191730`](https://github.com/kaechele/bonaparte/commit/3191730f7368e1379ef00475fcd5dccf25b38901))

* chore(deps): update pre-commit hook charliermarsh/ruff-pre-commit to v0.0.273 ([`925a733`](https://github.com/kaechele/bonaparte/commit/925a73366a4663f82a60916f0844d39bbbd3f81e))

* chore(deps): update pre-commit hook commitizen-tools/commitizen to v3.4.0 ([`28264fa`](https://github.com/kaechele/bonaparte/commit/28264fad6a6ef5887e78a272908a0ac6869ed2e2))

* chore(deps): update pre-commit hook asottile/pyupgrade to v3.7.0 ([`0a7ba65`](https://github.com/kaechele/bonaparte/commit/0a7ba65567e1b56acd14cb709c70c9a59b7d4bea))

* chore(deps): update relekang/python-semantic-release action to v7.34.6 ([`5333b5e`](https://github.com/kaechele/bonaparte/commit/5333b5e5e32f36d2697378a82d16c0ac865a8fed))

* chore(deps): update relekang/python-semantic-release action to v7.34.4 ([`10a8e17`](https://github.com/kaechele/bonaparte/commit/10a8e17a602287df518df2719fb39543e8cfa43f))

* chore(deps): update pre-commit hook codespell-project/codespell to v2.2.5 ([`54b2067`](https://github.com/kaechele/bonaparte/commit/54b20671e37ff139460795ce19968bf5ac76aee5))

* chore(deps): update pre-commit hook johnnymorganz/stylua to v0.18.0 ([`7f0fb65`](https://github.com/kaechele/bonaparte/commit/7f0fb658dd0abc7afde6881d0d72380cd0dc3dbe))

* chore(deps): update pre-commit hook asottile/pyupgrade to v3.6.0 ([`19cdd35`](https://github.com/kaechele/bonaparte/commit/19cdd35f14b609ef55c0030fab4066ebe2ee413b))

* chore(deps): update sphinx packages ([`40bea23`](https://github.com/kaechele/bonaparte/commit/40bea23f7c16e57c0ab5ba608234801881d16e84))

* chore(deps): update pre-commit hook commitizen-tools/commitizen to v3.3.0 ([`64099ea`](https://github.com/kaechele/bonaparte/commit/64099ea185b488052a507fe9ec1ae3df2f60de18))

* chore(deps): update pre-commit hook asottile/pyupgrade to v3.5.0 ([`9136adf`](https://github.com/kaechele/bonaparte/commit/9136adf9ecc683ff48055ef0c30043648ba6dbf3))

* chore(deps): update dependency pytest to v7.3.2 ([`19eccf9`](https://github.com/kaechele/bonaparte/commit/19eccf90cd161ee3e491439fda4745648f35a652))

* chore(deps): update pre-commit hook lunarmodules/luacheck to v1.1.1 ([`bd90853`](https://github.com/kaechele/bonaparte/commit/bd9085321f5c7f2eae9e285544bd676cafd073f6))

* chore(deps): update dependency sphinx to v7 ([`e04efb6`](https://github.com/kaechele/bonaparte/commit/e04efb630ab4adf94912a977d6d6d62d1dbead2e))

* chore(deps): update pre-commit hook charliermarsh/ruff-pre-commit to v0.0.272 ([`e3ceb4a`](https://github.com/kaechele/bonaparte/commit/e3ceb4a0585573c75724142793af928282b841fa))

* chore(deps): update dependency sphinx-rtd-theme to v1.2.2 ([`0172881`](https://github.com/kaechele/bonaparte/commit/017288170e8e525df64e47d452338cb968705e1b))

* chore(deps): update pre-commit hook charliermarsh/ruff-pre-commit to v0.0.271 ([`c297007`](https://github.com/kaechele/bonaparte/commit/c297007dfb2b4472b0a572ef357ce89783359b07))

* chore(deps): update dependency pytest-cov to v4 ([`f9c3299`](https://github.com/kaechele/bonaparte/commit/f9c32999ed6dfd96ce85cd83210ee006d82eebb6))

* chore(deps): update dependency reportlab to v4 ([`1117c6e`](https://github.com/kaechele/bonaparte/commit/1117c6eddfe31ba173d0c89bdb19814776c8df4a))

* chore(deps): update dependency bleak to ^0.20.0 ([`2a55dff`](https://github.com/kaechele/bonaparte/commit/2a55dfff62ff594254596ffc1d34e75069c7e526))

* chore(deps): update wagoid/commitlint-github-action action to v5.4.1 (#5)

Co-authored-by: renovate[bot] &lt;29139614+renovate[bot]@users.noreply.github.com&gt; ([`79b7245`](https://github.com/kaechele/bonaparte/commit/79b72459b6ed56f268f3464707a5d0b3d7eeaab6))

* chore(deps): update relekang/python-semantic-release action to v7.34.3 (#4)

Co-authored-by: renovate[bot] &lt;29139614+renovate[bot]@users.noreply.github.com&gt; ([`1c04026`](https://github.com/kaechele/bonaparte/commit/1c040264aabcb2caefdfc295cc9b5654a888833e))

* chore(deps): update pre-commit hook python-poetry/poetry to v1.5.1 (#1)

Co-authored-by: renovate[bot] &lt;29139614+renovate[bot]@users.noreply.github.com&gt; ([`a4a7c9a`](https://github.com/kaechele/bonaparte/commit/a4a7c9a61b842a1e593630dc167fc768820be946))

* chore: fix linter errors

Yes, at some point I will reduce the number of linters running at the
same time ;-)

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`851968c`](https://github.com/kaechele/bonaparte/commit/851968cadfbff5773f8a53ee5b86b59b59a1ebd3))

* chore: update dependencies and pre-commit hooks

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`5922da5`](https://github.com/kaechele/bonaparte/commit/5922da59410bb8373bf756efe03863371063d769))

* chore: reformat wireshark dissector using spaces

StyLua now uses the .editorconfig to read preferred formatting settings.
So make sure we are consistent across files.

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`4d5e0c1`](https://github.com/kaechele/bonaparte/commit/4d5e0c1cb32d78ba5d199fc663e822f905873729))

* chore: update readthedocs settings

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`30d425d`](https://github.com/kaechele/bonaparte/commit/30d425dbf3f0256d7301cb69c9426944ff59c9a7))

* chore: update pre-commit hooks

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`8286659`](https://github.com/kaechele/bonaparte/commit/82866598e8f085e536d8da3db9941124f70ac8a6))

* chore: update dependencies

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`221310f`](https://github.com/kaechele/bonaparte/commit/221310fb74cc124bc310494006d8c677bd0b5f1c))

* chore: add docstrings and enable linting

Also rename some functions for clarity.

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`4d0eedd`](https://github.com/kaechele/bonaparte/commit/4d0eedd11d71712650ff1f314894a42b2dd6af6d))

* chore: update dependencies

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`6cc3b56`](https://github.com/kaechele/bonaparte/commit/6cc3b565aeb293bb537d8ce0f8b4878ea4f20f6a))

* chore: test run with all ruff rules enabled

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`f257adf`](https://github.com/kaechele/bonaparte/commit/f257adfd8575e0722a9e2deb1df8c442891ff1fc))

* chore: add some more pre-commit hooks

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`1cdb314`](https://github.com/kaechele/bonaparte/commit/1cdb31498711fe85698c92bacdf05002acef32bb))

* chore: update pre-commit hooks

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`371847e`](https://github.com/kaechele/bonaparte/commit/371847e03210a2e6c6d694c8a1e5eb0a63cd1309))

* chore: add black as a dev dependency

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`a9b8942`](https://github.com/kaechele/bonaparte/commit/a9b894294effb701c53e3c402612198fa0ec4e26))

* chore: add core dependencies

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`c0f5fc9`](https://github.com/kaechele/bonaparte/commit/c0f5fc95e209c006c4bfe4566ec6b70de482061d))

* chore: only publish release on tagged commits

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`3362c96`](https://github.com/kaechele/bonaparte/commit/3362c960992ffe2b0478f36509218832b0084922))

* chore: fix Python version in GitHub Actions flows

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`c3b949e`](https://github.com/kaechele/bonaparte/commit/c3b949e05a84d3cad3bdde68f1600aff746b41cc))

* chore: create VSCode config

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`8b31419`](https://github.com/kaechele/bonaparte/commit/8b314198b069416e67708840b84a0dcb4c9e3033))

* chore: initial commit using template

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`1c82e70`](https://github.com/kaechele/bonaparte/commit/1c82e7018fc0e15a495033317248b829ae679286))

### Documentation

* docs: update README for release

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`8fba4cb`](https://github.com/kaechele/bonaparte/commit/8fba4cbe33987d7a207b8e5cbf02bfb1c3a46751))

* docs: change theme to furo

This also updates sphinx to version 7.

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`c1622a7`](https://github.com/kaechele/bonaparte/commit/c1622a7983bbabc1b501541ef04440d9df63b5ef))

* docs: clarify UART connector on IFC

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`7efa2ac`](https://github.com/kaechele/bonaparte/commit/7efa2acd31d45eacc948346aa89776d1b1b9bbd4))

* docs: reformat CONTRIBUTING.md

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`915b63a`](https://github.com/kaechele/bonaparte/commit/915b63a495159a9991011f8c7ef919cf5260fc9c))

* docs: fix spelling mistakes

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`03efb6e`](https://github.com/kaechele/bonaparte/commit/03efb6eb2a79e34cd9d5390ec0e0392cccc7f2ff))

* docs: remove references to PyPI for now

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`dc6b60b`](https://github.com/kaechele/bonaparte/commit/dc6b60bb32a31b2ae84935340d4e6afc61256838))

* docs: first version of docs

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`fa3146f`](https://github.com/kaechele/bonaparte/commit/fa3146f8a83ef2277650ee632cd266d8fe35af86))

* docs: credit where credit is due

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`0ffd38b`](https://github.com/kaechele/bonaparte/commit/0ffd38b2b229870cf26827baa1651ba7dc21e738))

### Feature

* feat: correct parsers and tests based on new info

Further studying the ProFlame 2 controller I was able to identify what
some of these other bits do. Adding that to the functions and tests.

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`9247698`](https://github.com/kaechele/bonaparte/commit/924769890737366a1337e1f32558f12b2c70b7d8))

* feat: rewrite most of the device class again

Turns out we need more handling of disconnects. This is done nicely in
the yalexs-ble library, so this is mostly taken from there.

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`4fda679`](https://github.com/kaechele/bonaparte/commit/4fda679b38bf125cef7cf36ef3082d4cd90b3bd3))

* feat: allow setting of BLE Advertisement data

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`ee96f41`](https://github.com/kaechele/bonaparte/commit/ee96f412a1d64d5acd099fbfde216bc96c1c4aaa))

* feat: add set_features function

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`c81ae62`](https://github.com/kaechele/bonaparte/commit/c81ae6239c46e62fa2b524d67a6ac5e6b6cf4784))

* feat: add BLE/MCU versions to state

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`8c1a859`](https://github.com/kaechele/bonaparte/commit/8c1a85906170719678ca2d991089c598a8885674))

* feat: add Feature enum

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`f635f76`](https://github.com/kaechele/bonaparte/commit/f635f76cdf1cb2a520a2193851faed17d20bb83a))

* feat: add __all__ exports

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`29508c7`](https://github.com/kaechele/bonaparte/commit/29508c799cf12b9104d038d613c8ca54982c11ec))

* feat: add feature properties

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`db8f188`](https://github.com/kaechele/bonaparte/commit/db8f188080fe818fe12acc4b3819f59d1bc65de1))

* feat: add parser tests

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`f0fa7a8`](https://github.com/kaechele/bonaparte/commit/f0fa7a8af4e98a1871fabdd5070261c5786f899e))

* feat: add initial device communication

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`880eb73`](https://github.com/kaechele/bonaparte/commit/880eb7357ab7091603429cb05540b8291239ddb8))

* feat: add more details to Wireshark dissector

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`6bce5bd`](https://github.com/kaechele/bonaparte/commit/6bce5bdde0ce05ca8dca885e550f5d9991897cce))

* feat: add Wireshark dissector

Also add according Lua tooling.

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`3647c80`](https://github.com/kaechele/bonaparte/commit/3647c806037b69a0d756a27cd2dad4e90a1d47aa))

### Fix

* fix: update tests for bleak 0.20 API

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`a4a92f8`](https://github.com/kaechele/bonaparte/commit/a4a92f8803eb2e4ebcf2bcf8827b08d9f50175a7))

* fix: make log messages uniform in device.py

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`dfa64a1`](https://github.com/kaechele/bonaparte/commit/dfa64a19c97a16482816b1393c849467df998fcd))

* fix: fix log messages and make one more uniform

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`43bd72c`](https://github.com/kaechele/bonaparte/commit/43bd72c4aba45c3f84fd0f61d2af1d71c6dc665c))

* fix: ensure consistent state when using flame_height to turn on

This works around a quirk in which the eFIRE controller maintains its
own state for on/off which goes out of sync if the fireplace is enabled
by moving the flame height from 0 to a higher value without first
turning the fireplace on through the eFIRE controller.

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`f072fe8`](https://github.com/kaechele/bonaparte/commit/f072fe8b0b1963f959dc37ff7386a5bbb775ecac))

* fix: check for blower feature, not aux feature

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`6e68ea7`](https://github.com/kaechele/bonaparte/commit/6e68ea7622be74698616937bc4fde82c21122905))

* fix: test_full_invalid_featureset error message parsing

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`6e1cd6f`](https://github.com/kaechele/bonaparte/commit/6e1cd6fb78756034e53c298a24f572a0b055e054))

* fix: drop get_running_loop call, it&#39;s not needed

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`4367a89`](https://github.com/kaechele/bonaparte/commit/4367a8973568482a5550ceadb7e66d8b3fe4fbd9))

* fix: implement all linter suggestions

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`8c075e0`](https://github.com/kaechele/bonaparte/commit/8c075e02ce44be1c578a000ffd451d92dfd62ee6))

* fix: aux state is part of the &#34;on state&#34; commands

Signed-off-by: Felix Kaechele &lt;felix@kaechele.ca&gt; ([`cd70ff6`](https://github.com/kaechele/bonaparte/commit/cd70ff60b6e252649a4585d5da6f0262bf708341))

### Unknown

* Revert &#34;0.1.0&#34;

This reverts commit eee3522ee3d7e2450ce65d7d8d593334241b841f. ([`69395aa`](https://github.com/kaechele/bonaparte/commit/69395aae663c529b3babeaec68c65da0f92e933e))

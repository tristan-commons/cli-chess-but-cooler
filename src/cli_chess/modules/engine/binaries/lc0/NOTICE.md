# lc0 (Leela Chess Zero) binaries

These binaries are built from unmodified source via the
`build-lc0-binaries.yml` GitHub Actions workflow in this repository.

Source repository: https://github.com/LeelaChessZero/lc0

lc0 is licensed under the GNU General Public License, version 3 or later
(GPL-3.0-or-later), matching cli-chess's own license. See the workflow run
that produced the currently vendored binaries for the exact source tag used.

Bundling these prebuilt binaries alongside cli-chess (invoked as a separate
subprocess over stdio, not linked) follows the same "mere aggregation" model
already used for the vendored Fairy-Stockfish binaries in this directory's
parent folder.

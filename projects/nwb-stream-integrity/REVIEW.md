# NWB stream-preservation review package

Status: local technical review package; nothing submitted upstream. Reviewed 27 October 2026 against Inspector `e6d968a1e0a62aa8f6611f45f242196d9ce75ea5`. [Implementation and replay](README.md).

## Problem, mechanism and beneficiary

Conversion engineers and researchers inspecting buffered neurophysiology data before saving can advance a single-pass iterator through the Inspector's local shape helper. A subsequent writer receives only the remaining chunks. In the constructed 500-row case, 300 rows become zeros; 50- and 100-row cases lose all rows. Inspector errors are returned in our baseline replay, but writing still succeeds. The underlying report is [#771](https://github.com/NeurodataWithoutBorders/nwbinspector/issues/771).

The integration is the existing `inspect_nwbfile_object` call, followed by the existing NWB writer and reader. The patch reuses HDMF 6.2.0's shape helper. It does not infer scientific validity, repair already-damaged files or establish that the defect affects most conversions.

## Evidence available for review

- [Patch](non-consuming-shape.patch), source pin, upstream licence and environment are retained with the project.
- [Baseline](baseline.json) and [patched](patched.json) results cover two storage backends, two iterator types and three lengths, with uninspected controls. Compare every value and dtype, plus full-array hashes.
- Eleven new stream/shape regression cases accompany the patch. The full selected unit run passed 341 tests, with 5 skipped.
- The existing required scientific CI check now runs the actual replay and unit checks. [Main run 40613968067](https://github.com/ahmedkhaledmohamed/kufu-labs/actions/runs/40613968067) passed all three delivery gates. Fresh results from that run were verified in the packaged and deployed website. Its source is merged main `ebe44bf6ccb1c2b92b769e7694f0acae36110e05`.
- Independent production checks matched eleven sampled asset hashes, verified desktop/mobile navigation and confirmed authentication protection remained enabled. These verify delivery, not real-recording usefulness.

## Alternatives and ownership

[Inspector #760](https://github.com/NeurodataWithoutBorders/nwbinspector/issues/760) already proposes reusing HDMF's helper. This is an existing upstream idea; Kufu's local patch must not be presented as originating it. [HDMF PR #1606](https://github.com/hdmf-dev/hdmf/pull/1606), at `10b22a4688af136ac0fd70cbdf1780cf081e6c35`, also preserves all values in the constructed replay with unmodified Inspector. Both remained open at this review.

Prefer an accepted upstream design over maintaining a separate implementation. If the dependency fix lands and covers the supported workflow, reassess whether the Inspector change is needed. The replay and regression cases can still help evaluate the existing work. Do not open a competing PR merely to attach Kufu's name to a fix.

## Review findings and remaining assumptions

The released HDMF helper preserves the tested wrapped streams and returns the current shape of resizable stored arrays; the selected existing unit checks pass. The earlier custom arbitrary-iterator policy was removed because it broadened the reported task. This package inherits HDMF's semantics for other input types.

Unknown dimensions, invalid declared shape metadata, every NWB extension, arbitrary generators, recording-scale memory/performance, other dependency versions and downstream production ingestion remain outside the demonstrated contract. The fixtures are constructed positive integer arrays, not neural recordings. No clinical or biological claim follows from their preservation.

## Questions for a future authorised upstream discussion

1. Is reuse of the dependency helper preferred to relying on the DataIO dependency fix, and should the Inspector retain its compatibility export?
2. Which supported dependency versions and iterator/extension types need additional coverage?
3. Would the round-trip regression cases be useful on the existing issue or dependency PR even if our implementation is not selected?
4. What real conversion workflow should independently assess the change after the technical contract is agreed?

The upstream guide requires issue approval before a PR. No such approval is claimed. Outreach is deferred; this document is a review artifact, not a message sent to maintainers. Next work can refine this local package and compare candidates without crossing that boundary.

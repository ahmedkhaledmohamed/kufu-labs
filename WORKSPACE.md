# Scientific software lab workspace

## Active goal

Deliver independent navigation pages, meaningful CI/CD, runnable demonstrations and protected Vercel production for the scientific-software lab. The approved production target is Ahmed's personal Vercel scope; outreach, new accounts, paid add-ons, model weights and research recordings remain outside this goal.

## Entry points

| Task | Entry |
| --- | --- |
| Browse the lab | [Home](index.html), [explorations/demos](explorations.html), [problems](problems.html), [sources](sources.html), [validation](validation.html) |
| Build, run and deploy | [Delivery guide](site/DELIVERY.md), [hub maintenance](site/README.md) |
| Verify the pose inspector | [Project record](projects/overlap-inspector/README.md) and its pinned oracle generator |
| Verify movement filtering | [Project](projects/movement-edit-filtering/README.md), [widget replay](projects/movement-edit-filtering/verify_workflow.py), [negative deletion reproduction](projects/movement-edit-filtering/DELETION-PROVENANCE.md) |
| Evaluate resolution claims | [Validation review](site/VALIDATION.md) and the website's separate execution/integration/problem-resolution descriptions |

## Source and publication state

PRs #3–#7 are merged; no lab PR remains open at this checkpoint. Current main is `16e4cdb65ff79c614b7201a0349d986e5706c018`. The isolated `fix/empty-promotion-response` branch starts from that refreshed commit. Existing research worktrees are preserved.

Main run [40572525361](https://github.com/ahmedkhaledmohamed/scientific-software-lab/actions/runs/40572525361) passed scientific, local browser and deployed browser verification. The project promotion API accepted the request, but its empty successful response caused the helper to fail JSON parsing before recording success. Read-only server inspection confirmed that the current production target is ready and matches merged main; `lastAliasRequest` is absent.

## Actual verification versus remaining work

Production is live at [the protected lab](https://scientific-software-lab-ahmed-khaled-mohameds-projects.vercel.app). Independent read-only verification matched its current production source commit to main and four served asset hashes to the exact CI artifact. Desktop/mobile browser checks passed across five pages, 25 problems, 15 source boards, four explorations, two demonstration entries, 16 research pages and 180 local links, without page errors. Unauthenticated hub, catalogue and demo requests were blocked. Vercel Authentication remains enabled for all deployments.

The focused local fix accepts an empty successful mutation response while rejecting empty required reads, and observes the current production target's exact deployment ID, ready state and source commit instead of requiring optional job metadata. Eleven simulated full-helper cases passed, covering both empty/JSON mutation responses, absent job metadata and the existing failure gates. Real cloud CI with this final fix remains unverified.

Remaining gates: approve the exact diff/commit for publication; open the fix PR; verify cloud checks; explicitly authorised merge; wait for a green main release and repeat the independent production audit. The website is verified live, but the CI/CD goal remains unfinished until the release job itself passes. No manual promotion, credential broadening, outreach or recordings were used.

## Validation discipline

A runnable browser or ephemeral CI example establishes execution. Pinned host checks establish only the tested integration semantics. Resolving the original researcher problem requires the stated workflow outcome evidence. No adoption, researcher time saving, biological correctness or full upstream resolution is claimed. The next scientific feature candidate remains read-only host-native SLEAP instance/skeleton/score mapping, not a generic hosted code runner.

## Continuation authority

Ahmed asked future authorised goals to continue without additional goal-approval pauses. Repository publication instructions still require exact-diff/exact-commit approval and an explicitly authorised merge. PR #7 was approved and merged; its approval does not cover this new response-handling fix. Prepare the reviewable change before requesting the final publication approval. Preserve boundaries around outreach, spending, new accounts and data access.

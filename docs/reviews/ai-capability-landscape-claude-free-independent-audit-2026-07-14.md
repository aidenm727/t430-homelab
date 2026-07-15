# Claude Free Independent Audit of the Aiden Platform Cloud-AI Capability Landscape

## Authority Banner

- **Authority class:** Source Record and Evidence.
- **Canonical:** No.
- **Generated:** No.
- **Producing environment:** Claude Free.
- **Audit date:** July 14, 2026.
- **Model and mode:** Sonnet 5, Max effort, Thinking enabled.
- Provider facts, prices, availability, limits, and product labels are dated and require re-verification.
- Live Git, Atlas, canonical repository documentation, and human-reviewed evaluation conclusions supersede source-artifact claims.
- Human-reviewed interpretation is owned by `docs/reviews/ai-workflow-evaluation-cycle-2026-07.md`.
- Claude Free successfully completed a substantial independent audit.
- Claude independently supported the core operating recommendation: retain ChatGPT Plus, avoid new spending, and use bounded pilots.
- Claude added useful critique concerning evaluation overhead, shared-usage-pool symmetry, product newness, and adjustable numerical heuristics.
- Claude incorrectly claimed Google AI Plus was $7.99; the official Google page reviewed by the human showed $4.99.
- OpenAI officially confirmed that the standalone ChatGPT Atlas product is being sunset, but the exact August 9 shutdown date was not established by the reviewed official source.
- Anthropic’s Fable/Mythos export-control event is confirmed; Claude’s broader cross-vendor government-release-pattern conclusion remains interpretation rather than established fact.
- SWE-Bench Pro numbers are dated benchmark evidence and remain subordinate to real Aiden workflow evidence.
- Claude Free is supported as an occasional independent challenger.
- The artifact does not justify Claude Pro, replacing ChatGPT Plus, standing dual subscriptions, Claude Code, or Cowork.

## Original Claude Free Independent Audit Artifact

# Independent Audit: Aiden Platform Cloud-AI Capability Landscape and Operating Recommendation

**Audit date:** July 14, 2026
**Artifact audited:** "Aiden Platform Cloud-AI Capability Landscape and Operating Recommendation" (research date July 14, 2026)
**Method:** The existing report's load-bearing claims were independently re-checked against primary sources (official pricing/help pages, provider announcement posts) rather than re-summarized. Claims are marked **Confirmed** (verified directly against a primary source today), **Largely confirmed** (verified against converging secondary sources, not a primary page directly), or **Needs re-verification** (conflicting or single-source evidence). The live Aiden repository state supplied in the task brief is treated as authoritative and is not second-guessed here.

---

## 1. Executive Judgment

The existing report's core call — **keep ChatGPT Plus, spend nothing new yet, evaluate the included ChatGPT Work and Codex first, then run a Claude Free-first comparison, and hold APIs/local AI/cloud platforms until a concrete need appears** — holds up. Nearly every load-bearing factual claim I re-checked against primary sources was accurate, including several unusually current and easy-to-get-wrong details (the Fable 5 credit-billing timeline, the Vertex AI → Gemini Enterprise Agent Platform rename, the GPT-5.6 tier structure). This is a well-researched artifact, not a superficial one.

Two things materially qualify it, and both point the same direction: **be more skeptical of "ChatGPT Plus" as a stable baseline right now, and don't wait to start the Claude comparison.**

- The exact capabilities the report proposes piloting first — ChatGPT Work, and Codex inside the ChatGPT desktop app — are five days old at the research date. GPT‑5.6, ChatGPT Work, and a full merger of the Codex app into ChatGPT all shipped July 9, 2026, in the same release that killed off OpenAI's separate "Atlas" browser (shutting down August 9, 2026 — coincidentally the same name Aiden's own repository uses for its deterministic engineering interface, an unrelated but worth-noting collision while it's still live in search results). The report frames ChatGPT Plus as the "proven incumbent," which is true of the *subscription*, but the specific *features* being recommended for Pilot 1/2 are a brand-new product surface, not a settled one.
- Claude Free costs nothing and draws from no shared pool with ChatGPT Work/Codex. There's no reason in the report's own logic to run it third; it can start on day one, in parallel with Pilot 1, and compress the 8–12 week window at zero added cost or risk.

No finding below changes the top-line "don't buy anything yet" conclusion.

---

## 2. Strongest Parts of the Existing Report

- **Native-app-vs-API discipline (Section 7).** The report never slips into treating API or third-party access as equivalent to a provider's own app — a distinction that's genuinely easy to blur and that it maintains consistently across nine access models.
- **The authority ladder (Section 9, levels 0–5).** A clean, provider-agnostic framework for what an agent may do without asking. This is reusable regardless of which pilot wins and is worth keeping in the Aiden repository on its own merits.
- **Privacy table.** Correctly avoids the common mistake of treating "training opt-out" as "zero retention, zero human review, zero logging." Matches what I could verify on both Anthropic's and OpenAI's current data-control pages.
- **Specific, current facts that many write-ups get wrong or stale**, all confirmed directly against primary sources today:
  - Claude Pro at $20/month ($17/month, $200 upfront, on the annual plan) bundling Claude Code, Cowork, Design, Science, Research, and more models — [Claude pricing](https://claude.com/pricing).
  - Claude's API rate card — Fable 5 $10/$50, Opus 4.8 $5/$25, Sonnet 5 $2/$10 (introductory through Aug 31, 2026, then $3/$15), Haiku 4.5 $1/$5 per million tokens — matched the live pricing page exactly.
  - Fable 5's post-restoration billing: Anthropic's own post confirms Fable 5 was included for up to 50% of weekly usage on Pro/Max/Team/select Enterprise only **through July 7, 2026**, moving to usage-credit billing after that — [Redeploying Fable 5](https://www.anthropic.com/news/redeploying-fable-5). As of the research date (July 14), the report's claim that Fable 5 sits outside ordinary plan usage is correct.
  - GPT-5.6 Sol/Terra/Luna pricing ($5/$30, $2.50/$15, $1/$6) and the Medium/High/Sol-Pro-for-Pro structure — [GPT-5.6](https://openai.com/index/gpt-5-6/), [GPT-5.6 in ChatGPT](https://help.openai.com/en/articles/20001325-a-preview-of-gpt-56-sol-terra-and-luna).
  - ChatGPT Pro's two tiers ($100/5x, $200/20x, identical core capability) — [About ChatGPT Pro tiers](https://help.openai.com/en/articles/9793128-about-chatgpt-pro-tiers).
  - Vertex AI's rebrand to the Gemini Enterprise Agent Platform, correctly dated to the April 2026 Google Cloud Next timeframe.
- **The financial logic.** "Exhaust what you're already paying for before buying anything else" is sound advice independent of which vendor eventually wins, and the report applies it evenhandedly to both ChatGPT and Claude.

---

## 3. Material Errors or Re-verification Needs

| Claim in report | Finding | Confidence |
|---|---|---|
| Google AI Plus is $4.99/month | Two independently sourced, dated checks against the post–I/O 2026 restructure (May 19, 2026) put **AI Plus at $7.99/month**; one source explicitly flags $4.99/$30-type figures as pre-restructure or stale. AI Pro ($19.99) and Ultra ($99.99/$199.99, confirmed directly on [gemini.google/subscriptions](https://gemini.google/subscriptions/)) check out. | Largely confirmed — doesn't change any Aiden decision, since Google AI isn't in the near-term stack, but worth fixing if this table is reused. |
| GitHub Copilot: "Verified students get unlimited completions at no cost" | Directionally right but incomplete. Since March 12, 2026, free student access moved to a distinct **Copilot Student** plan that restricts model choice to Auto-mode selection only — Claude Opus/Sonnet and top-tier GPT models are no longer manually selectable on it ([GitHub Docs](https://docs.github.com/en/copilot/concepts/billing/individual-plans), [community announcement](https://github.com/orgs/community/discussions/189268)). One dated secondary source also reports GitHub **paused new Student-plan sign-ups on April 20, 2026** with no announced reopening. If Aiden isn't already GitHub-Education-verified, this reserve pilot may not currently be available — a two-minute check at `github.com/settings/education/benefits` before relying on it is warranted. | Needs re-verification (the sign-up pause specifically) — directly relevant since Aiden is a student and the report lists this as a reserve pilot. |
| "Sol Pro and Extra High require Pro" | OpenAI's own phrasing on this is ambiguous — it's plausible Extra High reasoning is reachable through plain Sol on Plus, with Sol *Pro* (a related but distinct variant) reserved for the ChatGPT Pro tier. Not a confirmed error, but the report states it more confidently than the source supports. | Needs re-verification directly in-app rather than from documentation. |
| Citation for "GPT-5.6 in ChatGPT" | The report's link uses article ID `20001354`; the live help-center article with that title I could locate is ID `20001325`. Possibly two related articles, possibly a transposed digit. | Minor — re-click the link before relying on it. |
| Implicit framing of ChatGPT Plus as a settled, proven bundle | GPT-5.6 (GA), ChatGPT Work, and the Codex-into-desktop-app merge all shipped **July 9, 2026** — five days before the research date — in the same release that discontinued the standalone "ChatGPT Atlas" browser (shutdown Aug 9, 2026). None of this instability is flagged. It doesn't make any individual fact wrong, but it means Pilot 1/2 would run against a less-than-one-week-old product surface, not a mature one. | Confirmed (the timeline), interpretation (what it implies for the report's framing). |

---

## 4. Missing or Underweighted Capabilities

- **Both providers' flagship models are currently subject to unusual, government-coordinated release gating, and the report doesn't connect this dot.** Fable 5/Mythos 5 were suspended under U.S. export controls June 12–30, 2026, and restored under new cyber-safety classifiers. GPT-5.6 launched as a ~20-organization, government-vetted preview before its July 9 general release. Both traces back to the same regulatory moment (a June 2, 2026 executive order on frontier AI security). This is worth tracking as an ongoing, cross-vendor dynamic for the next 8–12 weeks — not a one-off quirk of either company — since it means further mid-course suspensions, safety-classifier false positives, or staggered rollouts are plausible for either provider, independent of which one Aiden picks.
- **A relevant, current benchmark data point for Aiden's specific interest area (coding/DevOps) is absent.** On SWE-Bench Pro, a repository-oriented coding benchmark, Anthropic's and OpenAI's own published tables both show Claude Fable 5 (80%) and Mythos 5 (80.3%) well ahead of GPT-5.6 Sol (64.6%), even though Sol leads on several agentic/tool-use benchmarks. This doesn't override the report's own — correct — instinct to weight matched real-task results over benchmarks, but it's a relevant prior heading into Pilot 3 given Aiden's stated engineering focus.
- **The taxonomy silently scopes out DeepSeek, Kimi/Moonshot, xAI's Grok, Mistral Le Chat, and Meta AI** from the general-purpose-assistant category. That's a defensible choice given the engineering-repository context (data-handling and terms-of-service considerations differ meaningfully for some of these), but the report should say so in one line rather than omit them silently, since "don't rank every model" doesn't fully justify leaving them out of a taxonomy that otherwise aims to be exhaustive.
- **Symmetric shared-pool risk isn't named as symmetric.** The report flags that Work/Codex draw from one shared agentic pool on ChatGPT Plus. It doesn't note as clearly that Claude Code and Claude.ai chat likewise draw from **one shared pool** on Pro (confirmed directly on Anthropic's pricing FAQ). A Code-heavy Pilot 3 stage could burn Aiden's weekly Claude allowance the same way a Work-heavy Pilot 1 could burn ChatGPT's — this is a wash between providers, not a ChatGPT-specific downside.
- **Migration cost is asserted, not itemized.** The "Replace ChatGPT Plus" gate mentions acceptable "migration and context-rebuild costs" without listing what would actually need rebuilding (Project memory contents, custom instructions, any saved Work/Codex task history). A one-paragraph inventory would make that gate easier to evaluate honestly when the time comes.

---

## 5. Reasoning and Decision-Threshold Critique

- **The specific numeric bars (20% edit-time reduction, 25% mechanical-effort reduction, 4-of-6 task wins, 70%-of-10-over-4–6-weeks for a full replacement) are internally consistent but not derived from anything** — no citation, prior study, or Aiden baseline supports *why* 20% rather than 15% or 30%, or *why* four-of-six rather than three-of-five. That's not a flaw in wanting numeric bars — pre-committing to a threshold is exactly how to avoid motivated reasoning later — but the report presents them with more precision than their provenance earns. Treat them as Aiden's own adjustable operating heuristics, not externally validated science.
- **The measurement overhead is disproportionate to the dollar stakes, and the report doesn't weigh that tradeoff.** Timing median edit/intervention effort across six-plus matched tasks, two providers, and multiple pilot stages is a real cost for someone who is also a full-time student with a part-time job. The decision being measured this carefully is, in the worst case, whether to spend an extra $20/month for one month. That doesn't mean skip the discipline — it means Aiden should consciously decide how much rigor is proportionate rather than adopt the full scorecard by default.
- **The recommended order — incumbent's unused capacity first, then Claude, then everything else — is sound risk-sequencing** and I found no logical flaw in it. The one adjustment worth making: **Claude Free Stage A doesn't need to wait for Pilots 1–2 to finish.** It costs nothing and shares no resource pool with ChatGPT Work/Codex, so running it in parallel from week one shortens the overall evaluation window at zero additional cost or risk. The report doesn't explain why it's sequenced strictly after rather than alongside, and I don't see a reason grounded in the report's own stated logic.
- **The "stop condition" language throughout each pilot is genuinely well-designed** — specific and falsifiable, which is a harder property to achieve than the round-number success thresholds next to it. Worth flagging as a strength precisely because it shows the report's rigor is uneven: strong on qualitative stop conditions, softer on the quantitative bars.

---

## 6. Claude-Specific Distinct Value

- **Bundling is real, not just framing.** Claude Pro ($20/month, or ~$17/month billed annually) includes Claude Code, Cowork, Design, Science, Research, and broader model access in one tier — confirmed directly on Anthropic's pricing page. ChatGPT spreads comparable capability across Plus (Work/Codex) plus a separate $100–$200 Pro step for some model variants. For a single-subscription student budget, that's a genuine structural difference, not marketing language.
- **Cowork and Work are both unproven right now, which makes this a fair moment to compare them, not a bad one.** Both are recently emphasized "agent produces a finished deliverable" products; neither has an established track record yet. Testing them side by side while both are new is arguably better timing than waiting for one to mature into an incumbent.
- **A real, current, citable coding-benchmark edge exists on repository-style tasks.** SWE-Bench Pro results (both Anthropic's and OpenAI's own published tables) show Claude's top current models ahead of GPT-5.6 Sol by a wide margin — relevant context for Aiden's DevOps/engineering focus, though it should inform expectations rather than substitute for Pilot 3's matched real-task testing, exactly as the original report insists.
- **The comparison is genuinely apples-to-apples if the pilot avoids each side's newest/most-gated model.** Fable 5 requires separately billed usage credits post-July 7; GPT-5.6 Sol *Pro* is gated to the $100+ ChatGPT Pro tier. Restricting Pilot 3 to Claude's included Pro-tier models (as the original report specifies) correctly mirrors restricting the ChatGPT side to what Plus already includes.
- **Shared usage-pool design is now symmetric across both providers** (see Section 4) — this cuts against treating "limits disrupt normal tasks" as more of a risk on one side than the other; it's worth measuring evenhandedly on both.

---

## 7. Recommended Operating Stack for the Next 8–12 Weeks

Endorsing the original stack (GitHub as canonical truth, Aiden's own Atlas as the deterministic interface, existing ChatGPT Project as primary reasoning, human authority unchanged) with two changes:

| Layer | Change from original report |
|---|---|
| Research/deliverables (Pilot 1) | Same, but confirm at kickoff that the desktop app reflects the post–July 9 merged Work/Codex build, not a stale cached version — the app changed materially days before the research date. |
| Independent comparison (Pilot 3, Stage A) | **Start immediately, in parallel with Pilot 1**, rather than after Pilots 1–2 conclude. Zero cost, zero shared-pool conflict. |
| Reserve: GitHub Copilot Student | Contingent — verify current sign-up availability and the Auto-mode-only model restriction (both changed March–April 2026) before counting on it as a fallback pilot. |
| Everything else (Codex/Pilot 2, hold on APIs/local AI/cloud platforms, authority ladder) | Unchanged. No evidence surfaced that changes this. |

---

## 8. Recommended Next Three Pilots

The three pilots as designed are sound; the only substantive change is timing, not content:

1. **ChatGPT Work + Deep Research** — as specified, with the added kickoff check above.
2. **Codex on one bounded Atlas Engineering Review task** — as specified, no changes.
3. **Claude comparison, Free first, Pro only through a gate** — **run Stage A now, concurrently with Pilot 1**, not after it. Keep the Stage B gate, the four-of-six/20% success bar, and the "no Fable 5 overage" boundary exactly as written — they're reasonable and, per Section 6, fairly matched against what ChatGPT Plus itself includes.

Before treating "GitHub Copilot Free/Student" as an available reserve pilot, spend five minutes confirming sign-up status given the findings in Section 3.

---

## 9. Purchase and Replacement Decision Gates

The original gate table (Section 12 of the source report) is directionally sound and I'd keep it with two additions:

- **Treat every numeric bar in that table as Aiden's own adjustable heuristic**, per Section 5 — there's nothing wrong with 20%/four-of-six/70%-of-ten as starting points, but they weren't derived from anything external and can be revised without abandoning the framework.
- **Add a pause clause:** if either provider's flagship model is suspended, rate-limited, or materially changed mid-pilot — a real possibility given the current government-coordinated release pattern described in Section 4 — that period shouldn't count against that provider's evaluation clock. Extend the window rather than score a suspension as a loss.

The four decisions the original table addresses (keep ChatGPT Plus only / add Claude Pro / replace ChatGPT Plus / keep Claude as an occasional challenger) don't need new evidence categories — the existing ones (matched task wins, intervention-time deltas, named recurring weekly workflow) are the right ones to track.

---

## 10. Primary-Source Record

All checked July 14, 2026 unless noted. This list covers claims independently re-verified for this audit; it is not a re-verification of every citation in the original report.

| Source | Used for |
|---|---|
| [Claude pricing](https://claude.com/pricing) (fetched directly) | Free/Pro/Max feature lists, Pro's $20/$17/$200 pricing, Claude Code/Cowork inclusion, full API rate card |
| [Redeploying Fable 5](https://www.anthropic.com/news/redeploying-fable-5) (fetched directly) | Export-control suspension/restoration timeline, the July 7, 2026 included-usage cutoff, post-cutoff credit billing |
| [About ChatGPT Pro tiers](https://help.openai.com/en/articles/9793128-about-chatgpt-pro-tiers) | $100/5x and $200/20x structure, identical core capability |
| [GPT-5.6: Frontier intelligence](https://openai.com/index/gpt-5-6/), [Previewing GPT-5.6 Sol](https://openai.com/index/previewing-gpt-5-6-sol/), [GPT-5.6 in ChatGPT](https://help.openai.com/en/articles/20001325-a-preview-of-gpt-56-sol-terra-and-luna) | Sol/Terra/Luna pricing, plan-level access, preview-to-GA timeline (June 26 → July 9, 2026) |
| [Using Codex with your ChatGPT plan](https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan), [ChatGPT Work and Codex](https://help.openai.com/en/articles/20001275-chatgpt-work-and-codex), [Codex pricing](https://developers.openai.com/codex/pricing) | Shared agentic usage pool confirmation, Work/Codex plan availability |
| [ChatGPT is now a partner for your most ambitious work](https://openai.com/index/chatgpt-for-your-most-ambitious-work/) | Work rollout sequencing (Pro/Enterprise/Edu first, Plus "over the next few days"), July 9, 2026 |
| [Introducing ChatGPT Atlas](https://openai.com/index/introducing-chatgpt-atlas/); retirement coverage via [MacRumors](https://www.macrumors.com/2026/07/10/openais-chatgpt-atlas-browser-shutting-down/), [9to5Mac](https://9to5mac.com/2026/07/09/openai-is-discontinuing-chatgpt-atlas-its-standalone-desktop-browser/), [ppc.land](https://ppc.land/openai-kills-atlas-browser-folds-it-into-new-chatgpt-work-agent/) | Atlas browser launch (Oct 2025) and discontinuation (announced July 9–10, 2026; shutdown Aug 9, 2026) |
| [gemini.google/subscriptions](https://gemini.google/subscriptions/) (fetched directly) | Google AI Ultra pricing ($99.99/$199.99) confirmed directly |
| Converging secondary sources (dated May 2026, post–I/O 2026 restructure) | Google AI Plus ($7.99) and Pro ($19.99) pricing — not confirmed against Google's own page text directly; flagged accordingly in Section 3 |
| [GitHub Copilot plans](https://docs.github.com/en/copilot/get-started/plans), [individual plans](https://docs.github.com/en/copilot/concepts/billing/individual-plans), [Copilot for Students update](https://github.com/orgs/community/discussions/189268) | Free (2,000 completions), Student (unlimited completions, Auto-mode-only models since March 12, 2026), Pro/Pro+/Max credit figures |

---

## 11. Final Independent Recommendation

**Follow the original report's recommendation.** Don't add any subscription, API account, or local-AI workload yet. Start Pilot 1 (ChatGPT Work + Deep Research) and Pilot 2 (Codex on a bounded Atlas task) as designed, and start Claude Free comparisons **immediately and in parallel** rather than waiting. Gate any Claude Pro spend behind the original Stage A→B criteria — they're reasonable, if somewhat arbitrarily precise (Section 5).

Before relying on any specific number in either report, re-verify three things directly: the current Google AI Plus price if Google ever enters consideration, GitHub's current Copilot Student sign-up availability given Aiden's student status, and the state of the ChatGPT desktop app given how recently it changed. None of these change the recommendation; all three are cheap to check and would be embarrassing to get wrong in a decision log meant to survive 8–12 weeks.

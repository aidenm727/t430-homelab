# Current AI Operating Baseline

## Status

Dated operating review accepted for current use on July 14, 2026.

This document records provisional operating decisions based on current access, owner preferences, firsthand workflow evidence, and current provider documentation.

It is canonical evidence for how AI should be used now.

It is not permanent provider architecture, a model leaderboard, a purchasing commitment, or authorization for automatic routing.

Reassess this baseline when its evidence changes.

---

## Review Date

July 14, 2026

---

## Purpose

Apply the canonical AI Operating Model and Knowledge Authority Architecture to the owner's current AI access and representative recurring workflows.

The baseline should answer:

- What AI access currently exists?
- Which tasks should each arrangement support?
- Which data and authority boundaries apply?
- How should results be validated?
- Where does a real capability gap exist?
- What evidence would justify changing the arrangement?

---

## Evidence Classes

### Owner-Observed Evidence

The owner currently:

- Has ChatGPT Plus.
- Uses the current GPT-5.6 model family through the ChatGPT model picker.
- Prefers stronger reasoning over speed for meaningful work.
- Has experienced better Aiden Platform progress while using High reasoning.
- Uses ChatGPT Projects, project instructions, uploaded repository context, web research, files, and connected GitHub access.
- Uses WSL, VS Code, Git, GitHub, Python, and Atlas as the engineering environment.
- Does not want to pay for additional AI products without a demonstrated capability improvement.
- Wants AI to increase understanding and agency rather than replace judgment.
- Wants the platform to remain provider-independent and understandable without AI.
- Does not currently operate a local model runtime.
- Has not confirmed an active paid Claude, Google AI, or GitHub Copilot subscription.

Owner-observed product labels are treated as current account evidence.

They are not treated as permanent architecture because provider menus, model names, limits, and modes change.

### Provider Documentation

Current provider facts were checked against primary documentation on July 14, 2026.

The source list is preserved at the end of this review.

### Provisional Interpretation

Workflow assignments and purchase decisions are human-reviewed operating interpretations.

They should change when firsthand evidence shows a better arrangement.

---

## Current Access Inventory

### ChatGPT Plus

**Status:** Active primary subscription.

**Cost:** $20 per month.

**Officially documented capabilities include:**

- Broader model and tool access than Free.
- Higher model limits than Free.
- Advanced reasoning options available to the account.
- Voice.
- Image generation.
- File uploads and analysis.
- Deep Research where available.
- Custom GPT creation and use.

Model availability and usage limits vary.

The model picker is the operational source of truth for the owner's current account.

API usage is separate and billed independently.

### Current ChatGPT Account Modes

The owner currently observes access to:

- GPT-5.6.
- Instant.
- Medium.
- High.
- Work.

These labels represent different layers and should not be collapsed:

- GPT-5.6 is the observed model family.
- Instant, Medium, and High are observed response or reasoning settings.
- Work is an extended task-execution mode rather than merely a stronger chat response.

Exact internal routing may change.

Operating decisions should use visible behavior and results rather than assume a permanent mapping.

### ChatGPT Projects

The Aiden Platform Project is the primary persistent AI workspace for platform engineering.

Official project behavior supports:

- Project-specific instructions.
- Uploaded reference files.
- Project chats and memory.
- Web search.
- Study mode.
- Voice.
- Image generation.
- Paid-plan access to additional tools such as agent mode and Deep Research where available.

Project instructions override global custom instructions.

Plus projects currently support up to 25 files.

This makes source curation necessary.

Project memory and uploaded files improve continuity but do not replace canonical repository knowledge.

The repository and Atlas remain authoritative for engineering state.

### ChatGPT Data Controls

OpenAI provides an account-wide control named `Improve the model for everyone`.

When disabled, chats remain in history but are not used to train ChatGPT.

Temporary Chats:

- Are deleted from OpenAI systems after 30 days.
- Are not used to train models.
- Do not appear in history.
- Do not create memories.
- May be reviewed for abuse monitoring.

Temporary Chat is a privacy tool, not an approved location for Highly Restricted information.

### OpenAI API

**Status:** Not part of the current baseline.

ChatGPT Plus does not include API usage.

Do not add API spending until a programmatic workflow demonstrates value that the ChatGPT application cannot provide adequately.

### Claude

**Status:** Free evaluation candidate; no paid subscription adopted.

Claude Pro is currently documented at $20 per month in the United States.

Pro includes Claude Code and Cowork access, but remains usage-limited.

Anthropic documents:

- At least five times free usage per session during peak hours.
- A session-based limit that resets every five hours.
- A weekly limit across models.
- Additional possible capacity limits.
- Separate API billing.
- No standing standard discount.

This makes Claude Pro a meaningful alternative but not a justified purchase without firsthand task evidence.

### Google AI and NotebookLM

**Status:** Potential challenger; no paid plan adopted.

Google currently markets paid AI plans with expanded Gemini, Deep Research, NotebookLM, Google application, and coding-tool access.

The owner has not demonstrated a recurring workflow that requires a paid Google AI plan.

NotebookLM or Gemini may be evaluated through currently available access when a source-grounded study or Google-workspace workflow provides a real comparison case.

### GitHub Copilot

**Status:** Access not confirmed; not part of the current baseline.

Do not assume Copilot is available merely because the owner uses GitHub and VS Code.

Evaluate it later only if inline IDE completion, repository-native chat, or code-review integration reveals a gap not served adequately by the current ChatGPT and Atlas workflow.

### Local AI

**Status:** Not deployed.

No current evidence justifies purchasing hardware, operating a model runtime, or accepting the maintenance burden.

Local AI remains a future option when one or more of the following becomes true:

- A valuable Sensitive workflow cannot use hosted AI acceptably.
- Offline operation matters.
- Repeated volume creates a credible cost advantage.
- Low-latency local integration materially improves a capability.
- A local model is sufficiently capable for the defined task.
- Experimentation creates durable learning value proportionate to burden.

---

## Primary Operating Decision

ChatGPT Plus remains the primary AI platform.

The current arrangement already combines:

- Strong reasoning.
- Long-running Projects.
- Repository and file context.
- Web research.
- Deep Research.
- Tool access.
- Multimodal input.
- Existing owner familiarity.
- No additional subscription cost.

Do not add a second paid general-purpose AI subscription now.

The correct next step is structured evaluation of current workflows, not purchasing broader access.

---

## Mode Selection Baseline

### Instant

Use for:

- Low-stakes factual questions where current research is unnecessary.
- Simple rewriting.
- Small formatting changes.
- Basic calculations when a deterministic calculator is available.
- Reversible everyday assistance.
- Quick orientation before deeper work.

Do not use Instant as the default for architecture, difficult debugging, strategic decisions, or dense learning.

### Medium

Use for:

- Ordinary analysis where High is unnecessary.
- Iterative refinement after a difficult conclusion is already established.
- Lower-consequence planning.
- Situations where latency matters more than marginal depth.

Medium is a useful efficiency option, not the owner's default for meaningful work.

### High

Use as the default for meaningful work, including:

- Aiden Platform architecture.
- Repository analysis.
- Difficult debugging.
- Implementation review.
- Strategic planning.
- Complex current-information synthesis.
- Difficult AI and computer-science learning.
- Consequential personal decisions where AI is appropriate.

The owner's firsthand evidence indicates that High has improved engineering progress enough to justify its additional reasoning cost.

### Work

Use for bounded multi-step work where the deliverable, permitted scope, checkpoints, and validation are explicit.

Good uses include:

- Read-only repository inspection.
- Producing a bounded implementation runner.
- Reviewing a defined document set.
- Applying a pre-approved multi-file change.
- Repetitive research with a clear report contract.
- Executing a testable engineering sequence.

Do not use Work as an open-ended autonomous engineer.

Every Work task should define:

- Goal.
- Inputs.
- Writable scope.
- Prohibited actions.
- Required output.
- Validation.
- Approval gates.
- Stop conditions.

High chat remains preferable when the core problem is still architectural judgment.

---

## Representative Workflow Profiles

## 1. Aiden Platform Architecture and Repository Engineering

**Goal:** Design, implement, verify, document, and evolve the Aiden Platform.

**Primary arrangement:** ChatGPT Plus inside the Aiden Platform Project.

**Default mode:** High.

**Use Work when:** The architecture and bounded change contract are already clear.

**Required context:**

- Canonical repository architecture.
- Current Mission.
- Generated context.
- Relevant infrastructure records.
- Live Atlas output.
- Relevant Git diff or file contents.

**Data sensitivity:** Ordinary Personal by default; Sensitive when private operational details, educational records, personal finances, health information, or unpublished personal material are involved.

**Highly Restricted exclusion:** Never provide passwords, tokens, API keys, private keys, recovery codes, or secret environment files.

**Authority:**

- AI may explain, recommend, critique, and prepare reviewable artifacts.
- The owner approves architecture, mission changes, repository writes, commits, pushes, and high-impact operational changes.
- Atlas and Git determine engineering state.

**Validation:**

- Review the proposed architecture.
- Run tests.
- Run `./atlas validate`.
- Run `./atlas missing`.
- Run `./atlas sync`.
- Inspect the diff.
- Commit and push only after verification.
- Confirm the final working tree is clean.

**Fallback:**

- Reduce scope.
- Return to architecture discussion.
- Use a safer artifact transport.
- Ask for live repository evidence.
- Stop before mutation when ownership or authority is unclear.

**Current decision:** ChatGPT Plus High is sufficient as the primary reasoning environment. Work is a secondary bounded execution mode. No second paid provider is currently justified.

---

## 2. Code Debugging and Implementation Review

**Goal:** Understand failures, design fixes, review code, and produce changes the owner can explain.

**Primary arrangement:** ChatGPT Plus High with exact error output, relevant files, and local verification.

**Use Work when:** The task spans multiple files but has explicit scope, tests, and rollback.

**Required context:**

- Error message.
- Reproduction steps.
- Relevant code only.
- Runtime and dependency versions.
- Expected behavior.
- Recent changes.
- Test output.

**Data sensitivity:** Ordinary Personal unless source includes private credentials, user records, or sensitive business or school data.

**Authority:**

- AI may propose or prepare code.
- The owner remains responsible for understanding, running, reviewing, and committing it.
- Generated code is not accepted because it compiles once.

**Validation:**

- Reproduce before changing.
- Test the narrow fix.
- Run broader regression tests where appropriate.
- Review security and edge cases.
- Explain the causal mechanism.
- Confirm the owner can describe the change.

**Fallback:**

- Use deterministic debugging tools.
- Minimize the reproducer.
- Compare a second free model only when the primary analysis remains uncertain.
- Preserve the failure as evidence rather than widening scope blindly.

**Current decision:** Keep ChatGPT High as the main debugging partner. Do not purchase Copilot or Claude solely for code generation.

---

## 3. Long-Form Planning and Strategic Reasoning

**Goal:** Compare choices, expose tradeoffs, sequence work, and make decisions without losing human judgment.

**Primary arrangement:** ChatGPT Plus High.

**Use Work when:** Research collection or a structured multi-stage deliverable is clearly bounded.

**Required context:**

- Decision.
- Goals.
- Constraints.
- Time horizon.
- Current state.
- Reversibility.
- Opportunity cost.
- Evidence quality.
- Unknowns.

**Data sensitivity:** Ordinary Personal or Sensitive depending on finances, health, education, relationships, or unpublished plans.

**Authority:**

- AI recommends and critiques.
- The owner decides.
- Recommendations do not become commitments automatically.

**Validation:**

- State assumptions.
- Compare at least one serious alternative.
- Separate current facts from inference.
- Use current sources when facts may have changed.
- Revisit decisions when assumptions change.

**Fallback:**

- Narrow the decision.
- Gather missing evidence.
- Delay irreversible commitments.
- Use a second free model as a critique pass when stakes justify it.

**Current decision:** High is the default. A second paid general-purpose model is unnecessary until repeated comparative evidence shows a material reasoning advantage.

---

## 4. Current-Information Research and Source Synthesis

**Goal:** Obtain current, attributable, source-grounded information.

**Primary arrangement:** ChatGPT web search for bounded questions; Deep Research for broad or source-intensive questions.

**Default mode:** High when interpretation matters.

**Required context:**

- Research question.
- Date sensitivity.
- Preferred source authority.
- Geographic or legal scope.
- Required depth.
- Decision the research will support.

**Data sensitivity:** Public for ordinary external research; may become Ordinary Personal or Sensitive when combined with personal context.

**Authority:**

- External sources own external facts.
- AI summaries remain interpretations.
- Repository promotion requires separate review.

**Validation:**

- Prefer primary sources.
- Check dates.
- Compare conflicting evidence.
- Verify the strongest claim directly.
- Cite load-bearing facts.
- Separate event date from publication date.

**Fallback:**

- Open the primary source directly.
- Use a specialized official database.
- Mark unresolved conflicts.
- Stop rather than fabricate certainty.

**Current decision:** Existing ChatGPT search and Deep Research capabilities are sufficient. Google or Claude may be compared through free access for a defined research task, but no paid plan is justified.

---

## 5. AI and Computer-Science Learning

**Goal:** Improve durable understanding, problem solving, and independent capability.

**Primary arrangement:** ChatGPT Plus High or Study mode.

**Required context:**

- Topic.
- Current understanding.
- Course or project constraints.
- Desired depth.
- Whether the task is practice, review, or graded work.

**Data sensitivity:** Public or Ordinary Personal; transcripts and detailed educational records are Sensitive.

**Authority:**

- AI teaches, questions, critiques, and provides examples.
- It should not replace the owner's reasoning or produce unexplained graded work.

**Validation:**

- Explain the concept without the AI.
- Solve a new example.
- Predict output before running code.
- Identify why an incorrect approach fails.
- Use retrieval practice and spaced review where appropriate.

**Fallback:**

- Reduce explanation complexity.
- Use visual or concrete examples.
- Switch to guided questions.
- Compare a second explanation only when the first remains unclear.

**Current decision:** Keep ChatGPT Plus. Use High for difficult concepts and Study mode for interactive learning. Do not buy another subscription to compensate for weak learning habits.

---

## 6. Everyday Personal Decision Support

**Goal:** Improve ordinary decisions while preserving privacy, judgment, and proportionality.

**Primary arrangement:** ChatGPT Plus.

**Mode:**

- Instant for simple, low-stakes, reversible questions.
- High for consequential planning or multi-factor decisions.
- Web research when current facts matter.

**Data sensitivity:**

- Ordinary Personal for meals, routines, purchases, travel preferences, and scheduling.
- Sensitive for health, finances, private communications, precise location patterns, educational records, and intimate personal information.
- Highly Restricted information is excluded.

**Authority:**

- AI may explain and recommend.
- The owner makes commitments.
- Medical, legal, and financial guidance requires appropriate current sources and professional judgment where stakes warrant it.

**Validation:**

- Check current facts.
- Identify personal assumptions.
- Prefer reversible tests.
- Avoid optimizing trivial choices beyond their value.
- Escalate high-stakes matters appropriately.

**Fallback:**

- Provide less context.
- Use Temporary Chat for appropriate one-off Sensitive discussions.
- Use an official source or qualified professional.
- Stop when safe advice requires unavailable information.

**Current decision:** ChatGPT Plus is adequate. Additional subscriptions would add fragmentation without a demonstrated capability improvement.

---

## Privacy and Context Baseline

### Required Configuration Check

Verify that `Improve the model for everyone` is disabled for the account used with Aiden Platform and personal context.

Record the outcome as a user configuration decision, not as a repository secret.

### Aiden Platform Project

Continue using the existing Aiden Platform Project for continuity.

Treat:

- Repository documents as canonical.
- Project files as context copies.
- Project memory as useful but non-canonical.
- Conversation summaries as generated context.
- Assistant conclusions as candidate findings until reviewed.
- Terminal output and tests as evidence.
- Commits and verified state as completed engineering actions.

Do not rebuild the Project solely to obtain project-only memory during this milestone.

Evaluate that migration later only if cross-project context leakage becomes an observed problem.

### Data Minimization

Send only the context needed for the task.

Do not attach whole repositories, transcripts, health records, financial histories, or private conversations when a smaller relevant excerpt is sufficient.

### Highly Restricted Information

Never provide general hosted AI with:

- Passwords.
- API keys.
- Tokens.
- Private keys.
- Recovery codes.
- Secret environment files.
- Authentication cookies.
- Information that directly compromises systems or safety.

Use deterministic secret-management tools instead.

---

## Challenger Evaluation Policy

A challenger is evaluated to discover a capability gap, not to collect subscriptions.

### Claude Free

Use as the first challenger for:

- Long-document critique.
- Architecture review.
- Alternative reasoning on a difficult decision.
- Comparing code-review explanations.

Run at least three representative comparisons before considering Pro.

### Claude Pro Purchase Threshold

Consider Claude Pro only when at least one condition is supported by repeated firsthand evidence:

- Claude materially outperforms ChatGPT on a recurring high-value workflow.
- ChatGPT limits repeatedly block important work.
- Claude Code or Cowork enables a workflow that the current stack cannot perform adequately.
- The time or result-quality improvement reasonably exceeds the additional $20 monthly cost.
- The workflow remains useful after accounting for Claude's session and weekly limits.

A single impressive response is insufficient.

### Google AI Evaluation

Evaluate Gemini or NotebookLM when:

- A source-grounded notebook workflow is needed.
- Google Drive, Gmail, Docs, Sheets, or Search integration provides clear value.
- A current Google model offers a distinct capability relevant to a recurring task.

Do not purchase a plan for storage or bundled features unless those benefits are independently valuable.

### GitHub Copilot Evaluation

First confirm actual student or account access.

Evaluate only if:

- Inline completion would reduce friction without reducing understanding.
- IDE-local context improves a real coding workflow.
- Repository-native review provides value beyond ChatGPT and Atlas.
- Privacy and training settings are acceptable.

### Local AI Evaluation

Begin only with a defined task and success criteria.

Do not begin with hardware shopping.

---

## Lightweight Workflow Evaluation Record

For a meaningful comparison, record:

- Date.
- Workflow.
- Task.
- Provider and application.
- Visible model and mode.
- Context supplied.
- Tools used.
- Data-sensitivity class.
- Result.
- Validation method.
- Corrections required.
- Scope violations.
- Time or friction.
- Usage-limit impact.
- Learning retained.
- Would use again.
- Decision or unresolved question.

Do not collapse these observations into one opaque score.

A short narrative and a few comparable measures are enough.

---

## Reassessment Triggers

Review this baseline when:

- A provider changes model availability materially.
- Usage limits block important work repeatedly.
- Privacy or retention terms change.
- A recurring task performs poorly three times despite good context.
- A challenger wins at least three comparable high-value tasks.
- A new workflow requires programmatic API access.
- Sensitive processing becomes a repeated unmet need.
- Local hardware becomes available for another justified reason.
- The owner begins paying for another AI product.
- Personal AI, task-scoped context, or bounded agents enter active architecture.
- Three months pass without another trigger.

---

## Current Capability Gaps

The current baseline reveals gaps, but not all require implementation.

### Evidence Capture

There is no lightweight, repository-owned record of cross-model workflow evidence.

Start with manual review notes before designing a new Repository Object.

### Configuration Evidence

The account's current training toggle and Project memory mode are not yet recorded as verified user configuration.

Verify them manually.

### Cross-Model Evidence

The owner has preferences and impressions but not a consistent comparison set across representative tasks.

Begin with free or already-included access when it can support a fair evaluation.

A paid one-month trial is acceptable when free limits prevent a meaningful comparison and the evaluation has a defined task, duration, evidence record, and cancellation decision.

### Task-Scoped Context

The Aiden Platform Project supplies broad context rather than a deterministic task package.

EO-2026-013 remains the future architecture for task-scoped context compilation.

### Sensitive Local Processing

No local AI path exists.

This is acceptable until a valuable blocked workflow proves the need.

---

## Current Decisions

1. Keep ChatGPT Plus as the primary AI subscription.
2. Use High as the default for meaningful work.
3. Use Instant for low-stakes reversible assistance.
4. Use Medium when efficiency matters and deep reasoning is unnecessary.
5. Use Work only for bounded multi-step tasks with explicit contracts and validation.
6. Continue using the Aiden Platform Project while keeping GitHub and Atlas canonical.
7. Verify that account training is disabled.
8. Keep Highly Restricted information out of general hosted AI and the repository.
9. Use web search or Deep Research when current facts matter.
10. Test free challengers before buying another subscription.
11. Do not purchase Claude Pro, Google AI, Copilot, API usage, or local-AI hardware without evidence; additional spending is acceptable when repeated real-task value justifies it.
12. Do not implement automatic routing, Personal AI, or autonomous agents during this baseline.
13. Reassess through workflow evidence rather than hype or permanent model rankings.

---

## Recommended Next Checkpoint

Run a short manual evaluation cycle using known tasks.

Evaluate:

- One Aiden architecture task.
- One debugging task.
- One current research task.
- One difficult learning task.

Use ChatGPT High as the baseline.

Use one free challenger where practical.

Record corrections, validation, friction, and whether the challenger provides a distinct capability.

Do not design automation until the manual evidence reveals a stable repeated need.

---

## Source Record

Primary provider documentation reviewed July 14, 2026:

- OpenAI, “What is ChatGPT Plus?”
  https://help.openai.com/en/articles/6950777-what-is-chatgpt-plus

- OpenAI, “Data Controls FAQ.”
  https://help.openai.com/en/articles/7730893-data-controls-faq

- OpenAI, “Projects in ChatGPT.”
  https://help.openai.com/en/articles/10169521-projects-in-chatgpt

- OpenAI, “ChatGPT Plans.”
  https://chatgpt.com/pricing/

- Anthropic, “What is the Pro plan?”
  https://support.claude.com/en/articles/8325606-what-is-the-pro-plan

- Google, “Google AI plans.”
  https://one.google.com/about/google-ai-plans/

Provider documentation is evidence for current product facts.

It does not own Aiden Platform operating decisions.

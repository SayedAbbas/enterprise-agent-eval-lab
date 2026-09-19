# Your AI Agent Passed 99% of Evals. Why Can It Still Fail in Production?

A 99% evaluation pass rate sounds production-ready. It may not be.

Imagine an enterprise AI agent passes 990 out of 1,000 evaluation cases. The remaining 10 failures look small when averaged into a dashboard. But what if one is an unauthorized action? What if the agent uses the wrong tool with valid-looking arguments? What if it invents evidence in a regulated workflow?

For production AI agents, **average accuracy is not enough**.

> **What failed, how severe was the failure, and will we detect the next failure when the agent meets the real world?**

This is why production AI needs **golden datasets, offline evaluations, online evaluations, and observability working together**.

## 1. Why 99% Can Still Be a Production Failure

Two agents can both show a 99% pass rate:

| Agent | Failures |
|---|---|
| A | 10 formatting failures; no incorrect business actions |
| B | 9 formatting failures; 1 unauthorized high-impact action |

Operationally, these are very different systems.

For enterprise agents, evaluate failures by **severity as well as frequency**:

| Severity | Example | Release implication |
|---|---|---|
| Critical | Unauthorized action, fabricated consequential evidence, sensitive-data violation | Block release |
| High | Wrong policy applied, materially incorrect recommendation | Usually block and investigate |
| Medium | Incomplete response, unnecessary tool call | Investigate against business tolerance |
| Low | Formatting or style issue | Usually non-blocking |

> **A high average score cannot compensate for a catastrophic failure mode.**

## 2. Why We Need a Golden Dataset

A **golden dataset** is a curated collection of representative cases with clearly defined expected behaviors or evaluation criteria.

It should contain more than happy paths:
- representative historical cases
- SME-created scenarios
- known production failures
- edge and adversarial cases
- missing or conflicting information
- tool failures/timeouts
- authorization-boundary scenarios

For an insurance claims agent, one case might include an active policy, prescription and invoice, but a missing mandatory clinical document. Expected behavior might require the agent to retrieve the correct policy, identify the missing evidence, avoid inventing it, avoid approval, escalate appropriately, and cite the relevant policy.

That becomes a reusable regression test whenever we change the **model, prompt, retrieval logic, tools, policies, or orchestration**.

### Golden does not mean frozen

When production exposes a legitimate new failure:

Production failure → human validation → root-cause analysis → add representative case to golden dataset → fix → rerun regression suite.

The dataset becomes institutional memory for the agent.

## 3. Offline Evals: Can We Release This Change?

**Offline evaluation happens in a controlled environment before release.**

A candidate system runs against the golden dataset after changes to prompts, models, retrieval, MCP/tools, tool descriptions, or orchestration.

Useful dimensions include:
- task success
- grounding and retrieval quality
- tool selection and arguments
- policy/authorization compliance
- escalation behavior
- latency and cost

For agents, evaluating only the final answer is dangerous. An agent can choose the wrong tool, retry another tool, and eventually produce the correct answer. A final-answer grader may say PASS while a trajectory evaluator identifies incorrect tool selection, unnecessary calls, added latency/cost, or unsafe intermediate behavior.

> **A correct final answer does not necessarily mean the agent behaved correctly.**

Offline evals become much more useful when connected to **release gates**. Thresholds should be workload-specific and based on business risk. A high-impact financial workflow should not have the same tolerance as an internal content assistant.

## 4. Why Offline Evals Are Not Enough

Even an excellent golden dataset is still a model of reality.

Production is reality.

Users ask questions we did not anticipate. Enterprise systems time out. Data is incomplete. Policies change. Tools return unexpected results. Traffic shifts. Model behavior can change outside the test distribution.

> **Offline evals tell us how the agent behaves on cases we know enough to test. They cannot guarantee every future production interaction.**

That is why we also need online evaluation.

## 5. Online Evals: Is the Agent Still Good in the Real World?

**Online evaluation measures actual production behavior after deployment.**

Signals can include:
- user acceptance, modification, and rejection rates
- escalation rate
- tool failure and invalid-argument rates
- sampled groundedness
- policy violations
- latency and cost
- business outcomes

Imagine an AI campaign agent passes offline gates. Production might still reveal that users heavily edit recommendations, a customer-data tool times out frequently, latency doubles for complex campaigns, or a new campaign type performs poorly.

Those are signals the original golden dataset may not have represented.

Online evaluation closes that gap.

## 6. Observability and Evals Are Different

I use a simple distinction:

> **Observability tells me what happened. Evals tell me whether what happened was acceptable.**

A trace might show request → model → customer-profile tool → 1.8-second tool latency → model → response.

That is valuable, but it does not automatically tell us whether the correct tool was selected, the arguments were semantically correct, the response was grounded, the action complied with policy, or the user received a useful outcome.

Production systems need both.

## 7. The Offline → Online Feedback Loop

The lifecycle is:

Golden dataset → offline evals → release gates → controlled/canary rollout → online evals → production failure discovery → human validation/root-cause analysis → new golden case → regression testing.

This creates a compounding effect: every meaningful production failure can make the offline regression suite stronger.

## 8. Automating Evals in the Engineering Lifecycle

Evaluation becomes especially powerful when it is part of CI/CD rather than a manual activity before a major launch.

A simplified flow:

Prompt/model/RAG/tool change → code commit → CI pipeline → candidate test environment → run golden dataset → deterministic + model-based graders → compare release gates → block or promote → controlled rollout → online evals.

Deterministic graders can check expected tools, arguments, calculations, required fields, unauthorized actions, and schema compliance.

Model-based graders can help assess groundedness, completeness, relevance, and explanation quality.

Human SMEs remain important for defining criteria, calibrating graders, adjudicating ambiguous/high-risk cases, and reviewing consequential failures.

The goal is not to remove humans. It is to make evaluation **repeatable enough to become part of engineering**.

## 9. Production Readiness Is Not a Single Score

The question should not be:

> **Did the agent pass 99% of our tests?**

A better question is:

> **What evidence do we have that this agent can be trusted to take this particular action, at this level of autonomy, under these business constraints?**

A successful demo demonstrates capability. A golden dataset creates repeatability. Offline evals reduce release risk. Release gates turn evaluation into an engineering decision. Online evals reveal what the test environment missed. Observability provides evidence for investigation. Production failures make the next golden dataset stronger.

**The higher the consequence and autonomy, the higher the evidence bar should be.**

## About the Frontier Enterprise Agent Eval Lab

I built the **Frontier Enterprise Agent Eval Lab** as a vendor-neutral reference implementation for evaluating enterprise agent behavior across frontier models.

It focuses on task success, grounding, tool selection and arguments, safety/escalation, and latency.

The objective is not *Which model is best?*

It is:

> **Which agent can we trust to perform this workload under our requirements?**

If you are working on production AI agents, I would be interested in how your team combines offline evaluation, production monitoring, and release gates—and which failures have been hardest to capture before deployment.

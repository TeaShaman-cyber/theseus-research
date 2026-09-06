# Theseus Methodology: Sadhana of Engineering

**Status:** explanatory and operational companion to the `1.0` program contract

**Languages:** English (international reference) · [Русский перевод](methodology.ru.md)

**Type:** methodology and working culture

**Scope:** human-agent engineering in a public-interest research program

This document explains how Theseus tries to turn its contract into everyday engineering practice. It is explanatory and operational: its working rules translate the [program contract](../README.md) into bounded practice, remain subordinate to it, and may not weaken its invariants. A change to consent, autonomy, provenance, sponsor independence, public status, or another contract boundary must be handled as a contract revision, not smuggled in as methodology wording.

## From DevOps to human-agent engineering

DevOps is more than a collection of CI/CD tools, containers, monitoring, and infrastructure-as-code. At its best, it is a sociotechnical practice that reduces the distance between the people who build a system and the people who operate and take responsibility for it.

When an agent enters the engineering process, another distance becomes important: the distance between human intent and the agent's actual action.

```text
        human
          |
          | intent, context, approval
          v
        agent -------- memory
          |              |
          | actions      | decisions, history, provenance
          v              v
      tools ----------> external world
```

Within explicitly approved, bounded operational envelopes, the agent can read, search, edit, run commands, publish, and communicate with external systems. It is therefore a participant with capabilities, limitations, routing failures, and a tendency to continue confidently along the wrong path when the contract is implicit. The envelope must identify the permitted scope, authority, tool or wrapper, expected postcondition, and stopping condition; broad capability is not blanket permission.

Human-agent engineering makes the route explicit.

## Contract before trust

People may describe work as collaboration between a human and an agent. That description is useful, but it is not enough for an engineering operation. A signature or a friendly interaction establishes neither permission nor verification.

For each meaningful action, the route should make clear:

- who has authority to approve it;
- which protocol and runtime are current;
- which tool or wrapper is in scope;
- what counts as success;
- what should happen after an error;
- which part of the result has actually been checked.

Provenance complements the contract. It does not replace it.

## Operational distinctions

Maturity begins when several easily confused voices are kept separate:

```text
memory says:       this was described or decided before
README says:       this is how the system is intended to work
runtime says:      this is what happened now
postcondition says: this is what was confirmed afterward
```

Theseus therefore maintains explicit distinctions between:

- historical memory and current operational truth;
- human intention and granted permission;
- a tool and a wrapper around that tool;
- an observation, an inference, a hypothesis, and an unknown;
- a local machine, a remote runtime, and a container;
- an MVP, an audit boundary, and production readiness.

These distinctions are not bureaucracy for its own sake. They prevent a plausible story from being mistaken for evidence.

## The smallest responsible repair

When an agent or an engineer takes the wrong route, the first question is not “who is to blame?” It is:

```text
What signal allowed the confusion?
Which contract was missing or ambiguous?
Why was the correct tool not selected first?
What observation stopped the wrong route?
Which smallest layer can prevent a recurrence?
```

This is a blameless practice in the precise sense: name the error accurately, keep responsibility visible, and repair the system that made the error likely. A good correction may involve the prompt, tool description, wrapper, permission boundary, success criterion, or read-back—not only the agent's future behavior.

Blameless does not mean consequence-free. An unauthorized action, a false success claim, or a skipped verification remains an engineering defect and must be recorded as such. This is an operational rule subordinate to the contract, not a new independent authority to publish or act.

## A two-way engineering culture

The familiar DevOps themes of Culture, Automation, Lean, Measurement, and Sharing become two-way responsibilities in an agent environment.

### Culture

Human and agent share rules for scope, consent, uncertainty, provenance, and stopping. The agent does not guess architecture from the emotional tone of a request.

### Automation

Automate repeatable safe routes, not every possible action. A visible VS Code task or narrow wrapper is valuable when it exposes the target, the result, and the stop condition.

### Lean

An MVP does not need to impersonate production. Unnecessary architecture is a defect when it consumes attention, creates new failure surfaces, or hides the actual experiment.

### Measurement

Green indicators are not the only useful results. `UNKNOWN`, `NOT CLAIMED`, `404`, and `readback verified` are all engineering data. They make the boundary of knowledge visible.

### Sharing

Issues, blog entries, checkpoints, and signatures turn a private failure into material for the next cycle. Sharing should preserve the decision, evidence boundary, and applicability—not publish raw logs or private memory by default.

## The working loop

Theseus uses a small loop that can be applied to a tool call, a repository change, or a public research step:

```text
intent
  -> boundary and permission
  -> concrete contour and tool
  -> expected postcondition
  -> action
  -> read-back
  -> result classification
  -> reusable lesson
  -> next cycle
```

Progress is real only when the intended postcondition becomes more observable. A plan, a skill selection, a memory recall, or a successful build is not by itself proof that the requested outcome exists.

## Sadhana of Engineering

Sadhana is not a promise never to make a mistake. It is a discipline of returning to reality after a mistake without losing the dignity of the participants or the continuity of the work.

We may confuse Codex Desktop with a remote machine, memory with current runtime, Git with GitHub, a signature with permission, or a successful command with a verified publication. The goal is not to pretend these confusions are impossible. The goal is to maintain a language and a process that can distinguish them, repair them, and preserve the lesson.

The practical commitment is therefore modest:

```text
not “let the agent do everything”
but
“build an environment where human and agent understand
what they are doing, how it can be checked,
and where to stop”
```

## Relationship to the contract

This methodology document may be clarified without changing the program's core mission. A change that alters consent, autonomy, provenance, sponsor independence, public status, or another core invariant must follow the contract's versioning rules and cannot be smuggled in as mere documentation.

## Research context: ComBodied Agents

The external paper [ComBodied Agents: a New Paradigm of Human-Centric Agentic AI](https://arxiv.org/abs/2608.10915) is a useful adjacent reference for this methodology. It organizes a long-term support loop around event-based perception, longitudinal and correctable memory, personal-state prediction, and an admissible intervention policy. Its central distinction between observation, inferred state, predicted trajectory, and authorized intervention reinforces Theseus's own separation of evidence from interpretation and permission.

The connection is conceptual, not a claim of implementation. Theseus does not thereby become a health agent, a robotics system, or a Human Digital Twin. The paper helps us ask whether continuity, memory, and automation leave the person more able to understand, choose, correct, recover, and grow. Theseus answers those questions through its own contract, evidence, and review process.

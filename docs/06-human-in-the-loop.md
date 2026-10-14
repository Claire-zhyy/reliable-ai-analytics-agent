# Human-in-the-Loop Points

> Where a person, not the model or the code, makes or confirms a decision in this project, and where that point would sit if the workflow were used in a company.

The workflow automates query writing, execution and first-pass checking. It does not automate deciding what the business means, deciding whether an answer is right, or acting on a flagged result. Those stay with a person.

| Point | What the person does | In this project | In a production setting |
| --- | --- | --- | --- |
| Business definitions | Writes and approves metric definitions, populations and field meanings | Analyst-authored `03-olist-business-semantics.md` and `02-tables-model-context.md`; changes only through logged, development-driven edits | Metric owners approve the semantic layer; changes go through review like code |
| Reference answers | Writes and verifies reference SQL and expected results | Every benchmark answer verified in DuckDB by the analyst before the freeze | Not applicable per question; replaced by monitoring and spot checks |
| Clarification | Answers the model's clarifying question | The benchmark is single-turn: a clarifying question is the final output and is graded as such | The stakeholder chooses the definition; the answer is computed only after that choice |
| Flagged results | Reviews answers carrying a Version C warning (join fan-out, duplicate entity, failed repair) | Warnings are logged per query and visible in the trace for grading | Answers with unresolved warnings are routed to an analyst instead of being sent directly |
| Grading | Gives the final grade on behaviour, result and assumption disclosure | Code comparison first, then human review; no LLM-as-a-judge in headline numbers | Periodic human audit of a sample of answers |
| Change control and freeze | Decides which rule changes are general, and when the system is frozen | Change log under methodology §7; held-out run blocked by code until a `system-frozen` tag exists | Release approval before a new prompt or rule set goes live |

The common principle is that the model may propose an interpretation, but it never silently settles a business definition, and a result that the program has flagged is never presented as final without a person seeing it.

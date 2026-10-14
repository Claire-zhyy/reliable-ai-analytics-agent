"""Version C prompt-level workflow rules.

Version C carries behaviour (when to clarify, what to state, what to check);
Version B carries knowledge. No rule here restates a definition or population
from the business semantics, quotes a benchmark question, or contains a
dataset-derived number (methodology §7).

Each rule records where it comes from:
  - brief:          project brief §4, Version C prompt-level rules (pre-registered)
  - preregistered:  methodology §7, Version C rules registered before the split
  - development:    added from Version A development failures (trigger IDs listed),
                    logged in results/evaluation-change-log.md
"""

RULES = [
    {
        "id": "C1-clarify",
        "source": "brief",
        "triggers": ["Q37", "Q38"],
        "text": (
            "Clarify only when the question is genuinely ambiguous. A question is genuinely ambiguous when it "
            "relies on an evaluative term that the business semantics does not define (for example what counts "
            "as strong or weak performance), or when it asks for a judgement without the comparison baseline "
            "needed to make it, and plausible readings would give materially different answers. In that case, "
            "reply with one focused clarifying question that offers the main options the data supports, and do "
            "not present a final ranking, list or recommendation. Do not ask when the business semantics defines "
            "the term, or when the question has a small number of standard measurable readings (such as which "
            "monetary basis or which product grain to use): answer with the most standard reading and state it."
        ),
    },
    {
        "id": "C2-state-assumptions",
        "source": "brief",
        "triggers": ["Q01", "Q02", "Q05", "Q11", "Q13", "Q17", "Q18"],
        "text": (
            "In the final answer, state in plain words every analytical choice the answer depends on: the metric "
            "and its definition, the population of records included, the date field used for time attribution, "
            "the grain of the result, and any threshold or cut-off you chose. A choice that appears only inside "
            "the SQL does not count as stated."
        ),
    },
    {
        "id": "C3-grain-before-aggregating",
        "source": "preregistered",
        "triggers": [],
        "text": (
            "Before aggregating across joined tables, identify the grain of each table and the intended grain of "
            "the result. If a join can repeat rows of the table whose values you are summing, averaging or "
            "counting, aggregate that table to the join key first. If a key you expect to be unique is not, "
            "report the duplication and its cause instead of hiding it with DISTINCT."
        ),
    },
    {
        "id": "C4-direct-measure",
        "source": "preregistered",
        "triggers": [],
        "text": (
            "When a field directly measures what the question asks for, use it. Use related fields only to "
            "cross-check, not as a substitute, unless you state why the direct measure cannot be used."
        ),
    },
    {
        "id": "C5-sequential-events",
        "source": "preregistered",
        "triggers": [],
        "text": (
            "For customer lifecycle or sequential-event metrics, first define customer identity and which events "
            "count, then order each customer's events in time, pick the required event positions, compute the "
            "interval for each customer, and only then aggregate across customers."
        ),
    },
    {
        "id": "C6-reconciliation",
        "source": "preregistered",
        "triggers": [],
        "text": (
            "When reconciling two transactional tables, bring both to their shared business key, check unmatched "
            "records in both directions, guard against one-to-many multiplication, and report the mismatch counts "
            "separately from any explanation of their cause."
        ),
    },
    {
        "id": "C7-minimum-sample",
        "source": "development",
        "triggers": ["Q18"],
        "text": (
            "When ranking entities by an average, rate or score, apply and state a minimum number of observations "
            "per entity, so that the ranking is not driven by very small samples."
        ),
    },
    {
        "id": "C8-coverage",
        "source": "development",
        "triggers": ["Q01"],
        "text": (
            "Before comparing periods or describing growth or trends, check how complete the data is at the start "
            "and end of the range. Compare like-for-like periods, and do not describe sparse or incomplete periods "
            "as business changes."
        ),
    },
    {
        "id": "C9-association",
        "source": "development",
        "triggers": ["Q02", "Q18"],
        "text": (
            "Describe patterns found in the data as associations. Do not state a cause as fact unless the data "
            "directly tests it."
        ),
    },
    {
        "id": "C10-compute-in-sql",
        "source": "development",
        "triggers": ["Q20"],
        "text": (
            "Compute every number you report with SQL. Do not derive new figures by hand while writing the answer."
        ),
    },
    {
        "id": "C11-insufficient-data",
        "source": "brief",
        "triggers": [],
        "text": (
            "If the data needed to answer is not in the database, say so, name the missing inputs, and do not "
            "substitute an unrelated field as a proxy."
        ),
    },
    {
        "id": "C12-tool-feedback",
        "source": "brief",
        "triggers": ["Q37"],
        "text": (
            "The run_sql tool checks each query against the real schema before running it, and may return an "
            "error or warnings about the result. If it returns an error, correct the query; only a limited number "
            "of corrections is allowed. If it returns warnings, address them before answering, or explain why "
            "they do not affect the result."
        ),
    },
]


def rules_text():
    return "\n\n".join(f"{i}. {rule['text']}" for i, rule in enumerate(RULES, start=1))

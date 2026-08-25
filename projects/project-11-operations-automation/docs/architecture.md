# System Architecture

Project 11 is designed around a simple rule: automate repeatable checks, but keep uncertain business decisions visible to a person.

```text
CSV / Excel sources
        |
        v
Batch intake + source tagging
        |
        v
Schema checks + normalization
        |
        v
Validation + exact deduplication
        |
        +----------------------+
        |                      |
        v                      v
Quality scoring          Audit change log
        |
        v
Fuzzy reconciliation / master matching
        |
        +-------------------------------+
        |                               |
        v                               v
Safe records                        Review queue
        |                               |
        +---------------+---------------+
                        v
                 Master data output
                        |
            +-----------+-----------+
            |                       |
            v                       v
       QA report              Dashboard metrics
            |                       |
            +-----------+-----------+
                        v
                    Run history
```

## Why it is split this way

The intake layer handles file differences. The validation layer handles objective rules. Quality scoring makes incomplete or suspicious records measurable. Reconciliation looks for records that may represent the same entity without silently merging them. The review queue is intentionally separate because a close name match is not the same thing as proof.

## Human decision points

The system can safely normalize whitespace, casing, status labels, dates, and exact duplicate IDs. It can also surface likely entity matches. It does not automatically merge fuzzy matches, overwrite ambiguous master records, or delete incomplete records simply because they are inconvenient.

That boundary is deliberate. In operations work, a small amount of human review is often safer than an aggressive automation rule that quietly damages data.

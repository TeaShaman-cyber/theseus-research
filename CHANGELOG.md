# Theseus Contract Changelog

Each accepted change records: **version, date, summary, reason, review status, level** — as promised in "Knowledge as code" (README.md). A change that is not recorded here has not been accepted.

## Review status: state model

Every entry carries exactly one of three states:

- **`draft / proposed`** — published for public review; not yet binding.
- **`accepted`** — accepted by the named program maintainer through merge (see "Acceptance authority" in README.md) and recorded here as an accepted change.
- **`superseded`** — replaced by a later version; kept for history and provenance.

A version moves `draft / proposed` → `accepted` only by maintainer merge, and `accepted` → `superseded` only when the next version is accepted.

## 0.3-draft — 2026-08-13

- **Summary:** incorporated the accepted CISO / Zero-Trust / OWASP review directions into the program contract and methodology, including technical interchangeability, bounded external action, contract/methodology authority, non-commercial public-interest status, stronger version compatibility, and experimental-tool boundaries.
- **Reason:** apply the dispositions recorded in issue #1 and make the public contract clearer and safer without weakening existing invariants.
- **Review status:** `accepted` — merged by the named maintainer after public review; the `-draft` label means the text remains open to later reviewed revision, not that this merged revision lacks repository acceptance.
- **Level:** MINOR — compatible clarification and strengthening; no existing invariant was removed or weakened.

## 0.2-draft — 2026-08

- **Summary:** added the "Methodological foundation" section to the contract and published the explanatory companion [docs/methodology.md](docs/methodology.md) (human-agent engineering, Sadhana of Engineering).
- **Reason:** first public review round requested methodological grounding for the contract's invariants.
- **Review status:** `superseded` — replaced by 0.3-draft.
- **Level:** MINOR (compatible clarification; mission, invariants, and non-goals unchanged).

## 0.1-draft

- **Summary:** initial publication of the Theseus program contract: mission, core invariants, non-goals, versioning rules, current boundary.
- **Reason:** move the program from private practice to a reviewable public artifact.
- **Review status:** `superseded` — replaced by 0.2-draft.
- **Level:** initial version.

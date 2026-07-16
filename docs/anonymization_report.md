# Anonymization report

## Scope and method

The original notebook was read non-destructively. All code, markdown, outputs, cell metadata, and notebook metadata were inspected. Code was parsed and re-rendered so comments were removed; potentially identifying non-technical string literals were replaced consistently. Persisted outputs and execution counts were removed. Metadata was reduced to a neutral Python kernel declaration.

The confidential original-to-alias mapping is stored only in the operating-system temporary directory outside this project. It is not included in the repository.

## Areas inspected

- Code cells: 12
- Markdown cells: 3
- Persisted outputs: 14
- Cell metadata and notebook metadata: inspected and minimized
- Python/SQL text, comments, docstrings, parameters, paths, identifiers, chart labels, displayed data, and serialized output text: included in the scan policy

## Replacement counts

Counts below are replacement occurrences, not unique original values.

- Filesystem paths: 7
- Usernames and emails: 0
- Hosts and urls: 0
- Credential references: 0
- Business labels and messages: 20
- Named entities and identifiers: 68
- Internal identifiers: 11
- Markdown cells neutralized: 3
- Notebook outputs removed: 14

## Output and metadata cleaning

All persisted notebook outputs were removed, including displayed tables, stream output, and any chart or path text stored there. Execution counts were cleared. Cell metadata was cleared, and notebook metadata was replaced with a minimal neutral kernel description.

## Unresolved confidentiality risks

The required second scan passed again after portfolio preparation. It checked 39 private original-to-alias pairs across 48 generated text artifacts, decoded notebook fields, credential/email/private-key patterns, outputs, execution state, and cell metadata. Results were zero residual locations, zero outputs, zero execution counts, and zero cell-metadata entries. The scan excluded the original confidential inputs, ignored reference checkout, local environments, build outputs, and Databricks deployment state. No unresolved candidate locations were found.

Automated anonymization cannot provide an absolute guarantee that an arbitrary ordinary lowercase word is non-sensitive. Comments and original markdown were neutralized, outputs were removed, metadata was minimized, and non-technical identifiers, labels, and matching variable-name tokens were consistently aliased to reduce this residual risk. The original notebook must remain access-controlled and must not be committed.

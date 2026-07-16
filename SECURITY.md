# Security and confidentiality

## Reporting

Do not open a public issue containing credentials, client data, source records, internal identifiers, or original-to-anonymized mappings. Use GitHub's private vulnerability reporting for this repository, or contact the repository owner privately.

## Credential policy

- Authenticate to Databricks and GitHub through OAuth or workload identity.
- Never commit personal access tokens, `.env` files, private keys, CLI profiles, or deployment-state directories.
- Revoke any credential immediately if it appears in chat, logs, screenshots, commits, or issue content.

## Data policy

Only synthetic or explicitly approved anonymized data belongs in tests and demonstrations. Original notebooks, workbooks, production outputs, and the private alias mapping must remain outside version control.

## Supported versions

Security fixes are applied to the latest `main` branch. The project is currently pre-1.0 and does not maintain older release branches.

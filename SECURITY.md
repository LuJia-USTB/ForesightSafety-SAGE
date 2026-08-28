# Security policy

## Credentials

Do not commit API keys, access tokens, cookies, private endpoints, or credential files. Store credentials in local environment variables and reference their variable names with `api_key_env` in YAML configuration files.

The repository ignores `.env`, credential-like files, runtime outputs, logs, and generated backups. `.gitignore` is not a security boundary: always run `python scripts/check_release.py` and inspect staged changes before pushing.

If a credential is ever committed, deleting it from the current file is insufficient because it remains in Git history. Revoke or rotate it immediately, remove it from all published history, and create a clean history before making the repository public.

## Simulated tools

Released tool implementations are simulations. They update in-memory evaluation state and return synthetic observations. They must not contain network calls, shell execution, real credentials, destructive filesystem operations, or integrations with production systems.

## Reporting

Please report suspected credential exposure or a security issue privately to the repository maintainers rather than opening a public issue containing sensitive details.

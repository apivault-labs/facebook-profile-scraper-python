# Contributing

Thanks for your interest in improving this SDK.

## Reporting bugs

Open a [GitHub issue](https://github.com/apivault-labs/facebook-profile-scraper-python/issues)
with:
- Python version (`python --version`)
- SDK version (`pip show facebook-profile-scraper`)
- The Facebook URL that triggered the issue
- The full traceback or unexpected output
- A minimal reproducer

## Suggesting features

Two flavors:
- **Client-side improvements** (better error messages, async client, helpers, retries) — open an issue here
- **New extracted fields or scoring tweaks** — those live in the underlying
  Apify actor; open an issue and we'll discuss where it fits

## Development setup

```bash
git clone https://github.com/apivault-labs/facebook-profile-scraper-python.git
cd facebook-profile-scraper-python
python -m venv .venv
. .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e .
```

## Pull requests

- Keep changes focused — one PR per feature/bugfix
- Add a line to `CHANGELOG.md` under `[Unreleased]`
- Match the existing code style (PEP 8, type hints, no unnecessary abstractions)

## License

By contributing you agree that your code will be released under the MIT license.

# mdlex

A utility for managing markdown documents with YAML frontmatter in SQLite.

## Installation

```bash
pip install git+https://github.com/luebken/mdlex.git
```

## Usage

### Loading Documents

```bash
mdlex load /path/to/markdown/files
```

### Querying Documents

```bash
mdlex query "SELECT * FROM documents WHERE json_extract(frontmatter, '$.tags') LIKE '%python%'"
```

### Environment Variables

- `MDLEX_DB_PATH`: Set the default database path

## Development

```sh
python -m venv venv
source venv/bin/activate
pip install -e .
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
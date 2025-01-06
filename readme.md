# mdlex

A utility for managing markdown documents with YAML frontmatter in SQLite.

## Installation

```bash
pip install git+https://github.com/luebken/mdlex.git
```

## Usage

### Loading Documents

```bash
mdlex load sample/
```

### Querying Documents

```bash
mdlex query "SELECT json_extract(frontmatter, '$.episode') as episode, COUNT(*) as count FROM documents GROUP BY episode"
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
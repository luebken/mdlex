# mdlex

A utility for managing markdown documents with YAML frontmatter in SQLite.

## Why?

A simple markdown / yaml based document tool that can be used on the command line to use with other tools like [llm](https://llm.datasette.io). 

Example:
```sh
$ mdlex query "SELECT title, content FROM documents WHERE tags LIKE '%Picard%'" | llm -s "Briefly list the key themes."
Key Themes:
1. Exploration and Discovery
2. Humans vs. Higher Powers
3. Reality vs. Fiction
4. Diplomacy and Responsibility
5. Teamwork and Problem-Solving
6. Dependence on Technology
```

## Installation

```bash
pip install git+https://github.com/luebken/mdlex.git
```

## Usage

### Loading Documents

The markdown documents need to have consistent schema. Currently `mdlex` only supports one schema.

```bash
mdlex load sample/
```

### Querying Documents

```bash
# Query schema aware view
mdlex query "SELECT episode, COUNT(*) as count FROM documents GROUP BY episode"
# Query raw documents
mdlex query "SELECT json_extract(frontmatter, '$.episode') as episode, COUNT(*) as count FROM documents_raw GROUP BY episode"

# By Date
mdlex query "SELECT date, filepath, title FROM documents ORDER BY date DESC NULLS LAST"
# All Tags
mdlex query "SELECT json_each.value as tag, COUNT(*) as count FROM documents, json_each(tags) GROUP BY json_each.value ORDER BY count DESC"
# Tag
mdlex query "SELECT title, content FROM documents WHERE tags LIKE '%Picard%'"
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
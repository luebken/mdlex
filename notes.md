# Example usage:

```sh
export MDLEX_DB_PATH=mdlex.db
python mdlex.py load /Users/mdl/Library/Mobile\ Documents/com~apple~CloudDocs/workspace2/zweitgeist-multicloud
python mdlex.py query "SELECT json_extract(frontmatter, '$.doctype') as doctype, COUNT(*) as count FROM documents GROUP BY doctype ORDER BY count DESC"
```
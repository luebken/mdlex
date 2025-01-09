# Prints all relevant python files in the src directory
catdevfiles:
	find src/ -type d -name '__pycache__' -prune -o -type f -name '*.py' -print -exec cat {} \; -exec echo '\n---\n' \;

# Usees https://llm.datasette.io/
llm-review:
	$(MAKE) catdevfiles | llm -s review
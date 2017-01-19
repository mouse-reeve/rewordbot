# Re-Word Bot

Replace words in a piece of text with a synonym (via [Wordnik](wordnik.com)), and make some effort to retain the orginal formatting.

Examples:

Convert text:
```bash
$ python synonymizer.py -t 'The thesaurus makes you sound smarter'

The synonymicon mate you healthy smarter
```

Show the tokenization and part of speech tagging:
```bash
$ python synonymizer.py -t 'The thesaurus makes you sound smarter' --show_tokens=true

[('The', 'DT'), ('thesaurus', 'NN'), ('makes', 'VBZ'), ('you', 'PRP'), ('sound', 'VBP'), ('smarter', 'NN')]
The thesaurus cause you healthy smarter
```

Load a text file:
```bash
$ python synonymizer.py -f file-to-convert.txt
```

Use as a python class:
```python
from synonymizer import Reword
print Reword().reword('The thesaurus makes you sound smarter')
# u'The synonymicon cause you strong smarter'
```

# misc version

## description

seriously, are you a master of webshell?  
rules: you should build a **python script** that takes a randomly generated **lowercase** string and **outputs** a php script. the php script should:

1. output the given string
2. bypass the waf rule described in the following code:

```python
def waf(phpshell):
    if not phpshell.startswith(b'<?php'):
        return False
    phpshell = phpshell[6:]
    for c in phpshell:
        if c not in b'0-9$_;+[].<?=>':
            return False # wafed
    return True # not wafed
```

most importantly, the generated shell SHALL NOT be longer than a competing algorithm for the same goal.  
the initial algorithm is kept in secret. (can be found in gen.py)

```bash
echo -n {random_str()} |
    python3 /your_script.py |
    waf |
    php
```

the result of the command above should be exactly the same as the generated random_str

## deployment

needless to use rootless docker now, `docker-compose up -d` will do.

target = input()


def get():
    q = []
    for c in '09_':
        q.append(c)
    while True:
        base = q.pop(0)
        yield base
        for c in '09_':
            q.append(base + c)


freq = {}
gen = get()

for c in target:
    freq[c] = freq.get(c, 0) + 1
freq = list(freq.items())
freq.sort(key=lambda x: x[1], reverse=True)
varname = {i: next(gen) for i in range(len(freq))}
hash_char = {freq[i][0]: varname[i] for i in range(len(freq))}

print('<?php')
print('$_=[].[];$_=$_[0.9+0.9+0.9+0.9];', end='')

for c in range(ord('a'), ord(max(target)) + 1):
    if chr(c) in target:
        print(f'$_{hash_char[chr(c)]}=$_;', end='')
    print('$_++;', end='')

print(f'$_=$_{hash_char[target[0]]};', end='')
for c in target[1:]:
    print(f'$_.=$_{hash_char[c]};', end='')
print('?><?=$_;')

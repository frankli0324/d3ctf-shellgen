from bisect import bisect
print('<?php')
target = input()
original = target


def subsequence(seq, key=None):
    rank = seq
    if not rank:
        return []

    lastoflength = [0]
    predecessor = [None]

    for i in range(1, len(seq)):
        j = bisect([rank[k] for k in lastoflength], rank[i])
        try:
            lastoflength[j] = i
        except:
            lastoflength.append(i)
        predecessor.append(lastoflength[j - 1] if j > 0 else None)

    def trace(i):
        if i is not None:
            yield from trace(predecessor[i])
            yield i
    indices = trace(lastoflength[-1])

    return list(indices)


lists = []
while target:
    M = subsequence(target)
    res = ''
    for i in M:
        res += target[i]
    lists.append(res)
    while M:
        pos = M.pop()
        target = target[:pos] + target[pos + 1:]

varnames = ['$' + '_' * i for i in range(len(lists))]
state = [0] * len(lists)
print('$_="";$__=([]."")[3];', end='')
for i in range(1, len(lists)):
    print(f'$__{"_" * i}=$__;', end='')
for c in original:
    for i in range(0, len(lists)):
        if len(lists[i]) > state[i] and lists[i][state[i]] == c:
            lst = lists[i][state[i] - 1] if state[i] else 'a'
            cnt = ord(lists[i][state[i]]) - ord(lst)
            print(f'$__{"_" * i}++;' * cnt, end='')
            print(f'$_.=$__{"_" * i};', end='')
            state[i] += 1
            break
print('?><?=$_;')

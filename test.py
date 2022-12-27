##def grouper(iterable):
##    prev = None
##    group = []
##    flag = 0
##    for item in iterable:
##        if prev is None or item - prev <= 14:
##                if flag == 0:
##                        start_index = item
##                        flag = 1
##                if item - start_index <= 14:
##                        flag = 0
##                group.append(item)
##        else:
##            yield group
##            group = [item]
##        prev = item
##    if group:
##        yield group

def grouper(iterable):
        cluster = []
        group = []
        head = iterable[0]
        for i in range(len(iterable)-1):
                if iterable[i] - head <= 15:
                        group.append(iterable[i])
                else:
                        cluster.append(group)
                        group = []
                        head = iterable[i]
        print(cluster)

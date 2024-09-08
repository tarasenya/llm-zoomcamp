def mrr(relevance_total):
    total_score = 0
    for line in relevance_total:
        for rank in range(len(line)):
            if line[rank] is True:
                total_score += 1 / (rank + 1)
    return total_score / len(relevance_total)

def hit_rate(relevance_total):
    cnt = 0
    for line in relevance_total:
        if True in line:
                cnt += 1
    return cnt / len(relevance_total)
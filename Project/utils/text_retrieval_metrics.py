def mrr(relevance_total: list)-> float:
    """
    Calculate the Mean Reciprocal Rank (MRR) for a list of relevance judgments.
    :param relevance_total: A list of lists, where each inner list represents a query's
    relevance judgments. Each judgment is a boolean value
    indicating whether the item at that rank is relevant (True)
    or not (False).
    :type relevance_total: list
    :return: The Mean Reciprocal Rank score.
    :rtype: float
    """
    total_score = 0
    for line in relevance_total:
        for rank in range(len(line)):
            if line[rank] is True:
                total_score += 1 / (rank + 1)
    return total_score / len(relevance_total)

def hit_rate(relevance_total: list) -> float:
    """
    Calculate the Hit Rate for a list of relevance judgments.
    :param relevance_total: List of relevance judgments per query.
    :type relevance_total: list
    :return: Hit Rate score.
    :rtype: float
    """
    cnt = 0
    for line in relevance_total:
        if True in line:
                cnt += 1
    return cnt / len(relevance_total)
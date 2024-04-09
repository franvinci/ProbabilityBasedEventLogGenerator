from Levenshtein import ratio

def get_more_similar_prefix(p, prefixes):

    max_similarity = 0
    similar_prefix = None

    for cur_pref in prefixes:
        similarity = ratio(p, cur_pref)
        if similarity > max_similarity:
            similar_prefix = cur_pref
    
    return similar_prefix
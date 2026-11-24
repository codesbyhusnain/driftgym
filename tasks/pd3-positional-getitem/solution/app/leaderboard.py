def _ranked(scores):
    return scores.sort_values(ascending=False)


def leader(scores):
    ranked = _ranked(scores)
    return ranked.index[0], ranked.iloc[0]


def last_place(scores):
    ranked = _ranked(scores)
    return ranked.index[-1], ranked.iloc[-1]


def gap_to_leader(scores, player):
    ranked = _ranked(scores)
    return ranked.iloc[0] - ranked.loc[player]

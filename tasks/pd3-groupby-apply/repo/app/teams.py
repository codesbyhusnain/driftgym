def top_per_team(players, n=1):
    top = players.groupby("team").apply(lambda g: g.nlargest(n, "points"))
    return top.reset_index(drop=True)


def team_shares(players):
    shares = players.groupby("team").apply(
        lambda g: g.assign(share=(g["points"] / g["points"].sum()).round(3))
    )
    return shares.reset_index(drop=True)

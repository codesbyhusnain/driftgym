def top_per_team(players, n=1):
    ranked = players.sort_values(["team", "points"], ascending=[True, False])
    return ranked.groupby("team").head(n).reset_index(drop=True)


def team_shares(players):
    totals = players.groupby("team")["points"].transform("sum")
    shares = players.assign(share=(players["points"] / totals).round(3))
    return shares.sort_values("team", kind="stable").reset_index(drop=True)

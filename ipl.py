import pandas as pd
import numpy as np

ipl_matches = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRy2DUdUbaKx_Co9F0FSnIlyS-8kp4aKv_I0-qzNeghiZHAI_hw94gKG22XTxNJHMFnFVKsO4xWOdIs/pub?gid=1655759976&single=true&output=csv"
matches = pd.read_csv(ipl_matches)

ipl_ball = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRu6cb6Pj8C9elJc5ubswjVTObommsITlNsFy5X0EiBY7S-lsHEUqx3g_M16r50Ytjc0XQCdGDyzE_Y/pub?output=csv"
balls = pd.read_csv(ipl_ball)

ball_withmatch = balls.merge(matches, on='ID', how='inner').copy()
ball_withmatch['BowlingTeam'] = ball_withmatch.Team1 + ball_withmatch.Team2
ball_withmatch['BowlingTeam'] = ball_withmatch[['BowlingTeam', 'BattingTeam']].apply(lambda x: x.values[0].replace(x.values[1], ''), axis=1)
batter_data = ball_withmatch[np.append(balls.columns.values, ['BowlingTeam', 'Player_of_Match'])]  

def allTeamsAPI():
    teams = list(set(list(matches['Team1']) + list(matches['Team2'])))
    team_dict = {
        'teams':teams
    }
    return team_dict
def batterListAPI():
    batter = sorted(list(batter_data['batter'].value_counts().index))
    batter_dict = {
        'batters' : batter
    }
    return batter_dict

def bowlerListAPI():
    bowler = sorted(list(batter_data['bowler'].value_counts().index))
    bowler_dict = {
        'bowler' : bowler
    }
    return bowler_dict
def teamVSteamAPI(team1, team2): # when user wants to see the data between only 2 teams
    temp_df = matches[((matches['Team1'] == team1) & (matches['Team2'] == team2)) | ((matches['Team2'] == team1) & (matches['Team1'] == team2))]
    matches_played = temp_df.shape[0]
    matches_won_team1 = temp_df[temp_df.WinningTeam == team1].shape[0]
    matches_won_team2 = temp_df[temp_df.WinningTeam == team2].shape[0]
    noResult = temp_df['WinningTeam'].isnull().sum()

    response = {
        'total_matches' : str(matches_played),
        team1 : str(matches_won_team1),
        team2 : str(matches_won_team2),
        'No Result' : str(noResult)
    }

    return response
def team1vsteam2(team, team2): # while comparing team with another team
    df = matches[((matches['Team1'] == team) & (matches['Team2'] == team2)) | ((matches['Team2'] == team) & (matches['Team1'] == team2))].copy()
    mp = df.shape[0]
    won = df[df.WinningTeam == team].shape[0]
    nr = df[df.WinningTeam.isnull()].shape[0]
    loss = mp - won - nr

    return {'matchesplayed': mp,
            'won': won,
            'loss': loss,
            'noResult': nr}


def allRecord(team):
    df = matches[(matches['Team1'] == team) | (matches['Team2'] == team)].copy()
    mp = df.shape[0]
    won = df[df.WinningTeam == team].shape[0]
    nr = df[df.WinningTeam.isnull()].shape[0]
    loss = mp - won - nr
    nt = df[(df.MatchNumber == 'Final') & (df.WinningTeam == team)].shape[0]
    return {'matchesplayed': mp,
            'won': won,
            'loss': loss,
            'noResult': nr,
            'title': nt}


def teamAPI(team, matches=matches):
    df = matches[(matches['Team1'] == team) | (matches['Team2'] == team)].copy()
    self_record = allRecord(team)
    TEAMS = matches.Team1.unique()
    against = {team2: team1vsteam2(team, team2) for team2 in TEAMS}
    data = {team: {'Overall': self_record,
                   'against': against}}
    return data


def batsmanRecord(batsman, df):
    if df.empty:
        return np.nan
    out = df[df.player_out == batsman].shape[0]
    df = df[df['batter'] == batsman]
    inngs = df.ID.unique().shape[0]
    runs = df.batsman_run.sum()
    fours = df[(df.batsman_run == 4) & (df.non_boundary == 0)].shape[0]
    sixes = df[(df.batsman_run == 6) & (df.non_boundary == 0)].shape[0]
    if out:
        avg = (runs / out).round(2)
    else:
        avg = np.inf

    nballs = df[~(df.extra_type == 'wides')].shape[0]
    if nballs:
        strike_rate = (runs / nballs * 100).round(2)
    else:
        strike_rate = 0
    gb = df.groupby('ID').sum()
    fifties = gb[(gb.batsman_run >= 50) & (gb.batsman_run < 100)].shape[0]
    hundreds = gb[gb.batsman_run >= 100].shape[0]
    try:
        highest_score = gb.batsman_run.sort_values(ascending=False).head(1).values[0]
        hsindex = gb.batsman_run.sort_values(ascending=False).head(1).index[0]
        if (df[df.ID == hsindex].player_out == batsman).any():
            highest_score = str(highest_score)
        else:
            highest_score = str(highest_score) + '*'
    except:
        highest_score = gb.batsman_run.max()

    not_out = inngs - out
    mom = df[df.Player_of_Match == batsman].drop_duplicates('ID', keep='first').shape[0]
    data = {
        'innings': str(inngs),
        'runs': str(runs),
        'fours': str(fours),
        'sixes': str(sixes),
        'avg': str(avg),
        'strikeRate': str(strike_rate),
        'fifties': str(fifties),
        'hundreds': str(hundreds),
        'highestScore': str(highest_score),
        'notOut': str(not_out),
        'mom': str(mom)
    }

    return data


def batsmanVsTeam(batsman, team, df):
    df = df[df.BowlingTeam == team].copy()
    return batsmanRecord(batsman, df)


def batsmanAPI(batsman, balls=batter_data):
    df = balls[balls.innings.isin([1, 2])]  # Excluding Super overs
    self_record = batsmanRecord(batsman, df=df)
    TEAMS = matches.Team1.unique()
    against = {team: batsmanVsTeam(batsman, team, df) for team in TEAMS}
    data = {
        batsman: {'All': self_record,
                  'against': against}
    }
    return data

bowler_data = batter_data.copy()

def bowlerRun(x):
    if x[0] in ['penalty', 'legbyes', 'byes']:
        return 0
    else:
        return x[1]
bowler_data['bowler_run'] = bowler_data[['extra_type', 'total_run']].apply(bowlerRun, axis=1)

def bowlerWicket(x):
    if x[0] in ['caught', 'caught and bowled', 'bowled', 'stumped', 'lbw', 'hit wicket']:
        return x[1]
    else:
        return 0
bowler_data['isBowlerWicket'] = bowler_data[['kind', 'isWicketDelivery']].apply(bowlerWicket, axis=1)


def bowlerRecord(bowler, df):
    #if df.empty:
        #return np.nan

    df = df[df['bowler'] == bowler]
    inngs = df.ID.unique().shape[0]
    nballs = df[~(df.extra_type.isin(['wides', 'noballs']))].shape[0]
    runs = df['bowler_run'].sum()
    if nballs:
        eco = (runs / nballs * 6).round(2)
    else:
        eco = 0
    fours = df[(df.batsman_run == 4) & (df.non_boundary == 0)].shape[0]
    sixes = df[(df.batsman_run == 6) & (df.non_boundary == 0)].shape[0]

    wicket = df.isBowlerWicket.sum()
    if wicket:
        avg = (runs / wicket).round(2)
    else:
        avg = np.inf

    if wicket:
        strike_rate = (nballs / wicket).round(2)
    else:
        strike_rate = np.nan

    gb = df.groupby('ID').sum()
    w3 = gb[(gb.isBowlerWicket >= 3)].shape[0]

    best_wicket = gb.sort_values(['isBowlerWicket', 'bowler_run'], ascending=[False, True])[
        ['isBowlerWicket', 'bowler_run']].head(1).values
    if best_wicket.size > 0:

        best_figure = f'{best_wicket[0][0]}/{best_wicket[0][1]}'
    else:
        best_figure = np.nan
    mom = df[df.Player_of_Match == bowler].drop_duplicates('ID', keep='first').shape[0]
    data = {
        'innings': str(inngs),
        'wicket': str(wicket),
        'economy': str(eco),
        'avg': str(avg),
        'strikeRate': str(strike_rate),
        'fours': str(fours),
        'sixes': str(sixes),
        'best_figure': str(best_figure),
        '3+W': str(w3),
        'mom': str(mom)
    }

    return data


def bowlerVsTeam(bowler, team, df):
    df = df[df.BattingTeam == team].copy()
    return bowlerRecord(bowler, df)


def bowlerAPI(bowler, balls=bowler_data):
    df = balls[balls.innings.isin([1, 2])]  # Excluding Super overs
    self_record = bowlerRecord(bowler, df=df)
    TEAMS = matches.Team1.unique()
    against = {team: bowlerVsTeam(bowler, team, df) for team in TEAMS}
    data = {
        bowler: {'All': self_record,
                 'against': against}
    }
    return data
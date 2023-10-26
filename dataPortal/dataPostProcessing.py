from collections import defaultdict
from .models import Game, Teams, Player, PlayerEndGameStats, PlayerTimeData, Draft, Drakes, Heralds, Barons, FirstBlood, Plates, Towers
from django.db.models import Q, Count, Avg, ExpressionWrapper, F, FloatField, OuterRef, Subquery
from .forms import CommonDataSearchForm

def teamDataSearch(form:CommonDataSearchForm):
    patch = form.cleaned_data['patch']
    competition = form.cleaned_data['competition']
    team = form.cleaned_data['team']
    role = form.cleaned_data['role']
    player = form.cleaned_data['player']

    matches = Game.objects.all()

    if patch:
        matches = matches.filter(patch=patch)
    if competition:
        matches = matches.filter(competition__contains=competition)
    if team:
        matches = matches.filter(Q(teamB=team) | Q(teamR=team))
    if player:
        matches = matches.filter(Q(topB=player) | Q(jglB=player) | Q(midB=player) | Q(botB=player) | Q(supB=player) |
                                 Q(topR=player) | Q(jglR=player) | Q(midR=player) | Q(botR=player) | Q(supR=player))

    gameIDs = []
    for game in matches:
        gameIDs.append(game.gameID)

    draftData = getDraftData(gameIDs)
    endData = getEndGameDataStats(gameIDs)
    timeStampData = getTeamTimestampData(gameIDs)
    drakeData = getTeamDrakeInfo(gameIDs)


def getDraftData(gameIDs:list):
    draft_stats = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int))))

    drafts = Draft.objects.filter(gameID__gameID__in=gameIDs)
    for draft in drafts:
        side = draft['side']
        team = draft['team']
        for i in range(1, 6):  # Itera su ban1, ban2, ban3, ban4, ban5
            champion = draft[f'ban{i}']
            draft_stats[side][team][f'ban{i}'][champion] += 1
        for i in range(1, 6):
            champion = draft[f'pick{i}']
            draft_stats[side][team][f'pick{i}'][champion] += 1
        for i in ['top', 'jgl', 'mid', 'bot', 'sup']:
            champion = draft[i]
            draft_stats[side][team][i][champion] += 1

    return draft_stats


def getEndGameDataStats(gameIDs: list):
    endGameStats = {}
    endgameAvgData = (
        PlayerEndGameStats.objects.filters(gameID__gameID__in=gameIDs).values('team__triCode', 'side', 'role',
                                                                      'player__summonerName')
        .annotate(
            avg_kills=Avg('kills'),
            avg_deaths=Avg('deaths'),
            avg_assists=Avg('assists'),
            avg_gold=Avg('gold'),
            avg_minions=Avg('minions'),
            avg_wardPlaced=Avg('wardPlaced'),
            avg_wardKilled=Avg('wardKilled'),
            avg_visionScore=Avg('visionScore'),
            avg_DMGtoChamps=Avg('DMGtoChamps'),
            avg_DMGtoTowers=Avg('DMGtoTowers'),
        )
    )

    endgameAvgData = endgameAvgData.annotate(
        KDA=ExpressionWrapper(
            (F('avg_kills') + F('avg_assists')) / F('avg_deaths'),
            output_field=FloatField()
        ),
        GPM=ExpressionWrapper(
            F('avg_gold') / (F('gameID__gameLength').total_seconds() / 60),
            output_field=FloatField()
        ),
        CSPM=ExpressionWrapper(
            F('avg_minions') / (F('gameID__gameLength').total_seconds() / 60),
            output_field=FloatField()
        ),
        VSPM=ExpressionWrapper(
            F('avg_visionScore') / (F('gameID__gameLength').total_seconds() / 60),
            output_field=FloatField()
        ),
        DPM=ExpressionWrapper(
            F('avg_DMGtoChamps') / (F('gameID__gameLength').total_seconds() / 60),
            output_field=FloatField()
        )
    )

    for stats in endgameAvgData:
        team = stats['team__triCode']
        side = stats['side']
        role = stats['role']
        player = stats['player__summonerName']

        if team not in endGameStats:
            endGameStats[team] = {}
        if side not in endGameStats[team]:
            endGameStats[team][side] = {}
        if role not in endGameStats[team][side]:
            endGameStats[team][side][role] = {}
        endGameStats[team][side][role][player] = {
            "KDA": stats['KDA'],
            "GPM": stats['GPM'],
            "CSPM": stats['CSPM'],
            "VSPM": stats['VSPM'],
            "DPM": stats['DPM'],
            "avg_kills": stats['avg_kills'],
            "avg_deaths": stats['avg_deaths'],
            "avg_assists": stats['avg_assists'],
            "avg_gold": stats['avg_gold'],
            "avg_minions": stats['avg_minions'],
            "avg_wardPlaced": stats['avg_wardPlaced'],
            "avg_wardKilled": stats['avg_wardKilled'],
            "avg_visionScore": stats['avg_visionScore'],
            "avg_DMGtoChamps": stats['avg_DMGtoChamps'],
            "avg_DMGtoTowers": stats['avg_DMGtoTowers'],
        }

    return endGameStats


def getTeamTimestampData(gameIDs:list):
    player_data = PlayerTimeData.objects.filter(gameID__gameID__in=gameIDs).values('side', 'team__triCode', 'role',
                                                                                'player__summonerName', 'champ', 'time')

    average_data = player_data.values('side', 'team__triCode', 'role', 'player__summonerName', 'champ', 'time').\
        annotate(
            avg_kills=Avg('kills'),
            avg_deaths=Avg('deaths'),
            avg_assists=Avg('assists'),
            avg_gold=Avg('gold'),
            avg_minions=Avg('minions'),
            avg_exp=Avg('exp')
        )
    timeStampData = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict())))))

    for entry in average_data:
        side = entry['side']
        team = entry['team__triCode']
        role = entry['role']
        player = entry['player__summonerName']
        champ = entry['champ']
        time = entry['time']

        timeStampData[side][team][role][player][champ][time] = {
            'avg_kills': entry['avg_kills'],
            'avg_deaths': entry['avg_deaths'],
            'avg_assists': entry['avg_assists'],
            'avg_gold': entry['avg_gold'],
            'avg_minions': entry['avg_minions'],
            'avg_exp': entry['avg_exp']
        }
    return timeStampData


def getTeamDrakeInfo(gameIDs:list):
    drakeData = {}

    drakeTypeCountData = Drakes.objects.filter(gameID__gameID__in=gameIDs).values('team__triCode', 'side', 'drakeType'). \
        annotate(count=Count('id'))
    avgTimeDrakeData = Drakes.objects.filter(gameID__gameID__in=gameIDs, first=True).values('team__triCode', 'side'). \
        annotate(avgFirst=Avg('time'))
    firstDrakeInfo = Drakes.objects.filter(gameID__gameID__in=gameIDs, first=True).values('team__triCode', 'side',
                                                                                          'drakeType').annotate(
        count=Count('id'))

    for drake in drakeTypeCountData:
        team = drake['team__triCode']
        side = drake['side']
        drake_type = drake['drakeType']
        count = drake['count']

        if team not in drakeData:
            drakeData[team] = {}
        if side not in drakeData[team]:
            drakeData[team][side] = {}
        drakeData[team][side][drake_type] = count;

    for avgTime in avgTimeDrakeData:
        team = avgTime['team__triCode']
        side = avgTime['side']
        avgFirst = avgTime['avgFirst']

        if team not in drakeData:
            drakeData[team] = {}
        if side not in drakeData[team]:
            drakeData[team][side] = {}
        drakeData[team][side]['firstDrake']['avgTime'] = avgFirst

    for drake in firstDrakeInfo:
        team = drake['team__triCode']
        side = drake['side']
        drake_type = drake['drakeType']
        count = drake['count']

        if team not in drakeData:
            drakeData[team] = {}
        if side not in drakeData[team]:
            drakeData[team][side] = {}
        drakeData[team][side]['firstDrake'][drake_type] = count

    return drakeData


def getTeamHeraldInfo(gameIDs:list):
    heraldData = {}

    heraldCount = Heralds.objects.filter(gameID__gameID__in=gameIDs).values('team__triCode', 'side').annotate(count=Count('id'))
    firstHeraldCount = Heralds.objects.filter(gameID__gameID__in=gameIDs, first=True).values('team__triCode', 'side')\
        .annotate(first_count=Count('id'))
    avgFirstHeraldTime = Heralds.objects.filter(gameID__gameID__in=gameIDs, first=True).values('team__triCode', 'side')\
        .annotate(avg_time=Avg('time'))
    for herald in heraldCount:
        team = herald['team__triCode']
        side = herald['side']
        count = herald['count']

        if team not in heraldData:
            heraldData[team] = {}
        if side not in heraldData[team]:
            heraldData[team][side] = {}
        heraldData[team][side]['heralds'] = count

    for first_herald in firstHeraldCount:
        team = first_herald['team__triCode']
        side = first_herald['side']
        first_count = first_herald['first_count']

        if team not in heraldData:
            heraldData[team] = {}
        if side not in heraldData[team]:
            heraldData[team][side] = {}
        heraldData[team][side]['firstHeralds'] = first_count

    for avg_time in avgFirstHeraldTime:
        team = avg_time['team__triCode']
        side = avg_time['side']
        avg_time_value = avg_time['avg_time']

        if team not in heraldData:
            heraldData[team] = {}
        if side not in heraldData[team]:
            heraldData[team][side] = {}
        heraldData[team][side]['avgTimeToFirstHerald'] = avg_time_value

    return heraldData


def getBaronInfo(gameIDs:list):
    baronData = {}
    baronCount = Barons.objects.filter(gameID__gameID__in=gameIDs).values('team__triCode', 'side').annotate(count=Count('id'))

    for baron in baronCount:
        team = baron['team__triCode']
        side = baron['side']
        count = baron['count']

        if team not in baronData:
            baronData[team] = {}
        if side not in baronData[team]:
            baronData[team][side] = count

    return baronData


def getTeamFirstBloodInfo(gameIDs:list):
    firstBloodData = {}
    for side in ["B", "R"]:
        querySetTot = FirstBlood.objects.filter(gameID__gameID__in=gameIDs, side=side).values('team__triCode').annotate(count=Count('gameID'))
        querySetTime = FirstBlood.objects.filter(gameID__gameID__in=gameIDs, side=side).values('team__triCode').annotate(avgTime=Avg('time'))
        for query1, query2 in zip(querySetTot, querySetTime):
            firstBloodData[query1.team__triCode][side] = {
                'firstBloodPercentage': (query1.count/gameIDs.count())*100,
                'avgTime': query2.avg,
            }

    return firstBloodData


def getTeamTowersInfo(gameIDs:list):
    turretData = {}
    for side in ["B", "R"]:
        for lane in ["top", "mid", "bot"]:
            querySetTot = Towers.objects.filter(gameID__gameID__in=gameIDs, side=side, lane=lane).values('team__triCode').annotate(count=Count('gameID'))
            for query in querySetTot:
                turretData[query.team__triCode][side][lane] = query.count

    return turretData


def getTeamPlatesInfo(gameIDs:list):
    platesData = {}

    for side in ["B", "R"]:
        for lane in ["top", "mid", "bot"]:
            querySetTot = Plates.objects.filter(gameID__gameID__in=gameIDs, side=side, lane=lane).values('team__triCode').annotate(count=Count('gameID'))
            for query in querySetTot:
                platesData[query.team__triCode][side][lane] = query.count

    return platesData


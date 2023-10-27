from django.db import models
from django.core.validators import MinValueValidator


class Teams(models.Model):
    triCode = models.CharField(max_length=16)
    models.JSONField(blank=True, null=True)

    class Meta:
        unique_together = (("triCode", "competition"),)


class Player(models.Model):
    summonerName = models.CharField(max_length=32)
    playerCode = models.CharField(max_length=80)
    role = models.CharField(max_length=16, choices=(("top", "toplaner"), ("jgl", "jungler"), ("mid", "midlaner"), ("bot", "botlaner"), ("sup", "support"),), blank=True)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("summonerName", "playerCode", "team"),)


class Game(models.Model):
    gameID = models.CharField(max_length=30, unique=True)
    competition = models.JSONField(blank=True, null=True)
    date = models.DateField()
    patch = models.CharField(max_length=8)
    gameLength = models.DurationField()
    winnerTeam = models.ForeignKey(Teams, on_delete=models.CASCADE)
    teamB = models.ForeignKey(Teams, on_delete=models.CASCADE)
    teamR = models.ForeignKey(Teams, on_delete=models.CASCADE)
    topB = models.ForeignKey(Player, on_delete=models.CASCADE)
    jglB = models.ForeignKey(Player, on_delete=models.CASCADE)
    midB = models.ForeignKey(Player, on_delete=models.CASCADE)
    botB = models.ForeignKey(Player, on_delete=models.CASCADE)
    supB = models.ForeignKey(Player, on_delete=models.CASCADE)
    topR = models.ForeignKey(Player, on_delete=models.CASCADE)
    jlgR = models.ForeignKey(Player, on_delete=models.CASCADE)
    midR = models.ForeignKey(Player, on_delete=models.CASCADE)
    botR = models.ForeignKey(Player, on_delete=models.CASCADE)
    supR = models.ForeignKey(Player, on_delete=models.CASCADE)

    def __str__(self):
        return "Match: " + self.teamB + " vs " + self.teamR


class PlayerEndGameStats(models.Model):
    gameID = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    role = models.CharField(max_length=16, choices=(("top", "toplaner"), ("jgl", "jungler"), ("mid", "midlaner"), ("bot", "botlaner"), ("sup", "support"),), blank=True)
    side = models.CharField(max_length=1, choices=(("B", "blue"), ("R", "red"),))
    kills = models.IntegerField(validators=[MinValueValidator(0)])
    deaths = models.IntegerField(validators=[MinValueValidator(0)])
    assists = models.IntegerField(validators=[MinValueValidator(0)])
    gold = models.FloatField()
    minions = models.IntegerField(validators=[MinValueValidator(0)])
    wardPlaced = models.IntegerField()
    wardKilled = models.IntegerField()
    visionScore = models.IntegerField()
    DMGtoChamps = models.FloatField()
    DMGtoTowers = models.FloatField()

    class Meta:
        unique_together = (("gameID", "player"),)


class Draft(models.Model):
    gameID = models.ForeignKey(Game, on_delete=models.CASCADE)
    side = models.CharField(max_length=1, choices=(("B", "blue"), ("R", "red"),))
    ban1 = models.CharField(max_length=24)
    ban2 = models.CharField(max_length=24)
    ban3 = models.CharField(max_length=24)
    ban4 = models.CharField(max_length=24)
    ban5 = models.CharField(max_length=24)
    pick1 = models.CharField(max_length=24)
    pick2 = models.CharField(max_length=24)
    pick3 = models.CharField(max_length=24)
    pick4 = models.CharField(max_length=24)
    pick5 = models.CharField(max_length=24)
    top = models.CharField(max_length=24)
    jgl = models.CharField(max_length=24)
    mid = models.CharField(max_length=24)
    bot = models.CharField(max_length=24)
    sup = models.CharField(max_length=24)

    class Meta:
        unique_together = (("gameID", "side"),)


class PlayerTimeData(models.Model):
    gameID = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    side = models.CharField(max_length=1, choices=(("B", "blue"), ("R", "red"),))
    role = models.CharField(max_length=16, choices=(("top", "toplaner"), ("jgl", "jungler"), ("mid", "midlaner"), ("bot", "botlaner"), ("sup", "support"),), blank=True)
    champ = models.CharField(max_length=24)
    time = models.IntegerField()
    kills = models.IntegerField(validators=[MinValueValidator(0)])
    deaths = models.IntegerField(validators=[MinValueValidator(0)])
    assists = models.IntegerField(validators=[MinValueValidator(0)])
    gold = models.FloatField()
    minions = models.IntegerField(validators=[MinValueValidator(0)])
    exp = models.FloatField()
    opponent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = (("gameID", "player", "time"),)


class Drakes(models.Model):
    gameID = models.ForeignKey(Game, on_delete=models.CASCADE)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    side = models.CharField(max_length=1, choices=(("B", "blue"), ("R", "red"),))
    drakeType = models.CharField(max_length=24)
    first = models.BooleanField()
    time = models.DurationField()


class Heralds(models.Model):
    gameID = models.ForeignKey(Game, on_delete=models.CASCADE)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    side = models.CharField(max_length=1, choices=(("B", "blue"), ("R", "red"),))
    first = models.BooleanField()
    time = models.DurationField()


class Barons(models.Model):
    gameID = models.ForeignKey(Game, on_delete=models.CASCADE)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    side = models.CharField(max_length=1, choices=(("B", "blue"), ("R", "red"),))
    time = models.DurationField()


class FirstBlood(models.Model):
    gameID = models.ForeignKey(Game, on_delete=models.CASCADE)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    side = models.CharField(max_length=1, choices=(("B", "blue"), ("R", "red"),))
    killer = models.ForeignKey(Player, on_delete=models.CASCADE)
    assistants = models.JSONField(blank=True, null=True)
    time = models.DurationField()


class Plates(models.Model):
    gameID = models.ForeignKey(Game, on_delete=models.CASCADE)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    side = models.CharField(max_length=1, choices=(("B", "blue"), ("R", "red"),))
    lane = models.CharField(max_length=16, choices=(('bot', 'botlane'), ('mid', 'midlane'), ('top', 'toplane'),))
    killer = models.ForeignKey(Player, on_delete=models.CASCADE)
    assistants = models.JSONField(blank=True, null=True)
    time = models.DurationField()


class Towers(models.Model):
    gameID = models.ForeignKey(Game, on_delete=models.CASCADE)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    side = models.CharField(max_length=1, choices=(("B", "blue"), ("R", "red"),))
    lane = models.CharField(max_length=16, choices=(('bot', 'botlane'), ('mid', 'midlane'), ('top', 'toplane'),))
    killer = models.ForeignKey(Player, on_delete=models.CASCADE)
    assistants = models.JSONField(blank=True, null=True)
    first = models.BooleanField()
    time = models.DurationField()


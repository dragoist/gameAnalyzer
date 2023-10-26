from django import forms
from .models import Game, Player, Teams


class CommonDataSearchForm(forms.Form):
    patch = forms.ModelChoiceField(queryset=Game.objects.values_list('patch', flat=True).distinct(), required=False)
    competition = forms.ModelChoiceField(queryset=Game.objects.values_list('competition', flat=True).distinct(), required=False)
    team = forms.ModelChoiceField(queryset=Teams.objects.values_list('triCode', flat=True).distinct(), required=False)
    role = forms.ChoiceField(choices=[
        ('any', 'Any'),
        ('top', 'Toplane'),
        ('jgl', 'Jungle'),
        ('mid', 'Midlane'),
        ('bot', 'Botlane'),
        ('sup', 'Support'),
    ], required=False)
    player = forms.ModelChoiceField(queryset=Player.objects.values_list('summonerName', flat=True).distinct(),
                                    required=False)



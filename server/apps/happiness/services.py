from typing import List, Dict

from django.utils.timezone import now
from django.db.models import Count

from .models import Happiness


def get_stats(user, date: str = None) -> Dict[str, any]:
    if not date:
        date = now().date()
    tally = get_happiness_tally(user, date)
    average = get_average_happiness(tally)
    return {'tally': tally, 'average': average}


def get_happiness_tally(user, date: str) -> Dict[str, int]:
    qs = Happiness.objects.filter(date=date)
    if user.is_authenticated and user.userprofile.team_id:
        qs = qs.filter(user__userprofile__team_id=user.userprofile.team_id)
    return {
        x['level']: x['count']
        for x in qs.values('level')
        .annotate(count=Count('level'))
        .order_by('level')
        .values('level', 'count')
    }


def get_average_happiness(tally: List[Dict[int, int]]) -> float:
    sum = 0
    count = 0
    for level, level_count in tally.items():
        sum += level
        count += level_count
    average = sum / count if count else None
    return average


def get_average_happiness_from_db(user, date: str) -> float:
    qs = Happiness.objects.filter(date=date)
    if user.is_authenticated and user.userprofile.team_id:
        qs = qs.filter(user__userprofile__team_id=user.userprofile.team_id)
    return qs.aggregate(Avg('level'))['level__avg']

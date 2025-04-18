from django.db.models import Avg
from .models import Rating

def get_average_rating_for_user(user_id):
    result = Rating.objects.filter(id_evaluates_id=user_id).aggregate(avg_rating=Avg('rating'))
    return result['avg_rating']

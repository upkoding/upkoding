from dataclasses import dataclass
from django.conf import settings


@dataclass
class Plan:
    id: str
    name: str
    access_days: int
    price: int
    price_display: str

    @property
    def label(self):
        return f'{self.name} ({self.price_display})'

    @staticmethod
    def from_json(price_json):
        return Plan(
            id=price_json.get('id'),
            name=price_json.get('name'),
            access_days=price_json.get('access_days'),
            price=price_json.get('price'),
            price_display=price_json.get('price_display'),
        )


# Plan object list
plans = list(map(Plan.from_json, settings.PRICING))


def get_plan(plan_id):
    price = list(filter(lambda x: x.id == plan_id, plans))
    if len(price) != 1:
        return None
    return price[0]


def plan_id_is_valid(plan_id):
    return get_plan(plan_id) is not None

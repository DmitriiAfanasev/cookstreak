import hashlib
import json
import logging
import random
from datetime import date, datetime, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from bson import ObjectId
from pymongo.errors import DuplicateKeyError, OperationFailure

from ..db.mongodb import foods, menus
from .rules import normalize, recipe_text, resolve_profile

logger = logging.getLogger(__name__)

DAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
MEALS_PER_DAY = 1                         # одно блюдо в день; поменяй на 2-3, когда рецептов будет больше
REQUIRED_RECIPES = len(DAYS) * MEALS_PER_DAY

RECIPE_FIELDS = {"title": 1, "meal_type": 1, "servings": 1, "intro": 1, "ingredients": 1,
                 "instructions": 1, "tips": 1, "source": 1}

try:
    menus.create_index([("user_id", 1), ("year", 1), ("week", 1)], unique=True)
except OperationFailure as e:  # например, на сервере кончилось место
    logger.warning("menus index not created: %s", e)


class NotEnoughRecipesError(Exception):
    def __init__(self, found: int, required: int):
        self.found, self.required = found, required
        super().__init__(f"Only {found} suitable recipes found, {required} required")


# ---------- Текущая неделя ----------

def user_today(user: dict, now: Optional[datetime] = None) -> date:
    """Сегодняшняя дата в часовом поясе пользователя (иначе UTC),
    чтобы в ночь с воскресенья на понедельник неделя сменилась у юзера вовремя."""
    now = now or datetime.now(timezone.utc)
    tz_name = user.get("timezone")
    if tz_name:
        try:
            return now.astimezone(ZoneInfo(tz_name)).date()
        except (ZoneInfoNotFoundError, ValueError):
            pass
    return now.astimezone(timezone.utc).date()


def current_week(user: dict, now: Optional[datetime] = None) -> tuple[int, int, date]:
    """(ISO-год, ISO-неделя, понедельник этой недели).
    ISO-год важен: 29.12.2025 относится к 2026-W01, а не к 2025-му."""
    today = user_today(user, now)
    iso = today.isocalendar()
    monday = today - timedelta(days=iso.weekday - 1)
    return iso.year, iso.week, monday


# ---------- Генерация ----------

def profile_fingerprint(user: dict) -> str:
    """Хэш того, что влияет на подбор. Если юзер поменял аллергии/диету/цели, меню пересоберётся."""
    data = {k: sorted(normalize(x) for x in (user.get(k) or []))
            for k in ("dietary_preferences", "allergies", "goals")}
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]


def _snapshot(recipe: dict) -> dict:
    return {
        "recipe_id": str(recipe["_id"]),
        "title": recipe.get("title") or "",
        "meal_type": recipe.get("meal_type"),
        "servings": recipe.get("servings"),
        "intro": recipe.get("intro"),
        "ingredients": [i for i in (recipe.get("ingredients") or []) if isinstance(i, dict)],
        "instructions": [s for s in (recipe.get("instructions") or []) if isinstance(s, str)],
        "tips": [t for t in (recipe.get("tips") or []) if isinstance(t, str)],
        "source": recipe.get("source"),
    }


def select_recipes(user: dict, recipes: list[dict], seed: str) -> tuple[list[dict], list[str]]:
    """Фильтр (диета + аллергии) -> ранжирование по целям -> топ N без повторов."""
    profile = resolve_profile(user.get("dietary_preferences"), user.get("allergies"), user.get("goals"))
    rng = random.Random(seed)  # детерминированно: один и тот же юзер+неделя -> то же меню

    candidates, seen_titles = [], set()
    for recipe in recipes:
        title = normalize(recipe.get("title") or "")
        if not title or title in seen_titles:  # один и тот же рецепт мог лежать в разных неделях
            continue
        text = recipe_text(recipe)
        if profile.is_forbidden(text):
            continue
        seen_titles.add(title)
        # Случайная добавка < 1 разнообразит меню, но не перебивает разницу в очках по целям
        candidates.append((profile.score(recipe, text) + rng.random(), recipe))

    if len(candidates) < REQUIRED_RECIPES:
        raise NotEnoughRecipesError(len(candidates), REQUIRED_RECIPES)

    candidates.sort(key=lambda pair: pair[0], reverse=True)
    chosen = [recipe for _, recipe in candidates[:REQUIRED_RECIPES]]
    rng.shuffle(chosen)  # лучшие рецепты не должны все оказаться в начале недели
    return chosen, profile.warnings


def build_menu(user: dict, year: int, week: int, monday: date) -> dict:
    recipes = list(foods.find({}, RECIPE_FIELDS))
    chosen, warnings = select_recipes(user, recipes, seed=f"{user['_id']}:{year}:{week}")

    days = []
    for i, day_name in enumerate(DAYS):
        day_recipes = chosen[i * MEALS_PER_DAY:(i + 1) * MEALS_PER_DAY]
        days.append({
            "day_of_week": day_name,
            "date": (monday + timedelta(days=i)).isoformat(),
            "recipes": [_snapshot(r) for r in day_recipes],
        })

    return {
        "user_id": user["_id"],
        "year": year,
        "week": week,
        "week_start": monday.isoformat(),
        "week_end": (monday + timedelta(days=6)).isoformat(),
        "days": days,
        "warnings": warnings,
        "profile_fingerprint": profile_fingerprint(user),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def get_or_create_current_menu(user: dict) -> dict:
    year, week, monday = current_week(user)
    key = {"user_id": user["_id"], "year": year, "week": week}

    existing = menus.find_one(key)
    if existing and existing.get("profile_fingerprint") == profile_fingerprint(user):
        return existing

    menu = build_menu(user, year, week, monday)

    if existing:
        # Профиль изменился: старое меню могло содержать то, что теперь запрещено -> заменяем
        menus.replace_one({"_id": existing["_id"]}, menu)
        menu["_id"] = existing["_id"]
        return menu

    try:
        result = menus.insert_one(menu)
        menu["_id"] = result.inserted_id
        return menu
    except DuplicateKeyError:
        # Два одновременных запроса: второй отдаёт меню, которое создал первый
        return menus.find_one(key)

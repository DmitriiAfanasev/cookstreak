"""Правила фильтрации и ранжирования рецептов.

Ключевые слова ищутся в названии рецепта и названиях ингредиентов:
без учёта регистра, по границам слов, с учётом множественного числа
("egg" найдёт "eggs", но не "eggplant"; "nut" найдёт "nuts", но не "nutmeg").

Ложные срабатывания (например, "butter" в "peanut butter" там, где нет исключения)
сделаны в безопасную сторону: при аллергии лучше лишний раз выкинуть рецепт,
чем пропустить аллерген. Словари можно расширять, не трогая остальной код.
"""
import re
from dataclasses import dataclass, field
from typing import Iterable, Optional


def normalize(value: str) -> str:
    """'Gluten-Free ' -> 'gluten_free', 'без глютена' -> 'без_глютена'."""
    return re.sub(r"[\s\-]+", "_", (value or "").strip().lower())


def _compile(words: Iterable[str]) -> re.Pattern:
    words = sorted({w.lower() for w in words if w}, key=len, reverse=True)
    alternation = "|".join(re.escape(w) for w in words)
    return re.compile(rf"\b(?:{alternation})(?:e?s)?\b", re.IGNORECASE)


class Rule:
    """Набор ключевых слов + фразы-исключения (например, 'coconut milk' для молочки)."""

    def __init__(self, keywords: Iterable[str], exceptions: Iterable[str] = ()):
        self.pattern = _compile(keywords)
        exceptions = tuple(exceptions)
        self.exceptions = _compile(exceptions) if exceptions else None

    def _clean(self, text: str) -> str:
        return self.exceptions.sub(" ", text) if self.exceptions else text

    def matches(self, text: str) -> bool:
        return self.pattern.search(self._clean(text)) is not None

    def distinct_hits(self, text: str) -> set[str]:
        return {m.group(0).lower() for m in self.pattern.finditer(self._clean(text))}


# ---------- Словари ингредиентов ----------

PORK = ("pork", "bacon", "ham", "prosciutto", "pancetta", "chorizo", "salami", "pepperoni",
        "lard", "guanciale", "speck")
MEAT = PORK + ("beef", "steak", "veal", "lamb", "mutton", "chicken", "turkey", "duck", "goose",
               "mince", "meatball", "sausage", "venison", "rabbit", "liver", "bresaola", "brisket")
FISH = ("fish", "salmon", "tuna", "cod", "haddock", "trout", "mackerel", "sardine", "anchovy",
        "anchovies", "tilapia", "halibut", "sea bass", "pollock", "hake", "basa", "fish sauce")
SHELLFISH = ("shrimp", "prawn", "crab", "lobster", "mussel", "clam", "scallop", "oyster", "squid",
             "calamari", "octopus", "crayfish")
DAIRY = ("milk", "cheese", "butter", "cream", "yogurt", "yoghurt", "ghee", "parmesan", "mozzarella",
         "cheddar", "feta", "ricotta", "mascarpone", "halloumi", "paneer", "crème fraîche",
         "creme fraiche", "buttermilk", "whey", "custard", "burrata", "gouda", "brie", "gruyère",
         "gruyere", "pecorino", "labneh", "kefir", "quark")
EGG = ("egg", "mayonnaise", "mayo", "aioli", "meringue")
GLUTEN = ("flour", "wheat", "bread", "breadcrumb", "panko", "pasta", "spaghetti", "penne", "linguine",
          "fettuccine", "tagliatelle", "lasagne", "lasagna", "macaroni", "orzo", "gnocchi", "noodle",
          "udon", "couscous", "bulgur", "barley", "rye", "spelt", "semolina", "farro", "tortilla",
          "wrap", "pita", "naan", "bun", "brioche", "ciabatta", "baguette", "focaccia", "croissant",
          "pastry", "soy sauce", "seitan", "beer")
NUTS = ("nut", "almond", "walnut", "cashew", "pecan", "hazelnut", "pistachio", "macadamia",
        "pine nut", "brazil nut", "praline", "marzipan", "nutella", "peanut")
PEANUT = ("peanut", "groundnut", "satay")
SOY = ("soy", "soya", "tofu", "edamame", "miso", "tempeh", "tamari", "teriyaki", "hoisin")
SESAME = ("sesame", "tahini", "hummus", "houmous", "zaatar", "za'atar", "furikake")
SWEET = ("sugar", "honey", "syrup", "maple", "chocolate", "caramel", "jam", "agave", "molasses",
         "condensed milk", "icing")
ALCOHOL = ("wine", "beer", "rum", "vodka", "brandy", "whisky", "whiskey", "sherry", "mirin", "sake",
           "bourbon", "cider", "marsala")
HIGH_CARB = GLUTEN + SWEET + ("rice", "potato", "corn", "polenta", "oats", "quinoa", "lentil",
                              "chickpea", "bean", "banana")
VEGGIES = ("salad", "spinach", "kale", "broccoli", "cauliflower", "zucchini", "courgette",
           "bell pepper", "capsicum", "tomato", "cucumber", "lettuce", "cabbage", "carrot", "bean",
           "lentil", "chickpea", "asparagus", "mushroom", "eggplant", "aubergine", "greens", "pea",
           "celery", "leek", "beetroot", "radish", "rocket", "arugula", "bok choy", "pak choi")
PROTEIN = ("chicken", "turkey", "beef", "steak", "salmon", "tuna", "cod", "egg", "tofu", "tempeh",
           "lentil", "bean", "chickpea", "greek yogurt", "cottage cheese", "quinoa", "edamame",
           "prawn", "shrimp", "seitan")
RICH = ("cream", "butter", "bacon", "sausage", "fried", "cheese", "mayonnaise", "sugar", "pastry",
        "chorizo", "salami", "syrup", "chocolate")

# ---------- Правила ----------

MEAT_R = Rule(MEAT, exceptions=("beef tomato", "beefsteak tomato", "duck egg"))
PORK_R = Rule(PORK)
FISH_R = Rule(FISH)
SHELLFISH_R = Rule(SHELLFISH)
DAIRY_R = Rule(DAIRY, exceptions=(
    "coconut milk", "coconut cream", "coconut yogurt", "coconut yoghurt", "almond milk", "oat milk",
    "soy milk", "rice milk", "peanut butter", "almond butter", "cashew butter", "nut butter",
    "cocoa butter", "butter bean", "cream of tartar", "vegan butter", "vegan cheese"))
EGG_R = Rule(EGG, exceptions=("vegan mayo", "vegan mayonnaise", "egg-free", "eggless"))
GLUTEN_R = Rule(GLUTEN, exceptions=("rice noodle", "rice flour", "corn tortilla", "almond flour",
                                    "coconut flour", "chickpea flour", "rice paper"))
NUTS_R = Rule(NUTS)
PEANUT_R = Rule(PEANUT)
SOY_R = Rule(SOY)
SESAME_R = Rule(SESAME)
HONEY_R = Rule(("honey",))
GELATIN_R = Rule(("gelatin", "gelatine"))
ALCOHOL_R = Rule(ALCOHOL)
HIGH_CARB_R = Rule(HIGH_CARB, exceptions=("green bean", "string bean", "runner bean",
                                          "cauliflower rice", "almond flour", "coconut flour"))

DIET_RULES: dict[str, list[Rule]] = {
    "vegetarian": [MEAT_R, FISH_R, SHELLFISH_R, GELATIN_R],
    "vegan": [MEAT_R, FISH_R, SHELLFISH_R, DAIRY_R, EGG_R, HONEY_R, GELATIN_R],
    "pescatarian": [MEAT_R, GELATIN_R],
    "gluten_free": [GLUTEN_R],
    "dairy_free": [DAIRY_R],
    "low_carb": [HIGH_CARB_R],
    "keto": [HIGH_CARB_R],
    "halal": [PORK_R, ALCOHOL_R, GELATIN_R],
    "no_pork": [PORK_R],
}
DIET_ALIASES = {
    "veggie": "vegetarian", "вегетарианство": "vegetarian", "вегетарианец": "vegetarian",
    "вегетарианское": "vegetarian", "веган": "vegan", "веганство": "vegan", "plant_based": "vegan",
    "пескетарианство": "pescatarian", "glutenfree": "gluten_free", "без_глютена": "gluten_free",
    "lactose_free": "dairy_free", "без_лактозы": "dairy_free", "без_молочки": "dairy_free",
    "low_carbs": "low_carb", "низкоуглеводная": "low_carb", "кето": "keto", "халяль": "halal",
    "без_свинины": "no_pork",
}

ALLERGY_RULES: dict[str, list[Rule]] = {
    "nuts": [NUTS_R], "peanuts": [PEANUT_R], "dairy": [DAIRY_R], "eggs": [EGG_R],
    "gluten": [GLUTEN_R], "fish": [FISH_R], "shellfish": [SHELLFISH_R], "soy": [SOY_R],
    "sesame": [SESAME_R],
}
ALLERGY_ALIASES = {
    "nut": "nuts", "tree_nuts": "nuts", "орехи": "nuts", "peanut": "peanuts", "арахис": "peanuts",
    "milk": "dairy", "lactose": "dairy", "молоко": "dairy", "лактоза": "dairy", "молочка": "dairy",
    "egg": "eggs", "яйца": "eggs", "wheat": "gluten", "глютен": "gluten", "пшеница": "gluten",
    "рыба": "fish", "seafood": "shellfish", "морепродукты": "shellfish", "soya": "soy", "соя": "soy",
    "кунжут": "sesame",
}


@dataclass
class GoalRule:
    bonus: Optional[Rule] = None
    penalty: Optional[Rule] = None
    quick: bool = False

    def score(self, recipe: dict, text: str) -> float:
        s = 0.0
        if self.bonus:
            s += min(len(self.bonus.distinct_hits(text)), 5)
        if self.penalty:
            s -= 1.5 * min(len(self.penalty.distinct_hits(text)), 4)
        if self.quick:
            steps = len(recipe.get("instructions") or [])
            ingredients = len(recipe.get("ingredients") or [])
            s += 2 if steps <= 5 else (-1 if steps > 8 else 0)
            s += 1 if ingredients <= 8 else 0
        return s


VEGGIES_R = Rule(VEGGIES)
GOAL_RULES: dict[str, GoalRule] = {
    "lose_weight": GoalRule(bonus=VEGGIES_R, penalty=Rule(RICH)),
    "gain_muscle": GoalRule(bonus=Rule(PROTEIN)),
    "eat_healthier": GoalRule(bonus=VEGGIES_R, penalty=Rule(RICH + ("sausage", "salami", "ham"))),
    "less_sugar": GoalRule(penalty=Rule(SWEET)),
    "save_time": GoalRule(quick=True),
}
GOAL_ALIASES = {
    "weight_loss": "lose_weight", "похудеть": "lose_weight", "похудение": "lose_weight",
    "muscle_gain": "gain_muscle", "high_protein": "gain_muscle", "набрать_массу": "gain_muscle",
    "больше_белка": "gain_muscle", "healthy": "eat_healthier", "healthy_eating": "eat_healthier", "здоровое_питание": "eat_healthier",
    "меньше_сахара": "less_sugar", "quick": "save_time", "quick_meals": "save_time",
    "быстро": "save_time", "экономить_время": "save_time",
}


def canonical_diet(value: str) -> Optional[str]:
    key = normalize(value)
    key = DIET_ALIASES.get(key, key)
    return key if key in DIET_RULES else None


def canonical_goal(value: str) -> Optional[str]:
    key = normalize(value)
    key = GOAL_ALIASES.get(key, key)
    return key if key in GOAL_RULES else None


def recipe_text(recipe: dict) -> str:
    """Название + ингредиенты через разделитель, чтобы слова соседних ингредиентов не склеивались."""
    parts = [str(recipe.get("title") or "")]
    for ing in recipe.get("ingredients") or []:
        if isinstance(ing, dict):
            parts.append(str(ing.get("item") or ""))
        elif isinstance(ing, str):
            parts.append(ing)
    return " | ".join(parts)


@dataclass
class ProfileRules:
    forbidden: list[Rule] = field(default_factory=list)
    goals: list[GoalRule] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def is_forbidden(self, text: str) -> bool:
        return any(rule.matches(text) for rule in self.forbidden)

    def score(self, recipe: dict, text: str) -> float:
        return sum(goal.score(recipe, text) for goal in self.goals)


def resolve_profile(dietary_preferences, allergies, goals) -> ProfileRules:
    result = ProfileRules()

    for raw in allergies or []:
        key = normalize(raw)
        key = ALLERGY_ALIASES.get(key, key)
        if key in ALLERGY_RULES:
            result.forbidden += ALLERGY_RULES[key]
        elif raw and raw.strip():
            # Неизвестная аллергия: всё равно фильтруем по самому слову (безопасная сторона)
            result.forbidden.append(Rule((raw.strip(),)))
            result.warnings.append(
                f"Allergy '{raw}' is not in the dictionary: excluding recipes that contain this exact word")

    for raw in dietary_preferences or []:
        key = canonical_diet(raw)
        if key:
            result.forbidden += DIET_RULES[key]
        else:
            result.warnings.append(f"Dietary preference '{raw}' is unknown and was not applied")

    for raw in goals or []:
        key = canonical_goal(raw)
        if key:
            result.goals.append(GOAL_RULES[key])
        else:
            result.warnings.append(f"Goal '{raw}' is unknown and was not applied")

    return result

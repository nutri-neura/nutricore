from __future__ import annotations

PLAN_SET_VERSION = "adult_ambulatory_plan_v1"


class MealPlanInputError(ValueError):
    def __init__(self, missing_fields: list[str]):
        self.missing_fields = missing_fields
        super().__init__(", ".join(missing_fields))


def build_structure_blocks(meal_code: str) -> list[dict]:
    if meal_code == "breakfast":
        return [
            {
                "slot_code": "protein_base",
                "label": "Proteina base",
                "guidance": "Yogur, huevo, queso fresco o licuado alto en proteina.",
            },
            {
                "slot_code": "cereal_base",
                "label": "Cereal / avena / pan",
                "guidance": "Elegir una base simple para cubrir carbohidrato principal.",
            },
            {
                "slot_code": "fruit_optional",
                "label": "Fruta opcional",
                "guidance": "Agregar fruta si mejora adherencia o saciedad.",
            },
            {
                "slot_code": "light_fat",
                "label": "Grasa ligera",
                "guidance": "Semillas, crema de cacahuate o aguacate en porcion moderada.",
            },
        ]
    if meal_code in {"lunch", "dinner"}:
        return [
            {
                "slot_code": "main_protein",
                "label": "Proteina principal",
                "guidance": "Fuente magra como pollo, atun, carne magra o leguminosa reforzada.",
            },
            {
                "slot_code": "starch_base",
                "label": "Cereal o tuberculo",
                "guidance": "Arroz, tortilla, pasta, pan o papa segun contexto.",
            },
            {
                "slot_code": "vegetables",
                "label": "Verduras libres",
                "guidance": "Base alta en volumen para saciedad y adherencia.",
            },
            {
                "slot_code": "added_fat",
                "label": "Grasa de adicion",
                "guidance": "Aceite, aguacate, semillas o frutos secos si aplica.",
            },
        ]
    return [
        {
            "slot_code": "light_protein",
            "label": "Proteina ligera",
            "guidance": "Yogur, queso cottage, leche alta en proteina o similar.",
        },
        {
            "slot_code": "easy_carb",
            "label": "Fruta o carbohidrato simple",
            "guidance": "Fruta, tostadas, galletas simples o avena rapida.",
        },
        {
            "slot_code": "optional_fat",
            "label": "Grasa opcional",
            "guidance": "Usar solo si la distribucion del dia lo requiere.",
        },
    ]


def execute_meal_plan(distribution, notes: str | None) -> tuple[dict, list[dict], list[str]]:
    recommendation = distribution.recommendation_payload or {}
    meals = recommendation.get("meals")
    missing_fields: list[str] = []

    if meals is None:
        missing_fields.append("distribution.recommendation_payload.meals")

    if missing_fields:
        raise MealPlanInputError(missing_fields)

    plan_meals: list[dict] = []
    for index, meal in enumerate(meals, start=1):
        plan_meals.append(
            {
                "meal_code": meal["meal_code"],
                "label": meal["label"],
                "sort_order": index,
                "target_energy_kcal": meal["target_energy_kcal"],
                "protein_target_g": meal["protein_g"],
                "fat_target_g": meal["fat_g"],
                "carbs_target_g": meal["carbs_g"],
                "structure_payload": build_structure_blocks(meal["meal_code"]),
                "notes": None,
            }
        )

    warnings = [
        "MVP scope: base structure only, not a final prescribed menu",
        "Blocks are planning placeholders for clinician review",
    ]

    plan_summary = {
        "pattern_code": recommendation.get("pattern_code"),
        "goal_code": recommendation.get("goal_code"),
        "plan_set_version": PLAN_SET_VERSION,
        "generated_meals": len(plan_meals),
        "notes": notes,
    }
    return plan_summary, plan_meals, warnings

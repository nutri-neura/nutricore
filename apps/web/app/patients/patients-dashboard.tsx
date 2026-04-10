"use client";

import { useCallback, useEffect, useState } from "react";

type PatientRecord = {
  primary_goal?: string | null;
  allergies?: string | null;
  food_preferences?: string | null;
};

type Patient = {
  id: number;
  first_name: string;
  last_name: string;
  sex: string;
  birth_date: string;
  phone?: string | null;
  email?: string | null;
  record?: PatientRecord | null;
};

type Measurement = {
  weight_kg?: number | null;
  height_cm?: number | null;
  activity_level?: string | null;
};

type Consultation = {
  id: number;
  consultation_date: string;
  reason?: string | null;
  clinical_notes?: string | null;
  measurement?: Measurement | null;
};

type FormulaResult = {
  id: number;
  formula_code: string;
  formula_family: string;
  output_payload: Record<string, unknown>;
  source_note?: string | null;
};

type Evaluation = {
  id: number;
  consultation_id: number;
  status: string;
  formula_set_version: string;
  equation_selection_policy: string;
  summary_payload: Record<string, unknown>;
  warnings_payload: string[];
  formula_results: FormulaResult[];
  created_at: string;
};

type NutritionStrategy = {
  id: number;
  evaluation_id: number;
  goal_code: string;
  status: string;
  strategy_set_version: string;
  recommendation_payload: Record<string, unknown>;
  warnings_payload: string[];
  created_at: string;
};

type MealTarget = {
  meal_code: string;
  label: string;
  allocation_pct: number;
  target_energy_kcal: number;
  protein_g: number;
  fat_g: number;
  carbs_g: number;
};

type MealDistribution = {
  id: number;
  strategy_id: number;
  pattern_code: string;
  status: string;
  distribution_set_version: string;
  recommendation_payload: {
    meals?: MealTarget[];
    [key: string]: unknown;
  };
  warnings_payload: string[];
  created_at: string;
};

type MealPlanMeal = {
  id: number;
  meal_code: string;
  label: string;
  sort_order: number;
  target_energy_kcal: number;
  protein_target_g: number;
  fat_target_g: number;
  carbs_target_g: number;
  structure_payload: Array<{ slot_code: string; label: string; guidance: string }>;
  notes?: string | null;
};

type MealPlan = {
  id: number;
  distribution_id: number;
  status: string;
  plan_set_version: string;
  notes?: string | null;
  created_at: string;
  updated_at: string;
  meals: MealPlanMeal[];
};

type FoodCandidate = {
  food_id: number;
  name: string;
  category_code: string;
  portion_label: string;
  energy_kcal: number;
  protein_g: number;
  fat_g: number;
  carbs_g: number;
  fit_score: number;
  portion_multiplier?: number;
  suggested_portion_grams?: number | null;
  suggested_portion_text?: string;
  adjusted_energy_kcal?: number;
  adjusted_protein_g?: number;
  adjusted_fat_g?: number;
  adjusted_carbs_g?: number;
  fit_status?: string;
  warnings?: string[];
  notes?: string | null;
};

type MealSuggestionSlot = {
  slot_code: string;
  label: string;
  guidance: string;
  recommended_candidate?: FoodCandidate | null;
  selected_food?: FoodCandidate | null;
  candidates: FoodCandidate[];
};

type MealPlanSuggestionMeal = {
  id: number;
  meal_code: string;
  label: string;
  target_energy_kcal: number;
  protein_target_g: number;
  fat_target_g: number;
  carbs_target_g: number;
  slots: MealSuggestionSlot[];
};

type MealPlanSuggestions = {
  meal_plan_id: number;
  warnings: string[];
  meals: MealPlanSuggestionMeal[];
};

type DailyMenuSlot = {
  slot_code: string;
  label: string;
  guidance: string;
  status: string;
  selected_food?: FoodCandidate | null;
};

type DailyMenuMeal = {
  meal_plan_meal_id: number;
  meal_code: string;
  label: string;
  target_energy_kcal: number;
  protein_target_g: number;
  fat_target_g: number;
  carbs_target_g: number;
  selected_energy_kcal: number;
  selected_protein_g: number;
  selected_fat_g: number;
  selected_carbs_g: number;
  covered_slots: number;
  total_slots: number;
  completion_pct: number;
  pending_slots: string[];
  slots: DailyMenuSlot[];
};

type DailyMenu = {
  meal_plan_id: number;
  status: string;
  total_slots: number;
  selected_slots: number;
  pending_slots: number;
  completion_pct: number;
  target_energy_kcal: number;
  selected_energy_kcal: number;
  target_protein_g: number;
  selected_protein_g: number;
  target_fat_g: number;
  selected_fat_g: number;
  target_carbs_g: number;
  selected_carbs_g: number;
  warnings: string[];
  meals: DailyMenuMeal[];
};

type HistoryDelta = {
  weight_kg?: number | null;
  bmi?: number | null;
  maintenance_energy_kcal?: number | null;
  target_energy_kcal?: number | null;
  protein_g?: number | null;
  fat_g?: number | null;
  carbs_g?: number | null;
};

type HistoryMeasurement = {
  weight_kg?: number | null;
  height_cm?: number | null;
  activity_level?: string | null;
};

type HistoryEvaluation = {
  id: number;
  created_at: string;
  formula_set_version: string;
  bmi?: number | null;
  resting_energy_kcal?: number | null;
  maintenance_energy_kcal?: number | null;
};

type HistoryStrategy = {
  id: number;
  created_at: string;
  goal_code: string;
  target_energy_kcal?: number | null;
  protein_g?: number | null;
  fat_g?: number | null;
  carbs_g?: number | null;
};

type HistoryMealPlan = {
  id: number;
  created_at: string;
  status: string;
  pattern_code?: string | null;
  completion_pct: number;
  selected_slots: number;
  total_slots: number;
};

type PatientHistoryItem = {
  consultation_id: number;
  consultation_date: string;
  reason?: string | null;
  measurement?: HistoryMeasurement | null;
  evaluation?: HistoryEvaluation | null;
  strategy?: HistoryStrategy | null;
  meal_plan?: HistoryMealPlan | null;
  delta_vs_previous?: HistoryDelta | null;
};

type PatientHistory = {
  patient_id: number;
  patient_name: string;
  consultation_count: number;
  latest_consultation_date?: string | null;
  items: PatientHistoryItem[];
};

type FinalSummarySlot = {
  slot_code: string;
  label: string;
  guidance: string;
  status: string;
  food_name?: string | null;
  portion_text?: string | null;
  adjusted_energy_kcal?: number | null;
  adjusted_protein_g?: number | null;
  adjusted_fat_g?: number | null;
  adjusted_carbs_g?: number | null;
  notes?: string | null;
};

type FinalSummaryMeal = {
  meal_plan_meal_id: number;
  meal_code: string;
  label: string;
  completion_pct: number;
  target_energy_kcal: number;
  selected_energy_kcal: number;
  target_protein_g: number;
  selected_protein_g: number;
  target_fat_g: number;
  selected_fat_g: number;
  target_carbs_g: number;
  selected_carbs_g: number;
  pending_slots: string[];
  slots: FinalSummarySlot[];
};

type FinalSummary = {
  meal_plan_id: number;
  status: string;
  export_ready: boolean;
  consultation_id: number;
  consultation_date: string;
  patient: {
    id: number;
    full_name: string;
    sex: string;
    birth_date: string;
  };
  goal_code: string;
  pattern_code: string;
  plan_notes?: string | null;
  completion_pct: number;
  total_slots: number;
  selected_slots: number;
  pending_slots: number;
  target_energy_kcal: number;
  selected_energy_kcal: number;
  target_protein_g: number;
  selected_protein_g: number;
  target_fat_g: number;
  selected_fat_g: number;
  target_carbs_g: number;
  selected_carbs_g: number;
  warnings: string[];
  meals: FinalSummaryMeal[];
};

const TOKEN_STORAGE_KEY = "nutricore.jwt";
const strategyGoalOptions = [
  { value: "maintenance", label: "Mantenimiento" },
  { value: "fat_loss", label: "Perdida de grasa" },
  { value: "muscle_gain", label: "Ganancia muscular" },
  { value: "recomposition", label: "Recomposicion" },
];
const mealPatternOptions = [
  { value: "three_meals", label: "3 tiempos" },
  { value: "four_meals", label: "4 tiempos" },
  { value: "five_meals", label: "5 tiempos" },
];

async function requestJson(token: string, path: string, init?: RequestInit) {
  const response = await fetch(`/api/proxy${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    let detail = "No se pudo completar la solicitud";

    try {
      const payload = await response.json();
      detail = payload.detail?.message || payload.detail || detail;
    } catch {
      detail = response.statusText || detail;
    }

    throw new Error(detail);
  }

  return response.json();
}

function formatValue(value: unknown) {
  if (value === null || value === undefined || value === "") {
    return "sin dato";
  }

  if (typeof value === "number") {
    return Number.isInteger(value) ? `${value}` : value.toFixed(2);
  }

  return String(value);
}

function buildSlotDraftKey(mealPlanMealId: number, slotCode: string) {
  return `${mealPlanMealId}:${slotCode}`;
}

function roundToTwo(value: number) {
  return Math.round(value * 100) / 100;
}

function buildAutoPortionText(food: FoodCandidate, portionMultiplier: number) {
  const roundedMultiplier = roundToTwo(portionMultiplier);
  if (!food.suggested_portion_grams || !food.portion_multiplier || food.portion_multiplier <= 0) {
    return `${roundedMultiplier} x ${food.portion_label}`;
  }

  const basePortionGrams = food.suggested_portion_grams / food.portion_multiplier;
  const suggestedPortionGrams = roundToTwo(basePortionGrams * roundedMultiplier);
  return `${roundedMultiplier} x ${food.portion_label} (~${suggestedPortionGrams} g)`;
}

export function PatientsDashboard() {
  const [token, setToken] = useState("");
  const [tokenReady, setTokenReady] = useState(false);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [consultations, setConsultations] = useState<Consultation[]>([]);
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [strategies, setStrategies] = useState<NutritionStrategy[]>([]);
  const [distributions, setDistributions] = useState<MealDistribution[]>([]);
  const [mealPlans, setMealPlans] = useState<MealPlan[]>([]);
  const [mealPlanSuggestions, setMealPlanSuggestions] = useState<MealPlanSuggestions | null>(null);
  const [dailyMenu, setDailyMenu] = useState<DailyMenu | null>(null);
  const [finalSummary, setFinalSummary] = useState<FinalSummary | null>(null);
  const [patientHistory, setPatientHistory] = useState<PatientHistory | null>(null);
  const [slotMultiplierDrafts, setSlotMultiplierDrafts] = useState<Record<string, string>>({});
  const [slotPortionTextDrafts, setSlotPortionTextDrafts] = useState<Record<string, string>>({});
  const [slotNotesDrafts, setSlotNotesDrafts] = useState<Record<string, string>>({});
  const [selectedPatientId, setSelectedPatientId] = useState<number | null>(null);
  const [selectedConsultationId, setSelectedConsultationId] = useState<number | null>(null);
  const [selectedGoalCode, setSelectedGoalCode] = useState("fat_loss");
  const [selectedPatternCode, setSelectedPatternCode] = useState("five_meals");
  const [planNotesDraft, setPlanNotesDraft] = useState("");
  const [busyState, setBusyState] = useState("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadMealPlanArtifacts = useCallback(
    async (mealPlanId: number, currentToken: string = token.trim()) => {
      const suggestionsPayload = (await requestJson(
        currentToken,
        `/v1/meal-plans/${mealPlanId}/suggestions`,
      )) as MealPlanSuggestions;
      const dailyMenuPayload = (await requestJson(
        currentToken,
        `/v1/meal-plans/${mealPlanId}/daily-menu`,
      )) as DailyMenu;
      const finalSummaryPayload = (await requestJson(
        currentToken,
        `/v1/meal-plans/${mealPlanId}/final-summary`,
      )) as FinalSummary;
      setMealPlanSuggestions(suggestionsPayload);
      setDailyMenu(dailyMenuPayload);
      setFinalSummary(finalSummaryPayload);
    },
    [token],
  );

  useEffect(() => {
    const storedToken = window.localStorage.getItem(TOKEN_STORAGE_KEY);
    if (storedToken) {
      setToken(storedToken);
    }
    setTokenReady(true);
  }, []);

  useEffect(() => {
    if (!tokenReady) {
      return;
    }

    if (token.trim()) {
      window.localStorage.setItem(TOKEN_STORAGE_KEY, token.trim());
    } else {
      window.localStorage.removeItem(TOKEN_STORAGE_KEY);
    }
  }, [token, tokenReady]);

  async function loadPatients(currentToken: string = token.trim()) {
    if (!currentToken) {
      setErrorMessage("Pega un JWT valido antes de consultar datos.");
      return;
    }

    setBusyState("patients");
    setErrorMessage(null);

    try {
      const payload = (await requestJson(currentToken, "/v1/patients")) as Patient[];
      setPatients(payload);
      if (payload.length === 0) {
        setSelectedPatientId(null);
        setSelectedConsultationId(null);
        setConsultations([]);
        setEvaluations([]);
        setStrategies([]);
        setDistributions([]);
        setMealPlans([]);
        setMealPlanSuggestions(null);
        setDailyMenu(null);
        setFinalSummary(null);
        setPatientHistory(null);
        return;
      }

      setSelectedPatientId((current) =>
        payload.some((patient) => patient.id === current) ? current : payload[0].id,
      );
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "No se pudieron cargar pacientes.");
    } finally {
      setBusyState("idle");
    }
  }

  useEffect(() => {
    async function run() {
      if (!tokenReady || !token.trim()) {
        return;
      }

      setBusyState("patients");
      setErrorMessage(null);

      try {
        const payload = (await requestJson(token.trim(), "/v1/patients")) as Patient[];
        setPatients(payload);
        if (payload.length === 0) {
          setSelectedPatientId(null);
          setSelectedConsultationId(null);
          setConsultations([]);
          setEvaluations([]);
          setStrategies([]);
          setDistributions([]);
          setMealPlans([]);
          setMealPlanSuggestions(null);
          setDailyMenu(null);
          setFinalSummary(null);
          setPatientHistory(null);
          return;
        }

        setSelectedPatientId((current) =>
          payload.some((patient) => patient.id === current) ? current : payload[0].id,
        );
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : "No se pudieron cargar pacientes.");
      } finally {
        setBusyState("idle");
      }
    }

    void run();
  }, [tokenReady, token]);

  useEffect(() => {
    async function run() {
      if (!selectedPatientId || !token.trim()) {
        setConsultations([]);
        setSelectedConsultationId(null);
        setEvaluations([]);
        setStrategies([]);
        setDistributions([]);
        setMealPlans([]);
        setMealPlanSuggestions(null);
        setDailyMenu(null);
        setFinalSummary(null);
        return;
      }

      setBusyState("consultations");
      setErrorMessage(null);

      try {
        const payload = (await requestJson(
          token.trim(),
          `/v1/patients/${selectedPatientId}/consultations`,
        )) as Consultation[];
        setConsultations(payload);
        const historyPayload = (await requestJson(
          token.trim(),
          `/v1/patients/${selectedPatientId}/history`,
        )) as PatientHistory;
        setPatientHistory(historyPayload);
        setSelectedConsultationId((current) =>
          payload.some((consultation) => consultation.id === current) ? current : (payload[0]?.id ?? null),
        );
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : "No se pudieron cargar consultas.");
      } finally {
        setBusyState("idle");
      }
    }

    void run();
  }, [selectedPatientId, token]);

  useEffect(() => {
    async function run() {
      if (!selectedConsultationId || !token.trim()) {
        setEvaluations([]);
        setStrategies([]);
        return;
      }

      setBusyState("evaluations");
      setErrorMessage(null);

      try {
        const payload = (await requestJson(
          token.trim(),
          `/v1/consultations/${selectedConsultationId}/evaluations`,
        )) as Evaluation[];
        setEvaluations(payload);
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : "No se pudieron cargar evaluaciones.");
      } finally {
        setBusyState("idle");
      }
    }

    void run();
  }, [selectedConsultationId, token]);

  useEffect(() => {
    async function run() {
      const currentEvaluationId = evaluations[0]?.id;
      if (!currentEvaluationId || !token.trim()) {
        setStrategies([]);
        setDistributions([]);
        setMealPlans([]);
        setMealPlanSuggestions(null);
        setDailyMenu(null);
        setFinalSummary(null);
        return;
      }

      setBusyState("strategies");
      setErrorMessage(null);

      try {
        const payload = (await requestJson(
          token.trim(),
          `/v1/evaluations/${currentEvaluationId}/strategies`,
        )) as NutritionStrategy[];
        setStrategies(payload);
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : "No se pudieron cargar estrategias.");
      } finally {
        setBusyState("idle");
      }
    }

    void run();
  }, [evaluations, token]);

  useEffect(() => {
    async function run() {
      const currentStrategyId = strategies[0]?.id;
      if (!currentStrategyId || !token.trim()) {
        setDistributions([]);
        setMealPlans([]);
        setMealPlanSuggestions(null);
        setDailyMenu(null);
        setFinalSummary(null);
        return;
      }

      setBusyState("distributions");
      setErrorMessage(null);

      try {
        const payload = (await requestJson(
          token.trim(),
          `/v1/strategies/${currentStrategyId}/meal-distributions`,
        )) as MealDistribution[];
        setDistributions(payload);
      } catch (error) {
        setErrorMessage(
          error instanceof Error ? error.message : "No se pudieron cargar distribuciones.",
        );
      } finally {
        setBusyState("idle");
      }
    }

    void run();
  }, [strategies, token]);

  useEffect(() => {
    async function run() {
      const currentDistributionId = distributions[0]?.id;
      if (!currentDistributionId || !token.trim()) {
        setMealPlans([]);
        setMealPlanSuggestions(null);
        setDailyMenu(null);
        setFinalSummary(null);
        return;
      }

      setBusyState("mealPlans");
      setErrorMessage(null);

      try {
        const payload = (await requestJson(
          token.trim(),
          `/v1/distributions/${currentDistributionId}/meal-plans`,
        )) as MealPlan[];
        setMealPlans(payload);
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : "No se pudieron cargar planes.");
      } finally {
        setBusyState("idle");
      }
    }

    void run();
  }, [distributions, token]);

  useEffect(() => {
    async function run() {
      const currentMealPlanId = mealPlans[0]?.id;
      if (!currentMealPlanId || !token.trim()) {
        setMealPlanSuggestions(null);
        setDailyMenu(null);
        setFinalSummary(null);
        return;
      }

      setBusyState("suggestions");
      setErrorMessage(null);

      try {
        await loadMealPlanArtifacts(currentMealPlanId, token.trim());
      } catch (error) {
        setErrorMessage(
          error instanceof Error
            ? error.message
            : "No se pudieron cargar sugerencias y menu diario.",
        );
      } finally {
        setBusyState("idle");
      }
    }

    void run();
  }, [mealPlans, token, loadMealPlanArtifacts]);

  async function createEvaluation() {
    if (!selectedConsultationId) {
      setErrorMessage("Selecciona una consulta antes de calcular.");
      return;
    }

    setBusyState("calculate");
    setErrorMessage(null);

    try {
      const payload = (await requestJson(
        token.trim(),
        `/v1/consultations/${selectedConsultationId}/evaluations`,
        {
          method: "POST",
          body: JSON.stringify({}),
        },
      )) as Evaluation;
      setEvaluations((current) => [payload, ...current]);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "No se pudo ejecutar la evaluacion.");
    } finally {
      setBusyState("idle");
    }
  }

  async function createStrategy() {
    const currentEvaluationId = evaluations[0]?.id;
    if (!currentEvaluationId) {
      setErrorMessage("Genera o selecciona una evaluacion antes de crear estrategia.");
      return;
    }

    setBusyState("strategy");
    setErrorMessage(null);

    try {
      const payload = (await requestJson(
        token.trim(),
        `/v1/evaluations/${currentEvaluationId}/strategies`,
        {
          method: "POST",
          body: JSON.stringify({ goal_code: selectedGoalCode }),
        },
      )) as NutritionStrategy;
      setStrategies((current) => [payload, ...current]);
      setDistributions([]);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "No se pudo generar la estrategia.");
    } finally {
      setBusyState("idle");
    }
  }

  async function createDistribution() {
    const currentStrategyId = strategies[0]?.id;
    if (!currentStrategyId) {
      setErrorMessage("Genera una estrategia antes de crear la distribucion diaria.");
      return;
    }

    setBusyState("distribution");
    setErrorMessage(null);

    try {
      const payload = (await requestJson(
        token.trim(),
        `/v1/strategies/${currentStrategyId}/meal-distributions`,
        {
          method: "POST",
          body: JSON.stringify({ pattern_code: selectedPatternCode }),
        },
      )) as MealDistribution;
      setDistributions((current) => [payload, ...current]);
      setMealPlans([]);
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "No se pudo generar la distribucion diaria.",
      );
    } finally {
      setBusyState("idle");
    }
  }

  async function createMealPlan() {
    const currentDistributionId = distributions[0]?.id;
    if (!currentDistributionId) {
      setErrorMessage("Genera una distribucion antes de crear el plan base.");
      return;
    }

    setBusyState("mealPlan");
    setErrorMessage(null);

    try {
      const payload = (await requestJson(
        token.trim(),
        `/v1/distributions/${currentDistributionId}/meal-plans`,
        {
          method: "POST",
          body: JSON.stringify({ notes: planNotesDraft || null }),
        },
      )) as MealPlan;
      setMealPlans((current) => [payload, ...current]);
      setMealPlanSuggestions(null);
      setDailyMenu(null);
      setFinalSummary(null);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "No se pudo generar el plan base.");
    } finally {
      setBusyState("idle");
    }
  }

  async function updateMealPlanStatus(nextStatus: "reviewed" | "finalized" | "ready_for_export") {
    const currentPlan = mealPlans[0];
    if (!currentPlan) {
      setErrorMessage("Genera un plan antes de actualizar su estado.");
      return;
    }

    setBusyState("mealPlanUpdate");
    setErrorMessage(null);

    try {
      const payload = (await requestJson(
        token.trim(),
        `/v1/meal-plans/${currentPlan.id}`,
        {
          method: "PUT",
          body: JSON.stringify({ status: nextStatus, notes: planNotesDraft || currentPlan.notes || null }),
        },
      )) as MealPlan;
      setMealPlans((current) => [payload, ...current.slice(1)]);
      await loadMealPlanArtifacts(payload.id, token.trim());
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "No se pudo actualizar el plan.");
    } finally {
      setBusyState("idle");
    }
  }

  async function selectSlotFood(mealPlanMealId: number, slotCode: string, foodItemId: number) {
    setBusyState("slotSelection");
    setErrorMessage(null);

    try {
      await requestJson(token.trim(), `/v1/meal-plan-meals/${mealPlanMealId}/slot-selections`, {
        method: "POST",
        body: JSON.stringify({ slot_code: slotCode, food_item_id: foodItemId }),
      });

      const currentMealPlanId = mealPlans[0]?.id;
      if (!currentMealPlanId) {
        return;
      }

      await loadMealPlanArtifacts(currentMealPlanId, token.trim());
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "No se pudo guardar la seleccion.");
    } finally {
      setBusyState("idle");
    }
  }

  async function updateSlotSelection(
    mealPlanMealId: number,
    slotCode: string,
    fallbackMultiplier: number,
    fallbackNotes?: string | null,
  ) {
    const draftKey = buildSlotDraftKey(mealPlanMealId, slotCode);
    const portionMultiplier = Number(slotMultiplierDrafts[draftKey] || fallbackMultiplier);
    const hasPortionTextDraft = Object.prototype.hasOwnProperty.call(slotPortionTextDrafts, draftKey);
    const finalPortionText = hasPortionTextDraft
      ? (slotPortionTextDrafts[draftKey]?.trim() || null)
      : null;
    const hasNotesDraft = Object.prototype.hasOwnProperty.call(slotNotesDrafts, draftKey);
    const notes = hasNotesDraft ? (slotNotesDrafts[draftKey]?.trim() || null) : (fallbackNotes || null);

    setBusyState("slotFinalize");
    setErrorMessage(null);

    try {
      await requestJson(token.trim(), `/v1/meal-plan-meals/${mealPlanMealId}/slot-selections/${slotCode}`, {
        method: "PUT",
        body: JSON.stringify({
          portion_multiplier: portionMultiplier,
          final_portion_text: finalPortionText,
          notes,
        }),
      });

      const currentMealPlanId = mealPlans[0]?.id;
      if (!currentMealPlanId) {
        return;
      }

      await loadMealPlanArtifacts(currentMealPlanId, token.trim());
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "No se pudo actualizar el slot.");
    } finally {
      setBusyState("idle");
    }
  }

  async function downloadFinalSummaryJson() {
    const currentMealPlanId = mealPlans[0]?.id;
    if (!currentMealPlanId) {
      setErrorMessage("Genera un plan antes de exportar.");
      return;
    }

    setBusyState("export");
    setErrorMessage(null);

    try {
      const payload = (await requestJson(
        token.trim(),
        `/v1/meal-plans/${currentMealPlanId}/final-summary`,
      )) as FinalSummary;
      const blob = new Blob([JSON.stringify(payload, null, 2)], {
        type: "application/json;charset=utf-8",
      });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `meal-plan-${currentMealPlanId}-final-summary.json`;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "No se pudo descargar el resumen.");
    } finally {
      setBusyState("idle");
    }
  }

  function openPrintView() {
    const currentMealPlanId = mealPlans[0]?.id;
    if (!currentMealPlanId) {
      setErrorMessage("Genera un plan antes de abrir la vista imprimible.");
      return;
    }

    window.open(`/meal-plans/${currentMealPlanId}/print`, "_blank", "noopener,noreferrer");
  }

  const selectedPatient = patients.find((patient) => patient.id === selectedPatientId) || null;
  const selectedConsultation =
    consultations.find((consultation) => consultation.id === selectedConsultationId) || null;
  const latestEvaluation = evaluations[0] || null;
  const latestStrategy = strategies[0] || null;
  const latestDistribution = distributions[0] || null;
  const latestMealPlan = mealPlans[0] || null;

  useEffect(() => {
    setPlanNotesDraft(latestMealPlan?.notes || "");
  }, [latestMealPlan?.id, latestMealPlan?.notes]);

  return (
    <div className="dashboard-shell">
      <section className="hero">
        <p className="eyebrow">Evaluation Console</p>
        <h1>Pacientes, consultas y evaluaciones en una sola vista.</h1>
        <p className="lede">
          Esta interfaz usa el JWT de la API para consultar pacientes existentes,
          revisar mediciones y ejecutar la evaluacion energetica base del MVP.
        </p>
      </section>

      <section className="panel token-panel">
        <div>
          <h2>JWT de trabajo</h2>
          <p className="panel-copy">
            Pega aqui el `access_token` obtenido desde `POST /v1/auth/login`.
          </p>
        </div>
        <textarea
          className="token-input"
          value={token}
          onChange={(event) => setToken(event.target.value)}
          placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
          rows={4}
        />
        <div className="button-row">
          <button type="button" onClick={() => void loadPatients()} disabled={busyState !== "idle"}>
            {busyState === "patients" ? "Cargando..." : "Cargar pacientes"}
          </button>
          <button type="button" className="ghost-button" onClick={() => setToken("")}>
            Limpiar token
          </button>
        </div>
        {errorMessage ? <p className="status-error">{errorMessage}</p> : null}
      </section>

      <section className="dashboard-grid">
        <article className="panel">
          <div className="panel-heading">
            <h2>Pacientes</h2>
            <span>{patients.length} registrados</span>
          </div>
          <div className="stack-list">
            {patients.map((patient) => (
              <button
                key={patient.id}
                type="button"
                className={patient.id === selectedPatientId ? "list-card is-active" : "list-card"}
                onClick={() => setSelectedPatientId(patient.id)}
              >
                <strong>
                  {patient.first_name} {patient.last_name}
                </strong>
                <span>
                  {patient.sex} · {patient.birth_date}
                </span>
              </button>
            ))}
            {patients.length === 0 ? <p className="empty-state">Sin pacientes cargados todavia.</p> : null}
          </div>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <h2>Expediente</h2>
            <span>{selectedPatient ? `Paciente #${selectedPatient.id}` : "Selecciona un paciente"}</span>
          </div>
          {selectedPatient ? (
            <dl className="key-value-list">
              <div>
                <dt>Contacto</dt>
                <dd>{selectedPatient.email || selectedPatient.phone || "sin dato"}</dd>
              </div>
              <div>
                <dt>Objetivo</dt>
                <dd>{selectedPatient.record?.primary_goal || "sin dato"}</dd>
              </div>
              <div>
                <dt>Alergias</dt>
                <dd>{selectedPatient.record?.allergies || "sin dato"}</dd>
              </div>
              <div>
                <dt>Preferencias</dt>
                <dd>{selectedPatient.record?.food_preferences || "sin dato"}</dd>
              </div>
            </dl>
          ) : (
            <p className="empty-state">Sin expediente seleccionado.</p>
          )}
        </article>

        <article className="panel">
          <div className="panel-heading">
            <h2>Consultas</h2>
            <span>{consultations.length} disponibles</span>
          </div>
          <div className="stack-list">
            {consultations.map((consultation) => (
              <button
                key={consultation.id}
                type="button"
                className={consultation.id === selectedConsultationId ? "list-card is-active" : "list-card"}
                onClick={() => setSelectedConsultationId(consultation.id)}
              >
                <strong>{consultation.consultation_date}</strong>
                <span>{consultation.reason || "Sin motivo capturado"}</span>
              </button>
            ))}
            {consultations.length === 0 ? (
              <p className="empty-state">Este paciente no tiene consultas todavia.</p>
            ) : null}
          </div>
        </article>

        <article className="panel accent-panel">
          <div className="panel-heading">
            <h2>Consulta seleccionada</h2>
            <button
              type="button"
              onClick={() => void createEvaluation()}
              disabled={!selectedConsultationId || busyState !== "idle"}
            >
              {busyState === "calculate" ? "Calculando..." : "Ejecutar evaluacion"}
            </button>
          </div>
          {selectedConsultation ? (
            <dl className="key-value-list">
              <div>
                <dt>Fecha</dt>
                <dd>{selectedConsultation.consultation_date}</dd>
              </div>
              <div>
                <dt>Motivo</dt>
                <dd>{selectedConsultation.reason || "sin dato"}</dd>
              </div>
              <div>
                <dt>Peso</dt>
                <dd>{formatValue(selectedConsultation.measurement?.weight_kg)} kg</dd>
              </div>
              <div>
                <dt>Talla</dt>
                <dd>{formatValue(selectedConsultation.measurement?.height_cm)} cm</dd>
              </div>
              <div>
                <dt>Actividad</dt>
                <dd>{selectedConsultation.measurement?.activity_level || "sin dato"}</dd>
              </div>
            </dl>
          ) : (
            <p className="empty-state">Selecciona una consulta para revisar mediciones.</p>
          )}
        </article>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Historial clinico</h2>
          <span>
            {patientHistory
              ? `${patientHistory.consultation_count} consultas`
              : "Sin historial"}
          </span>
        </div>
        {patientHistory ? (
          <div className="formula-grid">
            {patientHistory.items.map((item) => (
              <article key={item.consultation_id} className="formula-card">
                <p className="formula-family">
                  Consulta #{item.consultation_id} · {item.consultation_date}
                </p>
                <h3>{item.reason || "Seguimiento clinico"}</h3>
                <div className="stack-list">
                  <div className="result-card">
                    <strong>Mediciones</strong>
                    <span>
                      Peso {formatValue(item.measurement?.weight_kg)} kg · Talla{" "}
                      {formatValue(item.measurement?.height_cm)} cm
                    </span>
                    <span>Actividad {formatValue(item.measurement?.activity_level)}</span>
                  </div>
                  {item.evaluation ? (
                    <div className="result-card">
                      <strong>Evaluacion #{item.evaluation.id}</strong>
                      <span>IMC {formatValue(item.evaluation.bmi)}</span>
                      <span>GET mantenimiento {formatValue(item.evaluation.maintenance_energy_kcal)} kcal</span>
                    </div>
                  ) : null}
                  {item.strategy ? (
                    <div className="result-card">
                      <strong>Estrategia #{item.strategy.id}</strong>
                      <span>{item.strategy.goal_code}</span>
                      <span>
                        Objetivo {formatValue(item.strategy.target_energy_kcal)} kcal · P{" "}
                        {formatValue(item.strategy.protein_g)} · G {formatValue(item.strategy.fat_g)} · C{" "}
                        {formatValue(item.strategy.carbs_g)}
                      </span>
                    </div>
                  ) : null}
                  {item.meal_plan ? (
                    <div className="result-card">
                      <strong>Plan #{item.meal_plan.id}</strong>
                      <span>
                        {item.meal_plan.status} · {item.meal_plan.pattern_code} ·{" "}
                        {formatValue(item.meal_plan.completion_pct)}%
                      </span>
                      <span>
                        Slots {item.meal_plan.selected_slots}/{item.meal_plan.total_slots}
                      </span>
                    </div>
                  ) : null}
                  {item.delta_vs_previous ? (
                    <div className="result-card">
                      <strong>Cambio vs consulta previa</strong>
                      <span>
                        Peso {formatValue(item.delta_vs_previous.weight_kg)} kg · IMC{" "}
                        {formatValue(item.delta_vs_previous.bmi)}
                      </span>
                      <span>
                        Mant {formatValue(item.delta_vs_previous.maintenance_energy_kcal)} kcal · Objetivo{" "}
                        {formatValue(item.delta_vs_previous.target_energy_kcal)} kcal
                      </span>
                      <span>
                        P {formatValue(item.delta_vs_previous.protein_g)} · G{" "}
                        {formatValue(item.delta_vs_previous.fat_g)} · C{" "}
                        {formatValue(item.delta_vs_previous.carbs_g)}
                      </span>
                    </div>
                  ) : null}
                </div>
              </article>
            ))}
          </div>
        ) : (
          <p className="empty-state">Selecciona un paciente para cargar su historial entre consultas.</p>
        )}
      </section>

      <section className="results-grid">
        <article className="panel">
          <div className="panel-heading">
            <h2>Evaluaciones</h2>
            <span>{evaluations.length} registradas</span>
          </div>
          <div className="stack-list">
            {evaluations.map((evaluation) => (
              <div key={evaluation.id} className="result-card">
                <strong>Evaluacion #{evaluation.id}</strong>
                <span>{evaluation.status}</span>
                <span>{evaluation.formula_set_version}</span>
                <span>{new Date(evaluation.created_at).toLocaleString("es-MX")}</span>
              </div>
            ))}
            {evaluations.length === 0 ? <p className="empty-state">No hay evaluaciones para esta consulta.</p> : null}
          </div>
        </article>

        <article className="panel accent-panel">
          <div className="panel-heading">
            <h2>Ultimo resultado</h2>
            <span>{latestEvaluation ? `Eval #${latestEvaluation.id}` : "Sin calculo"}</span>
          </div>
          {latestEvaluation ? (
            <>
              <dl className="metric-grid">
                {Object.entries(latestEvaluation.summary_payload).map(([key, value]) => (
                  <div key={key}>
                    <dt>{key}</dt>
                    <dd>{formatValue(value)}</dd>
                  </div>
                ))}
              </dl>
              <div className="warning-block">
                {latestEvaluation.warnings_payload.map((warning) => (
                  <p key={warning}>{warning}</p>
                ))}
              </div>
            </>
          ) : (
            <p className="empty-state">Ejecuta una evaluacion para ver el resumen calculado.</p>
          )}
        </article>
      </section>

      <section className="results-grid">
        <article className="panel">
          <div className="panel-heading">
            <h2>Estrategia nutricional</h2>
            <span>{strategies.length} generadas</span>
          </div>
          <div className="strategy-controls">
            <label className="strategy-label" htmlFor="strategy-goal">
              Objetivo
            </label>
            <select
              id="strategy-goal"
              className="strategy-select"
              value={selectedGoalCode}
              onChange={(event) => setSelectedGoalCode(event.target.value)}
            >
              {strategyGoalOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <button
              type="button"
              onClick={() => void createStrategy()}
              disabled={!latestEvaluation || busyState !== "idle"}
            >
              {busyState === "strategy" ? "Generando..." : "Generar estrategia"}
            </button>
          </div>
          <div className="stack-list">
            {strategies.map((strategy) => (
              <div key={strategy.id} className="result-card">
                <strong>Estrategia #{strategy.id}</strong>
                <span>{strategy.goal_code}</span>
                <span>{strategy.strategy_set_version}</span>
                <span>{new Date(strategy.created_at).toLocaleString("es-MX")}</span>
              </div>
            ))}
            {strategies.length === 0 ? (
              <p className="empty-state">Aun no hay estrategias para la evaluacion actual.</p>
            ) : null}
          </div>
        </article>

        <article className="panel accent-panel">
          <div className="panel-heading">
            <h2>Ultima estrategia</h2>
            <span>{latestStrategy ? `Strategy #${latestStrategy.id}` : "Sin estrategia"}</span>
          </div>
          {latestStrategy ? (
            <>
              <dl className="metric-grid">
                {Object.entries(latestStrategy.recommendation_payload).map(([key, value]) => (
                  <div key={key}>
                    <dt>{key}</dt>
                    <dd>{formatValue(value)}</dd>
                  </div>
                ))}
              </dl>
              <div className="warning-block">
                {latestStrategy.warnings_payload.map((warning) => (
                  <p key={warning}>{warning}</p>
                ))}
              </div>
            </>
          ) : (
            <p className="empty-state">Genera una estrategia para ver kcal objetivo y macros base.</p>
          )}
        </article>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Trazabilidad por formula</h2>
          <span>{latestEvaluation ? latestEvaluation.formula_results.length : 0} formulas</span>
        </div>
        {latestEvaluation ? (
          <div className="formula-grid">
            {latestEvaluation.formula_results.map((result) => (
              <article key={result.id} className="formula-card">
                <p className="formula-family">{result.formula_family}</p>
                <h3>{result.formula_code}</h3>
                <pre>{JSON.stringify(result.output_payload, null, 2)}</pre>
                <p className="formula-note">{result.source_note || "Sin nota de fuente"}</p>
              </article>
            ))}
          </div>
        ) : (
          <p className="empty-state">La trazabilidad aparecera cuando exista al menos una evaluacion.</p>
        )}
      </section>

      <section className="results-grid">
        <article className="panel">
          <div className="panel-heading">
            <h2>Distribucion diaria</h2>
            <span>{distributions.length} generadas</span>
          </div>
          <div className="strategy-controls">
            <label className="strategy-label" htmlFor="meal-pattern">
              Patron
            </label>
            <select
              id="meal-pattern"
              className="strategy-select"
              value={selectedPatternCode}
              onChange={(event) => setSelectedPatternCode(event.target.value)}
            >
              {mealPatternOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <button
              type="button"
              onClick={() => void createDistribution()}
              disabled={!latestStrategy || busyState !== "idle"}
            >
              {busyState === "distribution" ? "Generando..." : "Generar distribucion"}
            </button>
          </div>
          <div className="stack-list">
            {distributions.map((distribution) => (
              <div key={distribution.id} className="result-card">
                <strong>Distribucion #{distribution.id}</strong>
                <span>{distribution.pattern_code}</span>
                <span>{distribution.distribution_set_version}</span>
                <span>{new Date(distribution.created_at).toLocaleString("es-MX")}</span>
              </div>
            ))}
            {distributions.length === 0 ? (
              <p className="empty-state">Aun no hay distribuciones para la estrategia actual.</p>
            ) : null}
          </div>
        </article>

        <article className="panel accent-panel">
          <div className="panel-heading">
            <h2>Ultima distribucion</h2>
            <span>
              {latestDistribution ? `Distribution #${latestDistribution.id}` : "Sin distribucion"}
            </span>
          </div>
          {latestDistribution ? (
            <>
              <dl className="metric-grid">
                {Object.entries(latestDistribution.recommendation_payload).map(([key, value]) =>
                  key === "meals" ? null : (
                    <div key={key}>
                      <dt>{key}</dt>
                      <dd>{formatValue(value)}</dd>
                    </div>
                  ),
                )}
              </dl>
              <div className="stack-list">
                {(latestDistribution.recommendation_payload.meals || []).map((meal) => (
                  <div key={meal.meal_code} className="result-card">
                    <strong>{meal.label}</strong>
                    <span>{formatValue(meal.allocation_pct)}%</span>
                    <span>{formatValue(meal.target_energy_kcal)} kcal</span>
                    <span>
                      P {formatValue(meal.protein_g)} g · G {formatValue(meal.fat_g)} g · C{" "}
                      {formatValue(meal.carbs_g)} g
                    </span>
                  </div>
                ))}
              </div>
              <div className="warning-block">
                {latestDistribution.warnings_payload.map((warning) => (
                  <p key={warning}>{warning}</p>
                ))}
              </div>
            </>
          ) : (
            <p className="empty-state">Genera una distribucion para repartir kcal y macros por tiempo.</p>
          )}
        </article>
      </section>

      <section className="results-grid">
        <article className="panel">
          <div className="panel-heading">
            <h2>Plan base</h2>
            <span>{mealPlans.length} generados</span>
          </div>
          <div className="strategy-controls">
            <label className="strategy-label" htmlFor="plan-notes">
              Notas del plan
            </label>
            <textarea
              id="plan-notes"
              className="token-input"
              value={planNotesDraft}
              onChange={(event) => setPlanNotesDraft(event.target.value)}
              placeholder="Observaciones clinicas, adherencia, preferencias operativas..."
              rows={3}
            />
            <div className="button-row">
              <button
                type="button"
                onClick={() => void createMealPlan()}
                disabled={!latestDistribution || busyState !== "idle"}
              >
                {busyState === "mealPlan" ? "Generando..." : "Generar plan base"}
              </button>
              <button
                type="button"
                className="ghost-button"
                onClick={() => void updateMealPlanStatus("reviewed")}
                disabled={!latestMealPlan || busyState !== "idle"}
              >
                {busyState === "mealPlanUpdate" ? "Guardando..." : "Marcar como revisado"}
              </button>
              <button
                type="button"
                className="ghost-button"
                onClick={() => void updateMealPlanStatus("finalized")}
                disabled={!latestMealPlan || busyState !== "idle"}
              >
                {busyState === "mealPlanUpdate" ? "Guardando..." : "Finalizar plan"}
              </button>
              <button
                type="button"
                className="ghost-button"
                onClick={() => void updateMealPlanStatus("ready_for_export")}
                disabled={!latestMealPlan || busyState !== "idle"}
              >
                {busyState === "mealPlanUpdate" ? "Guardando..." : "Listo para exportar"}
              </button>
            </div>
          </div>
          <div className="stack-list">
            {mealPlans.map((mealPlan) => (
              <div key={mealPlan.id} className="result-card">
                <strong>Plan #{mealPlan.id}</strong>
                <span>{mealPlan.status}</span>
                <span>{mealPlan.plan_set_version}</span>
                <span>{new Date(mealPlan.created_at).toLocaleString("es-MX")}</span>
              </div>
            ))}
            {mealPlans.length === 0 ? (
              <p className="empty-state">Aun no hay planes base para la distribucion actual.</p>
            ) : null}
          </div>
        </article>

        <article className="panel accent-panel">
          <div className="panel-heading">
            <h2>Ultimo plan</h2>
            <span>{latestMealPlan ? `Plan #${latestMealPlan.id}` : "Sin plan"}</span>
          </div>
          {latestMealPlan ? (
            <>
              <dl className="metric-grid">
                <div>
                  <dt>status</dt>
                  <dd>{latestMealPlan.status}</dd>
                </div>
                <div>
                  <dt>plan_set_version</dt>
                  <dd>{latestMealPlan.plan_set_version}</dd>
                </div>
                <div>
                  <dt>notes</dt>
                  <dd>{latestMealPlan.notes || "sin dato"}</dd>
                </div>
              </dl>
              <div className="formula-grid">
                {latestMealPlan.meals.map((meal) => (
                  <article key={meal.id} className="formula-card">
                    <p className="formula-family">{meal.meal_code}</p>
                    <h3>{meal.label}</h3>
                    <p>
                      {formatValue(meal.target_energy_kcal)} kcal · P {formatValue(meal.protein_target_g)} g · G{" "}
                      {formatValue(meal.fat_target_g)} g · C {formatValue(meal.carbs_target_g)} g
                    </p>
                    <pre>{JSON.stringify(meal.structure_payload, null, 2)}</pre>
                  </article>
                ))}
              </div>
            </>
          ) : (
            <p className="empty-state">Genera un plan base para revisar la estructura por tiempo.</p>
          )}
        </article>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Sugerencias del catalogo</h2>
          <span>{mealPlanSuggestions ? `Plan #${mealPlanSuggestions.meal_plan_id}` : "Sin sugerencias"}</span>
        </div>
        {mealPlanSuggestions ? (
          <>
            <div className="warning-block">
              {mealPlanSuggestions.warnings.map((warning) => (
                <p key={warning}>{warning}</p>
              ))}
            </div>
            <div className="formula-grid">
              {mealPlanSuggestions.meals.map((meal) => (
                <article key={meal.meal_code} className="formula-card">
                  <p className="formula-family">{meal.meal_code}</p>
                  <h3>{meal.label}</h3>
                  <p>
                    {formatValue(meal.target_energy_kcal)} kcal · P {formatValue(meal.protein_target_g)} g · G{" "}
                    {formatValue(meal.fat_target_g)} g · C {formatValue(meal.carbs_target_g)} g
                  </p>
                  <div className="stack-list">
                    {meal.slots.map((slot) => (
                      <div key={slot.slot_code} className="result-card">
                        <strong>{slot.label}</strong>
                        <span>{slot.guidance}</span>
                        <span>
                          Recomendado:{" "}
                          {slot.recommended_candidate
                            ? `${slot.recommended_candidate.name} (${formatValue(slot.recommended_candidate.fit_score)})`
                            : "sin sugerencia"}
                        </span>
                        <span>
                          Seleccionado:{" "}
                          {slot.selected_food ? `${slot.selected_food.name}` : "sin seleccion"}
                        </span>
                        {slot.selected_food ? (
                          <>
                            <label>
                              Multiplicador final
                              <input
                                type="number"
                                min="0.5"
                                max="3"
                                step="0.25"
                                value={
                                  slotMultiplierDrafts[buildSlotDraftKey(meal.id, slot.slot_code)] ??
                                  String(slot.selected_food.portion_multiplier ?? 1)
                                }
                                onChange={(event) =>
                                  {
                                    const draftKey = buildSlotDraftKey(meal.id, slot.slot_code);
                                    const nextValue = event.target.value;
                                    setSlotMultiplierDrafts((current) => ({
                                      ...current,
                                      [draftKey]: nextValue,
                                    }));
                                    if (
                                      !Object.prototype.hasOwnProperty.call(slotPortionTextDrafts, draftKey)
                                      && slot.selected_food
                                      && nextValue !== ""
                                    ) {
                                      const parsedValue = Number(nextValue);
                                      if (!Number.isNaN(parsedValue) && parsedValue > 0) {
                                        setSlotPortionTextDrafts((current) => ({
                                          ...current,
                                          [draftKey]: buildAutoPortionText(slot.selected_food!, parsedValue),
                                        }));
                                      }
                                    }
                                  }
                                }
                              />
                            </label>
                            <label>
                              Porcion final
                              <input
                                type="text"
                                value={
                                  slotPortionTextDrafts[buildSlotDraftKey(meal.id, slot.slot_code)] ??
                                  (slot.selected_food.suggested_portion_text || "")
                                }
                                onChange={(event) =>
                                  setSlotPortionTextDrafts((current) => ({
                                    ...current,
                                    [buildSlotDraftKey(meal.id, slot.slot_code)]: event.target.value,
                                  }))
                                }
                              />
                            </label>
                            <label>
                              Nota del slot
                              <textarea
                                rows={2}
                                value={
                                  slotNotesDrafts[buildSlotDraftKey(meal.id, slot.slot_code)] ??
                                  (slot.selected_food.notes || "")
                                }
                                onChange={(event) =>
                                  setSlotNotesDrafts((current) => ({
                                    ...current,
                                    [buildSlotDraftKey(meal.id, slot.slot_code)]: event.target.value,
                                  }))
                                }
                              />
                            </label>
                            <button
                              type="button"
                              disabled={busyState !== "idle"}
                              onClick={() =>
                                void updateSlotSelection(
                                  meal.id,
                                  slot.slot_code,
                                  slot.selected_food?.portion_multiplier ?? 1,
                                  slot.selected_food?.notes,
                                )
                              }
                            >
                              {busyState === "slotFinalize" ? "Guardando..." : "Cerrar slot"}
                            </button>
                          </>
                        ) : null}
                        {slot.candidates.map((candidate) => (
                          <button
                            key={candidate.food_id}
                            type="button"
                            className="list-card"
                            disabled={busyState !== "idle"}
                            onClick={() => void selectSlotFood(meal.id, slot.slot_code, candidate.food_id)}
                          >
                            <strong>{candidate.name}</strong>
                            <span>
                              {candidate.portion_label} · {formatValue(candidate.energy_kcal)} kcal · fit{" "}
                              {formatValue(candidate.fit_score)}
                            </span>
                            <span>{candidate.suggested_portion_text || "sin porcion sugerida"}</span>
                            <span>
                              Ajustado: {formatValue(candidate.adjusted_energy_kcal)} kcal · P{" "}
                              {formatValue(candidate.adjusted_protein_g)} g · G{" "}
                              {formatValue(candidate.adjusted_fat_g)} g · C{" "}
                              {formatValue(candidate.adjusted_carbs_g)} g
                            </span>
                          </button>
                        ))}
                      </div>
                    ))}
                  </div>
                </article>
              ))}
            </div>
          </>
        ) : (
          <p className="empty-state">Genera un plan base para ver candidatos reales del catalogo por bloque.</p>
        )}
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Cierre clinico</h2>
          <span>
            {finalSummary ? `${finalSummary.status} · ${formatValue(finalSummary.completion_pct)}%` : "Sin resumen"}
          </span>
        </div>
        {finalSummary ? (
          <>
            <dl className="metric-grid">
              <div>
                <dt>paciente</dt>
                <dd>{finalSummary.patient.full_name}</dd>
              </div>
              <div>
                <dt>consulta</dt>
                <dd>{finalSummary.consultation_date}</dd>
              </div>
              <div>
                <dt>objetivo</dt>
                <dd>{finalSummary.goal_code}</dd>
              </div>
              <div>
                <dt>patron</dt>
                <dd>{finalSummary.pattern_code}</dd>
              </div>
              <div>
                <dt>slots</dt>
                <dd>
                  {finalSummary.selected_slots}/{finalSummary.total_slots}
                </dd>
              </div>
              <div>
                <dt>exportable</dt>
                <dd>{finalSummary.export_ready ? "si" : "no"}</dd>
              </div>
            </dl>
            {finalSummary.plan_notes ? (
              <div className="result-card">
                <strong>Notas del plan</strong>
                <span>{finalSummary.plan_notes}</span>
              </div>
            ) : null}
            <div className="button-row">
              <button
                type="button"
                className="ghost-button"
                disabled={busyState !== "idle"}
                onClick={() => openPrintView()}
              >
                Abrir vista imprimible
              </button>
              <button
                type="button"
                className="ghost-button"
                disabled={busyState !== "idle"}
                onClick={() => void downloadFinalSummaryJson()}
              >
                {busyState === "export" ? "Descargando..." : "Descargar JSON"}
              </button>
            </div>
            <div className="warning-block">
              {finalSummary.warnings.map((warning) => (
                <p key={warning}>{warning}</p>
              ))}
            </div>
            <div className="formula-grid">
              {finalSummary.meals.map((meal) => (
                <article key={meal.meal_plan_meal_id} className="formula-card">
                  <p className="formula-family">{meal.meal_code}</p>
                  <h3>{meal.label}</h3>
                  <p>
                    kcal {formatValue(meal.selected_energy_kcal)} / {formatValue(meal.target_energy_kcal)} · P{" "}
                    {formatValue(meal.selected_protein_g)} / {formatValue(meal.target_protein_g)} · G{" "}
                    {formatValue(meal.selected_fat_g)} / {formatValue(meal.target_fat_g)} · C{" "}
                    {formatValue(meal.selected_carbs_g)} / {formatValue(meal.target_carbs_g)}
                  </p>
                  <div className="stack-list">
                    {meal.slots.map((slot) => (
                      <div key={slot.slot_code} className="result-card">
                        <strong>{slot.label}</strong>
                        <span>{slot.guidance}</span>
                        <span>
                          {slot.food_name
                            ? `${slot.food_name} · ${slot.portion_text || "sin porcion"}`
                            : "Pendiente de seleccionar"}
                        </span>
                        {slot.food_name ? (
                          <>
                            <span>
                              Ajustado: {formatValue(slot.adjusted_energy_kcal)} kcal · P{" "}
                              {formatValue(slot.adjusted_protein_g)} g · G{" "}
                              {formatValue(slot.adjusted_fat_g)} g · C {formatValue(slot.adjusted_carbs_g)} g
                            </span>
                            {slot.notes ? <span>Nota: {slot.notes}</span> : null}
                          </>
                        ) : null}
                      </div>
                    ))}
                  </div>
                </article>
              ))}
            </div>
          </>
        ) : (
          <p className="empty-state">Genera y llena un plan para obtener el resumen final del dia.</p>
        )}
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Menu diario</h2>
          <span>{dailyMenu ? `${dailyMenu.status} · ${formatValue(dailyMenu.completion_pct)}%` : "Sin menu"}</span>
        </div>
        {dailyMenu ? (
          <>
            <dl className="metric-grid">
              <div>
                <dt>slots</dt>
                <dd>
                  {dailyMenu.selected_slots}/{dailyMenu.total_slots}
                </dd>
              </div>
              <div>
                <dt>kcal</dt>
                <dd>
                  {formatValue(dailyMenu.selected_energy_kcal)} / {formatValue(dailyMenu.target_energy_kcal)}
                </dd>
              </div>
              <div>
                <dt>proteina</dt>
                <dd>
                  {formatValue(dailyMenu.selected_protein_g)} / {formatValue(dailyMenu.target_protein_g)}
                </dd>
              </div>
              <div>
                <dt>grasa</dt>
                <dd>
                  {formatValue(dailyMenu.selected_fat_g)} / {formatValue(dailyMenu.target_fat_g)}
                </dd>
              </div>
              <div>
                <dt>carbs</dt>
                <dd>
                  {formatValue(dailyMenu.selected_carbs_g)} / {formatValue(dailyMenu.target_carbs_g)}
                </dd>
              </div>
            </dl>
            <div className="warning-block">
              {dailyMenu.warnings.map((warning) => (
                <p key={warning}>{warning}</p>
              ))}
            </div>
            <div className="formula-grid">
              {dailyMenu.meals.map((meal) => (
                <article key={meal.meal_plan_meal_id} className="formula-card">
                  <p className="formula-family">{meal.meal_code}</p>
                  <h3>{meal.label}</h3>
                  <p>
                    Cobertura {meal.covered_slots}/{meal.total_slots} · {formatValue(meal.completion_pct)}%
                  </p>
                  <p>
                    kcal {formatValue(meal.selected_energy_kcal)} / {formatValue(meal.target_energy_kcal)} · P{" "}
                    {formatValue(meal.selected_protein_g)} / {formatValue(meal.protein_target_g)} · G{" "}
                    {formatValue(meal.selected_fat_g)} / {formatValue(meal.fat_target_g)} · C{" "}
                    {formatValue(meal.selected_carbs_g)} / {formatValue(meal.carbs_target_g)}
                  </p>
                  <div className="stack-list">
                    {meal.slots.map((slot) => (
                      <div key={slot.slot_code} className="result-card">
                        <strong>{slot.label}</strong>
                        <span>{slot.guidance}</span>
                        <span>
                          {slot.selected_food
                            ? `${slot.selected_food.name} · ${
                                slot.selected_food.suggested_portion_text || slot.selected_food.portion_label
                              }`
                            : "Pendiente de seleccionar"}
                        </span>
                        {slot.selected_food ? (
                          <>
                            <span>
                              Ajustado: {formatValue(slot.selected_food.adjusted_energy_kcal)} kcal · P{" "}
                              {formatValue(slot.selected_food.adjusted_protein_g)} g · G{" "}
                              {formatValue(slot.selected_food.adjusted_fat_g)} g · C{" "}
                              {formatValue(slot.selected_food.adjusted_carbs_g)} g
                            </span>
                            {slot.selected_food.notes ? <span>Nota: {slot.selected_food.notes}</span> : null}
                          </>
                        ) : null}
                      </div>
                    ))}
                    {meal.pending_slots.length > 0 ? (
                      <div className="result-card">
                        <strong>Slots pendientes</strong>
                        <span>{meal.pending_slots.join(", ")}</span>
                      </div>
                    ) : null}
                  </div>
                </article>
              ))}
            </div>
          </>
        ) : (
          <p className="empty-state">Selecciona alimentos en el plan para consolidar el menu diario.</p>
        )}
      </section>
    </div>
  );
}

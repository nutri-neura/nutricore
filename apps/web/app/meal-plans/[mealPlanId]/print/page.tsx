"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

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

function formatValue(value: unknown) {
  if (value === null || value === undefined || value === "") {
    return "sin dato";
  }

  if (typeof value === "number") {
    return Number.isInteger(value) ? `${value}` : value.toFixed(2);
  }

  return String(value);
}

export default function PrintableMealPlanPage() {
  const params = useParams<{ mealPlanId: string }>();
  const mealPlanId = params.mealPlanId;
  const [summary, setSummary] = useState<FinalSummary | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    async function run() {
      const token = window.localStorage.getItem(TOKEN_STORAGE_KEY);
      if (!token) {
        setErrorMessage("No hay JWT en localStorage. Abre primero el dashboard y vuelve a intentar.");
        return;
      }

      const response = await fetch(`/api/proxy/v1/meal-plans/${mealPlanId}/final-summary`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        setErrorMessage("No se pudo cargar el resumen final para impresion.");
        return;
      }

      const payload = (await response.json()) as FinalSummary;
      setSummary(payload);
    }

    void run();
  }, [mealPlanId]);

  return (
    <main className="print-page">
      <div className="print-toolbar">
        <Link href="/patients" className="ghost-link">
          Volver al dashboard
        </Link>
        <button type="button" onClick={() => window.print()}>
          Imprimir / Guardar PDF
        </button>
      </div>

      {errorMessage ? <p className="status-error">{errorMessage}</p> : null}

      {summary ? (
        <article className="print-sheet">
          <header className="print-header">
            <div>
              <p className="eyebrow">NutriCore Clinical Export</p>
              <h1>Plan diario final</h1>
            </div>
            <div className="print-meta">
              <span>Plan #{summary.meal_plan_id}</span>
              <span>{summary.status}</span>
              <span>{summary.export_ready ? "listo para exportar" : "interno"}</span>
            </div>
          </header>

          <section className="print-grid">
            <div className="print-section">
              <h2>Paciente</h2>
              <p>{summary.patient.full_name}</p>
              <p>{summary.patient.sex}</p>
              <p>Nacimiento: {summary.patient.birth_date}</p>
            </div>
            <div className="print-section">
              <h2>Consulta</h2>
              <p>Consulta #{summary.consultation_id}</p>
              <p>{summary.consultation_date}</p>
              <p>Objetivo: {summary.goal_code}</p>
              <p>Patron: {summary.pattern_code}</p>
            </div>
            <div className="print-section">
              <h2>Resumen diario</h2>
              <p>Slots: {summary.selected_slots}/{summary.total_slots}</p>
              <p>Kcal: {formatValue(summary.selected_energy_kcal)} / {formatValue(summary.target_energy_kcal)}</p>
              <p>P: {formatValue(summary.selected_protein_g)} / {formatValue(summary.target_protein_g)}</p>
              <p>G: {formatValue(summary.selected_fat_g)} / {formatValue(summary.target_fat_g)}</p>
              <p>C: {formatValue(summary.selected_carbs_g)} / {formatValue(summary.target_carbs_g)}</p>
            </div>
          </section>

          {summary.plan_notes ? (
            <section className="print-section">
              <h2>Notas del plan</h2>
              <p>{summary.plan_notes}</p>
            </section>
          ) : null}

          {summary.warnings.length > 0 ? (
            <section className="print-section">
              <h2>Advertencias</h2>
              <ul>
                {summary.warnings.map((warning) => (
                  <li key={warning}>{warning}</li>
                ))}
              </ul>
            </section>
          ) : null}

          <section className="print-meals">
            {summary.meals.map((meal) => (
              <article key={meal.meal_plan_meal_id} className="print-meal">
                <h2>{meal.label}</h2>
                <p>
                  {formatValue(meal.selected_energy_kcal)} / {formatValue(meal.target_energy_kcal)} kcal · P{" "}
                  {formatValue(meal.selected_protein_g)} / {formatValue(meal.target_protein_g)} · G{" "}
                  {formatValue(meal.selected_fat_g)} / {formatValue(meal.target_fat_g)} · C{" "}
                  {formatValue(meal.selected_carbs_g)} / {formatValue(meal.target_carbs_g)}
                </p>
                <div className="print-slots">
                  {meal.slots.map((slot) => (
                    <div key={slot.slot_code} className="print-slot">
                      <strong>{slot.label}</strong>
                      <span>{slot.food_name ? `${slot.food_name} · ${slot.portion_text || "sin porcion"}` : "Pendiente"}</span>
                      <span>{slot.guidance}</span>
                      {slot.food_name ? (
                        <span>
                          Ajustado: {formatValue(slot.adjusted_energy_kcal)} kcal · P{" "}
                          {formatValue(slot.adjusted_protein_g)} g · G {formatValue(slot.adjusted_fat_g)} g · C{" "}
                          {formatValue(slot.adjusted_carbs_g)} g
                        </span>
                      ) : null}
                      {slot.notes ? <span>Nota: {slot.notes}</span> : null}
                    </div>
                  ))}
                </div>
              </article>
            ))}
          </section>
        </article>
      ) : null}
    </main>
  );
}

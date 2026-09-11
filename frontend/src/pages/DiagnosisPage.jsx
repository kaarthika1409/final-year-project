import React, { useState } from "react";
import {
  Brain, ChevronRight, Flame, Dumbbell, Sparkles,
  Activity, Heart, AlertCircle, CheckCircle, RefreshCw,
  Utensils, Coffee, Sun, Moon
} from "lucide-react";
import { api } from "../api";

// ─── Constants matching clean_patient_dataset.csv ───────────────────────────
const DISEASE_TYPES = ["Diabetes", "Hypertension", "Obesity"];
const SEVERITIES    = ["Mild", "Moderate", "Severe"];
const ACTIVITY_LEVELS = ["Active", "Moderate", "Sedentary"];
const DIETARY_RESTRICTIONS = ["Low_Sodium", "Low_Sugar"];
const ALLERGIES_LIST = ["Gluten", "Peanuts"];
const CUISINES = ["Chinese", "Indian", "Italian", "Mexican"];

const DIET_COLORS = {
  Balanced:   { bg: "from-emerald-500 to-teal-500",   badge: "bg-emerald-500/20 border-emerald-500/40 text-emerald-300" },
  Low_Carb:   { bg: "from-amber-500 to-orange-500",   badge: "bg-amber-500/20 border-amber-500/40 text-amber-300"     },
  Low_Sodium: { bg: "from-cyan-500 to-blue-500",      badge: "bg-cyan-500/20 border-cyan-500/40 text-cyan-300"        },
};

const DIET_DESCRIPTIONS = {
  Balanced:   "A well-rounded diet with balanced macronutrients — ideal for general health maintenance.",
  Low_Carb:   "A carbohydrate-restricted diet that helps manage blood glucose and support weight loss.",
  Low_Sodium: "A sodium-reduced diet that helps manage blood pressure and cardiovascular health.",
};

const MEAL_SLOT_META = {
  breakfast: { icon: Coffee, label: "Breakfast",  color: "text-amber-400"   },
  lunch:     { icon: Sun,    label: "Lunch",      color: "text-emerald-400" },
  dinner:    { icon: Moon,   label: "Dinner",     color: "text-purple-400"  },
  snacks:    { icon: Utensils, label: "Snacks",   color: "text-cyan-400"    },
};

// ─── Sub-component: DishCard ────────────────────────────────────────────────
function DishCard({ dish }) {
  return (
    <div className="p-4 rounded-2xl bg-white/5 border border-white/10 hover:border-emerald-500/30 transition-all">
      <div className="flex items-start justify-between gap-2 mb-2">
        <h4 className="font-bold text-sm text-white leading-tight">{dish.food_name}</h4>
        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 whitespace-nowrap">
          {dish.fit_reason}
        </span>
      </div>
      <p className="text-[11px] text-gray-500 mb-2 line-clamp-1">
        {dish.ingredients || dish.category}
      </p>
      <div className="flex items-center gap-3 text-xs">
        <span className="flex items-center gap-1 text-emerald-400 font-semibold">
          <Flame className="w-3 h-3" /> {Math.round(dish.calories_per_serving)} kcal
        </span>
        <span className="text-cyan-300">P: {dish.protein_g}g</span>
        <span className="text-amber-300">C: {dish.carbs_g}g</span>
        <span className="text-purple-300">F: {dish.fat_g}g</span>
      </div>
      <p className="text-[10px] text-gray-600 mt-1">{dish.serving_size_g}g serving • {dish.category}</p>
    </div>
  );
}

// ─── Main Page ───────────────────────────────────────────────────────────────
export default function DiagnosisPage() {
  const [form, setForm] = useState({
    age: 45,
    gender: "Male",
    weight_kg: 80,
    height_cm: 175,
    disease_type: "Hypertension",
    severity: "Mild",
    physical_activity_level: "Moderate",
    daily_caloric_intake: 2000,
    cholesterol: 200,
    blood_pressure: 130,
    glucose: 100,
    dietary_restrictions: "Low_Sodium",
    allergies: "Gluten",
    preferred_cuisine: "Indian",
    weekly_exercise_hours: 3,
    adherence_to_diet_plan: 7,
    dietary_nutrient_imbalance_score: 2.0,
  });

  const [prediction, setPrediction] = useState(null);
  const [dishes, setDishes]         = useState(null);
  const [mealPlan, setMealPlan]     = useState(null);
  const [loading, setLoading]       = useState(false);
  const [dishLoading, setDishLoading] = useState(false);
  const [error, setError]           = useState(null);
  const [activeTab, setActiveTab]   = useState("dishes"); // "dishes" | "mealplan"

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: ["age","weight_kg","height_cm","daily_caloric_intake","cholesterol","blood_pressure",
                "glucose","weekly_exercise_hours","adherence_to_diet_plan","dietary_nutrient_imbalance_score"]
              .includes(name) ? Number(value) : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setPrediction(null);
    setDishes(null);
    setMealPlan(null);

    try {
      // Step 1: Get ML prediction
      const pred = await api.predictDiet(form);
      setPrediction(pred);

      // Step 2: Fetch dish recommendations based on predicted diet
      setDishLoading(true);
      const recs = await api.getDishRecommendations(
        pred.diet_recommendation,
        form.allergies,
        20
      );
      setDishes(recs.dishes || []);
      setMealPlan(recs.meal_plan || null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setDishLoading(false);
    }
  };

  const dietMeta = prediction ? DIET_COLORS[prediction.diet_recommendation] || DIET_COLORS.Balanced : null;

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-16">

      {/* Header */}
      <div className="glass-card p-6 border border-white/10">
        <div className="flex items-center gap-3 mb-1">
          <div className="p-2 rounded-xl bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 border border-emerald-500/20">
            <Brain className="w-6 h-6 text-emerald-400" />
          </div>
          <h1 className="text-2xl font-extrabold text-white">Diet Diagnosis</h1>
        </div>
        <p className="text-sm text-gray-400 ml-14">
          Enter your health parameters to receive a personalised diet recommendation from the trained ML model,
          with real dish suggestions from our dataset of 4,768 dishes.
        </p>
      </div>

      {/* Form */}
      <div className="glass-card p-8 border border-white/10">
        <h2 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
          <Activity className="w-5 h-5 text-cyan-400" /> Patient Health Parameters
        </h2>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Row 1: Demographics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1.5">Age</label>
              <input type="number" name="age" required min={1} max={120}
                value={form.age} onChange={handleChange}
                className="w-full px-3 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-sm focus:border-emerald-500 focus:outline-none" />
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1.5">Gender</label>
              <select name="gender" value={form.gender} onChange={handleChange}
                className="w-full px-3 py-2.5 rounded-xl bg-[#151c2e] border border-white/10 text-white text-sm focus:border-emerald-500 focus:outline-none">
                <option>Female</option><option>Male</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1.5">Weight (kg)</label>
              <input type="number" name="weight_kg" required step="0.5" min={1}
                value={form.weight_kg} onChange={handleChange}
                className="w-full px-3 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-sm focus:border-emerald-500 focus:outline-none" />
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1.5">Height (cm)</label>
              <input type="number" name="height_cm" required min={1}
                value={form.height_cm} onChange={handleChange}
                className="w-full px-3 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-sm focus:border-emerald-500 focus:outline-none" />
            </div>
          </div>

          {/* Row 2: Medical */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1.5">Disease Type</label>
              <select name="disease_type" value={form.disease_type} onChange={handleChange}
                className="w-full px-3 py-2.5 rounded-xl bg-[#151c2e] border border-white/10 text-white text-sm focus:border-emerald-500 focus:outline-none">
                {DISEASE_TYPES.map(d => <option key={d}>{d}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1.5">Severity</label>
              <select name="severity" value={form.severity} onChange={handleChange}
                className="w-full px-3 py-2.5 rounded-xl bg-[#151c2e] border border-white/10 text-white text-sm focus:border-emerald-500 focus:outline-none">
                {SEVERITIES.map(s => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1.5">Activity Level</label>
              <select name="physical_activity_level" value={form.physical_activity_level} onChange={handleChange}
                className="w-full px-3 py-2.5 rounded-xl bg-[#151c2e] border border-white/10 text-white text-sm focus:border-emerald-500 focus:outline-none">
                {ACTIVITY_LEVELS.map(a => <option key={a}>{a}</option>)}
              </select>
            </div>
          </div>

          {/* Row 3: Clinical Values */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1.5">Daily Caloric Intake</label>
              <input type="number" name="daily_caloric_intake" required step="50"
                value={form.daily_caloric_intake} onChange={handleChange}
                className="w-full px-3 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-sm focus:border-emerald-500 focus:outline-none" />
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1.5">Cholesterol (mg/dL)</label>
              <input type="number" name="cholesterol" required
                value={form.cholesterol} onChange={handleChange}
                className="w-full px-3 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-sm focus:border-emerald-500 focus:outline-none" />
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1.5">Blood Pressure (mmHg)</label>
              <input type="number" name="blood_pressure" required
                value={form.blood_pressure} onChange={handleChange}
                className="w-full px-3 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-sm focus:border-emerald-500 focus:outline-none" />
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1.5">Glucose (mg/dL)</label>
              <input type="number" name="glucose" required
                value={form.glucose} onChange={handleChange}
                className="w-full px-3 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-sm focus:border-emerald-500 focus:outline-none" />
            </div>
          </div>

          {/* Row 4: Lifestyle */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1.5">Weekly Exercise (hrs)</label>
              <input type="number" name="weekly_exercise_hours" required step="0.5" min={0}
                value={form.weekly_exercise_hours} onChange={handleChange}
                className="w-full px-3 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-sm focus:border-emerald-500 focus:outline-none" />
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1.5">Diet Adherence (0–10)</label>
              <input type="number" name="adherence_to_diet_plan" required step="0.5" min={0} max={10}
                value={form.adherence_to_diet_plan} onChange={handleChange}
                className="w-full px-3 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-sm focus:border-emerald-500 focus:outline-none" />
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1.5">Nutrient Imbalance Score</label>
              <input type="number" name="dietary_nutrient_imbalance_score" required step="0.1" min={0}
                value={form.dietary_nutrient_imbalance_score} onChange={handleChange}
                className="w-full px-3 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-sm focus:border-emerald-500 focus:outline-none" />
            </div>
          </div>

          {/* Row 5: Dietary preferences */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1.5">Dietary Restriction</label>
              <select name="dietary_restrictions" value={form.dietary_restrictions} onChange={handleChange}
                className="w-full px-3 py-2.5 rounded-xl bg-[#151c2e] border border-white/10 text-white text-sm focus:border-emerald-500 focus:outline-none">
                {DIETARY_RESTRICTIONS.map(r => <option key={r}>{r}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1.5">Allergy</label>
              <select name="allergies" value={form.allergies} onChange={handleChange}
                className="w-full px-3 py-2.5 rounded-xl bg-[#151c2e] border border-white/10 text-white text-sm focus:border-emerald-500 focus:outline-none">
                {ALLERGIES_LIST.map(a => <option key={a}>{a}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1.5">Preferred Cuisine</label>
              <select name="preferred_cuisine" value={form.preferred_cuisine} onChange={handleChange}
                className="w-full px-3 py-2.5 rounded-xl bg-[#151c2e] border border-white/10 text-white text-sm focus:border-emerald-500 focus:outline-none">
                {CUISINES.map(c => <option key={c}>{c}</option>)}
              </select>
            </div>
          </div>

          {error && (
            <div className="flex items-center gap-2 p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <button type="submit" disabled={loading}
            className="w-full py-3.5 rounded-xl glow-button text-white font-bold text-sm flex items-center justify-center gap-2 disabled:opacity-60">
            {loading ? (
              <><RefreshCw className="w-4 h-4 animate-spin" /> Running ML Model...</>
            ) : (
              <><Brain className="w-4 h-4" /> Get Diet Recommendation <ChevronRight className="w-4 h-4" /></>
            )}
          </button>
        </form>
      </div>

      {/* ─── Prediction Result ─── */}
      {prediction && dietMeta && (
        <div className={`glass-card p-6 border border-white/10 relative overflow-hidden`}>
          <div className={`absolute inset-0 bg-gradient-to-br ${dietMeta.bg} opacity-5 pointer-events-none`} />
          <div className="relative flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-2xl bg-gradient-to-br ${dietMeta.bg} shadow-lg`}>
                <CheckCircle className="w-8 h-8 text-white" />
              </div>
              <div>
                <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-0.5">ML Model Recommendation</p>
                <h2 className="text-3xl font-extrabold text-white">
                  {prediction.diet_recommendation.replace("_", " ")}
                </h2>
                <p className="text-sm text-gray-400 mt-0.5">
                  {DIET_DESCRIPTIONS[prediction.diet_recommendation]}
                </p>
              </div>
            </div>

            <div className="flex flex-col items-end gap-2">
              <span className={`px-4 py-2 rounded-xl border font-bold text-lg ${dietMeta.badge}`}>
                {prediction.confidence ? `${(prediction.confidence * 100).toFixed(1)}% confidence` : "Predicted"}
              </span>
              <span className="text-xs text-gray-500">{prediction.model_name}</span>
            </div>
          </div>

          {prediction.all_class_probabilities && (
            <div className="mt-4 pt-4 border-t border-white/10 grid grid-cols-3 gap-3">
              {Object.entries(prediction.all_class_probabilities).map(([cls, prob]) => (
                <div key={cls} className="text-center">
                  <p className="text-xs text-gray-400 mb-1">{cls.replace("_", " ")}</p>
                  <div className="h-1.5 rounded-full bg-white/5 overflow-hidden">
                    <div className={`h-full rounded-full bg-gradient-to-r ${DIET_COLORS[cls]?.bg || 'from-gray-500 to-gray-400'}`}
                      style={{ width: `${(prob * 100).toFixed(1)}%` }} />
                  </div>
                  <p className="text-xs font-bold text-white mt-1">{(prob * 100).toFixed(1)}%</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ─── Dish Recommendations ─── */}
      {(dishLoading || dishes) && (
        <div className="glass-card p-6 border border-white/10">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Utensils className="w-5 h-5 text-emerald-400" />
              Personalised Dish Recommendations
            </h2>
            <div className="flex gap-2">
              {["dishes", "mealplan"].map((tab) => (
                <button key={tab} onClick={() => setActiveTab(tab)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold capitalize transition-all ${
                    activeTab === tab
                      ? "bg-gradient-to-r from-emerald-500 to-cyan-500 text-white"
                      : "text-gray-400 hover:text-white bg-white/5"
                  }`}>
                  {tab === "dishes" ? "All Dishes" : "Meal Plan"}
                </button>
              ))}
            </div>
          </div>

          {dishLoading ? (
            <div className="flex items-center justify-center py-12 text-gray-400 gap-3">
              <Sparkles className="w-6 h-6 text-emerald-400 animate-spin" />
              <span className="text-sm">Loading dishes from dataset...</span>
            </div>
          ) : activeTab === "dishes" ? (
            <>
              <p className="text-xs text-gray-500 mb-4">
                {dishes.length} dishes from final_dish_dataset.csv • Filtered for{" "}
                <span className="text-emerald-400 font-semibold">{prediction?.diet_recommendation?.replace("_", " ")}</span>{" "}
                {form.allergies && `• Excluding ${form.allergies} allergen`}
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {dishes.map((dish) => <DishCard key={dish.id} dish={dish} />)}
              </div>
            </>
          ) : (
            mealPlan && (
              <div className="space-y-6">
                {Object.entries(MEAL_SLOT_META).map(([slot, meta]) => {
                  const SlotIcon = meta.icon;
                  const slotDishes = mealPlan[slot] || [];
                  return (
                    <div key={slot}>
                      <h3 className={`text-sm font-bold ${meta.color} flex items-center gap-2 mb-3`}>
                        <SlotIcon className="w-4 h-4" /> {meta.label}
                      </h3>
                      {slotDishes.length === 0 ? (
                        <p className="text-xs text-gray-500">No dishes assigned</p>
                      ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          {slotDishes.map((dish) => <DishCard key={dish.id} dish={dish} />)}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )
          )}
        </div>
      )}
    </div>
  );
}

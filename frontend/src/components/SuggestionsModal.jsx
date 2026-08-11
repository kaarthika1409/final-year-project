import React, { useState, useEffect } from "react";
import { X, Sparkles, Plus, Flame, Dumbbell, ShieldCheck, Check } from "lucide-react";
import { api } from "../api";

export default function SuggestionsModal({ onClose, onSuccess }) {
  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState(null);
  const [selectedSlot, setSelectedSlot] = useState("lunch");
  const [loggingId, setLoggingId] = useState(null);

  useEffect(() => {
    const fetchRecs = async () => {
      setLoading(true);
      try {
        const res = await api.getRecommendations();
        setRecommendations(res);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchRecs();
  }, []);

  const handleQuickLog = async (item) => {
    setLoggingId(item.id);
    try {
      await api.logMealManual({
        meal_slot: selectedSlot,
        food_name: item.food_name,
        quantity_g: item.serving_size_g,
        source: "recommendation",
      });
      onSuccess();
      onClose();
    } catch (err) {
      alert("Failed to log recommendation: " + err.message);
    } finally {
      setLoggingId(null);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <div className="glass-card w-full max-w-2xl p-6 border border-white/10 relative shadow-2xl animate-fade-in max-h-[90vh] overflow-y-auto">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-gray-400 hover:text-white rounded-lg bg-white/5 hover:bg-white/10"
        >
          <X className="w-5 h-5" />
        </button>

        <h2 className="text-xl font-bold text-white flex items-center gap-2 mb-1">
          <Sparkles className="w-5 h-5 text-emerald-400" /> AI Adaptive Meal Suggestions
        </h2>
        <p className="text-xs text-gray-400 mb-6">
          Tailored to your remaining daily budget & dietary preferences
        </p>

        {/* Slot Selector */}
        <div className="flex items-center space-x-3 mb-6 bg-white/5 p-2 rounded-xl border border-white/10">
          <span className="text-xs font-semibold text-gray-300 ml-2">Log to Slot:</span>
          {["breakfast", "lunch", "snacks", "dinner"].map((s) => (
            <button
              key={s}
              onClick={() => setSelectedSlot(s)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold capitalize transition-all ${
                selectedSlot === s
                  ? "bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-md"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              {s}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-12 text-gray-400 space-y-3">
            <Sparkles className="w-8 h-8 text-emerald-400 animate-spin" />
            <p className="text-sm font-medium">Matching database meals to your macro profile...</p>
          </div>
        ) : !recommendations?.suggestions?.length ? (
          <div className="text-center py-12 text-gray-400">
            No suitable recommendations found matching strict calorie/allergy criteria.
          </div>
        ) : (
          <div className="space-y-4">
            {recommendations.suggestions.map((item) => (
              <div
                key={item.id}
                className="p-4 rounded-2xl bg-white/5 border border-white/10 hover:border-emerald-500/30 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4 group"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-extrabold text-base text-white">{item.food_name}</h3>
                    <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      {item.fit_reason}
                    </span>
                  </div>

                  <p className="text-xs text-gray-400">
                    Standard Serving: {item.serving_size_g}g • Category: {item.category}
                  </p>

                  {/* Macro Badges */}
                  <div className="flex items-center space-x-3 text-xs pt-1">
                    <span className="flex items-center gap-1 font-semibold text-emerald-400">
                      <Flame className="w-3.5 h-3.5" /> {Math.round(item.calories_per_serving)} kcal
                    </span>
                    <span className="flex items-center gap-1 text-cyan-300">
                      <Dumbbell className="w-3.5 h-3.5" /> P: {item.protein_g}g
                    </span>
                    <span className="text-amber-300">C: {item.carbs_g}g</span>
                    <span className="text-purple-300">F: {item.fat_g}g</span>
                  </div>
                </div>

                <button
                  onClick={() => handleQuickLog(item)}
                  disabled={loggingId === item.id}
                  className="px-4 py-2.5 rounded-xl glow-button text-white font-bold text-xs flex items-center justify-center gap-1.5 self-start md:self-auto min-w-[110px]"
                >
                  {loggingId === item.id ? (
                    "Logging..."
                  ) : (
                    <>
                      <Plus className="w-4 h-4" /> Log Meal
                    </>
                  )}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

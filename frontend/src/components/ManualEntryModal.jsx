import React, { useState, useEffect } from "react";
import { X, Search, Check, Flame, Dumbbell, Wheat, Droplets } from "lucide-react";
import { api } from "../api";

export default function ManualEntryModal({ slotKey, onClose, onSuccess }) {
  const [searchTerm, setSearchTerm] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
  const [quantityG, setQuantityG] = useState(150);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    let active = true;
    const fetchResults = async () => {
      try {
        const res = await api.searchFood(searchTerm);
        if (active) setSearchResults(res || []);
      } catch (err) {
        console.error(err);
      }
    };
    fetchResults();
    return () => {
      active = false;
    };
  }, [searchTerm]);

  const handleSelectFood = (food) => {
    setSelectedItem(food);
    setQuantityG(food.serving_size_g || 100);
  };

  const handleLog = async () => {
    const foodName = selectedItem ? selectedItem.food_name : searchTerm;
    if (!foodName || !foodName.trim()) return;

    setSubmitting(true);
    try {
      await api.logMealManual({
        meal_slot: slotKey,
        food_name: foodName,
        quantity_g: Number(quantityG),
        source: "manual",
      });
      onSuccess();
      onClose();
    } catch (err) {
      alert("Failed to log meal: " + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  // Compute live macros
  const portionFactor = selectedItem ? quantityG / 100.0 : quantityG / 100.0;
  const cal = selectedItem ? Math.round(selectedItem.calories * portionFactor) : Math.round(200 * portionFactor);
  const pro = selectedItem ? Math.round(selectedItem.protein * portionFactor * 10) / 10 : Math.round(10 * portionFactor * 10) / 10;
  const carb = selectedItem ? Math.round(selectedItem.carbs * portionFactor * 10) / 10 : Math.round(25 * portionFactor * 10) / 10;
  const fat = selectedItem ? Math.round(selectedItem.fat * portionFactor * 10) / 10 : Math.round(7 * portionFactor * 10) / 10;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <div className="glass-card w-full max-w-lg p-6 border border-white/10 relative shadow-2xl animate-fade-in">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-gray-400 hover:text-white rounded-lg bg-white/5 hover:bg-white/10"
        >
          <X className="w-5 h-5" />
        </button>

        <h2 className="text-xl font-bold text-white flex items-center gap-2 mb-1">
          <Search className="w-5 h-5 text-cyan-400" /> Manual Food Search & Entry
        </h2>
        <p className="text-xs text-gray-400 mb-6 capitalize">Target slot: {slotKey}</p>

        {/* Search Bar */}
        <div className="relative mb-4">
          <Search className="w-5 h-5 text-gray-400 absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search food database (e.g. Apple, Salmon, Rice...)"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 text-sm focus:outline-none focus:border-cyan-400"
          />
        </div>

        {/* Search Dropdown Results */}
        <div className="max-h-48 overflow-y-auto space-y-1.5 mb-6 pr-1">
          {searchResults.map((item) => (
            <div
              key={item.id}
              onClick={() => handleSelectFood(item)}
              className={`p-3 rounded-xl border text-xs cursor-pointer transition-all flex items-center justify-between ${
                selectedItem?.id === item.id
                  ? "bg-cyan-500/20 border-cyan-500 text-white font-bold"
                  : "bg-white/5 border-white/5 text-gray-300 hover:bg-white/10"
              }`}
            >
              <div>
                <p className="font-semibold text-sm">{item.food_name}</p>
                <p className="text-gray-400 text-[11px]">
                  Category: {item.category} • {item.calories} kcal/100g
                </p>
              </div>
              <span className="text-[11px] px-2 py-1 rounded bg-white/10 text-cyan-300 font-mono">
                P:{item.protein}g C:{item.carbs}g F:{item.fat}g
              </span>
            </div>
          ))}
        </div>

        {/* Selected / Custom Item Portion Selection */}
        <div className="space-y-4 p-4 rounded-xl bg-white/5 border border-white/10 mb-6">
          <div className="flex justify-between items-center text-sm font-semibold">
            <span className="text-gray-200">
              Food: <strong className="text-cyan-400">{selectedItem ? selectedItem.food_name : searchTerm || "Custom Food"}</strong>
            </span>
            <span className="text-emerald-400 font-bold">{quantityG} g</span>
          </div>

          <input
            type="range"
            min="20"
            max="600"
            step="10"
            value={quantityG}
            onChange={(e) => setQuantityG(Number(e.target.value))}
            className="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
          />

          <div className="grid grid-cols-4 gap-2 text-center pt-2">
            <div className="p-2 rounded-lg bg-black/40">
              <Flame className="w-3.5 h-3.5 text-emerald-400 mx-auto mb-0.5" />
              <span className="text-xs font-bold text-white">{cal}</span>
              <p className="text-[9px] text-gray-400">kcal</p>
            </div>
            <div className="p-2 rounded-lg bg-black/40">
              <Dumbbell className="w-3.5 h-3.5 text-cyan-400 mx-auto mb-0.5" />
              <span className="text-xs font-bold text-white">{pro}g</span>
              <p className="text-[9px] text-gray-400">Protein</p>
            </div>
            <div className="p-2 rounded-lg bg-black/40">
              <Wheat className="w-3.5 h-3.5 text-amber-400 mx-auto mb-0.5" />
              <span className="text-xs font-bold text-white">{carb}g</span>
              <p className="text-[9px] text-gray-400">Carbs</p>
            </div>
            <div className="p-2 rounded-lg bg-black/40">
              <Droplets className="w-3.5 h-3.5 text-purple-400 mx-auto mb-0.5" />
              <span className="text-xs font-bold text-white">{fat}g</span>
              <p className="text-[9px] text-gray-400">Fat</p>
            </div>
          </div>
        </div>

        <button
          onClick={handleLog}
          disabled={submitting || (!selectedItem && !searchTerm.trim())}
          className="w-full py-3 rounded-xl glow-button text-white font-bold text-sm flex items-center justify-center gap-2 disabled:opacity-50"
        >
          <Check className="w-5 h-5" /> Log Meal to {slotKey}
        </button>
      </div>
    </div>
  );
}

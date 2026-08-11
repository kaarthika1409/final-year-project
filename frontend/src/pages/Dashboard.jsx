import React, { useState, useEffect } from "react";
import { Sparkles, Camera, Search, RefreshCw, Flame } from "lucide-react";
import { api } from "../api";
import CalorieRing from "../components/CalorieRing";
import MealSlotCard from "../components/MealSlotCard";
import PhotoUploadModal from "../components/PhotoUploadModal";
import ManualEntryModal from "../components/ManualEntryModal";
import SuggestionsModal from "../components/SuggestionsModal";

export default function Dashboard({ user }) {
  const [targetData, setTargetData] = useState(null);
  const [mealLogs, setMealLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  // Modal controls
  const [activePhotoSlot, setActivePhotoSlot] = useState(null);
  const [activeManualSlot, setActiveManualSlot] = useState(null);
  const [showSuggestions, setShowSuggestions] = useState(false);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [targetRes, logsRes] = await Promise.all([
        api.getTodayTarget(),
        api.getMealLogs(),
      ]);
      setTargetData(targetRes);
      setMealLogs(logsRes || []);
    } catch (err) {
      console.error("Dashboard load error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleDeleteLog = async (logId) => {
    try {
      const res = await api.deleteMealLog(logId);
      setTargetData(res.updated_target);
      setMealLogs((prev) => prev.filter((l) => l.id !== logId));
    } catch (err) {
      alert("Delete failed: " + err.message);
    }
  };

  if (loading && !targetData) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-3 text-gray-400">
        <Sparkles className="w-8 h-8 text-emerald-400 animate-spin" />
        <p className="text-sm font-medium">Calculating Mifflin-St Jeor Daily Targets...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      {/* Top Banner / Quick Actions */}
      <div className="glass-card p-6 border border-white/10 flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white">
            Daily Adaptive Dashboard
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Real-time remaining calorie redistribution across meal slots
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={() => setShowSuggestions(true)}
            className="px-4 py-2.5 rounded-xl glow-button text-white font-bold text-xs flex items-center gap-2"
          >
            <Sparkles className="w-4 h-4" /> Get AI Suggestions
          </button>

          <button
            onClick={() => setActiveManualSlot("lunch")}
            className="px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 border border-white/10 text-white font-semibold text-xs flex items-center gap-2 transition-all"
          >
            <Search className="w-4 h-4 text-cyan-400" /> Manual Entry
          </button>

          <button
            onClick={() => setActivePhotoSlot("lunch")}
            className="px-4 py-2.5 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/20 text-emerald-400 font-semibold text-xs flex items-center gap-2 transition-all"
          >
            <Camera className="w-4 h-4" /> AI Photo Upload
          </button>

          <button
            onClick={fetchDashboardData}
            className="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white border border-white/10 transition-all"
            title="Refresh Targets"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Daily Calorie & Macro Progress */}
      <CalorieRing target={targetData} />

      {/* 4 Adaptive Meal Slot Cards Grid */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Flame className="w-5 h-5 text-emerald-400" /> Adaptive Meal Slot Breakdown
          </h2>
          <span className="text-xs text-emerald-400 font-medium px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">
            Auto-Redistributes Remaining Target
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {["breakfast", "lunch", "snacks", "dinner"].map((slotKey) => (
            <MealSlotCard
              key={slotKey}
              slotKey={slotKey}
              slotData={targetData?.[slotKey]}
              mealLogs={mealLogs}
              onOpenManual={(slot) => setActiveManualSlot(slot)}
              onOpenPhoto={(slot) => setActivePhotoSlot(slot)}
              onDeleteLog={handleDeleteLog}
            />
          ))}
        </div>
      </div>

      {/* Modals */}
      {activePhotoSlot && (
        <PhotoUploadModal
          slotKey={activePhotoSlot}
          onClose={() => setActivePhotoSlot(null)}
          onSuccess={fetchDashboardData}
        />
      )}

      {activeManualSlot && (
        <ManualEntryModal
          slotKey={activeManualSlot}
          onClose={() => setActiveManualSlot(null)}
          onSuccess={fetchDashboardData}
        />
      )}

      {showSuggestions && (
        <SuggestionsModal
          onClose={() => setShowSuggestions(false)}
          onSuccess={fetchDashboardData}
        />
      )}
    </div>
  );
}

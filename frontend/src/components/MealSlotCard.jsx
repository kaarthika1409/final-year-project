import React from "react";
import { Coffee, Sun, Cookie, Moon, Plus, Trash2, Camera, Search } from "lucide-react";

const SLOT_ICONS = {
  breakfast: Coffee,
  lunch: Sun,
  snacks: Cookie,
  dinner: Moon,
};

const SLOT_COLORS = {
  breakfast: "from-amber-500/20 to-orange-500/20 text-amber-400 border-amber-500/30",
  lunch: "from-cyan-500/20 to-blue-500/20 text-cyan-400 border-cyan-500/30",
  snacks: "from-purple-500/20 to-pink-500/20 text-purple-400 border-purple-500/30",
  dinner: "from-emerald-500/20 to-teal-500/20 text-emerald-400 border-emerald-500/30",
};

export default function MealSlotCard({
  slotKey,
  slotData,
  mealLogs = [],
  onOpenManual,
  onOpenPhoto,
  onDeleteLog,
}) {
  const Icon = SLOT_ICONS[slotKey] || Sun;
  const colorStyle = SLOT_COLORS[slotKey] || "from-gray-500/20 to-gray-600/20 text-gray-300";

  const logsForSlot = mealLogs.filter((l) => l.meal_slot.toLowerCase() === slotKey.toLowerCase());
  const consumed = slotData?.consumed || 0;
  const target = slotData?.target || 0;
  const remaining = slotData?.remaining || 0;

  const pct = target > 0 ? Math.min(100, Math.round((consumed / target) * 100)) : 0;

  return (
    <div className="glass-card p-5 border border-white/10 flex flex-col justify-between hover:border-white/20 transition-all duration-300">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className={`p-2.5 rounded-xl bg-gradient-to-tr ${colorStyle} border`}>
              <Icon className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white capitalize">{slotKey}</h3>
              <span className="text-xs text-gray-400 font-medium">Adaptive Target</span>
            </div>
          </div>

          <div className="text-right">
            <span className="text-lg font-extrabold text-white">{Math.round(consumed)}</span>
            <span className="text-xs text-gray-400"> / {Math.round(target)} kcal</span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden mb-3">
          <div
            className="h-full bg-gradient-to-r from-emerald-400 to-cyan-400 transition-all duration-500"
            style={{ width: `${pct}%` }}
          />
        </div>

        <div className="flex justify-between items-center text-xs mb-4">
          <span className="text-gray-400">
            {remaining > 0 ? `${Math.round(remaining)} kcal left` : "Slot target completed"}
          </span>
          <span className="text-emerald-400 font-semibold">{pct}%</span>
        </div>

        {/* Logged Foods List */}
        <div className="space-y-2 mb-4 max-h-36 overflow-y-auto pr-1">
          {logsForSlot.length === 0 ? (
            <div className="text-center py-4 text-xs text-gray-500 italic bg-gray-900/30 rounded-xl border border-white/5">
              No meals logged yet for {slotKey}
            </div>
          ) : (
            logsForSlot.map((log) => (
              <div
                key={log.id}
                className="flex items-center justify-between p-2.5 rounded-xl bg-[#1e273e] border border-white/5 text-xs group"
              >
                <div>
                  <p className="font-semibold text-white">{log.food_name}</p>
                  <p className="text-gray-400 text-[10px]">
                    {log.quantity_g}g • {Math.round(log.calories)} kcal ({log.source})
                  </p>
                </div>
                <button
                  onClick={() => onDeleteLog(log.id)}
                  className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-all"
                  title="Remove log"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-2 gap-2 pt-2 border-t border-white/10">
        <button
          onClick={() => onOpenManual(slotKey)}
          className="py-2 px-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-semibold text-gray-200 flex items-center justify-center gap-1.5 transition-all"
        >
          <Search className="w-3.5 h-3.5 text-cyan-400" /> Manual
        </button>

        <button
          onClick={() => onOpenPhoto(slotKey)}
          className="py-2 px-3 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/20 text-xs font-semibold text-emerald-400 flex items-center justify-center gap-1.5 transition-all"
        >
          <Camera className="w-3.5 h-3.5" /> AI Photo
        </button>
      </div>
    </div>
  );
}

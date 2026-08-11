import React from "react";
import { Flame, Dumbbell, Wheat, Droplets } from "lucide-react";

export default function CalorieRing({ target }) {
  if (!target) return null;

  const consumed = target.consumed_calories || 0;
  const total = target.target_calories || 2000;
  const remaining = target.remaining_calories || 0;

  const percentage = Math.min(100, Math.round((consumed / total) * 100));

  // SVG Circular Ring parameters
  const radius = 80;
  const strokeWidth = 14;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="glass-card p-6 border border-white/10 shadow-2xl relative overflow-hidden">
      <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/10 rounded-full filter blur-3xl -z-10 pointer-events-none" />

      <h2 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
        <Flame className="w-5 h-5 text-emerald-400" /> Daily Calorie & Macro Target
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center">
        {/* SVG Circle Progress */}
        <div className="md:col-span-5 flex flex-col items-center justify-center relative">
          <div className="relative w-52 h-52 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="104"
                cy="104"
                r={radius}
                className="stroke-gray-800"
                strokeWidth={strokeWidth}
                fill="transparent"
              />
              <circle
                cx="104"
                cy="104"
                r={radius}
                className="stroke-gradient transition-all duration-1000 ease-out"
                strokeWidth={strokeWidth}
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                fill="transparent"
                style={{
                  stroke: "url(#emeraldGradient)",
                }}
              />
              <defs>
                <linearGradient id="emeraldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#10b981" />
                  <stop offset="100%" stopColor="#06b6d4" />
                </linearGradient>
              </defs>
            </svg>

            <div className="absolute flex flex-col items-center justify-center text-center">
              <span className="text-4xl font-extrabold text-white tracking-tight">
                {Math.round(remaining)}
              </span>
              <span className="text-xs uppercase font-bold tracking-wider text-emerald-400 mt-0.5">
                Kcal Remaining
              </span>
              <span className="text-xs text-gray-400 mt-1">
                Goal: {Math.round(total)} kcal
              </span>
            </div>
          </div>
          <div className="mt-4 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs font-semibold text-emerald-400">
            {percentage}% Achieved Today
          </div>
        </div>

        {/* Macros Breakdown */}
        <div className="md:col-span-7 space-y-5">
          {/* Protein Bar */}
          <div>
            <div className="flex justify-between items-center text-sm font-semibold mb-1.5">
              <span className="flex items-center gap-2 text-cyan-400">
                <Dumbbell className="w-4 h-4" /> Protein
              </span>
              <span className="text-gray-300">
                {Math.round(target.consumed_protein)} / {Math.round(target.target_protein)} g
              </span>
            </div>
            <div className="w-full h-3 bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all duration-700"
                style={{
                  width: `${Math.min(100, (target.consumed_protein / maxVal(target.target_protein)) * 100)}%`,
                }}
              />
            </div>
          </div>

          {/* Carbs Bar */}
          <div>
            <div className="flex justify-between items-center text-sm font-semibold mb-1.5">
              <span className="flex items-center gap-2 text-amber-400">
                <Wheat className="w-4 h-4" /> Carbs
              </span>
              <span className="text-gray-300">
                {Math.round(target.consumed_carbs)} / {Math.round(target.target_carbs)} g
              </span>
            </div>
            <div className="w-full h-3 bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-amber-500 to-yellow-500 rounded-full transition-all duration-700"
                style={{
                  width: `${Math.min(100, (target.consumed_carbs / maxVal(target.target_carbs)) * 100)}%`,
                }}
              />
            </div>
          </div>

          {/* Fat Bar */}
          <div>
            <div className="flex justify-between items-center text-sm font-semibold mb-1.5">
              <span className="flex items-center gap-2 text-purple-400">
                <Droplets className="w-4 h-4" /> Fat
              </span>
              <span className="text-gray-300">
                {Math.round(target.consumed_fat)} / {Math.round(target.target_fat)} g
              </span>
            </div>
            <div className="w-full h-3 bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all duration-700"
                style={{
                  width: `${Math.min(100, (target.consumed_fat / maxVal(target.target_fat)) * 100)}%`,
                }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function maxVal(v) {
  return v > 0 ? v : 1;
}

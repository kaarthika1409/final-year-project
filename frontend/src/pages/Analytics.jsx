import React, { useState, useEffect } from "react";
import { BarChart3, RefreshCw, Sparkles, ShieldCheck } from "lucide-react";
import { api } from "../api";
import DemographicAccuracyChart from "../components/DemographicAccuracyChart";

export default function Analytics({ user }) {
  const [accuracyData, setAccuracyData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchReport = async () => {
    setLoading(true);
    try {
      const data = await api.getAccuracyReport();
      setAccuracyData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, []);

  return (
    <div className="space-y-8 pb-12">
      {/* Header Banner */}
      <div className="glass-card p-6 border border-white/10 flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-emerald-400" /> Accuracy & Demographic Evaluation Report
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Comparing predicted calorie targets vs actual intake logs (MAE & RMSE per group)
          </p>
        </div>

        <button
          onClick={fetchReport}
          className="px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 border border-white/10 text-white font-semibold text-xs flex items-center gap-2 transition-all"
        >
          <RefreshCw className="w-4 h-4 text-emerald-400" /> Re-evaluate Model Accuracy
        </button>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-3 text-gray-400">
          <Sparkles className="w-8 h-8 text-emerald-400 animate-spin" />
          <p className="text-sm font-medium">Computing MAE and RMSE across demographic groups...</p>
        </div>
      ) : (
        <DemographicAccuracyChart data={accuracyData} />
      )}
    </div>
  );
}

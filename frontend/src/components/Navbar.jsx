import React from "react";
import { Activity, LayoutDashboard, User, BarChart3, LogOut } from "lucide-react";

export default function Navbar({ activeTab, setActiveTab, user, onLogout }) {
  return (
    <nav className="sticky top-0 z-40 bg-[#0b0f19]/80 backdrop-blur-md border-b border-white/10 px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab("dashboard")}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center text-white shadow-lg shadow-emerald-500/20">
            <Activity className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h1 className="font-extrabold text-xl tracking-tight text-white flex items-center gap-2">
              Nutri<span className="gradient-text">Adaptive</span>
            </h1>
            <p className="text-xs text-gray-400 font-medium">Smart Dietary Recommendation</p>
          </div>
        </div>

        <div className="flex items-center space-x-2 bg-[#151c2e] p-1.5 rounded-xl border border-white/10">
          <button
            onClick={() => setActiveTab("dashboard")}
            className={`px-4 py-2 rounded-lg font-medium text-sm transition-all flex items-center gap-2 ${
              activeTab === "dashboard"
                ? "bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-md"
                : "text-gray-400 hover:text-white"
            }`}
          >
            <LayoutDashboard className="w-4 h-4" /> Dashboard
          </button>

          <button
            onClick={() => setActiveTab("analytics")}
            className={`px-4 py-2 rounded-lg font-medium text-sm transition-all flex items-center gap-2 ${
              activeTab === "analytics"
                ? "bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-md"
                : "text-gray-400 hover:text-white"
            }`}
          >
            <BarChart3 className="w-4 h-4" /> Accuracy & BMI
          </button>

          <button
            onClick={() => setActiveTab("profile")}
            className={`px-4 py-2 rounded-lg font-medium text-sm transition-all flex items-center gap-2 ${
              activeTab === "profile"
                ? "bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-md"
                : "text-gray-400 hover:text-white"
            }`}
          >
            <User className="w-4 h-4" /> Profile
          </button>
        </div>

        <div className="flex items-center space-x-4">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-semibold text-white">{user?.email}</p>
            <span className="inline-block text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 capitalize font-medium">
              Goal: {user?.goal}
            </span>
          </div>

          <button
            onClick={onLogout}
            className="p-2.5 rounded-xl bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/20 transition-all"
            title="Log out"
          >
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </div>
    </nav>
  );
}

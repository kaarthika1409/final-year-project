import React, { useState } from "react";
import { User, Activity, Flame, Heart, Save } from "lucide-react";
import { api } from "../api";

export default function Profile({ user, onProfileUpdated }) {
  const [formData, setFormData] = useState({
    age: user?.age || 28,
    weight: user?.weight || 70,
    height: user?.height || 175,
    gender: user?.gender || "male",
    activity_level: user?.activity_level || "moderate",
    goal: user?.goal || "maintain",
    dietary_preferences: user?.dietary_preferences || "balanced",
    allergies: user?.allergies || "",
  });

  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === "age" || name === "weight" || name === "height" ? Number(value) : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);

    try {
      const updatedUser = await api.updateProfile(formData);
      onProfileUpdated(updatedUser);
      setMessage("Profile parameters and Mifflin-St Jeor targets updated!");
    } catch (err) {
      alert("Update failed: " + err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass-card p-5 border border-white/10 text-center">
          <Flame className="w-6 h-6 text-emerald-400 mx-auto mb-1" />
          <p className="text-xs text-gray-400 font-semibold uppercase">Mifflin BMR</p>
          <p className="text-2xl font-extrabold text-white">{Math.round(user?.bmr || 0)} <span className="text-xs text-gray-400 font-medium">kcal</span></p>
        </div>

        <div className="glass-card p-5 border border-white/10 text-center">
          <Activity className="w-6 h-6 text-cyan-400 mx-auto mb-1" />
          <p className="text-xs text-gray-400 font-semibold uppercase">Calculated TDEE</p>
          <p className="text-2xl font-extrabold text-cyan-400">{Math.round(user?.tdee || 0)} <span className="text-xs text-gray-400 font-medium">kcal</span></p>
        </div>

        <div className="glass-card p-5 border border-white/10 text-center">
          <Heart className="w-6 h-6 text-purple-400 mx-auto mb-1" />
          <p className="text-xs text-gray-400 font-semibold uppercase">Body Mass Index</p>
          <p className="text-2xl font-extrabold text-purple-400">{user?.bmi || 0}</p>
        </div>

        <div className="glass-card p-5 border border-white/10 text-center">
          <User className="w-6 h-6 text-amber-400 mx-auto mb-1" />
          <p className="text-xs text-gray-400 font-semibold uppercase">BMI Category</p>
          <p className="text-lg font-bold text-amber-400 mt-1">{user?.bmi_category || "Normal"}</p>
        </div>
      </div>

      {/* Edit Profile Form */}
      <div className="glass-card p-8 border border-white/10">
        <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <User className="w-5 h-5 text-emerald-400" /> Edit Demographic & Health Parameters
        </h2>

        {message && (
          <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs mb-6 text-center font-medium">
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="block text-xs font-bold text-gray-300 uppercase tracking-wider mb-1.5">
                Age (years)
              </label>
              <input
                type="number"
                name="age"
                required
                value={formData.age}
                onChange={handleChange}
                className="w-full px-3.5 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-sm focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-300 uppercase tracking-wider mb-1.5">
                Weight (kg)
              </label>
              <input
                type="number"
                name="weight"
                step="0.5"
                required
                value={formData.weight}
                onChange={handleChange}
                className="w-full px-3.5 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-sm focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-300 uppercase tracking-wider mb-1.5">
                Height (cm)
              </label>
              <input
                type="number"
                name="height"
                required
                value={formData.height}
                onChange={handleChange}
                className="w-full px-3.5 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-sm focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-300 uppercase tracking-wider mb-1.5">
                Gender
              </label>
              <select
                name="gender"
                value={formData.gender}
                onChange={handleChange}
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#151c2e] border border-white/10 text-white text-sm focus:border-emerald-500"
              >
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-300 uppercase tracking-wider mb-1.5">
                Activity Level
              </label>
              <select
                name="activity_level"
                value={formData.activity_level}
                onChange={handleChange}
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#151c2e] border border-white/10 text-white text-sm focus:border-emerald-500"
              >
                <option value="sedentary">Sedentary (1.2x)</option>
                <option value="light">Lightly Active (1.375x)</option>
                <option value="moderate">Moderately Active (1.55x)</option>
                <option value="active">Active (1.725x)</option>
                <option value="very_active">Very Active (1.9x)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-300 uppercase tracking-wider mb-1.5">
                Dietary Goal
              </label>
              <select
                name="goal"
                value={formData.goal}
                onChange={handleChange}
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#151c2e] border border-white/10 text-white text-sm focus:border-emerald-500"
              >
                <option value="lose">Lose Weight (-500 kcal)</option>
                <option value="maintain">Maintain Weight</option>
                <option value="gain">Gain Weight (+500 kcal)</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
            <div>
              <label className="block text-xs font-bold text-gray-300 uppercase tracking-wider mb-1.5">
                Dietary Preference
              </label>
              <select
                name="dietary_preferences"
                value={formData.dietary_preferences}
                onChange={handleChange}
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#151c2e] border border-white/10 text-white text-sm focus:border-emerald-500"
              >
                <option value="balanced">Balanced</option>
                <option value="vegetarian">Vegetarian</option>
                <option value="vegan">Vegan</option>
                <option value="keto">Keto (Low Carb)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-300 uppercase tracking-wider mb-1.5">
                Allergies & Restrictions
              </label>
              <input
                type="text"
                name="allergies"
                value={formData.allergies}
                onChange={handleChange}
                placeholder="e.g. nuts, dairy, gluten"
                className="w-full px-3.5 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-sm focus:border-emerald-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={saving}
            className="px-6 py-3 rounded-xl glow-button text-white font-bold text-sm flex items-center justify-center gap-2"
          >
            <Save className="w-4 h-4" /> {saving ? "Saving Changes..." : "Save Profile & Update Targets"}
          </button>
        </form>
      </div>
    </div>
  );
}

import React, { useState } from "react";
import { Activity, ArrowRight, UserCheck } from "lucide-react";
import { api } from "../api";

export default function Signup({ onSignupSuccess, onSwitchToLogin }) {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    age: 28,
    weight: 70,
    height: 175,
    gender: "male",
    activity_level: "moderate",
    goal: "maintain",
    dietary_preferences: "balanced",
    allergies: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === "age" || name === "weight" || name === "height" ? Number(value) : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const data = await api.signup(formData);
      localStorage.setItem("token", data.access_token);
      onSignupSuccess(data.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-[#0b0f19] relative overflow-hidden py-12">
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-emerald-500/10 rounded-full filter blur-3xl pointer-events-none" />

      <div className="glass-card w-full max-w-xl p-8 border border-white/10 relative z-10 shadow-2xl">
        <div className="text-center mb-6">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center text-white mx-auto mb-2 shadow-lg shadow-emerald-500/20">
            <Activity className="w-6 h-6 animate-pulse" />
          </div>
          <h1 className="text-2xl font-extrabold text-white">Create Nutritional Profile</h1>
          <p className="text-xs text-gray-400 mt-1">
            Personalized BMR & Adaptive Dietary Recommendation Engine
          </p>
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs mb-4 text-center font-medium">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-gray-300 uppercase tracking-wider mb-1">
                Email Address
              </label>
              <input
                type="email"
                name="email"
                required
                value={formData.email}
                onChange={handleChange}
                placeholder="you@example.com"
                className="w-full px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 text-xs focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-300 uppercase tracking-wider mb-1">
                Password
              </label>
              <input
                type="password"
                name="password"
                required
                value={formData.password}
                onChange={handleChange}
                placeholder="At least 6 characters"
                className="w-full px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 text-xs focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-300 uppercase tracking-wider mb-1">
                Age (years)
              </label>
              <input
                type="number"
                name="age"
                required
                min="12"
                max="100"
                value={formData.age}
                onChange={handleChange}
                className="w-full px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-300 uppercase tracking-wider mb-1">
                Gender
              </label>
              <select
                name="gender"
                value={formData.gender}
                onChange={handleChange}
                className="w-full px-3.5 py-2 rounded-xl bg-[#151c2e] border border-white/10 text-white text-xs focus:border-emerald-500"
              >
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-300 uppercase tracking-wider mb-1">
                Weight (kg)
              </label>
              <input
                type="number"
                name="weight"
                step="0.5"
                required
                value={formData.weight}
                onChange={handleChange}
                className="w-full px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-300 uppercase tracking-wider mb-1">
                Height (cm)
              </label>
              <input
                type="number"
                name="height"
                required
                value={formData.height}
                onChange={handleChange}
                className="w-full px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-300 uppercase tracking-wider mb-1">
                Activity Level
              </label>
              <select
                name="activity_level"
                value={formData.activity_level}
                onChange={handleChange}
                className="w-full px-3.5 py-2 rounded-xl bg-[#151c2e] border border-white/10 text-white text-xs focus:border-emerald-500"
              >
                <option value="sedentary">Sedentary (Little or no exercise)</option>
                <option value="light">Lightly Active (1-3 days/wk)</option>
                <option value="moderate">Moderately Active (3-5 days/wk)</option>
                <option value="active">Active (6-7 days/wk)</option>
                <option value="very_active">Very Active (Heavy exercise)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-300 uppercase tracking-wider mb-1">
                Weight Goal
              </label>
              <select
                name="goal"
                value={formData.goal}
                onChange={handleChange}
                className="w-full px-3.5 py-2 rounded-xl bg-[#151c2e] border border-white/10 text-white text-xs focus:border-emerald-500"
              >
                <option value="lose">Lose Weight (-500 kcal/day)</option>
                <option value="maintain">Maintain Weight</option>
                <option value="gain">Gain Weight (+500 kcal/day)</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            <div>
              <label className="block text-xs font-bold text-gray-300 uppercase tracking-wider mb-1">
                Dietary Preference
              </label>
              <select
                name="dietary_preferences"
                value={formData.dietary_preferences}
                onChange={handleChange}
                className="w-full px-3.5 py-2 rounded-xl bg-[#151c2e] border border-white/10 text-white text-xs focus:border-emerald-500"
              >
                <option value="balanced">Balanced</option>
                <option value="vegetarian">Vegetarian</option>
                <option value="vegan">Vegan</option>
                <option value="keto">Keto (Low Carb)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-300 uppercase tracking-wider mb-1">
                Food Allergies
              </label>
              <input
                type="text"
                name="allergies"
                value={formData.allergies}
                onChange={handleChange}
                placeholder="e.g. nuts, dairy, gluten"
                className="w-full px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 text-xs focus:border-emerald-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 mt-4 rounded-xl glow-button text-white font-bold text-sm flex items-center justify-center gap-2"
          >
            {loading ? "Calculating Mifflin-St Jeor Budget..." : <>Calculate Target & Register <ArrowRight className="w-4 h-4" /></>}
          </button>
        </form>

        <div className="mt-4 text-center text-xs text-gray-400">
          Already registered?{" "}
          <button
            onClick={onSwitchToLogin}
            className="text-emerald-400 font-bold hover:underline ml-1"
          >
            Sign In
          </button>
        </div>
      </div>
    </div>
  );
}

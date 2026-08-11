import React, { useState } from "react";
import { X, Upload, Sparkles, Check, Flame, Dumbbell, Wheat, Droplets, Camera } from "lucide-react";
import { api } from "../api";

export default function PhotoUploadModal({ slotKey, onClose, onSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [detectionResult, setDetectionResult] = useState(null);
  const [portionG, setPortionG] = useState(150);
  const [submitting, setSubmitting] = useState(false);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setDetectionResult(null);
    }
  };

  const handleAnalyzePhoto = async () => {
    if (!selectedFile) return;
    setLoading(true);
    try {
      const res = await api.detectPhoto(selectedFile);
      setDetectionResult(res);
      setPortionG(res.portion_g || 150);
    } catch (err) {
      alert("Photo analysis failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmLog = async () => {
    if (!detectionResult) return;
    setSubmitting(true);
    try {
      await api.logMealManual({
        meal_slot: slotKey,
        food_name: detectionResult.detected_food,
        quantity_g: portionG,
        source: "photo",
      });
      onSuccess();
      onClose();
    } catch (err) {
      alert("Failed to confirm meal log: " + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  // Adjust macros dynamically as portion slider moves
  const portionFactor = detectionResult ? portionG / (detectionResult.portion_g || 100) : 1;
  const computedCalories = detectionResult ? Math.round(detectionResult.calories * portionFactor) : 0;
  const computedProtein = detectionResult ? Math.round(detectionResult.protein * portionFactor * 10) / 10 : 0;
  const computedCarbs = detectionResult ? Math.round(detectionResult.carbs * portionFactor * 10) / 10 : 0;
  const computedFat = detectionResult ? Math.round(detectionResult.fat * portionFactor * 10) / 10 : 0;

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
          <Camera className="w-5 h-5 text-emerald-400" /> AI Food Image Recognition
        </h2>
        <p className="text-xs text-gray-400 mb-6 capitalize">Target slot: {slotKey}</p>

        {/* Upload Box */}
        {!detectionResult ? (
          <div className="space-y-4">
            <div className="border-2 border-dashed border-white/20 hover:border-emerald-500/50 rounded-2xl p-6 text-center transition-all bg-white/5 cursor-pointer relative">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
              />
              {previewUrl ? (
                <div className="flex flex-col items-center">
                  <img
                    src={previewUrl}
                    alt="Preview"
                    className="max-h-48 rounded-xl object-contain shadow-lg mb-2"
                  />
                  <p className="text-xs text-emerald-400 font-medium">Click to change photo</p>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-6 text-gray-400 space-y-2">
                  <Upload className="w-10 h-10 text-emerald-400 animate-bounce" />
                  <p className="text-sm font-semibold text-white">Upload or drop meal image</p>
                  <p className="text-xs text-gray-400">JPEG, PNG, WebP supported</p>
                </div>
              )}
            </div>

            <button
              onClick={handleAnalyzePhoto}
              disabled={!selectedFile || loading}
              className="w-full py-3 rounded-xl glow-button text-white font-bold text-sm flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Sparkles className="w-5 h-5 animate-spin" /> Running PyTorch Vision Model...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" /> Analyze Image & Predict Macros
                </>
              )}
            </button>
          </div>
        ) : (
          /* Detection Results & Portion Adjuster */
          <div className="space-y-5">
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-start gap-4">
              {previewUrl && (
                <img
                  src={previewUrl}
                  alt="Detected"
                  className="w-20 h-20 rounded-lg object-cover border border-white/10"
                />
              )}
              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  {Math.round((detectionResult.confidence || 0.85) * 100)}% Confidence
                </span>
                <h3 className="text-lg font-extrabold text-white mt-1">
                  {detectionResult.detected_food}
                </h3>
                <p className="text-xs text-gray-400 mt-0.5">{detectionResult.match_source}</p>
              </div>
            </div>

            {/* Portion Slider */}
            <div>
              <div className="flex justify-between items-center text-sm font-semibold mb-2">
                <span className="text-gray-300">Estimated Serving Portion</span>
                <span className="text-emerald-400 font-bold">{portionG} g</span>
              </div>
              <input
                type="range"
                min="30"
                max="500"
                step="10"
                value={portionG}
                onChange={(e) => setPortionG(Number(e.target.value))}
                className="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-emerald-400"
              />
            </div>

            {/* Macro Summary Grid */}
            <div className="grid grid-cols-4 gap-3 text-center">
              <div className="p-3 rounded-xl bg-white/5 border border-white/10">
                <Flame className="w-4 h-4 text-emerald-400 mx-auto mb-1" />
                <p className="text-base font-extrabold text-white">{computedCalories}</p>
                <p className="text-[10px] text-gray-400">Calories</p>
              </div>
              <div className="p-3 rounded-xl bg-white/5 border border-white/10">
                <Dumbbell className="w-4 h-4 text-cyan-400 mx-auto mb-1" />
                <p className="text-base font-extrabold text-white">{computedProtein}g</p>
                <p className="text-[10px] text-gray-400">Protein</p>
              </div>
              <div className="p-3 rounded-xl bg-white/5 border border-white/10">
                <Wheat className="w-4 h-4 text-amber-400 mx-auto mb-1" />
                <p className="text-base font-extrabold text-white">{computedCarbs}g</p>
                <p className="text-[10px] text-gray-400">Carbs</p>
              </div>
              <div className="p-3 rounded-xl bg-white/5 border border-white/10">
                <Droplets className="w-4 h-4 text-purple-400 mx-auto mb-1" />
                <p className="text-base font-extrabold text-white">{computedFat}g</p>
                <p className="text-[10px] text-gray-400">Fat</p>
              </div>
            </div>

            <div className="flex space-x-3 pt-2">
              <button
                onClick={() => setDetectionResult(null)}
                className="w-1/3 py-3 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold text-sm transition-all"
              >
                Retake Photo
              </button>
              <button
                onClick={handleConfirmLog}
                disabled={submitting}
                className="w-2/3 py-3 rounded-xl glow-button text-white font-bold text-sm flex items-center justify-center gap-2"
              >
                <Check className="w-5 h-5" /> Confirm & Log Meal
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

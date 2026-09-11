import React, { useState, useEffect } from "react";
import Navbar from "./components/Navbar";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import Profile from "./pages/Profile";
import Analytics from "./pages/Analytics";
import DiagnosisPage from "./pages/DiagnosisPage";
import { api } from "./api";

export default function App() {
  const [user, setUser] = useState(null);
  const [authView, setAuthView] = useState("login"); // "login" | "signup"
  const [activeTab, setActiveTab] = useState("dashboard"); // "dashboard" | "diagnosis" | "analytics" | "profile"
  const [initializing, setInitializing] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      api
        .getMe()
        .then((userData) => setUser(userData))
        .catch(() => localStorage.removeItem("token"))
        .finally(() => setInitializing(false));
    } else {
      setInitializing(false);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    setUser(null);
    setAuthView("login");
  };

  if (initializing) {
    return (
      <div className="min-h-screen bg-[#0b0f19] flex items-center justify-center text-emerald-400 font-semibold text-sm">
        Initializing NutriAdaptive Application...
      </div>
    );
  }

  if (!user) {
    if (authView === "signup") {
      return (
        <Signup
          onSignupSuccess={(u) => setUser(u)}
          onSwitchToLogin={() => setAuthView("login")}
        />
      );
    }
    return (
      <Login
        onLoginSuccess={(u) => setUser(u)}
        onSwitchToSignup={() => setAuthView("signup")}
      />
    );
  }

  return (
    <div className="min-h-screen bg-[#0b0f19] text-gray-100 selection:bg-emerald-500 selection:text-white">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        user={user}
        onLogout={handleLogout}
      />

      <main className="max-w-7xl mx-auto px-6 pt-8">
        {activeTab === "dashboard" && <Dashboard user={user} />}
        {activeTab === "diagnosis" && <DiagnosisPage />}
        {activeTab === "analytics" && <Analytics user={user} />}
        {activeTab === "profile" && (
          <Profile user={user} onProfileUpdated={(updated) => setUser(updated)} />
        )}
      </main>
    </div>
  );
}

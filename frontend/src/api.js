const API_BASE = "http://localhost:8000/api";

const getAuthHeader = () => {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const api = {
  async signup(data) {
    const res = await fetch(`${API_BASE}/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.detail || "Signup failed");
    return json;
  },

  async login(data) {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.detail || "Login failed");
    return json;
  },

  async getMe() {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getAuthHeader(),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.detail || "Failed to fetch user profile");
    return json;
  },

  async updateProfile(data) {
    const res = await fetch(`${API_BASE}/auth/profile`, {
      method: "PUT",
      headers: { ...getAuthHeader(), "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.detail || "Failed to update profile");
    return json;
  },

  async getTodayTarget() {
    const res = await fetch(`${API_BASE}/targets/today`, {
      headers: getAuthHeader(),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.detail || "Failed to fetch daily targets");
    return json;
  },

  async searchFood(query) {
    const res = await fetch(`${API_BASE}/meals/search?q=${encodeURIComponent(query)}`, {
      headers: getAuthHeader(),
    });
    return await res.json();
  },

  async logMealManual(mealData) {
    const res = await fetch(`${API_BASE}/meals/manual`, {
      method: "POST",
      headers: { ...getAuthHeader(), "Content-Type": "application/json" },
      body: JSON.stringify(mealData),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.detail || "Failed to log meal");
    return json;
  },

  async detectPhoto(file) {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API_BASE}/meals/photo`, {
      method: "POST",
      headers: getAuthHeader(),
      body: formData,
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.detail || "Photo detection failed");
    return json;
  },

  async getMealLogs() {
    const res = await fetch(`${API_BASE}/meals/logs`, {
      headers: getAuthHeader(),
    });
    return await res.json();
  },

  async deleteMealLog(id) {
    const res = await fetch(`${API_BASE}/meals/logs/${id}`, {
      method: "DELETE",
      headers: getAuthHeader(),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.detail || "Failed to delete log");
    return json;
  },

  async getRecommendations() {
    const res = await fetch(`${API_BASE}/recommendations`, {
      headers: getAuthHeader(),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.detail || "Failed to fetch recommendations");
    return json;
  },

  async getAccuracyReport() {
    const res = await fetch(`${API_BASE}/analytics/accuracy`, {
      headers: getAuthHeader(),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.detail || "Failed to fetch accuracy report");
    return json;
  },
};

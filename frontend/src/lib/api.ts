import axios from "axios";

const BASE_URL = "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: BASE_URL,
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export async function promptGPT(data: { chat_id: string; content: string }) {
  try {
    const response = await api.post("/prompt_gpt/", data);

    return response.data;
  } catch (err: unknown) {
    if (err instanceof Error) {
      throw new Error(err.message);
    }
    throw new Error("An unknown error occured!");
  }
}

export async function getChatMessages(chatId: string) {
  if (!chatId) return;
  try {
    const response = await api.get(`/get_chat_messages/${chatId}/`);

    return response.data;
  } catch (err: unknown) {
    if (err instanceof Error) {
      throw new Error(err.message);
    }
    throw new Error("An unknown error occured!");
  }
}

export async function getTodaysChats() {
  try {
    const response = await api.get("/todays_chat/");

    return response.data;
  } catch (err: unknown) {
    if (err instanceof Error) {
      throw new Error(err.message);
    }
    throw new Error("An unknown error occured!");
  }
}

export async function getYesterdaysChats() {
  try {
    const response = await api.get("/yesterdays_chat/");

    return response.data;
  } catch (err: unknown) {
    if (err instanceof Error) {
      throw new Error(err.message);
    }
    throw new Error("An unknown error occured!");
  }
}

export async function getSevenDaysChats() {
  try {
    const response = await api.get("/seven_days_chat/");
    return response.data;
  } catch (err: unknown) {
    if (err instanceof Error) {
      throw new Error(err.message);
    }
    throw new Error("An unknown error occured!");
  }
}

// Authentication API functions
export interface User {
  id: number;
  email_address: string;
  first_name: string;
  last_name: string;
  date_joined: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

export async function register(data: {
  email_address: string;
  password: string;
  password_confirm: string;
  first_name?: string;
  last_name?: string;
}): Promise<AuthResponse> {
  try {
    const response = await api.post("/auth/register/", data);

    return response.data;
  } catch (err: unknown) {
    if (err instanceof Error) {
      throw new Error(err.message);
    }
    throw new Error("An unknown error occurred!");
  }
}

export async function login(data: {
  email_address: string;
  password: string;
}): Promise<AuthResponse> {
  try {
    const response = await api.post("/auth/login/", data);

    return response.data;
  } catch (err: unknown) {
    if (err instanceof Error) {
      throw new Error(err.message);
    }
    throw new Error("An unknown error occurred!");
  }
}

export async function logout(): Promise<void> {
  try {
    await api.post("/auth/logout/");
  } catch (err: unknown) {
    if (err instanceof Error) {
      throw new Error(err.message);
    }
    throw new Error("An unknown error occurred!");
  }
}

export async function getUserProfile(): Promise<User> {
  try {
    const response = await api.get("/auth/profile/");
    return response.data;
  } catch (err: unknown) {
    if (err instanceof Error) {
      throw new Error(err.message);
    }
    throw new Error("An unknown error occurred!");
  }
}
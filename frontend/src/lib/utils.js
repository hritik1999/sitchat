import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { supabase } from '@/composables/useSupabase';
import { Capacitor } from '@capacitor/core';

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export function valueUpdater(updaterOrValue, ref) {
  ref.value =
    typeof updaterOrValue === 'function'
      ? updaterOrValue(ref.value)
      : updaterOrValue;
}

/**
 * Utility for making authenticated API requests
 * @param {string} endpoint - API endpoint path (without base URL)
 * @param {Object} options - Fetch options
 * @returns {Promise<Object>} - Response data
 */
export async function fetchApi(endpoint, options = {}) {
  const platform = Capacitor.getPlatform();
  let API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001';
  

    if (platform === 'android') {
    // Android emulator → host machine
    API_BASE_URL = import.meta.env.VITE_API_URL  || 'http://10.0.2.2:5001';
  } else if (platform === 'ios' && !import.meta.env.VITE_API_URL) {
    // iOS simulator can still use localhost
    API_BASE_URL =  import.meta.env.VITE_API_URL || 'http://localhost:5001';
  }
  const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  // Get current session
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;

  const isFormData = options.body instanceof FormData;

  // Setup headers with authentication
  const headers = {
    ...(token && { 'Authorization': `Bearer ${token}` }),
    ...options.headers
  };

  if (!isFormData) {
    headers['Content-Type'] = 'application/json'; // ✅ only set for JSON
  }

  const config = {
    ...options,
    headers
  };

  const response = await fetch(url, config);

  if (response.status === 401) {
    console.error('Unauthorized - session may have expired');
  }
  if (response.status === 503) {
    throw new Error('Server is at full capacity, please try again later.');
  }

  if (response.headers.get('content-type')?.includes('application/json')) {
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'API request failed');
    }
    return data;
  }

  if (!response.ok) {
    throw new Error('API request failed');
  }

  return await response.text();
}

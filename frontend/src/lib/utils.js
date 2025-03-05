import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { supabase } from '@/composables/useSupabase';

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
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001';
  const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  
  // Get current session
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  
  // Setup headers with authentication
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
    ...options.headers
  };
  
  const config = {
    ...options,
    headers
  };
  
  const response = await fetch(url, config);
  
  // Handle unauthorized
  if (response.status === 401) {
    // Attempt to refresh token or redirect to login
    console.error('Unauthorized - session may have expired');
    // Could redirect to login: window.location.href = '/auth';
  }
  
  // Parse JSON response
  if (response.headers.get('content-type')?.includes('application/json')) {
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'API request failed');
    }
    return data;
  }
  
  // Handle non-JSON responses
  if (!response.ok) {
    throw new Error('API request failed');
  }
  
  return await response.text();
}

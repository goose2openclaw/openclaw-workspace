/**
 * 🪿 GO2SE Theme System
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

type Theme = 'light' | 'dark' | 'system'

interface ThemeState {
  theme: Theme
  resolvedTheme: 'light' | 'dark'
  setTheme: (theme: Theme) => void
}

export const useTheme = create<ThemeState>()(
  persist(
    (set, get) => ({
      theme: 'dark',
      resolvedTheme: 'dark',
      
      setTheme: (theme) => {
        const resolved = theme === 'system' 
          ? window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
          : theme
        
        set({ theme, resolvedTheme: resolved })
        
        // Apply to document
        document.documentElement.classList.remove('light', 'dark')
        document.documentElement.classList.add(resolved)
      }
    }),
    {
      name: 'go2se-theme'
    }
  )
)

// Theme CSS Variables
export const themeVars = {
  dark: {
    '--bg-primary': '#0a0a0f',
    '--bg-secondary': '#12121a',
    '--bg-tertiary': '#1a1a25',
    '--text-primary': '#f0f0f5',
    '--text-secondary': '#a0a0b0',
    '--accent': '#00d4aa',
    '--accent-secondary': '#7c3aed',
    '--success': '#10b981',
    '--danger': '#ef4444',
    '--warning': '#f59e0b',
    '--border': '#2a2a3a',
  },
  light: {
    '--bg-primary': '#ffffff',
    '--bg-secondary': '#f8f9fa',
    '--bg-tertiary': '#e9ecef',
    '--text-primary': '#1a1a2e',
    '--text-secondary': '#6c757d',
    '--accent': '#00b894',
    '--accent-secondary': '#6c5ce7',
    '--success': '#00b894',
    '--danger': '#e74c3c',
    '--warning': '#f39c12',
    '--border': '#dee2e6',
  }
}

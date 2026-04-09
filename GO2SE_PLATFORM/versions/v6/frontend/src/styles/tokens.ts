/**
 * 🪿 GO2SE Design Tokens - 设计系统
 * 金融仪表盘风格
 */

export const designTokens = {
  // 颜色系统
  colors: {
    // 主色 - 夜空深蓝
    bg: {
      primary: '#0A0E17',
      secondary: '#111827',
      tertiary: '#1F2937',
      elevated: '#283548',
    },
    // 强调色 - 翡翠绿
    accent: {
      DEFAULT: '#00D4AA',
      hover: '#00F5C4',
      muted: 'rgba(0, 212, 170, 0.15)',
      glow: 'rgba(0, 212, 170, 0.4)',
    },
    // 辅助色
    secondary: '#7C3AED',
    gold: '#F59E0B',
    // 语义色
    success: '#10B981',
    successBg: 'rgba(16, 185, 129, 0.15)',
    danger: '#EF4444',
    dangerBg: 'rgba(239, 68, 68, 0.15)',
    warning: '#F59E0B',
    warningBg: 'rgba(245, 158, 11, 0.15)',
    // 文字
    text: {
      primary: '#F9FAFB',
      secondary: '#9CA3AF',
      muted: '#6B7280',
    },
    // 边框
    border: {
      DEFAULT: '#374151',
      light: '#4B5563',
    },
  },

  // 字体系统
  fonts: {
    sans: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
    mono: 'JetBrains Mono, Consolas, monospace',
  },

  // 字号
  fontSize: {
    xs: '0.75rem',    // 12px
    sm: '0.875rem',   // 14px
    base: '1rem',     // 16px
    lg: '1.125rem',   // 18px
    xl: '1.25rem',    // 20px
    '2xl': '1.5rem',  // 24px
    '3xl': '1.875rem', // 30px
    '4xl': '2.25rem', // 36px
  },

  // 间距
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
    '2xl': '48px',
    '3xl': '64px',
  },

  // 圆角
  radius: {
    sm: '4px',
    DEFAULT: '8px',
    md: '12px',
    lg: '16px',
    xl: '24px',
    full: '9999px',
  },

  // 阴影
  shadows: {
    sm: '0 1px 2px rgba(0, 0, 0, 0.3)',
    DEFAULT: '0 4px 6px rgba(0, 0, 0, 0.3)',
    md: '0 10px 15px rgba(0, 0, 0, 0.3)',
    lg: '0 20px 25px rgba(0, 0, 0, 0.4)',
    glow: '0 0 20px rgba(0, 212, 170, 0.4)',
    glowDanger: '0 0 20px rgba(239, 68, 68, 0.4)',
  },

  // 过渡
  transitions: {
    fast: '150ms ease',
    DEFAULT: '250ms ease',
    slow: '400ms ease',
  },

  // 层级
  zIndex: {
    base: 0,
    dropdown: 100,
    sticky: 200,
    modal: 300,
    popover: 400,
    tooltip: 500,
    loading: 900,
    toast: 950,
  },
}

// 导出CSS变量
export const cssVariables = `
  :root {
    /* Background */
    --bg-primary: ${designTokens.colors.bg.primary};
    --bg-secondary: ${designTokens.colors.bg.secondary};
    --bg-tertiary: ${designTokens.colors.bg.tertiary};
    --bg-elevated: ${designTokens.colors.bg.elevated};
    
    /* Accent */
    --accent: ${designTokens.colors.accent.DEFAULT};
    --accent-hover: ${designTokens.colors.accent.hover};
    --accent-muted: ${designTokens.colors.accent.muted};
    --accent-glow: ${designTokens.colors.accent.glow};
    --secondary: ${designTokens.colors.secondary};
    --gold: ${designTokens.colors.gold};
    
    /* Semantic */
    --success: ${designTokens.colors.success};
    --success-bg: ${designTokens.colors.successBg};
    --danger: ${designTokens.colors.danger};
    --danger-bg: ${designTokens.colors.dangerBg};
    --warning: ${designTokens.colors.warning};
    --warning-bg: ${designTokens.colors.warningBg};
    
    /* Text */
    --text-primary: ${designTokens.colors.text.primary};
    --text-secondary: ${designTokens.colors.text.secondary};
    --text-muted: ${designTokens.colors.text.muted};
    
    /* Border */
    --border: ${designTokens.colors.border.DEFAULT};
    --border-light: ${designTokens.colors.border.light};
    
    /* Fonts */
    --font-sans: ${designTokens.fonts.sans};
    --font-mono: ${designTokens.fonts.mono};
    
    /* Spacing */
    --space-xs: ${designTokens.spacing.xs};
    --space-sm: ${designTokens.spacing.sm};
    --space-md: ${designTokens.spacing.md};
    --space-lg: ${designTokens.spacing.lg};
    --space-xl: ${designTokens.spacing.xl};
    --space-2xl: ${designTokens.spacing['2xl']};
    
    /* Radius */
    --radius-sm: ${designTokens.radius.sm};
    --radius: ${designTokens.radius.DEFAULT};
    --radius-md: ${designTokens.radius.md};
    --radius-lg: ${designTokens.radius.lg};
    
    /* Shadows */
    --shadow-sm: ${designTokens.shadows.sm};
    --shadow: ${designTokens.shadows.DEFAULT};
    --shadow-md: ${designTokens.shadows.md};
    --shadow-glow: ${designTokens.shadows.glow};
    
    /* Transitions */
    --transition-fast: ${designTokens.transitions.fast};
    --transition: ${designTokens.transitions.DEFAULT};
  }
`

export default designTokens

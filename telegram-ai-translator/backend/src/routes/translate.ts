import { Router } from 'express'

export const translateRouter = Router()

// 翻译接口
translateRouter.post('/', async (req, res) => {
  const { text, targetLang, sourceLang = 'auto' } = req.body
  
  if (!text) {
    return res.status(400).json({ error: '文本不能为空' })
  }
  
  try {
    // 方式1: 使用 OpenAI GPT API (需要配置 OPENAI_API_KEY)
    // const translatedText = await translateWithGPT(text, targetLang)
    
    // 方式2: 使用免费翻译API
    const translatedText = await translateWithFreeAPI(text, targetLang, sourceLang)
    
    res.json({
      originalText: text,
      translatedText,
      sourceLang,
      targetLang
    })
  } catch (error) {
    console.error('翻译失败:', error)
    res.status(500).json({ error: '翻译失败' })
  }
})

// 使用免费翻译API (示例 - 使用 MyMemory API)
async function translateWithFreeAPI(text: string, targetLang: string, sourceLang: string): Promise<string> {
  const langPair = sourceLang === 'auto' ? 'auto' : sourceLang + '|' + targetLang
  
  const url = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=${langPair}`
  
  try {
    const response = await fetch(url)
    const data = await response.json()
    
    if (data.responseStatus === 200) {
      return data.responseData.translatedText
    }
    
    throw new Error(data.responseDetails)
  } catch (error) {
    console.error('免费翻译API失败:', error)
    // 返回原文作为后备
    return `[${targetLang}] ${text}`
  }
}

// 使用 OpenAI GPT 翻译 (需要API Key)
async function translateWithGPT(text: string, targetLang: string): Promise<string> {
  const apiKey = process.env.OPENAI_API_KEY
  
  if (!apiKey) {
    throw new Error('OPENAI_API_KEY 未配置')
  }
  
  const langMap: Record<string, string> = {
    'zh': '中文',
    'en': 'English',
    'ja': '日本語',
    'ko': '한국어',
    'fr': 'Français',
    'es': 'Español',
    'de': 'Deutsch'
  }
  
  const targetLanguage = langMap[targetLang] || targetLang
  
  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`
    },
    body: JSON.stringify({
      model: 'gpt-3.5-turbo',
      messages: [
        {
          role: 'system',
          content: `你是一个专业翻译助手。请将以下文本翻译成${targetLanguage}，保持原文的语气和风格。只需要返回翻译结果，不需要其他解释。`
        },
        {
          role: 'user',
          content: text
        }
      ],
      temperature: 0.3
    })
  })
  
  const data = await response.json()
  return data.choices[0].message.content
}

// 批量翻译
translateRouter.post('/batch', async (req, res) => {
  const { texts, targetLang, sourceLang = 'auto' } = req.body
  
  if (!Array.isArray(texts) || texts.length === 0) {
    return res.status(400).json({ error: '文本数组不能为空' })
  }
  
  try {
    const results = await Promise.all(
      texts.map(text => translateWithFreeAPI(text, targetLang, sourceLang))
    )
    
    res.json({
      results: texts.map((text, i) => ({
        original: text,
        translated: results[i]
      }))
    })
  } catch (error) {
    console.error('批量翻译失败:', error)
    res.status(500).json({ error: '批量翻译失败' })
  }
})

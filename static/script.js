// ============================================================
// i18n Translations
// ============================================================
const translations = {
  en: {
    badge: "✈️ TripMate AI — A Multi-Agent Travel Planner with LangGraph & MCP",
    heroTitle: "Plan Your Perfect Trip with AI",
    heroDesc:
      "Search flights, discover hotels, and generate a complete travel itinerary using a multi-agent LangGraph system.",
    plannerTitle: "Where do you want to go?",
    plannerSubtitle:
      "Example: Plan a complete 7 days Japan trip from Bangladesh under 2 lakhs.",
    online: "Online",
    inputPlaceholder:
      "Plan a complete 7 days Japan trip including flights, hotels and sightseeing under 2 lakhs...",
    generateBtn: "Generate Plan",
    japanTrip: "🇯🇵 Japan Trip",
    dubaiTrip: "🇦🇪 Dubai Trip",
    thailandTrip: "🇹🇭 Thailand Trip",
    japanPrompt:
      "Plan a complete 7 days Japan trip from China including flights, hotels and sightseeing under 20000 yuan.",
    dubaiPrompt:
      "Plan a 5 days Dubai trip from Shanghai with flights, hotels and sightseeing.",
    thailandPrompt:
      "Plan a 7 days Thailand trip from Bangladesh with budget hotels and sightseeing.",
    resultTitle: "Your AI Travel Plan",
    threadLabel: "Thread ID:",
    copy: "Copy",
    copied: "Copied!",
    downloadPDF: "Download PDF",
    preparingPDF: "Preparing PDF...",
    footer:
      "Built with FastAPI, LangGraph, Groq, PostgreSQL, Tavily and AviationStack",
    emptyError: "Please enter your travel request first.",
    genericError: "Something went wrong.",
    noPlanError: "No travel plan available to download.",
    copyError: "Could not copy result.",
    pdfError: "Could not download PDF.",
  },
  zh: {
    badge: "✈️ TripMate AI — 基于LangGraph与MCP的多智能体旅行规划器",
    heroTitle: "用AI规划您的完美旅行",
    heroDesc:
      "使用多智能体LangGraph系统，搜索航班、发现酒店并生成完整的旅行行程。",
    plannerTitle: "您想去哪里？",
    plannerSubtitle:
      "示例：规划一个7天北京到日本之旅，含航班、酒店和观光，预算2万以内。",
    online: "在线",
    inputPlaceholder:
      "规划一个7天北京到日本之旅，含航班、酒店和观光，预算2万以内...",
    generateBtn: "生成计划",
    japanTrip: "🇯🇵 日本之旅",
    dubaiTrip: "KR 韩国之旅",
    thailandTrip: "🇹🇭 泰国之旅",
    japanPrompt:
      "规划一个7天日本之旅，从北京出发，含航班、酒店和观光，预算2万以内。",
    dubaiPrompt: "规划一个5天韩国之旅，从上海出发，含航班、酒店和观光。",
    thailandPrompt: "规划一个7天泰国之旅，从上海出发，含航班、酒店和观光。",
    resultTitle: "您的AI旅行计划",
    threadLabel: "会话ID：",
    copy: "复制",
    copied: "已复制！",
    downloadPDF: "下载PDF",
    preparingPDF: "正在准备PDF...",
    footer:
      "基于 FastAPI、LangGraph、Groq、PostgreSQL、Tavily 和 AviationStack 构建",
    emptyError: "请先输入您的旅行需求。",
    genericError: "出了点问题。",
    noPlanError: "没有可下载的旅行计划。",
    copyError: "无法复制结果。",
    pdfError: "无法下载PDF。",
  },
}

// ============================================================
// Language State
// ============================================================
let currentLang = localStorage.getItem("tripMate_lang") || "zh"

function setLanguage(lang) {
  currentLang = lang
  localStorage.setItem("tripMate_lang", lang)

  // Update toggle buttons
  document.querySelectorAll(".lang-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.lang === lang)
  })

  // Update all data-i18n elements
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.dataset.i18n
    if (translations[lang][key] !== undefined) {
      el.textContent = translations[lang][key]
    }
  })

  // Update placeholders
  const textarea = document.getElementById("userInput")
  if (textarea) {
    textarea.placeholder = translations[lang].inputPlaceholder
  }

  // Update generate button text
  const btnText = document.getElementById("btnText")
  if (btnText && !btnText.classList.contains("hidden")) {
    btnText.textContent = translations[lang].generateBtn
  }

  // Update quick prompt buttons
  document.querySelectorAll(".quick-prompts button").forEach((btn) => {
    const key = btn.dataset.i18n
    if (key && translations[lang][key]) {
      btn.textContent = translations[lang][key]
    }
  })

  // Update result section if visible
  const resultSection = document.getElementById("resultSection")
  if (resultSection && !resultSection.classList.contains("hidden")) {
    const threadInfo = document.getElementById("threadInfo")
    if (threadInfo && currentThreadId) {
      threadInfo.textContent = `${translations[lang].threadLabel} ${currentThreadId}`
    }
  }

  // Update document lang attribute
  document.documentElement.lang = lang === "zh" ? "zh-CN" : "en"
}

// Init language on page load
document.addEventListener("DOMContentLoaded", () => {
  setLanguage(currentLang)
})

// ============================================================
// App Logic
// ============================================================
let currentThreadId = localStorage.getItem("travel_thread_id") || null
let latestAnswerMarkdown = ""

function setPrompt(text) {
  document.getElementById("userInput").value = text
}

function setLoading(isLoading) {
  const sendBtn = document.getElementById("sendBtn")
  const btnText = document.getElementById("btnText")
  const btnLoader = document.getElementById("btnLoader")

  sendBtn.disabled = isLoading

  if (isLoading) {
    btnText.classList.add("hidden")
    btnLoader.classList.remove("hidden")
  } else {
    btnText.classList.remove("hidden")
    btnLoader.classList.add("hidden")
    btnText.textContent = translations[currentLang].generateBtn
  }
}

function showError(message) {
  const errorBox = document.getElementById("errorBox")

  errorBox.textContent = message
  errorBox.classList.remove("hidden")
}

function hideError() {
  const errorBox = document.getElementById("errorBox")

  errorBox.classList.add("hidden")
  errorBox.textContent = ""
}

function showResult(answer, threadId) {
  latestAnswerMarkdown = answer

  const resultSection = document.getElementById("resultSection")
  const resultBox = document.getElementById("resultBox")
  const threadInfo = document.getElementById("threadInfo")

  if (typeof marked !== "undefined") {
    resultBox.innerHTML = marked.parse(answer)
  } else {
    resultBox.innerText = answer
  }

  threadInfo.textContent = `${translations[currentLang].threadLabel} ${threadId}`

  resultSection.classList.remove("hidden")

  resultSection.scrollIntoView({
    behavior: "smooth",
    block: "start",
  })
}

async function sendMessage() {
  hideError()

  const input = document.getElementById("userInput")
  const message = input.value.trim()

  if (!message) {
    showError(translations[currentLang].emptyError)
    return
  }

  setLoading(true)

  try {
    const response = await fetch("/api/travel", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: message,
        thread_id: currentThreadId,
      }),
    })

    const data = await response.json()

    if (!response.ok || !data.success) {
      throw new Error(data.error || translations[currentLang].genericError)
    }

    currentThreadId = data.thread_id
    localStorage.setItem("travel_thread_id", currentThreadId)

    showResult(data.answer, data.thread_id)
  } catch (error) {
    showError(error.message)
  } finally {
    setLoading(false)
  }
}

function copyResult() {
  const resultBox = document.getElementById("resultBox")
  const text = resultBox.innerText

  if (!text) {
    return
  }

  navigator.clipboard
    .writeText(text)
    .then(() => {
      const copyBtn = document.querySelector(".copy-btn")
      const oldText = copyBtn.textContent

      copyBtn.textContent = translations[currentLang].copied

      setTimeout(() => {
        copyBtn.textContent = oldText
      }, 1400)
    })
    .catch(() => {
      showError(translations[currentLang].copyError)
    })
}

function downloadPDF() {
  const pdfContent = document.getElementById("pdfContent")

  if (!latestAnswerMarkdown || !pdfContent) {
    showError(translations[currentLang].noPlanError)
    return
  }

  const downloadBtn = document.querySelector(".download-btn")
  const oldText = downloadBtn.textContent

  downloadBtn.textContent = translations[currentLang].preparingPDF
  downloadBtn.disabled = true

  const options = {
    margin: 0.5,
    filename: "ai-travel-plan.pdf",
    image: {
      type: "jpeg",
      quality: 0.98,
    },
    html2canvas: {
      scale: 2,
      useCORS: true,
      backgroundColor: "#ffffff",
    },
    jsPDF: {
      unit: "in",
      format: "a4",
      orientation: "portrait",
    },
    pagebreak: {
      mode: ["avoid-all", "css", "legacy"],
    },
  }

  html2pdf()
    .set(options)
    .from(pdfContent)
    .save()
    .then(() => {
      downloadBtn.textContent = oldText
      downloadBtn.disabled = false
    })
    .catch(() => {
      downloadBtn.textContent = oldText
      downloadBtn.disabled = false
      showError(translations[currentLang].pdfError)
    })
}

// Quick prompt buttons — use data-prompt-key to set the prompt text
document.querySelectorAll(".quick-prompts button").forEach((btn) => {
  btn.addEventListener("click", () => {
    const promptKey = btn.dataset.promptKey
    if (promptKey && translations[currentLang][promptKey]) {
      setPrompt(translations[currentLang][promptKey])
    }
  })
})

document.addEventListener("keydown", function (event) {
  if (event.ctrlKey && event.key === "Enter") {
    sendMessage()
  }
})

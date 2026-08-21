// ============================================================
// i18n Translations
// ============================================================
const translations = {
  en: {
    badge: "✈️ TripMate AI — A Multi-Agent Travel Planner with LangGraph & MCP",
    heroTitle: "Plan Your Perfect Trip with AI",
    heroDesc:
      "The supervisor dispatches specialist agents, the guardrail blocks off-topic requests, and a human review (HITL) finalizes your itinerary.",
    plannerTitle: "Where do you want to go?",
    plannerSubtitle:
      "Example: Plan a complete 7 days Japan trip from China under 20000 yuan.",
    online: "Online",
    inputPlaceholder:
      "Plan a complete 7 days Japan trip including flights, hotels and sightseeing under 20000 yuan...",
    generateBtn: "Generate Plan",
    japanTrip: "🇯🇵 Japan Trip",
    koreaTrip: "🇰🇷 Korea Trip",
    thailandTrip: "🇹🇭 Thailand Trip",
    japanPrompt:
      "Plan a complete 7 days Japan trip from China including flights, hotels and sightseeing under 20000 yuan.",
    koreaPrompt:
      "Plan a 5 days Korea trip from Shanghai with flights, hotels and sightseeing.",
    thailandPrompt:
      "Plan a 7 days Thailand trip from Shanghai with budget hotels and sightseeing.",
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
    revisionRequired:
      "Please provide revision feedback before requesting changes.",
    reviewBadge: "Review",
    processing: "Generating your travel plan — this may take a moment...",
    planTitle: "Agent Plan",
    planSubtitle: "The supervisor routed your request to these specialists.",
    guardrailOk: "Guardrail passed",
    agentsLabel: "Selected agents",
    tripConstraintsLabel: "Trip constraints",
    constDestination: "Destination",
    constOrigin: "Origin",
    constDuration: "Duration",
    constBudget: "Budget",
    constStyle: "Style",
    constPrefs: "Preferences",
    noConstraints: "No specific trip constraints were extracted.",
    agentFlight: "✈️ Flights",
    agentHotel: "🏨 Hotels",
    agentWeather: "🌤️ Weather",
    agentBudget: "💰 Budget",
    agentItinerary: "🗺️ Itinerary",
    blockedTitle: "🛡️ This request was blocked",
    blockedReason: "Reason",
    blockedHint:
      "TripMate AI only handles travel planning. Try asking about a destination, flight, hotel, weather, budget, or itinerary.",
    approvalTitle: "Human Review Required",
    approvalSubtitle:
      "The draft itinerary is ready. Approve it to receive your final polished plan, or send revision feedback.",
    feedbackPlaceholder:
      "Optional: leave revision feedback for a better plan...",
    approveBtn: "✓ Approve",
    reviseBtn: "↩ Request Changes",
    submitApproving: "Finalizing your plan...",
    submitRevising: "Revising your plan...",
    finalApproved: "✓ Approved",
    finalRevised: "↩ Revised with your feedback",
    llmCallsLabel: "AI calls",
  },
  zh: {
    badge: "✈️ TripMate AI — 基于LangGraph与MCP的多智能体旅行规划器",
    heroTitle: "用AI规划您的完美旅行",
    heroDesc:
      "Supervisor 智能调度专家智能体，安全防护拦截无关请求，并支持人工审批（Human-in-the-Loop）后生成最终行程。",
    plannerTitle: "您想去哪里？",
    plannerSubtitle:
      "示例：规划一个7天北京到日本之旅，含航班、酒店和观光，预算2万以内。",
    online: "在线",
    inputPlaceholder:
      "规划一个7天北京到日本之旅，含航班、酒店和观光，预算2万以内...",
    generateBtn: "生成计划",
    japanTrip: "🇯🇵 日本之旅",
    koreaTrip: "🇰🇷 韩国之旅",
    thailandTrip: "🇹🇭 泰国之旅",
    japanPrompt:
      "规划一个7天日本之旅，从北京出发，含航班、酒店和观光，预算2万以内。",
    koreaPrompt: "规划一个5天韩国之旅，从上海出发，含航班、酒店和观光。",
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
    revisionRequired: "请先填写修改意见，再请求修改草案。",
    reviewBadge: "人工审批",
    processing: "正在生成您的旅行计划，请稍候…",
    planTitle: "智能体规划方案",
    planSubtitle: "Supervisor 已将您的请求分派给以下专家智能体。",
    guardrailOk: "安全防护已通过",
    agentsLabel: "已选专家",
    tripConstraintsLabel: "行程约束",
    constDestination: "目的地",
    constOrigin: "出发地",
    constDuration: "行程时长",
    constBudget: "预算",
    constStyle: "旅行风格",
    constPrefs: "特别偏好",
    noConstraints: "未提取到具体的行程约束。",
    agentFlight: "✈️ 航班",
    agentHotel: "🏨 酒店",
    agentWeather: "🌤️ 天气",
    agentBudget: "💰 预算",
    agentItinerary: "🗺️ 行程",
    blockedTitle: "🛡️ 该请求已被拦截",
    blockedReason: "拦截原因",
    blockedHint:
      "TripMate AI 仅支持旅行规划。请尝试询问目的地、航班、酒店、天气、预算或行程相关的内容。",
    approvalTitle: "需要人工审批",
    approvalSubtitle:
      "行程草案已生成，请审批。批准后将生成最终方案，或填写反馈让我们为您修改。",
    feedbackPlaceholder: "可选：填写修改意见，为您生成更合适的方案...",
    approveBtn: "✓ 批准",
    reviseBtn: "↩ 请求修改",
    submitApproving: "正在生成最终方案…",
    submitRevising: "正在根据反馈修订方案…",
    finalApproved: "✓ 已批准",
    finalRevised: "↩ 已根据反馈修订",
    llmCallsLabel: "次AI调用",
  },
}

// ============================================================
// Constants
// ============================================================
const AGENT_LABELS = {
  flight_agent: "agentFlight",
  hotel_agent: "agentHotel",
  weather_agent: "agentWeather",
  budget_agent: "agentBudget",
  itinerary_agent: "agentItinerary",
}

const CONSTRAINT_LABELS = [
  ["destination", "constDestination"],
  ["origin", "constOrigin"],
  ["duration", "constDuration"],
  ["budget", "constBudget"],
  ["travel_style", "constStyle"],
  ["special_preferences", "constPrefs"],
]

// ============================================================
// Language State
// ============================================================
let currentLang = localStorage.getItem("tripMate_lang") || "zh"

const t = (key) => {
  const val = translations[currentLang] && translations[currentLang][key]
  return val !== undefined ? val : (translations.en[key] ?? key)
}

function setLanguage(lang) {
  currentLang = lang
  localStorage.setItem("tripMate_lang", lang)

  document.querySelectorAll(".lang-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.lang === lang)
  })

  // Update all static data-i18n elements
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

  const feedbackInput = document.getElementById("feedbackInput")
  if (feedbackInput) {
    feedbackInput.placeholder = translations[lang].feedbackPlaceholder
  }

  document.documentElement.lang = lang === "zh" ? "zh-CN" : "en"

  // Rebuild dynamic content with the new language
  if (lastData) {
    renderResponse(lastData, true)
  }
}

// ============================================================
// State
// ============================================================
let currentThreadId = localStorage.getItem("travel_thread_id") || null
let latestAnswerMarkdown = ""
let lastData = null

// DOM refs
const els = {}
const grabEls = () => {
  ;["sendBtn", "btnText", "btnLoader", "processingSection", "processingText",
    "planPanel", "guardrailBadge", "agentsRow", "constraintsGrid", "supervisorNote",
    "blockedCard", "blockedReason", "approvalCard", "approvalDraft", "feedbackInput",
    "approveBtn", "approveText", "approveLoader", "reviseBtn", "reviseText", "reviseLoader",
    "resultSection", "resultBox", "resultBadge", "threadInfo", "llmCalls",
    "errorBox", "userInput",
  ].forEach((id) => {
    els[id] = document.getElementById(id)
  })
}

// ============================================================
// Processing status
// ============================================================
function showProcessing() {
  els.processingSection.classList.remove("hidden")
  els.processingText.textContent = t("processing")
}

function hideProcessing() {
  els.processingSection.classList.add("hidden")
}

// ============================================================
// Loading / error helpers
// ============================================================
function setLoading(isLoading) {
  els.sendBtn.disabled = isLoading

  if (isLoading) {
    els.btnText.classList.add("hidden")
    els.btnLoader.classList.remove("hidden")
  } else {
    els.btnText.classList.remove("hidden")
    els.btnLoader.classList.add("hidden")
    els.btnText.textContent = t("generateBtn")
  }
}

let approvalMode = null // "approve" | "revise"

function setApprovalLoading(isLoading) {
  els.approveBtn.disabled = isLoading
  els.reviseBtn.disabled = isLoading

  if (isLoading) {
    if (approvalMode === "revise") {
      els.reviseLoader.classList.remove("hidden")
      els.reviseText.classList.add("hidden")
    } else {
      els.approveLoader.classList.remove("hidden")
      els.approveText.classList.add("hidden")
    }
  } else {
    els.approveLoader.classList.add("hidden")
    els.approveText.classList.remove("hidden")
    els.reviseLoader.classList.add("hidden")
    els.reviseText.classList.remove("hidden")
    els.approveText.textContent = t("approveBtn")
    els.reviseText.textContent = t("reviseBtn")
  }
}

function showError(message) {
  els.errorBox.textContent = message
  els.errorBox.classList.remove("hidden")
}

function hideError() {
  els.errorBox.classList.add("hidden")
  els.errorBox.textContent = ""
}

// ============================================================
// Rendering
// ============================================================
function markdownToHtml(md) {
  if (typeof marked !== "undefined") {
    return marked.parse(md || "")
  }
  const div = document.createElement("div")
  div.textContent = md || ""
  return div.innerHTML
}

function renderPlanPanel(data) {
  els.planPanel.classList.remove("hidden")

  const constraints = data.trip_constraints || {}

  // Guardrail badge (always green here — blocked requests never reach here)
  els.guardrailBadge.className = "guardrail-badge ok"
  els.guardrailBadge.innerHTML = `🛡️ ${t("guardrailOk")}`

  // Selected agents
  const selected = Array.isArray(data.selected_agents)
    ? data.selected_agents.filter((a) => AGENT_LABELS[a])
    : []
  els.agentsRow.innerHTML = ""
  if (selected.length) {
    selected.forEach((agent) => {
      const chip = document.createElement("span")
      chip.className = "agent-chip"
      chip.dataset.agent = agent
      chip.textContent = t(AGENT_LABELS[agent])
      els.agentsRow.appendChild(chip)
    })
  } else {
    els.agentsRow.innerHTML = `<span class="agents-empty">—</span>`
  }

  // Trip constraints
  els.constraintsGrid.innerHTML = ""
  let tileCount = 0
  CONSTRAINT_LABELS.forEach(([key, labelKey]) => {
    let value = constraints[key]
    if (Array.isArray(value)) {
      value = value.filter(Boolean).join("、")
    }
    if (value === undefined || value === null || String(value).trim() === "") {
      return
    }
    const tile = document.createElement("div")
    tile.className = "constraint-tile"
    tile.innerHTML = `
      <div class="ct-label">${t(labelKey)}</div>
      <div class="ct-value"></div>
    `
    tile.querySelector(".ct-value").textContent = value
    els.constraintsGrid.appendChild(tile)
    tileCount += 1
  })
  if (!tileCount) {
    els.constraintsGrid.innerHTML = `<span class="constraints-empty">${t(
      "noConstraints"
    )}</span>`
  }

  // Supervisor reasoning
  els.supervisorNote.textContent = data.supervisor_reasoning || ""
}

function renderBlocked(data) {
  els.blockedCard.classList.remove("hidden")
  els.blockedReason.textContent =
    data.guardrail_reason ||
    data.final_response ||
    t("blockedHint")
}

function renderApproval(data) {
  els.approvalCard.classList.remove("hidden")

  const draft = data.itinerary || data.answer || ""
  els.approvalDraft.innerHTML = markdownToHtml(draft)

  els.feedbackInput.value = data.human_feedback || ""

  els.approveBtn.disabled = false
  els.reviseBtn.disabled = false
  els.approveText.textContent = t("approveBtn")
  els.reviseText.textContent = t("reviseBtn")
}

function renderFinal(data) {
  els.resultSection.classList.remove("hidden")

  const answer = data.answer || data.final_response || ""
  latestAnswerMarkdown = answer
  els.resultBox.innerHTML = markdownToHtml(answer)

  els.threadInfo.textContent = `${t("threadLabel")} ${currentThreadId}`
  els.llmCalls.textContent = data.llm_calls ?? 0

  if (data.approved === true) {
    els.resultBadge.textContent = t("finalApproved")
    els.resultBadge.className = "result-badge approved"
  } else if (data.human_feedback) {
    els.resultBadge.textContent = t("finalRevised")
    els.resultBadge.className = "result-badge revised"
  } else {
    els.resultBadge.className = "result-badge hidden"
  }
}

function renderResponse(data, silent = false) {
  lastData = data
  if (data.thread_id) {
    currentThreadId = data.thread_id
    localStorage.setItem("travel_thread_id", currentThreadId)
  }

  hideError()

  // Hide all dynamic sections first
  els.planPanel.classList.add("hidden")
  els.blockedCard.classList.add("hidden")
  els.approvalCard.classList.add("hidden")
  els.resultSection.classList.add("hidden")

  // Guardrail blocked
  if (data.guardrail_allowed === false) {
    renderBlocked(data)
    if (!silent) scrollToEl(els.blockedCard)
    return
  }

  // Supervisor plan panel (shown whenever routing info exists)
  const hasRouting =
    (Array.isArray(data.selected_agents) && data.selected_agents.length > 0) ||
    data.supervisor_reasoning
  if (hasRouting) {
    renderPlanPanel(data)
  }

  // HITL — waiting for human approval
  if (data.requires_approval) {
    renderApproval(data)
    if (!silent) scrollToEl(els.approvalCard)
    return
  }

  // Final polished response
  renderFinal(data)
  if (!silent) scrollToEl(els.resultSection)
}

function scrollToEl(el) {
  if (!el) return
  el.scrollIntoView({ behavior: "smooth", block: "start" })
}

// ============================================================
// API calls
// ============================================================
function setPrompt(text) {
  els.userInput.value = text
}

async function sendMessage() {
  hideError()

  const message = els.userInput.value.trim()

  if (!message) {
    showError(t("emptyError"))
    return
  }

  setLoading(true)
  showProcessing()

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
      throw new Error(data.error || t("genericError"))
    }

    renderResponse(data)
  } catch (error) {
    showError(error.message)
  } finally {
    hideProcessing()
    setLoading(false)
  }
}

async function submitApproval(approved) {
  hideError()

  const feedback = els.feedbackInput.value.trim()

  if (!approved && !feedback) {
    showError(t("revisionRequired"))
    return
  }

  approvalMode = approved ? "approve" : "revise"
  setApprovalLoading(true)

  if (approved) {
    els.approveText.textContent = t("submitApproving")
  } else {
    els.reviseText.textContent = t("submitRevising")
  }

  try {
    const response = await fetch("/api/travel/approve", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        thread_id: currentThreadId,
        approved: approved,
        feedback: feedback,
      }),
    })

    const data = await response.json()

    if (!response.ok || !data.success) {
      throw new Error(data.error || t("genericError"))
    }

    renderResponse(data)
  } catch (error) {
    showError(error.message)
    setApprovalLoading(false)
  }
}

// ============================================================
// Copy / PDF
// ============================================================
function copyResult() {
  const text = els.resultBox.innerText

  if (!text) {
    return
  }

  navigator.clipboard
    .writeText(text)
    .then(() => {
      const copyBtn = document.querySelector(".copy-btn")
      const oldText = copyBtn.textContent

      copyBtn.textContent = t("copied")

      setTimeout(() => {
        copyBtn.textContent = oldText
      }, 1400)
    })
    .catch(() => {
      showError(t("copyError"))
    })
}

function downloadPDF() {
  const pdfContent = document.getElementById("pdfContent")

  if (!latestAnswerMarkdown || !pdfContent) {
    showError(t("noPlanError"))
    return
  }

  const downloadBtn = document.querySelector(".download-btn")
  const oldText = downloadBtn.textContent

  downloadBtn.textContent = t("preparingPDF")
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
      showError(t("pdfError"))
    })
}

// ============================================================
// Init
// ============================================================
document.addEventListener("DOMContentLoaded", () => {
  grabEls()
  setLanguage(currentLang)
})

// Quick prompt buttons — use data-prompt-key to set the prompt text
document.querySelectorAll(".quick-prompts button").forEach((btn) => {
  btn.addEventListener("click", () => {
    const promptKey = btn.dataset.promptKey
    if (promptKey && translations[currentLang][promptKey]) {
      setPrompt(translations[currentLang][promptKey])
    }
  })
})

// Ctrl/Cmd + Enter to send
document.addEventListener("keydown", function (event) {
  if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
    sendMessage()
  }
})

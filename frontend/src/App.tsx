import React, { useState, useEffect, useRef } from "react";
import {
  Sparkles,
  Dna,
  Bot,
  ArrowRight,
  Activity,
  FileText,
  ShieldCheck,
  Compass,
  Cpu,
  Search,
  CheckCircle2,
  Terminal,
  HelpCircle,
  BarChart3
} from "lucide-react";
import { SystemTelemetry } from "./components/SystemTelemetry";
import { ChatHeader } from "./components/ChatHeader";
import { ChatMessage, ChatMessageData } from "./components/ChatMessage";
import { ChatInput, PRESET_DATASETS } from "./components/ChatInput";

const API_BASE = "";

export const App: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessageData[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<string>("GSE202768");

  const [currentModel, setCurrentModel] = useState<string>("gemma-3-4b");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [activeStepIndex, setActiveStepIndex] = useState<number>(0);
  const [loadingStepText, setLoadingStepText] = useState<string>("Initializing Planner Agent...");

  const chatBottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom whenever messages or loading state changes
  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // Loading animation step cycle simulation
  useEffect(() => {
    if (!isLoading) {
      setActiveStepIndex(0);
      return;
    }

    const stepsCycle = [
      "Planner Agent: Inspecting count matrix schema and checking guardrails...",
      "Computational Analyst: Fitting PyDESeq2 Negative Binomial GLM...",
      "Computational Analyst: Computing Benjamini-Hochberg FDR adjustments...",
      "Biological Interpreter: Querying Reactome & Gene Ontology pathways...",
      "Evidence Retriever: Cross-verifying statistical claims with literature...",
      "Adversarial Critic: Inspecting fold-change directions & certifying outputs..."
    ];

    let step = 0;
    const interval = setInterval(() => {
      step = (step + 1) % stepsCycle.length;
      setActiveStepIndex(step);
      setLoadingStepText(stepsCycle[step]);
    }, 1200);

    return () => clearInterval(interval);
  }, [isLoading]);

  // Send message handler
  const handleSendMessage = async (query: string, dataset: string, uploadedFile?: any) => {
    if (isLoading) return;

    const userMessageId = `user-${Date.now()}`;
    const assistantMessageId = `assistant-${Date.now()}`;

    // Add user's message to stream
    const userMsg: ChatMessageData = {
      id: userMessageId,
      sender: "user",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      query: query,
      dataset: uploadedFile ? uploadedFile.name : dataset,
      modelName: currentModel,
      uploadedFileName: uploadedFile ? uploadedFile.name : undefined
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/api/run`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          dataset: dataset,
          model: currentModel,
          query: query,
          use_critic: true,
          custom_filename: uploadedFile ? uploadedFile.name : undefined
        })
      });

      if (!response.ok) {
        throw new Error(`Pipeline API returned status ${response.status}`);
      }

      const data = await response.json();

      const assistantMsg: ChatMessageData = {
        id: assistantMessageId,
        sender: "assistant",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        query: query,
        dataset: data.dataset || dataset,
        modelName: data.model?.name || currentModel,
        plainSummary: data.plain_summary,
        steps: data.steps,
        totalLatency: data.total_latency_s,
        stats: data.stats,
        topGenes: data.top_genes,
        sigPathways: data.sig_pathways,
        interp: data.interp,
        figures: data.figures,
        downloads: data.downloads
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      console.error("Execution error:", err);

      // Fallback assistant error message
      const errorMsg: ChatMessageData = {
        id: assistantMessageId,
        sender: "assistant",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        plainSummary: `Unable to complete pipeline execution: ${err.message || "Network error"}. Please make sure the backend service is running at http://localhost:8000.`,
        dataset: dataset
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setMessages([]);
    setSelectedDataset("GSE202768");
  };

  const handleQuickPrompt = (datasetId: string, promptText: string) => {
    setSelectedDataset(datasetId);
    handleSendMessage(promptText, datasetId);
  };

  return (
    <div className="relative min-h-screen bg-[#070A0A] text-[#F2F4F3] font-sans grain flex flex-col selection:bg-[#14BE8A]/30">
      
      {/* Top Floating Telemetry Card (Desktop pinned top-left, mobile collapsible) */}
      <SystemTelemetry
        currentModel={currentModel}
        onModelChange={(newModel) => setCurrentModel(newModel)}
        apiBaseUrl={API_BASE}
      />

      {/* Main App Navigation Header */}
      <ChatHeader onReset={handleReset} apiBaseUrl={API_BASE} />

      {/* Central Conversational Stream */}
      <main className="flex-1 w-full max-w-4xl mx-auto px-4 pt-6 pb-72 overflow-y-auto">
        
        {/* Welcome Empty State */}
        {messages.length === 0 && (
          <div className="py-12 md:py-20 flex flex-col items-center text-center animate-in fade-in duration-500">
            
            {/* Edge Badge */}
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#14BE8A]/10 border border-[#14BE8A]/30 text-[#14BE8A] text-xs font-semibold mb-6 shadow-sm">
              <Sparkles className="w-3.5 h-3.5 text-[#14BE8A]" />
              Autonomous Edge Multi-Agent Transcriptomics
            </div>

            {/* Main Greeting */}
            <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight text-white mb-4 max-w-2xl leading-tight">
              What biological insight can we discover today?
            </h1>
            
            <p className="text-sm md:text-base text-gray-400 max-w-xl mb-10 leading-relaxed">
              Upload your RNA-seq matrix or pick a benchmark dataset. Five autonomous agents 
              will formulate plans, compute differential expression, ground claims in scientific literature, 
              and verify conclusions against hallucinations.
            </p>

            {/* Quick-Start Prompt Cards */}
            <div className="w-full grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl text-left">
              
              <button
                onClick={() =>
                  handleQuickPrompt(
                    "GSE202768",
                    "Execute complete multi-agent analysis for PRRX1 knockdown in Hs578T Triple-Negative Breast Cancer."
                  )
                }
                className="group p-4 rounded-2xl bg-white/[0.03] hover:bg-white/[0.06] border border-white/10 hover:border-[#14BE8A]/50 transition-all text-left flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-mono font-bold text-[#14BE8A] bg-[#14BE8A]/10 px-2 py-0.5 rounded border border-[#14BE8A]/20">
                      GSE202768
                    </span>
                    <ArrowRight className="w-4 h-4 text-gray-500 group-hover:text-[#14BE8A] group-hover:translate-x-1 transition-all" />
                  </div>
                  <h3 className="text-sm font-semibold text-white group-hover:text-[#14BE8A] transition-colors">
                    PRRX1 Knockdown in TNBC
                  </h3>
                  <p className="text-xs text-gray-400 mt-1 line-clamp-2">
                    PyDESeq2 GLM on 14,009 genes. Demonstrates agent detection of ECM upregulation and critic self-correction.
                  </p>
                </div>
              </button>

              <button
                onClick={() =>
                  handleQuickPrompt(
                    "GSE113650",
                    "Analyze differential expression between Triple-Negative and Receptor-Positive breast cancer lines."
                  )
                }
                className="group p-4 rounded-2xl bg-white/[0.03] hover:bg-white/[0.06] border border-white/10 hover:border-[#14BE8A]/50 transition-all text-left flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-mono font-bold text-[#14BE8A] bg-[#14BE8A]/10 px-2 py-0.5 rounded border border-[#14BE8A]/20">
                      GSE113650
                    </span>
                    <ArrowRight className="w-4 h-4 text-gray-500 group-hover:text-[#14BE8A] group-hover:translate-x-1 transition-all" />
                  </div>
                  <h3 className="text-sm font-semibold text-white group-hover:text-[#14BE8A] transition-colors">
                    TNBC vs Receptor-Positive Lines
                  </h3>
                  <p className="text-xs text-gray-400 mt-1 line-clamp-2">
                    CuffDiff cross-reference across 22,048 genes to evaluate aggressive epithelial-mesenchymal markers.
                  </p>
                </div>
              </button>

              <button
                onClick={() =>
                  handleQuickPrompt(
                    "GSE95304",
                    "Verify how the system handles normalized FPKM matrices and prevents discrete model misuse."
                  )
                }
                className="group p-4 rounded-2xl bg-white/[0.03] hover:bg-white/[0.06] border border-white/10 hover:border-amber-500/50 transition-all text-left flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-mono font-bold text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded border border-amber-400/20">
                      GSE95304
                    </span>
                    <ArrowRight className="w-4 h-4 text-gray-500 group-hover:text-amber-400 group-hover:translate-x-1 transition-all" />
                  </div>
                  <h3 className="text-sm font-semibold text-white group-hover:text-amber-400 transition-colors">
                    Refusal Guardrail Test (FPKM)
                  </h3>
                  <p className="text-xs text-gray-400 mt-1 line-clamp-2">
                    shMyc and shFra-1 knockdown. Tests Planner refusal of DESeq2 on non-integer data.
                  </p>
                </div>
              </button>

              <button
                onClick={() =>
                  handleQuickPrompt(
                    "GSE336903",
                    "Execute zero-shot smoke test on mouse colorectal organoid treatment profiles."
                  )
                }
                className="group p-4 rounded-2xl bg-white/[0.03] hover:bg-white/[0.06] border border-white/10 hover:border-[#14BE8A]/50 transition-all text-left flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-mono font-bold text-[#14BE8A] bg-[#14BE8A]/10 px-2 py-0.5 rounded border border-[#14BE8A]/20">
                      GSE336903
                    </span>
                    <ArrowRight className="w-4 h-4 text-gray-500 group-hover:text-[#14BE8A] group-hover:translate-x-1 transition-all" />
                  </div>
                  <h3 className="text-sm font-semibold text-white group-hover:text-[#14BE8A] transition-colors">
                    Zero-Shot Organoid Smoke Test
                  </h3>
                  <p className="text-xs text-gray-400 mt-1 line-clamp-2">
                    Unseen mouse colorectal dataset. Tests pipeline adaptation, organism auto-detection, and Welch's t-test.
                  </p>
                </div>
              </button>
            </div>

            {/* Architecture Highlights Footer */}
            <div className="mt-12 flex flex-wrap items-center justify-center gap-6 text-xs text-gray-500 font-mono">
              <span className="flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-[#14BE8A]" />
                100% Schema Compliant
              </span>
              <span className="flex items-center gap-1.5">
                <Activity className="w-4 h-4 text-[#14BE8A]" />
                0% Hallucinated Genes
              </span>
              <span className="flex items-center gap-1.5">
                <FileText className="w-4 h-4 text-[#14BE8A]" />
                IEEE/ACM LaTeX Verified
              </span>
            </div>
          </div>
        )}

        {/* Message Thread */}
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} apiBaseUrl={API_BASE} />
        ))}

        {/* Active Pipeline Orchestration Loader */}
        {isLoading && (
          <div className="mb-8 p-6 rounded-2xl bg-gradient-to-b from-[#111815] to-[#0D1412] border border-[#14BE8A]/30 shadow-[0_4px_30px_rgba(20,190,138,0.1)] animate-in fade-in duration-300">
            
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="relative flex items-center justify-center w-8 h-8 rounded-xl bg-[#14BE8A]/20 text-[#14BE8A] border border-[#14BE8A]/40">
                  <Bot className="w-4 h-4 animate-bounce" />
                  <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-[#14BE8A] animate-ping" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    BioAgent-Lite Autonomous Pipeline Running
                    <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded-full bg-[#14BE8A]/20 text-[#14BE8A] border border-[#14BE8A]/30">
                      LangGraph DAG
                    </span>
                  </h3>
                  <p className="text-xs text-[#14BE8A] font-mono mt-0.5 flex items-center gap-1.5">
                    <span className="inline-block w-2 h-2 rounded-full bg-[#14BE8A] animate-pulse" />
                    {loadingStepText}
                  </p>
                </div>
              </div>

              <div className="text-right hidden sm:block">
                <span className="text-[11px] font-mono text-gray-400">Target Dataset</span>
                <p className="text-xs font-mono font-bold text-white">{selectedDataset}</p>
              </div>
            </div>

            {/* Agent Progress Bar */}
            <div className="w-full bg-white/5 rounded-full h-1.5 mb-4 overflow-hidden">
              <div
                className="bg-gradient-to-r from-[#14BE8A] via-[#24f0b0] to-[#14BE8A] h-1.5 rounded-full transition-all duration-700 ease-out"
                style={{ width: `${Math.min(100, (activeStepIndex + 1) * 18)}%` }}
              />
            </div>

            {/* Agent Sequence Indicators */}
            <div className="grid grid-cols-5 gap-2 pt-2 border-t border-white/5">
              {[
                { name: "Planner", icon: Compass, idx: 0 },
                { name: "Analyst", icon: Cpu, idx: 1 },
                { name: "Interpreter", icon: Dna, idx: 2 },
                { name: "Retriever", icon: Search, idx: 3 },
                { name: "Critic", icon: ShieldCheck, idx: 4 }
              ].map((agent) => {
                const IconComponent = agent.icon;
                const isPassed = activeStepIndex >= agent.idx;
                const isCurrent = activeStepIndex === agent.idx;

                return (
                  <div
                    key={agent.name}
                    className={`flex items-center gap-1.5 px-2 py-1.5 rounded-lg text-[11px] font-mono transition-all ${
                      isCurrent
                        ? "bg-[#14BE8A]/20 text-[#14BE8A] border border-[#14BE8A]/40 font-bold"
                        : isPassed
                        ? "bg-white/5 text-gray-300"
                        : "text-gray-600 opacity-60"
                    }`}
                  >
                    <IconComponent className={`w-3.5 h-3.5 ${isCurrent ? "animate-spin" : ""}`} />
                    <span className="truncate hidden md:inline">{agent.name}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        <div ref={chatBottomRef} />
      </main>

      {/* Fixed Bottom Input Area with Smooth Fade Backdrop */}
      <div className="fixed bottom-0 left-0 right-0 z-20 pointer-events-none bg-gradient-to-t from-[#070A0A] via-[#070A0A]/95 to-transparent pt-8 pb-2">
        <div className="max-w-4xl mx-auto px-4 pointer-events-auto">
          <ChatInput
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            selectedDataset={selectedDataset}
            onSelectDataset={(ds) => setSelectedDataset(ds)}
            apiBaseUrl={API_BASE}
          />
        </div>
      </div>
    </div>
  );
};

export default App;

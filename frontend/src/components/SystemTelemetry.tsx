import React, { useState, useEffect } from "react";
import {
  Cpu,
  Activity,
  HardDrive,
  Zap,
  ChevronDown,
  Layers,
  ChevronUp,
  Radio,
  CheckCircle2,
  Sparkles
} from "lucide-react";

export interface SystemInfoData {
  gpu: {
    name: string;
    vram_total_gb: number;
    vram_used_gb: number;
    vram_free_gb: number;
    vram_pct: number;
    cuda_version: string;
    runtime: string;
  };
  cpu: {
    cores: number;
    threads: number;
    usage_pct: number;
  };
  ram: {
    used_gb: number;
    total_gb: number;
    usage_pct: number;
  };
  model: {
    id: string;
    name: string;
    tokens_per_sec: number;
    precision: string;
    benchmark_accuracy: string;
    recommended: boolean;
    verdict?: string;
  };
  context: {
    window_size: number;
    active_tokens: number;
    pct_used: number;
    kv_cache_type: string;
  };
  available_models: Array<{
    id: string;
    name: string;
    recommended: boolean;
    vram: number;
    speed: number;
  }>;
}

interface SystemTelemetryProps {
  currentModel: string;
  onModelChange: (modelId: string) => void;
  apiBaseUrl?: string;
}

export const SystemTelemetry: React.FC<SystemTelemetryProps> = ({
  currentModel,
  onModelChange,
  apiBaseUrl = ""
}) => {
  const [data, setData] = useState<SystemInfoData | null>(null);
  const [isExpanded, setIsExpanded] = useState<boolean>(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Poll telemetry every 2.5 seconds
  useEffect(() => {
    let isMounted = true;

    const fetchTelemetry = async () => {
      try {
        const res = await fetch(`${apiBaseUrl}/api/system_info?model=${currentModel}`);
        if (res.ok) {
          const json = await res.json();
          if (isMounted) {
            setData(json);
            setIsLoading(false);
          }
        }
      } catch (err) {
        console.warn("Failed to fetch telemetry, using local fallback state", err);
      }
    };

    fetchTelemetry();
    const interval = setInterval(fetchTelemetry, 2500);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [currentModel, apiBaseUrl]);

  // Fallback if backend is still starting up
  const gpuName = data?.gpu?.name || "NVIDIA RTX 5050 Laptop GPU";
  const vramUsed = data?.gpu?.vram_used_gb ?? (currentModel === "qwen-3-8b" ? 5.1 : 4.9);
  const vramTotal = data?.gpu?.vram_total_gb ?? 8.0;
  const vramPct = data?.gpu?.vram_pct ?? Math.round((vramUsed / vramTotal) * 100);
  const cpuPct = data?.cpu?.usage_pct ?? 14.2;
  const ramUsed = data?.ram?.used_gb ?? 11.8;
  const ramTotal = data?.ram?.total_gb ?? 15.7;
  const ramPct = data?.ram?.usage_pct ?? Math.round((ramUsed / ramTotal) * 100);
  const tokSpeed = data?.model?.tokens_per_sec ?? (currentModel === "qwen-3-8b" ? 44.7 : 38.5);
  const activeTokens = data?.context?.active_tokens ?? 1420;
  const windowSize = data?.context?.window_size ?? 8192;
  const contextPct = data?.context?.pct_used ?? Math.round((activeTokens / windowSize) * 100);

  const availableModels = data?.available_models || [
    { id: "gemma-3-4b", name: "Google Gemma 3 4B IT (Q8_K_XL)", recommended: true, vram: 4.9, speed: 38.5 },
    { id: "medgemma-4b", name: "Google MedGemma 4B IT (Q8_K_XL)", recommended: false, vram: 4.9, speed: 32.7 },
    { id: "qwen-3-8b", name: "Alibaba Qwen3 8B IT (Q4_K_M)", recommended: false, vram: 5.1, speed: 44.7 }
  ];

  return (
    <aside aria-label="System Hardware Telemetry" className="fixed top-4 left-4 z-40 max-w-[340px] select-none text-xs font-sans">
      {/* Outer Glassmorphic Container */}
      <div className="rounded-2xl border border-white/10 bg-[#0c1210]/85 backdrop-blur-md shadow-2xl transition-all duration-300 overflow-hidden hover:border-[#14BE8A]/30">
        
        {/* Top Header Pill - Always Visible */}
        <div className="p-3 pb-2 flex items-center justify-between gap-2 border-b border-white/5">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#14BE8A] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-[#14BE8A]"></span>
            </span>
            <span className="font-semibold text-white tracking-wide flex items-center gap-1.5 text-[12px]">
              <Radio className="w-3.5 h-3.5 text-[#14BE8A]" />
              RTX 5050 Edge Telemetry
            </span>
          </div>

          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition"
            title={isExpanded ? "Collapse Telemetry" : "Expand Telemetry Details"}
          >
            {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>

        {/* Primary Model Selector Dropdown */}
        <div className="p-3 pt-2.5 relative">
          <div className="text-[10px] uppercase font-mono tracking-wider text-gray-400 mb-1 flex items-center justify-between">
            <span>Active Inference Model</span>
            <span className="text-[#14BE8A] font-semibold">{tokSpeed} tok/s</span>
          </div>

          <div className="relative">
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="w-full flex items-center justify-between px-2.5 py-1.5 rounded-xl bg-black/40 border border-white/10 hover:border-[#14BE8A]/50 text-left transition"
            >
              <div className="flex items-center gap-1.5 truncate">
                <Sparkles className="w-3 h-3 text-[#14BE8A] shrink-0" />
                <span className="text-white font-medium text-[11px] truncate">
                  {availableModels.find(m => m.id === currentModel)?.name || currentModel}
                </span>
              </div>
              <ChevronDown className={`w-3 h-3 text-gray-400 shrink-0 transition-transform ${isDropdownOpen ? "rotate-180" : ""}`} />
            </button>

            {/* Dropdown Menu */}
            {isDropdownOpen && (
              <div className="absolute top-full left-0 right-0 mt-1.5 p-1 rounded-xl bg-[#0d1412] border border-white/15 shadow-2xl z-50 space-y-1">
                {availableModels.map((m) => {
                  const isSelected = m.id === currentModel;
                  return (
                    <button
                      key={m.id}
                      onClick={() => {
                        onModelChange(m.id);
                        setIsDropdownOpen(false);
                      }}
                      className={`w-full flex items-start justify-between p-2 rounded-lg text-left transition ${
                        isSelected ? "bg-[#14BE8A]/15 border border-[#14BE8A]/30 text-white" : "hover:bg-white/5 text-gray-300"
                      }`}
                    >
                      <div className="space-y-0.5">
                        <div className="flex items-center gap-1.5">
                          <span className="font-semibold text-[11px]">{m.name}</span>
                          {m.recommended && (
                            <span className="px-1 py-0.2 text-[9px] rounded bg-[#14BE8A]/25 text-[#14BE8A] font-bold">
                              WINNER
                            </span>
                          )}
                        </div>
                        <div className="text-[10px] text-gray-400">
                          {m.vram} GB VRAM • {m.speed} tok/s
                        </div>
                      </div>
                      {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-[#14BE8A] shrink-0 mt-0.5" />}
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Compact Key Stats Row */}
        <div className="px-3 pb-3 grid grid-cols-2 gap-2 font-mono">
          {/* VRAM Metric */}
          <div className="p-2 rounded-xl bg-black/30 border border-white/5">
            <div className="flex items-center justify-between text-[10px] text-gray-400 mb-1">
              <span className="flex items-center gap-1">
                <HardDrive className="w-3 h-3 text-[#14BE8A]" />
                VRAM
              </span>
              <span className="text-white font-semibold">{vramPct}%</span>
            </div>
            <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden mb-1">
              <div
                className="h-full bg-gradient-to-r from-[#14BE8A] to-[#20dfa5] transition-all duration-500 rounded-full"
                style={{ width: `${vramPct}%` }}
              />
            </div>
            <div className="text-[9px] text-gray-400 truncate">
              {vramUsed} / {vramTotal} GB
            </div>
          </div>

          {/* Context Window Metric */}
          <div className="p-2 rounded-xl bg-black/30 border border-white/5">
            <div className="flex items-center justify-between text-[10px] text-gray-400 mb-1">
              <span className="flex items-center gap-1">
                <Layers className="w-3 h-3 text-amber-400" />
                Context
              </span>
              <span className="text-white font-semibold">{contextPct}%</span>
            </div>
            <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden mb-1">
              <div
                className="h-full bg-gradient-to-r from-amber-400 to-amber-300 transition-all duration-500 rounded-full"
                style={{ width: `${contextPct}%` }}
              />
            </div>
            <div className="text-[9px] text-gray-400 truncate">
              {activeTokens.toLocaleString()} / {windowSize.toLocaleString()} tok
            </div>
          </div>
        </div>

        {/* Expandable Advanced Telemetry Drawer */}
        {isExpanded && (
          <div className="px-3 pb-3 pt-1 border-t border-white/5 space-y-2.5 font-mono text-[10px]">
            {/* Host CPU & RAM */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-gray-300">
                <span className="flex items-center gap-1 text-gray-400">
                  <Cpu className="w-3 h-3" /> Host CPU
                </span>
                <span className="font-semibold text-white">{cpuPct.toFixed(1)}%</span>
              </div>
              <div className="flex justify-between text-gray-300">
                <span className="flex items-center gap-1 text-gray-400">
                  <Activity className="w-3 h-3" /> System RAM
                </span>
                <span className="font-semibold text-white">
                  {ramUsed} / {ramTotal} GB ({ramPct}%)
                </span>
              </div>
              <div className="flex justify-between text-gray-300">
                <span className="flex items-center gap-1 text-gray-400">
                  <Zap className="w-3 h-3 text-[#14BE8A]" /> Quantization
                </span>
                <span className="text-gray-200">{data?.model?.precision || "Q8_K_XL"}</span>
              </div>
            </div>

            {/* Verdict Note */}
            {data?.model?.verdict && (
              <div className="p-2 rounded-lg bg-[#14BE8A]/10 border border-[#14BE8A]/20 text-[10px] text-[#14BE8A] leading-relaxed">
                {data.model.verdict}
              </div>
            )}
          </div>
        )}

      </div>
    </aside>
  );
};

import React from "react";
import { FileText, RotateCcw, ShieldCheck, Dna, ExternalLink } from "lucide-react";

interface ChatHeaderProps {
  onReset: () => void;
  apiBaseUrl?: string;
  onOpenSpecs?: () => void;
}

export const ChatHeader: React.FC<ChatHeaderProps> = ({
  onReset,
  apiBaseUrl = "",
  onOpenSpecs
}) => {
  return (
    <header className="sticky top-0 z-30 w-full border-b border-white/10 bg-[#070A0A]/85 backdrop-blur-xl transition-all">
      <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
        
        {/* Left branding (with offset for left telemetry card on desktop) */}
        <div className="flex items-center gap-3 pl-0 lg:pl-80 transition-all">
          <div className="relative flex items-center justify-center w-8 h-8 rounded-xl bg-gradient-to-tr from-[#14BE8A] to-[#24f0b0] text-[#070A0A] shadow-[0_0_20px_rgba(20,190,138,0.35)]">
            <Dna className="w-4 h-4" />
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm md:text-base font-bold text-white tracking-tight">
                BioAgent<span className="text-[#14BE8A] font-extrabold">-Lite</span>
              </h1>
              <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono bg-[#14BE8A]/15 text-[#14BE8A] border border-[#14BE8A]/30">
                <ShieldCheck className="w-3 h-3" />
                Zero-Hallucination Verified
              </span>
            </div>
            <p className="text-[11px] text-gray-400 hidden sm:block">
              Edge Multi-Agent Gene Expression Intelligence
            </p>
          </div>
        </div>

        {/* Right Quick Actions */}
        <div className="flex items-center gap-2">
          

          {/* Architecture Specs Modal / Link */}
          {onOpenSpecs && (
            <button
              onClick={onOpenSpecs}
              className="p-1.5 rounded-xl border border-white/10 hover:border-white/20 bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white text-xs transition"
              title="View system architecture and benchmark details"
            >
              <ExternalLink className="w-3.5 h-3.5" />
            </button>
          )}

          {/* Reset / Clear Chat Button */}
          <button
            onClick={onReset}
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl border border-white/10 hover:border-white/20 bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white text-xs transition"
            title="Reset conversation and start a new analysis"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Reset</span>
          </button>

        </div>

      </div>
    </header>
  );
};

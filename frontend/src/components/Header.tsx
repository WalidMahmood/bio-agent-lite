import { Badge } from "@/components/ui/badge"
import { Activity, FlaskConical, GitBranch, Zap } from "lucide-react"

export function Header({ live }: { live?: boolean }) {
  return (
    <header className="sticky top-0 z-30 backdrop-blur-xl bg-void/70 border-b border-[rgba(45,90,75,0.14)]">
      <div className="max-w-[1440px] mx-auto px-6 lg:px-8 h-[64px] flex items-center justify-between">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-sage flex items-center justify-center">
              <FlaskConical className="w-5 h-5 text-void" />
            </div>
            <div>
              <div className="text-[15px] font-bold tracking-tight leading-none">BioAgent<span className="font-light text-muted">-Lite</span></div>
              <div className="text-[10px] font-mono uppercase tracking-[0.12em] text-muted -mt-0.5">CSE 763 · Local 4B</div>
            </div>
          </div>
          <div className="hidden lg:flex items-center gap-2 ml-4">
            <Badge variant="sage" className="gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-sage animate-pulseDot" /> Gemma 3 4B Q4</Badge>
            <Badge variant="default" className="hidden xl:inline-flex gap-1"><GitBranch className="w-3 h-3" /> LangGraph · 5 roles</Badge>
            <Badge variant="default" className="hidden xl:inline-flex">DESeq2 · clusterProfiler</Badge>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden md:flex items-center gap-3 text-xs font-mono">
            <span className="flex items-center gap-1.5 text-muted"><Activity className="w-3.5 h-3.5 text-sage" />{live ? "LIVE WORKFLOW" : "IDLE"}</span>
            <span className="w-px h-4 bg-border" />
            <span className="text-muted">8GB VRAM · 16GB RAM</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="hidden sm:flex items-center gap-1.5 pl-3 pr-1 py-1 rounded-full bg-elevated border border-border">
              <Zap className="w-3 h-3 text-amber" />
              <span className="text-[11px] font-mono text-muted">LATENCY</span>
              <span className="text-xs font-mono font-semibold bg-void px-2 py-0.5 rounded-full border border-border">~1.8s</span>
            </div>
            <div className={`w-2 h-2 rounded-full ${live ? "bg-sage shadow-[0_0_8px_rgba(20,190,138,0.6)] animate-pulseDot" : "bg-muted/40"}`} />
          </div>
        </div>
      </div>
    </header>
  )
}

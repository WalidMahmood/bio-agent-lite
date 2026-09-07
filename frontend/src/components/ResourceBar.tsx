import { Cpu, HardDrive, Layers, Timer } from "lucide-react"
import { Badge } from "@/components/ui/badge"

export function ResourceBar() {
  return (
    <div className="rounded-[24px] bg-surface border border-border p-4 shadow-lab">
      <div className="flex items-center justify-between mb-3">
        <span className="text-[11px] font-mono uppercase tracking-[0.12em] text-muted flex items-center gap-2"><Layers className="w-3.5 h-3.5" /> Resource · Local</span>
        <Badge variant="sage" className="text-[10px]">llama.cpp · Q4_0</Badge>
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {[
          { k: "VRAM", v: "5.1 / 8.0 GB", pct: 64, icon: Cpu },
          { k: "RAM", v: "9.2 / 16 GB", pct: 57, icon: HardDrive },
          { k: "TOKENS", v: "2,412 · 5 calls", pct: 48, icon: Layers },
          { k: "LATENCY", v: "42.3s total", pct: 72, icon: Timer },
        ].map(m => (
          <div key={m.k} className="rounded-2xl bg-void border border-border p-3">
            <div className="flex items-center gap-1.5 text-[10px] font-mono uppercase tracking-[0.1em] text-muted"><m.icon className="w-3 h-3" />{m.k}</div>
            <div className="text-sm font-mono font-semibold mt-1">{m.v}</div>
            <div className="h-1.5 rounded-full bg-elevated mt-2 overflow-hidden"><div className="h-full bg-sage rounded-full" style={{ width: `${m.pct}%` }} /></div>
          </div>
        ))}
      </div>
      <div className="mt-3 flex flex-wrap gap-2 text-[11px] font-mono text-muted">
        <span className="px-2 py-1 rounded-full bg-void border border-border">Chroma bge-small 384d</span>
        <span className="px-2 py-1 rounded-full bg-void border border-border">Celery + Redis</span>
        <span className="px-2 py-1 rounded-full bg-void border border-border">Postgres · traces</span>
      </div>
    </div>
  )
}

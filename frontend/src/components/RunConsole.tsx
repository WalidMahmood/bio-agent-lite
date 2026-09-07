import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Play, Pause, RotateCcw, Settings2, Database, FlaskConical, AlertTriangle } from "lucide-react"

type Props = { running: boolean; onToggle: () => void; progress: number }

const datasets = [
  { id: "GSE202768", label: "PRRX1 KD", n: 16, type: "count", role: "development", active: true },
  { id: "GSE336903", label: "Control vs Trt", n: 6, type: "FPKM", role: "smoke", active: false },
  { id: "GSE95304", label: "shFra-1 etc", n: 20, type: "FPKM", role: "held-out", active: false },
  { id: "GSE113650", label: "TNBC vs non", n: 6, type: "processed", role: "external", active: false },
]

export function RunConsole({ running, onToggle, progress }: Props) {
  const [contrast, setContrast] = useState("PRRX1_KD vs Control")
  const [padj, setPadj] = useState("0.05")
  const [tick, setTick] = useState(0)
  useEffect(() => {
    if (!running) return
    const id = setInterval(() => setTick(t => (t + 1) % 1000), 120)
    return () => clearInterval(id)
  }, [running])

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle><FlaskConical className="w-3.5 h-3.5 text-sage" /> Run Console</CardTitle>
        <p className="text-xs text-muted font-mono">Deterministic first, LLM second — DESeq2 never hallucinates a p-value.</p>
      </CardHeader>
      <CardContent className="space-y-5">
        {/* Dataset picker - asymmetric */}
        <div className="grid grid-cols-2 gap-2">
          {datasets.map(d => (
            <button
              key={d.id}
              className={`text-left rounded-2xl p-3 border transition-all ${d.active ? "bg-sage text-void border-sage shadow-glow" : "bg-elevated border-border hover:border-[rgba(45,90,75,0.3)] text-ink"}`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold tracking-tight">{d.id}</span>
                {d.active && <span className="w-1.5 h-1.5 rounded-full bg-void animate-pulseDot" />}
              </div>
              <div className={`text-[11px] font-mono ${d.active ? "text-void/70" : "text-muted"}`}>{d.label} · {d.n} samples · {d.type}</div>
              <Badge variant={d.active ? "default" : "default"} className={`mt-2 text-[9px] ${d.active ? "bg-void text-sage border-void" : ""}`}>{d.role}</Badge>
            </button>
          ))}
        </div>

        <div className="grid grid-cols-[1.4fr_0.8fr] gap-3">
          <label className="space-y-1.5">
            <span className="text-[10px] font-mono uppercase tracking-[0.12em] text-muted">Contrast</span>
            <select value={contrast} onChange={e => setContrast(e.target.value)} className="w-full h-10 rounded-xl bg-void border border-border px-3 text-sm font-mono">
              <option>PRRX1_KD vs Control</option>
              <option>shFra-1 vs Scrambled</option>
              <option>TNBC vs non-TNBC</option>
            </select>
          </label>
          <label className="space-y-1.5">
            <span className="text-[10px] font-mono uppercase tracking-[0.12em] text-muted">padj threshold</span>
            <select value={padj} onChange={e => setPadj(e.target.value)} className="w-full h-10 rounded-xl bg-void border border-border px-3 text-sm font-mono">
              <option>0.05</option>
              <option>0.01</option>
              <option>0.10</option>
            </select>
          </label>
        </div>

        <div className="flex items-center gap-2 text-[11px] font-mono text-muted bg-void rounded-xl px-3 py-2 border border-border">
          <Database className="w-3.5 h-3.5" /> <span>Count matrix validated</span>
          <span className="ml-auto flex items-center gap-1.5 text-sage"><span className="w-1.5 h-1.5 bg-sage rounded-full animate-pulseDot" /> {tick % 2 === 0 ? "FPKM→DESeq2 blocked" : "count ok → proceed"}</span>
        </div>

        {/* Progress */}
        <div className="space-y-2">
          <div className="flex justify-between text-[11px] font-mono">
            <span className="text-muted uppercase tracking-[0.08em]">Pipeline</span>
            <span className="text-sage">{progress}% · {running ? "computing" : "idle"}</span>
          </div>
          <div className="h-2 rounded-full bg-void border border-border overflow-hidden">
            <motion.div className="h-full bg-sage" animate={{ width: `${progress}%` }} transition={{ type: "spring", stiffness: 100, damping: 20 }} />
          </div>
          <div className="flex gap-1.5">
            {["Validate","DESeq2","Enrich","Evidence","Critic"].map((s, i) => (
              <span key={s} className={`flex-1 h-1 rounded-full ${i * 20 < progress ? "bg-sage" : "bg-border"}`} />
            ))}
          </div>
        </div>

        <div className="flex gap-2">
          <Button onClick={onToggle} className="flex-1 gap-2">{running ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />} {running ? "Pause" : "Start run"}</Button>
          <Button variant="ghost" size="icon"><RotateCcw className="w-4 h-4" /></Button>
          <Button variant="ghost" size="icon"><Settings2 className="w-4 h-4" /></Button>
        </div>

        <div className="flex items-center gap-2 text-[11px] font-mono text-amber bg-amber/10 border border-amber/20 rounded-xl px-3 py-2">
          <AlertTriangle className="w-3.5 h-3.5" /> FPKM detected in GSE336903 — DESeq2 will refuse. Correct by design.
        </div>
      </CardContent>
    </Card>
  )
}

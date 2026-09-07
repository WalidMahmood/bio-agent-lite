import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Check, Clock, Loader2, Search, Dna, FlaskConical, ShieldCheck, BookOpen, Waypoints } from "lucide-react"

const steps = [
  { id: "planner", label: "Planner", icon: Waypoints, desc: "comparison · design formula", status: "done" as const, time: "0.4s" },
  { id: "analyst", label: "Computational Analyst", icon: FlaskConical, desc: "DESeq2 · padj < 0.05 · 1,247 sig", status: "done" as const, time: "18.2s" },
  { id: "interpreter", label: "Biological Interpreter", icon: Dna, desc: "top genes · pathway draft", status: "active" as const, time: "—" },
  { id: "evidence", label: "Evidence Retriever", icon: BookOpen, desc: "Chroma bge-small · 12 queries", status: "queued" as const, time: "—" },
  { id: "critic", label: "Critic / Verifier", icon: ShieldCheck, desc: "4 checks · bounded correction", status: "queued" as const, time: "—" },
]

export function AgentTrace({ running }: { running: boolean }) {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle><Search className="w-3.5 h-3.5" /> Agent Trace</CardTitle>
        <div className="flex gap-2">
          <Badge variant="sage" className="gap-1"><span className="w-1.5 h-1.5 bg-sage rounded-full animate-pulseDot" /> LangGraph stateful</Badge>
          <Badge variant="default">tokens 2.4k</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="relative">
          <div className="absolute left-[15px] top-2 bottom-2 w-px bg-border" />
          <div className="space-y-3">
            {steps.map((s, i) => (
              <motion.div
                key={s.id}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.08, type: "spring", stiffness: 100, damping: 20 }}
                className={`relative flex gap-3 rounded-2xl border p-3 ${s.status === "active" ? "bg-sage/10 border-sage/20 shadow-glow" : s.status === "done" ? "bg-void border-border" : "bg-transparent border-border/50"}`}
                style={{ ["--i" as string]: i } as never}
              >
                <div className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${s.status === "done" ? "bg-sage text-void" : s.status === "active" ? "bg-sage text-void animate-pulse" : "bg-elevated text-muted border border-border"}`}>
                  {s.status === "done" ? <Check className="w-4 h-4" /> : s.status === "active" ? <Loader2 className="w-4 h-4 animate-spin" /> : <s.icon className="w-4 h-4" />}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold tracking-tight">{s.label}</span>
                    <Badge variant={s.status === "done" ? "sage" : s.status === "active" ? "live" : "default"} className="text-[9px]">{s.status}</Badge>
                    <span className="ml-auto text-[11px] font-mono text-muted flex items-center gap-1"><Clock className="w-3 h-3" />{s.time}</span>
                  </div>
                  <div className="text-xs font-mono text-muted truncate">{s.desc}</div>
                  {s.status === "active" && running && (
                    <div className="mt-2 h-1 rounded-full bg-void overflow-hidden">
                      <motion.div className="h-full bg-sage w-1/3" animate={{ x: ["-100%", "300%"] }} transition={{ duration: 1.2, repeat: Infinity, ease: "linear" }} />
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        <div className="mt-4 rounded-xl bg-void border border-border p-3 font-mono text-xs leading-relaxed">
          <div className="text-muted uppercase tracking-[0.12em] text-[10px] mb-1">Latest · planner output</div>
          <pre className="text-[11px] whitespace-pre-wrap text-ink/90">{`{ "comparison": { "group_a": "PRRX1_KD", "group_b": "Control" },\n  "design": "~ condition", "steps": ["validate","deseq2","enrich","evidence","verify"] }`}</pre>
        </div>
      </CardContent>
    </Card>
  )
}

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

const genes = [
  { sym: "PRRX1", l2fc: -3.42, padj: 2.1e-12, dir: "down" },
  { sym: "TWIST1", l2fc: 2.81, padj: 4.3e-9, dir: "up" },
  { sym: "COL1A1", l2fc: 1.92, padj: 1.1e-7, dir: "up" },
  { sym: "ZEB1", l2fc: 1.64, padj: 8.4e-6, dir: "up" },
  { sym: "CDH1", l2fc: -1.28, padj: 3.2e-5, dir: "down" },
  { sym: "VIM", l2fc: 1.41, padj: 5.6e-6, dir: "up" },
  { sym: "FN1", l2fc: 2.04, padj: 9.1e-8, dir: "up" },
  { sym: "SNAI2", l2fc: 1.33, padj: 2.7e-4, dir: "up" },
]

export function LiveGenes({ running }: { running: boolean }) {
  const [tick, setTick] = useState(0)
  useEffect(() => {
    if (!running) return
    const id = setInterval(() => setTick(t => t + 1), 900)
    return () => clearInterval(id)
  }, [running])

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <CardTitle className="gap-2"><span className="w-2 h-2 rounded-full bg-sage animate-pulseDot" /> Live Differential · GSE202768</CardTitle>
        <Badge variant="sage">1,247 sig @ padj&lt;0.05</Badge>
      </CardHeader>
      <CardContent>
        {/* Expression strip */}
        <div className="grid grid-cols-12 gap-1 mb-4">
          {Array.from({ length: 48 }).map((_, i) => (
            <motion.div
              key={i}
              animate={running ? { opacity: [0.5, 1, 0.5] } : {}}
              transition={{ duration: 1.5 + (i % 5) * 0.3, repeat: Infinity, delay: i * 0.03 }}
              className="h-6 rounded-lg border border-border"
              style={{ background: i % 9 === 0 ? "#14BE8A" : i % 7 === 0 ? "#E85D5B" : `rgba(26,38,34,${0.6 + Math.random() * 0.4})` }}
            />
          ))}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2">
          {genes.map((g, i) => {
            const jitter = running ? (Math.sin(tick * 0.7 + i) * 0.06) : 0
            const l2 = (g.l2fc + jitter).toFixed(2)
            return (
              <motion.div
                key={g.sym}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className="rounded-2xl bg-void border border-border p-3 flex items-center justify-between"
              >
                <div>
                  <div className="text-sm font-mono font-bold tracking-tight">{g.sym}</div>
                  <div className="text-[11px] font-mono text-muted">padj {g.padj.toExponential(1)} · tick {tick}</div>
                </div>
                <div className="text-right">
                  <div className={`text-sm font-mono font-semibold tabular-nums ${parseFloat(l2) > 0 ? "text-sage" : "text-coral"}`}>{parseFloat(l2) > 0 ? "+" : ""}{l2}</div>
                  <Badge variant={g.dir === "up" ? "sage" : "coral"} className="text-[9px] h-5">{g.dir === "up" ? "UP" : "DOWN"}</Badge>
                </div>
              </motion.div>
            )
          })}
        </div>

        <div className="mt-4 flex items-center gap-2 text-[11px] font-mono text-muted">
          <span>Volcano preview</span>
          <span className="ml-auto flex items-center gap-1"><span className="w-2 h-2 rounded bg-sage" /> log2FC</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-coral" /> padj</span>
        </div>
        <div className="h-[86px] rounded-xl bg-void border border-border relative overflow-hidden flex items-end justify-center gap-[2px] p-2">
          {Array.from({ length: 64 }).map((_, i) => (
            <motion.div
              key={i}
              className="w-[5px] rounded-full"
              style={{ background: i % 10 === 0 ? "#E85D5B" : "#14BE8A", height: `${12 + Math.abs(Math.sin(i * 0.5 + tick * 0.1)) * 48}px`, opacity: 0.7 + Math.random() * 0.3 }}
              animate={running ? { height: `${10 + Math.random() * 54}px` } : {}}
              transition={{ duration: 0.9, delay: i * 0.01 }}
            />
          ))}
          <div className="absolute top-2 left-3 text-[10px] font-mono text-muted">−log10 padj</div>
        </div>
      </CardContent>
    </Card>
  )
}

import { motion } from "framer-motion"
import { ArrowUpRight, Dna, Microscope, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

export function Hero({ onStart }: { onStart: () => void }) {
  return (
    <div className="max-w-[1440px] mx-auto px-6 lg:px-8 pt-10 lg:pt-14 pb-6">
      <div className="grid lg:grid-cols-[1.15fr_0.85fr] gap-8 lg:gap-6 items-start">
        {/* Left - Asymmetric headline with inline micro images */}
        <div className="space-y-6">
          <div className="flex items-center gap-2">
            <Badge variant="sage" className="gap-1.5"><Sparkles className="w-3 h-3" /> Resource-efficient · Evidence-grounded</Badge>
            <span className="text-[11px] font-mono text-muted hidden sm:inline">LOCAL / OPEN</span>
            <span className="hidden sm:inline-flex w-1 h-1 rounded-full bg-muted/30" />
            <span className="hidden sm:inline text-[11px] font-mono text-muted">PQ: padj &lt; 0.05</span>
          </div>

          <h1 className="text-[36px] sm:text-[42px] lg:text-[56px] font-extrabold leading-[0.9] tracking-[-0.04em] text-balance">
            <span className="text-ink">A small model</span>{" "}
            <span className="inline-flex items-center gap-2 align-middle">
              <span className="inline-flex w-[52px] h-[32px] lg:w-[64px] lg:h-[36px] rounded-full overflow-hidden border border-border shadow-sm -rotate-1">
                <img src="https://picsum.photos/seed/lab01/120/80" alt="" className="w-full h-full object-cover" />
              </span>
            </span>{" "}
            <span className="text-sage">that knows</span>
            <br />
            <span className="text-ink">when to calculate</span>{" "}
            <span className="inline-flex items-center gap-1.5 align-middle">
              <span className="inline-flex w-[42px] h-[32px] lg:w-[52px] lg:h-[36px] rounded-xl overflow-hidden border border-border rotate-1">
                <img src="https://picsum.photos/seed/seq02/120/80" alt="" className="w-full h-full object-cover opacity-90" />
              </span>
              <Dna className="w-5 h-5 lg:w-6 lg:h-6 text-sage animate-float" />
            </span>
          </h1>

          <p className="text-[15px] leading-[1.6] text-muted max-w-[52ch]">
            Five specialized agents on a quantized 4B model. Deterministic DESeq2 + clusterProfiler for numbers, local Chroma + <em className="text-ink not-italic border-b border-sage/30">bge-small</em> for evidence, explicit Critic for every claim. Runs on your 8GB rig — not a cloud demo.
          </p>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <Button size="lg" onClick={onStart} className="group gap-2">
              Run development <span className="opacity-60 font-mono text-xs">GSE202768</span> <ArrowUpRight className="w-4 h-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
            </Button>
            <span className="text-xs font-mono text-muted flex items-center gap-2">
              <Microscope className="w-3.5 h-3.5" /> PRRX1 KD · 16 samples · TNBC
            </span>
          </div>

          <div className="flex items-center gap-3 pt-4 border-t border-border mt-6">
            <div className="flex -space-x-2">
              {["GSE202768","GSE95304","GSE113650","GSE336903"].map(s => (
                <span key={s} className="w-7 h-7 rounded-full bg-elevated border-2 border-void flex items-center justify-center text-[9px] font-mono font-bold text-muted">{s.slice(3,6)}</span>
              ))}
            </div>
            <span className="text-xs font-mono text-muted">4 datasets wired · 1 held-out frozen</span>
            <span className="ml-auto hidden sm:flex items-center gap-1.5 text-[11px] font-mono text-sage"><span className="w-1.5 h-1.5 bg-sage rounded-full animate-pulseDot" /> critic armed</span>
          </div>
        </div>

        {/* Right - Live helix / sequencer viz */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.25, 0.1, 0.25, 1] }}
          className="relative rounded-[28px] bg-surface border border-[rgba(45,90,75,0.16)] shadow-lab overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-sage/[0.06] via-transparent to-transparent pointer-events-none" />
          <div className="p-5 sm:p-6">
            <div className="flex items-center justify-between mb-4">
              <span className="text-[11px] font-mono uppercase tracking-[0.14em] text-muted">Live Sequencer</span>
              <span className="flex items-center gap-2 text-[11px] font-mono text-sage"><span className="w-2 h-2 rounded-full bg-sage animate-pulseDot shadow-[0_0_8px_rgba(20,190,138,0.5)]" /> STREAMING</span>
            </div>

            {/* Helix SVG */}
            <div className="relative h-[132px] rounded-2xl bg-void border border-border overflow-hidden flex items-center justify-center">
              <svg viewBox="0 0 400 120" className="w-full h-full">
                {Array.from({ length: 20 }).map((_, i) => {
                  const x = i * 20 + 6
                  const y1 = 60 + Math.sin(i * 0.6) * 28
                  const y2 = 60 + Math.sin(i * 0.6 + Math.PI) * 28
                  return (
                    <g key={i}>
                      <line x1={x} y1={y1} x2={x} y2={y2} stroke="rgba(20,190,138,0.22)" strokeWidth="1" />
                      <circle cx={x} cy={y1} r="3.5" fill="#14BE8A" opacity={0.9 - i * 0.02} />
                      <circle cx={x} cy={y2} r="3.5" fill="#8A9A93" opacity={0.7 - i * 0.02} />
                    </g>
                  )
                })}
              </svg>
              <div className="absolute bottom-2 left-3 right-3 flex justify-between text-[10px] font-mono text-muted">
                <span>5&apos; — ATG CAG TTA …</span><span className="text-sage">Q30 94.2% • 28.4M reads</span>
              </div>
            </div>

            {/* Expression barcode */}
            <div className="mt-4 grid grid-cols-12 gap-1">
              {Array.from({ length: 36 }).map((_, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0.3 }}
                  animate={{ opacity: [0.4, 1, 0.4] }}
                  transition={{ duration: 2 + Math.random(), repeat: Infinity, delay: i * 0.04 }}
                  className="h-[22px] rounded-[6px]"
                  style={{
                    background: i % 7 === 0 ? "#14BE8A" : i % 5 === 0 ? "#E85D5B" : i % 3 === 0 ? "#1A2622" : "#17201D",
                    opacity: 0.6 + Math.random() * 0.4,
                  }}
                />
              ))}
            </div>
            <div className="mt-3 flex items-center justify-between text-[11px] font-mono">
              <span className="text-muted">log2FC spectrum</span>
              <span className="flex items-center gap-2">
                <span className="w-3 h-3 rounded bg-coral" /> down
                <span className="w-3 h-3 rounded bg-sage ml-1" /> up
              </span>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

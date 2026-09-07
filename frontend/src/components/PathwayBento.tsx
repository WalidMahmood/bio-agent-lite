import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Beaker, Dna, GitBranch, ShieldCheck } from "lucide-react"

const pathways = [
  { name: "Extracellular matrix organization", db: "Reactome R-HSA-1474244", fdr: "2.4e-06", genes: 34, hit: true },
  { name: "Epithelial mesenchymal transition", db: "GO:0001837", fdr: "8.1e-05", genes: 22, hit: true },
  { name: "Collagen formation", db: "R-HSA-1474290", fdr: "1.2e-04", genes: 18, hit: true },
  { name: "Focal adhesion", db: "KEGG hsa04510", fdr: "3.7e-04", genes: 27, hit: false },
]

export function PathwayBento() {
  return (
    <div className="grid lg:grid-cols-[1.6fr_1fr_1fr] gap-4">
      <Card className="lg:col-span-1">
        <CardHeader>
          <CardTitle><Beaker className="w-3.5 h-3.5 text-sage" /> Pathway Enrichment</CardTitle>
          <p className="text-xs font-mono text-muted">clusterProfiler · org.Hs.eg.db · FDR &lt; 0.05</p>
        </CardHeader>
        <CardContent className="space-y-2">
          {pathways.map(p => (
            <div key={p.name} className="flex items-center gap-3 rounded-2xl bg-void border border-border p-3">
              <div className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${p.hit ? "bg-sage text-void" : "bg-elevated text-muted border border-border"}`}>
                <Dna className="w-4 h-4" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="text-sm font-medium leading-tight truncate">{p.name}</div>
                <div className="text-[11px] font-mono text-muted truncate">{p.db} · {p.genes} genes</div>
              </div>
              <div className="text-right shrink-0">
                <div className="text-xs font-mono font-semibold">{p.fdr}</div>
                <Badge variant={p.hit ? "sage" : "default"} className="text-[9px] h-5">{p.hit ? "HIT" : "NS"}</Badge>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle><GitBranch className="w-3.5 h-3.5" /> Evidence</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="rounded-2xl bg-void border border-border p-3">
            <div className="text-xs font-semibold">COL1A1 · PubMed 34123412</div>
            <div className="text-xs text-muted leading-relaxed mt-1">ECM remodeling correlates with PRRX1-driven EMT in TNBC — <em className="text-sage not-italic">supported</em></div>
            <Badge variant="sage" className="mt-2 text-[9px]">Supported · bge-small 0.82</Badge>
          </div>
          <div className="rounded-2xl bg-void border border-border p-3">
            <div className="text-xs font-semibold">TWIST1 · Reactome 1474244</div>
            <div className="text-xs text-muted leading-relaxed mt-1">Pathway overlap present in computed enrichment.</div>
            <Badge variant="default" className="text-[9px]">Partial</Badge>
          </div>
        </CardContent>
      </Card>

      <Card className="border-sage/20">
        <CardHeader>
          <CardTitle className="text-sage"><ShieldCheck className="w-3.5 h-3.5" /> Critic Verdict</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="rounded-2xl bg-sage/10 border border-sage/20 p-3">
            <div className="text-sm font-bold text-sage flex items-center gap-2"><span className="w-2 h-2 bg-sage rounded-full animate-pulseDot" /> PASS</div>
            <div className="text-xs font-mono text-muted mt-1">All sig genes verified in DE table. No padj/p confusion. Direction correct.</div>
          </div>
          <div className="rounded-2xl bg-void border border-border p-3">
            <div className="text-xs font-mono text-muted uppercase tracking-[0.08em]">Warnings 1</div>
            <div className="text-xs text-muted mt-1">GENE_X claim removed — padj 0.31 despite log2FC 1.9 (stat trap).</div>
          </div>
          <div className="flex gap-2">
            <Badge variant="sage">Errors 0</Badge><Badge variant="amber">Warnings 1</Badge><Badge variant="default">Corrections 1</Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

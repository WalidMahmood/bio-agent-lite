import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-[10px] font-mono font-medium uppercase tracking-[0.1em] transition-colors",
  {
    variants: {
      variant: {
        default: "border-[rgba(45,90,75,0.18)] bg-wash text-muted",
        sage: "border-[rgba(20,190,138,0.22)] bg-[rgba(20,190,138,0.08)] text-sage",
        amber: "border-[rgba(232,164,42,0.25)] bg-[rgba(232,164,42,0.08)] text-amber",
        coral: "border-[rgba(232,93,91,0.22)] bg-[rgba(232,93,91,0.08)] text-coral",
        live: "border-sage/30 bg-sage/10 text-sage animate-pulse",
      },
    },
    defaultVariants: { variant: "default" },
  }
)

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />
}
export { Badge, badgeVariants }

import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-[12px] text-sm font-semibold tracking-tight transition-all focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-sage disabled:pointer-events-none disabled:opacity-40 active:scale-[0.97]",
  {
    variants: {
      variant: {
        default: "bg-sage text-void hover:bg-[#1AC99A] shadow-glow",
        ghost: "bg-transparent border border-[rgba(45,90,75,0.22)] text-ink hover:bg-elevated hover:border-[rgba(45,90,75,0.3)]",
        subtle: "bg-elevated text-ink border border-border hover:bg-wash",
        danger: "bg-coral text-white hover:bg-[#E85D5B]/90",
      },
      size: {
        default: "h-11 px-6 py-2",
        sm: "h-8 px-4 text-xs",
        lg: "h-[48px] px-8 text-[15px]",
        icon: "h-9 w-9",
      },
    },
    defaultVariants: { variant: "default", size: "default" },
  }
)

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(({ className, variant, size, ...props }, ref) => (
  <button ref={ref} className={cn(buttonVariants({ variant, size, className }))} {...props} />
))
Button.displayName = "Button"
export { Button, buttonVariants }

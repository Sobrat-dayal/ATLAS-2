import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../utils/cn"

const badgeVariants = cva(
  "inline-flex items-center rounded-sm border px-2 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2",
  {
    variants: {
      variant: {
        default: "border-transparent bg-atlas-surface-hover text-atlas-text-primary",
        primary: "border-transparent bg-[#1E2B4D] text-[#60A5FA]", // Reusing the primary blue text tone
        positive: "border-transparent bg-green-900/40 text-atlas-positive",
        negative: "border-transparent bg-red-900/40 text-atlas-negative",
        warning: "border-transparent bg-yellow-900/40 text-atlas-warning",
        outline: "text-atlas-text-secondary border-atlas-border-default",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }

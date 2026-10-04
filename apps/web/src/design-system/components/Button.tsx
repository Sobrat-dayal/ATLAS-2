import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../utils/cn"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-sm text-sm font-medium ring-offset-atlas-bg-0 transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-accent disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        primary: "bg-atlas-accent text-white hover:bg-atlas-accent-hover",
        secondary: "bg-atlas-surface-2 border border-atlas-border-default text-atlas-text-primary hover:bg-atlas-surface-hover hover:border-atlas-border-strong",
        ghost: "hover:bg-atlas-surface-hover text-atlas-text-primary",
        danger: "bg-atlas-negative text-white hover:bg-red-600",
        success: "bg-atlas-positive text-atlas-bg-0 hover:bg-green-400",
      },
      size: {
        xs: "h-6 px-2 text-xs",
        sm: "h-8 px-3",
        md: "h-9 px-4",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "sm",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }

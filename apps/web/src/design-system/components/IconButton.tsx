import * as React from "react"
import { cn } from "../utils/cn"
import { Button, ButtonProps } from "./Button"

export interface IconButtonProps extends Omit<ButtonProps, "size"> {
  size?: "xs" | "sm" | "md";
}

const IconButton = React.forwardRef<HTMLButtonElement, IconButtonProps>(
  ({ className, size = "sm", ...props }, ref) => {
    const sizeClasses = {
      xs: "h-6 w-6 p-0",
      sm: "h-8 w-8 p-0",
      md: "h-9 w-9 p-0",
    }
    
    return (
      <Button
        ref={ref}
        size={size}
        className={cn(sizeClasses[size], className)}
        {...props}
      />
    )
  }
)
IconButton.displayName = "IconButton"

export { IconButton }

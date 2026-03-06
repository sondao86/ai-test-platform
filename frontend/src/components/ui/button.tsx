import * as React from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger" | "ghost" | "outline";
  size?: "sm" | "md" | "lg";
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", ...props }, ref) => {
    const baseStyles =
      "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-gray-400 disabled:pointer-events-none disabled:opacity-50";

    const variants = {
      primary: "bg-gray-900 text-white hover:bg-gray-900/90 shadow",
      secondary: "bg-gray-100 text-gray-900 hover:bg-gray-200",
      danger: "bg-red-500 text-white hover:bg-red-600 shadow-sm",
      ghost: "hover:bg-gray-100 hover:text-gray-900 text-gray-600",
      outline: "border border-gray-200 bg-white hover:bg-gray-100 hover:text-gray-900",
    };

    const sizes = {
      sm: "h-8 px-3 text-xs",
      md: "h-9 px-4 py-2",
      lg: "h-10 px-8",
    };

    return (
      <button
        ref={ref}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button };

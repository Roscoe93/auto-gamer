import { ButtonHTMLAttributes } from "react";
import "./Button.css";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "primary" | "pause" | "stop";
}

export function Button({ variant = "default", className = "", children, ...props }: ButtonProps) {
  const variantClass = variant !== "default" ? `btn-${variant}` : "";
  return (
    <button className={`btn ${variantClass} ${className}`.trim()} {...props}>
      {children}
    </button>
  );
}
import React from "react";
import "./Input.css";

export interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "onChange"> {
  onChange?: (value: string) => void;
}

export const Input: React.FC<InputProps> = ({ className, onChange, ...props }) => {
  return (
    <input
      className={`input ${className || ""}`}
      onChange={(e) => onChange?.(e.target.value)}
      {...props}
    />
  );
};

import { ReactNode } from "react";
import "./Card.css";

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <article className={`card ${className}`}>{children}</article>;
}
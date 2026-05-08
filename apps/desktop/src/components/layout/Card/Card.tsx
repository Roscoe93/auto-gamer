import { ReactNode, CSSProperties } from "react";
import "./Card.css";

export function Card({ children, className = "", style }: { children: ReactNode; className?: string; style?: CSSProperties }) {
  return <article className={`card ${className}`} style={style}>{children}</article>;
}
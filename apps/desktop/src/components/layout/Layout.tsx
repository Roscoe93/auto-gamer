import { ReactNode } from "react";

export function Page({ children }: { children: ReactNode }) {
  return <main className="page">{children}</main>;
}

export function Panel({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <section className={`panel ${className}`}>{children}</section>;
}

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <article className={`card ${className}`}>{children}</article>;
}

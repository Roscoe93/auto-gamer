import { ReactNode, memo } from "react";
import "./Panel.css";

export const Panel = memo(function Panel({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <section className={`panel ${className}`}>{children}</section>;
});
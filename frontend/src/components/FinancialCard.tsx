import React from "react";

interface FinancialCardProps {
  title: string;
  value: string;
  subtitle?: string;
  trend?: "up" | "down" | "neutral";
  highlight?: boolean;
}

export const FinancialCard: React.FC<FinancialCardProps> = ({
  title,
  value,
  subtitle,
  trend,
  highlight,
}) => {
  return (
    <div
      className={`p-5 rounded-xl border flex flex-col justify-between transition-all ${
        highlight
          ? "bg-[#0A0A0A] border-[#BEF264]/50 shadow-[0_0_15px_rgba(190,242,100,0.1)]"
          : "bg-[#0A0A0A] border-[#1A1A1A]"
      }`}
    >
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-sm font-medium text-neutral-400">{title}</h3>
        {trend === "up" && (
          <svg
            className="w-4 h-4 text-[#BEF264]"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
            />
          </svg>
        )}
        {trend === "down" && (
          <svg
            className="w-4 h-4 text-rose-500"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"
            />
          </svg>
        )}
      </div>
      <div>
        <div
          className={`text-3xl font-bold tracking-tight ${
            highlight ? "text-[#BEF264]" : "text-neutral-100"
          }`}
        >
          {value}
        </div>
        {subtitle && (
          <div className="text-xs text-neutral-500 mt-2 font-medium tracking-wide">
            {subtitle}
          </div>
        )}
      </div>
    </div>
  );
};

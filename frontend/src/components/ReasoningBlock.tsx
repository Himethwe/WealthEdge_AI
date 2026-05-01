import React, { useState } from "react";

interface ReasoningProps {
  steps: string[];
}

export const ReasoningBlock: React.FC<ReasoningProps> = ({ steps }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!steps || steps.length === 0) return null;

  return (
    <div className="mb-4 w-full">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 text-xs font-medium text-neutral-400 hover:text-[#BEF264] transition-colors py-1 px-2 rounded-md hover:bg-[#BEF264]/10"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className={`h-3 w-3 transition-transform ${
            isOpen ? "rotate-90" : ""
          }`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5l7 7-7 7"
          />
        </svg>
        Agent Chain of Thought ({steps.length} steps)
      </button>

      {isOpen && (
        <div className="mt-2 ml-2 pl-3 border-l-2 border-[#1A1A1A] space-y-2">
          {steps.map((step, index) => (
            <div
              key={index}
              className="text-[13px] text-neutral-500 font-mono flex items-start gap-2"
            >
              <span className="text-[#BEF264] opacity-50">[{index + 1}]</span>
              {step}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

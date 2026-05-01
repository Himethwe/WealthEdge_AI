import React from "react";

export const TypingLoader: React.FC = () => {
  return (
    <div className="flex w-full mb-6 justify-start">
      <div className="shrink-0 mr-3 mt-1">
        <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center">
          <div className="w-4 h-4 border-2 border-slate-500 border-t-[#BEF264] rounded-full animate-spin"></div>
        </div>
      </div>
      <div className="bg-slate-800 border border-slate-700/50 text-[#BEF264] rounded-2xl rounded-tl-sm px-5 py-3 text-sm flex items-center gap-3 shadow-sm">
        <span className="font-medium tracking-wide animate-pulse">
          Running market analysis...
        </span>
      </div>
    </div>
  );
};

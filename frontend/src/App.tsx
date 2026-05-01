import { useState, useRef, useEffect } from "react";
import { ChatMessage } from "./components/ChatMessage";
import { TypingLoader } from "./components/TypingLoader";
import { FinancialCard } from "./components/FinancialCard";

interface Message {
  role: "user" | "assistant";
  content: string;
  reasoning?: string[];
}

function App() {
  // Mobile Tab State
  const [activeTab, setActiveTab] = useState<"chat" | "data">("chat");

  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Ayubowan! I am **WealthEdge**, your AI Financial Advisor. \n\nI have live access to CSE stock fundamentals, CBSL T-Bills, and macroeconomic data. How can I assist you with your investments today?",
      reasoning: [
        "Initialized WealthEdge Core",
        "Connected to CBSL API",
        "Loaded CSE Market Open Data",
      ],
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => scrollToBottom(), [messages, isLoading]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage }),
      });

      const data = await response.json();

      // Map backend reasoning arrays
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.response,
          reasoning: data.reasoning || [
            "Parsed query constraints",
            "Executed market data retrieval",
            "Synthesized final comparison",
          ],
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "⚠️ Connection to Python backend failed.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-screen bg-black flex flex-col font-sans overflow-hidden text-neutral-200">
      {/* GLOBAL HEADER*/}
      <header className="w-full px-6 py-4 border-b border-[#1A1A1A] bg-[#0A0A0A] z-20 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-[#BEF264]/10 border border-[#BEF264]/30 flex items-center justify-center">
            <span className="text-[#BEF264] font-bold text-lg">W</span>
          </div>
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">
              Wealth<span className="text-[#BEF264]">Edge</span>{" "}
              <span className="text-neutral-500 font-medium text-sm ml-1">
                AI
              </span>
            </h1>
          </div>
        </div>

        {/* Mobile Tab Toggles*/}
        <div className="flex lg:hidden bg-black rounded-lg p-1 border border-[#1A1A1A]">
          <button
            onClick={() => setActiveTab("chat")}
            className={`px-4 py-1.5 text-xs font-medium rounded-md transition-all ${
              activeTab === "chat"
                ? "bg-[#262626] text-white shadow-sm"
                : "text-neutral-500"
            }`}
          >
            Chat
          </button>
          <button
            onClick={() => setActiveTab("data")}
            className={`px-4 py-1.5 text-xs font-medium rounded-md transition-all ${
              activeTab === "data"
                ? "bg-[#262626] text-white shadow-sm"
                : "text-neutral-500"
            }`}
          >
            Market Data
          </button>
        </div>

        <div className="hidden lg:flex items-center gap-2 text-xs font-mono text-neutral-400">
          <span className="w-2 h-2 rounded-full bg-[#BEF264] shadow-[0_0_10px_rgba(190,242,100,0.6)] animate-pulse"></span>
          SYS.ONLINE
        </div>
      </header>

      {/* MAIN CONTENT SPLIT */}
      <main className="flex-1 flex overflow-hidden relative">
        {/* LEFT PANE: Chat Engine (Hidden on mobile if 'data' tab is active) */}
        <div
          className={`w-full lg:w-[60%] flex flex-col h-full relative transition-all ${
            activeTab === "data" ? "hidden lg:flex" : "flex"
          }`}
        >
          <div className="flex-1 overflow-y-auto p-5 sm:p-8 pb-36 scrollbar-hide">
            <div className="max-w-3xl mx-auto">
              {messages.map((msg, index) => (
                <ChatMessage
                  key={index}
                  role={msg.role}
                  content={msg.content}
                  reasoning={msg.reasoning}
                />
              ))}
              {isLoading && <TypingLoader />}
              <div ref={messagesEndRef} />
            </div>
          </div>

          <div className="absolute bottom-0 w-full p-4 sm:p-6 bg-linear-to-t from-black via-black to-transparent">
            <div className="max-w-3xl mx-auto">
              <form
                onSubmit={handleSend}
                className="relative flex items-center"
              >
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Analyze yields..."
                  disabled={isLoading}
                  className="w-full bg-[#0A0A0A] border border-[#1A1A1A] text-white rounded-xl pl-5 pr-14 py-4 focus:outline-none focus:border-[#BEF264] focus:ring-1 focus:ring-[#BEF264] transition-all placeholder:text-neutral-600 text-[15px]"
                />
                <button
                  type="submit"
                  disabled={isLoading || !input.trim()}
                  className="absolute right-3 p-2 bg-[#BEF264] hover:bg-[#d9f99d] text-black rounded-lg transition-colors disabled:opacity-50"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                    className="w-5 h-5"
                  >
                    <path d="M3.478 2.404a.75.75 0 00-.926.941l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.404z" />
                  </svg>
                </button>
              </form>
            </div>
          </div>
        </div>

        {/* RIGHT PANE: Dashboard (Hidden on mobile if 'chat' tab is active) */}
        <div
          className={`w-full lg:w-[40%] bg-[#0A0A0A] border-l border-[#1A1A1A] flex-col h-full overflow-y-auto p-6 lg:p-8 ${
            activeTab === "chat" ? "hidden lg:flex" : "flex"
          }`}
        >
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-lg font-semibold text-white tracking-tight">
              Market Context
            </h2>
            <span className="text-[10px] uppercase tracking-widest text-neutral-500 font-mono">
              Live Data
            </span>
          </div>

          <div className="space-y-6">
            <div>
              <h3 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-3">
                Macro Indicators
              </h3>
              <div className="grid grid-cols-2 gap-3">
                <FinancialCard
                  title="CCPI Inflation"
                  value="2.2%"
                  subtitle="Latest CBSL Data"
                  trend="down"
                />
                <FinancialCard
                  title="Withholding Tax"
                  value="5.0%"
                  subtitle="Default WHT Rate"
                />
              </div>
            </div>

            <div>
              <h3 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-3">
                Real Net Yields
              </h3>
              <div className="grid grid-cols-1 gap-3">
                <FinancialCard
                  title="Commercial Bank (COMB)"
                  value="7.49%"
                  subtitle="Dividend Yield (Low P/E Risk)"
                  highlight={true}
                  trend="up"
                />
                <div className="grid grid-cols-2 gap-3">
                  <FinancialCard
                    title="364-Day T-Bill"
                    value="5.79%"
                    subtitle="Inflation Adjusted"
                  />
                  <FinancialCard
                    title="Sampath Bank"
                    value="6.65%"
                    subtitle="Dividend Yield"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;

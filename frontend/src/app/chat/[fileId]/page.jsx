"use client";
import { useEffect, useRef, useState } from "react";
import { User, Bot, Loader2, Send, Lightbulb } from "lucide-react";
import { useParams } from "next/navigation";
import { useAuth } from "@/provider/AuthProvider";
import { useForm } from "react-hook-form";

export default function ChatInterface() {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm();

  const [fileData, setFileData] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [suggestedQuestions, setSuggestedQuestions] = useState([
    "What are my top-selling products?",
    "Any revenue drop in Q2?",
    "Highlight unusual trends.",
  ]);
  const messagesEndRef = useRef(null);
  const { fileId } = useParams();
  const fileName = fileData ? fileData.filename : "Loading...";
  const { user, session } = useAuth();

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="text-center text-gray-400">
          <h1 className="text-3xl font-bold mb-4">
            Please log in to access your dashboard
          </h1>
          <p className="mb-6">
            You need to be authenticated to view this page.
          </p>
          <Link
            href="/login"
            className="inline-flex items-center justify-center gap-2 px-8 py-4 text-lg font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 rounded-full shadow-lg transform transition-all duration-300 ease-in-out hover:scale-105 hover:shadow-xl focus:outline-none focus:ring-4 focus:ring-blue-300 focus:ring-opacity-75"
          >
            Go to Login
          </Link>
        </div>
      </div>
    );
  }

  const fetchFileData = async () => {
    if (!fileId || !session) {
      console.log("File ID or session is missing.");
      return;
    }
    try {
      const response = await fetch(`/api/files/${fileId}`, {
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch file data");
      }

      const data = await response.json();
      setFileData(data);
      console.log("File data:", data);
    } catch (error) {
      console.log("Error fetching file data:", error);
      alert("Failed to load file data. Please try again later.");
    }
  };

  const getChatHistory = async () => {
    if (!fileId || !session) {
      console.log("File ID or session is missing.");
      return;
    }

    try {
      const response = await fetch(`/api/history/${fileId}`, {
        method: "GET",
        headers: { Authorization: `Bearer ${session.access_token}` },
      });

      if (!response.ok) {
        console.log("Error fetching chat history:", response.statusText);
        throw new Error("Failed to fetch conversation history");
      }

      const data = await response.json();
      console.log("Chat history:", data);
      // Format history to match messages state
      const formattedHistory = (data.history || [])
        .map((msg, index) => [
          {
            id: `${msg.created_at}-${index}-user`,
            type: "user",
            content: msg.question,
            timestamp: new Date(msg.created_at),
          },
          {
            id: `${msg.created_at}-${index}-ai`,
            type: "ai",
            content: msg.answer,
            timestamp: new Date(msg.created_at),
          },
        ])
        .flat();
      setMessages((prev) => {
        // Only include welcome message if no history
        const welcomeMessage = prev.find((msg) => msg.id === "welcome") || {
          id: "welcome",
          type: "ai",
          content: `👋 Hi! I'm your **AI analyst**. I've analyzed "${fileName}" and I'm ready to answer any questions about your sales data. Try asking me about trends, performance, or specific insights!`,
          timestamp: new Date(),
        };
        return formattedHistory.length ? formattedHistory : [welcomeMessage];
      });
    } catch (error) {
      console.log("Error fetching chat history:", error);
      alert("Failed to load chat history. Please try again later.");
    }
  };

  useEffect(() => {
    fetchFileData();
    getChatHistory();
  }, [fileId, session]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendChatMessage = async (formDetails) => {
    const { question } = formDetails;

    if (!question?.trim()) {
      return;
    }

    if (!fileId || !session) {
      alert("File ID or session is missing.");
      return;
    }

    // Add user message to chat
    const userMessage = {
      id: Date.now().toString(),
      type: "user",
      content: question,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    reset(); // Clear the form

    try {
      const response = await fetch(`/api/chat`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session.access_token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ file_id: fileId, question }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          `Chat failed: ${errorData.detail || response.statusText}`
        );
      }

      const result = await response.json();
      console.log("Chat response:", result);

      // Add AI response to chat
      const aiMessage = {
        id: Date.now().toString() + "-ai",
        type: "ai",
        content:
          result.answer ||
          "I received your question but couldn't generate a response.",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.log("Error sending message:", error);

      // Add error message to chat
      const errorMessage = {
        id: Date.now().toString() + "-error",
        type: "ai",
        content:
          "❌ Sorry, I encountered an error processing your question. Please try again later.",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestedQuestion = (question) => {
    // Simulate form submission with suggested question
    sendChatMessage({ question });
  };

  return (
    <section className="px-8 py-4 bg-gray-900 min-h-screen">
      <div className="min-h-screen relative flex flex-col">
        {/* Messages Container */}
        <div className="flex-1 p-6 space-y-4 scrollbar-thin scrollbar-thumb-indigo-300 scrollbar-track-indigo-50 pb-32">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.type === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`flex items-start max-w-[90%] lg:max-w-[75%] ${
                  message.type === "user" ? "flex-row-reverse" : "flex-row"
                }`}
              >
                <div
                  className={`flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center text-white text-lg font-bold shadow-md ${
                    message.type === "user"
                      ? "bg-indigo-600 ml-3"
                      : "bg-gray-700 mr-3"
                  }`}
                >
                  {message.type === "user" ? (
                    <User size={20} />
                  ) : (
                    <Bot size={20} />
                  )}
                </div>
                <div
                  className={`p-4 rounded-2xl shadow-lg break-words leading-relaxed ${
                    message.type === "user"
                      ? "bg-indigo-600 text-white rounded-br-none"
                      : "bg-white text-gray-900 rounded-bl-none border border-gray-100"
                  }`}
                >
                  {message.content}
                  <div className="text-xs text-gray-400 mt-1">
                    {message.timestamp.toLocaleString()}
                  </div>
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-800 px-4 py-2 rounded-lg flex items-center gap-3 shadow-md border border-gray-100">
                <Loader2 className="w-5 h-5 animate-spin text-indigo-500" />
                <span className="text-sm font-medium">
                  Analyzing your question...
                </span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Fixed Input Area */}
        <div className="p-6 bg-gray-900 border-t border-gray-700 shadow-lg">
          {/* Suggested Questions */}
          {suggestedQuestions.length > 0 && messages.length <= 1 && (
            <div className="pb-4">
              <div className="flex items-center gap-2 mb-3">
                <Lightbulb className="w-5 h-5 text-yellow-500" />
                <span className="text-sm font-semibold text-gray-300">
                  Suggested Questions:
                </span>
              </div>
              <div className="flex flex-wrap gap-2">
                {suggestedQuestions.slice(0, 3).map((question, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestedQuestion(question)}
                    className="text-sm bg-transparent border border-gray-300 rounded-full px-4 py-2 font-semibold text-gray-300
                             hover:bg-gray-600 hover:border-gray-400
                             transition-all duration-200 ease-in-out shadow-sm
                             disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer"
                    disabled={isLoading}
                    title={question}
                  >
                    {question.length > 45
                      ? question.substring(0, 45) + "..."
                      : question}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input Form */}
          <form onSubmit={handleSubmit(sendChatMessage)} className="flex gap-4">
            <input
              type="text"
              {...register("question", { required: "Please enter a question" })}
              placeholder="Ask about your sales data..."
              className="flex-1 border border-gray-600 bg-gray-800 rounded-full px-5 py-3 font-semibold text-gray-200 text-base
                       focus:outline-none focus:ring-3 focus:ring-indigo-400 focus:border-indigo-500
                       transition-all duration-200 ease-in-out placeholder-gray-400 shadow-sm"
              disabled={isLoading}
            />
            <button
              type="submit"
              className="bg-indigo-600 text-white px-6 py-3 rounded-full shadow-lg
                       hover:bg-indigo-700 focus:outline-none focus:ring-3 focus:ring-indigo-300 focus:ring-offset-2
                       disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2
                       transition-colors duration-200 ease-in-out transform hover:scale-105"
              disabled={isLoading}
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
              <span className="hidden sm:inline font-semibold">Send</span>
            </button>
          </form>

          {errors.question && (
            <p className="text-red-400 text-sm mt-2 ml-2">
              {errors.question.message}
            </p>
          )}
        </div>
      </div>
    </section>
  );
}

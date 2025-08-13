"use client";
import {
  Eye,
  EyeOff,
  Star,
  Trophy,
  TrendingUp,
  AlertTriangle,
  Zap,
} from "lucide-react";
import React, { useState } from "react";

// The main component that lays out the insight cards
const AIGeneratedInsigts = ({ data }) => {
  return (
    <div className="mt-10 grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
      {data.trends && (
        <AIInsightCard
          title="Trends"
          data={data.trends}
          icon={<TrendingUp className="h-6 w-6" />}
          color="green"
        />
      )}
      {data.anomalies && (
        <AIInsightCard
          title="Anomalies"
          data={data.anomalies}
          icon={<AlertTriangle className="h-6 w-6" />}
          color="yellow"
        />
      )}
      {data.predictions && (
        <AIInsightCard
          title="Predictions"
          data={data.predictions}
          icon={<Zap className="h-6 w-6" />}
          color="blue"
        />
      )}
    </div>
  );
};

export default AIGeneratedInsigts;

// The reusable card component for each insight type
function AIInsightCard({ title, data, icon, color }) {
  const colorClasses = {
    green:
      "border-green-500/20 bg-green-500/10 text-green-400 hover:shadow-green-500/20",
    blue: "border-blue-500/20 bg-blue-500/10 text-blue-400 hover:shadow-blue-500/20",
    yellow:
      "border-yellow-500/20 bg-yellow-500/10 text-yellow-400 hover:shadow-yellow-500/20",
  };

  return (
    <div
      className={`flex flex-col gap-6 rounded-2xl border border-white/20 bg-white/10 p-8 text-white shadow-2xl backdrop-blur-md transition-all duration-300 hover:scale-[1.02] ${colorClasses[color]}`}
    >
      <div className="flex items-center gap-4">
        <div
          className={`flex h-12 w-12 items-center justify-center rounded-xl ${colorClasses[color]}`}
        >
          {icon}
        </div>
        <div>
          <h3 className="text-2xl font-bold tracking-tight text-white">
            {title}
          </h3>
          <p className="text-sm text-gray-400">AI-generated insights</p>
        </div>
      </div>

      <hr className="my-2 border-gray-700" />

      <div className="space-y-4">
        {data.map((insight, index) => (
          <div
            key={index}
            className="rounded-xl bg-white/5 p-4 transition-colors hover:bg-white/10"
          >
            <p className="text-sm leading-relaxed text-gray-200">{insight}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

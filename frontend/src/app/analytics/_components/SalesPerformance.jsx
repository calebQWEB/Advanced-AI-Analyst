"use client";
import { Eye, EyeOff, Star, Trophy } from "lucide-react";
import React, { useState } from "react";

const SalesPerformance = ({ data }) => {
  const [showAll, setShowAll] = useState(false);
  const displayData = showAll ? data.all_reps : data.all_reps.slice(0, 5);

  return (
    <div className="mt-10 flex flex-col gap-6 rounded-2xl border border-white/20 bg-white/10 p-8 text-white shadow-2xl backdrop-blur-md transition-all duration-300 hover:scale-[1.02] hover:shadow-yellow-500/20">
      {/* Header Section */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-yellow-500/20 bg-yellow-500/10">
            <Trophy className="h-6 w-6 text-yellow-400" />
          </div>
          <div>
            <h3 className="text-2xl font-bold tracking-tight text-white">
              Sales Performance
            </h3>
            <p className="text-sm text-gray-400">
              Top performing sales representatives
            </p>
          </div>
        </div>
        {data.all_reps.length > 5 && (
          <button
            onClick={() => setShowAll(!showAll)}
            className="flex items-center gap-2 rounded-full border border-yellow-500/30 bg-yellow-500/10 px-4 py-2 text-sm font-medium text-yellow-400 transition-colors hover:bg-yellow-500/20"
          >
            {showAll ? (
              <>
                <EyeOff className="h-4 w-4" /> Show Less
              </>
            ) : (
              <>
                <Eye className="h-4 w-4" /> Show All
              </>
            )}
          </button>
        )}
      </div>

      <hr className="my-2 border-gray-700" />

      {/* Best Performer Highlight */}
      <div className="rounded-xl border border-yellow-500/20 bg-gradient-to-br from-yellow-500/5 to-orange-500/5 p-6 shadow-lg">
        <div className="flex items-center gap-3">
          <Star className="h-5 w-5 text-yellow-400" />
          <span className="font-medium text-yellow-400">Best Performer</span>
        </div>
        <div className="mt-4 flex items-center justify-between">
          <div>
            <h4 className="text-2xl font-bold text-white">
              {data.best_performer.name}
            </h4>
            <p className="text-gray-300">
              {data.best_performer.transactions} transactions
            </p>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold text-green-400">
              ${data.best_performer.total_sales.toLocaleString()}
            </p>
            <p className="text-gray-400 text-sm">
              Avg: ${data.best_performer.avg_transaction.toFixed(2)}
            </p>
          </div>
        </div>
      </div>

      <hr className="my-2 border-gray-700" />

      {/* All Reps List */}
      <div className="space-y-4">
        {displayData.map((rep, index) => (
          <div
            key={rep.name}
            className="flex items-center justify-between rounded-xl bg-white/5 p-4 transition-colors duration-200 hover:bg-white/10"
          >
            <div className="flex items-center gap-4">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-yellow-600 text-sm font-bold text-white shadow-md">
                {index + 1}
              </div>
              <div>
                <h4 className="font-semibold text-white">{rep.name}</h4>
                <p className="text-sm text-gray-400">
                  {rep.transactions} transactions
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="font-bold text-green-400">
                ${rep.total_sales.toLocaleString()}
              </p>
              <p className="text-sm text-gray-400">
                ${rep.avg_transaction.toFixed(2)} avg
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SalesPerformance;

"use client";
import React, { useState } from "react";
import { Users, Eye, EyeOff, Asterisk } from "lucide-react";

const Customers = ({ data, metric }) => {
  const [showAll, setShowAll] = useState(false);
  const displayData = showAll ? data : data.slice(0, 5);

  return (
    <div className="mt-10 flex flex-col gap-6 rounded-2xl border border-white/20 bg-white/10 p-8 text-white shadow-2xl backdrop-blur-md transition-all duration-300 hover:scale-[1.02] hover:shadow-green-500/20">
      {/* Header Section */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-green-500/20 bg-green-500/10">
            <Users className="h-6 w-6 text-green-400" />
          </div>
          <div>
            <h3 className="text-2xl font-bold tracking-tight text-white">
              Top Customers
            </h3>
            <p className="text-sm text-gray-400">
              Highest value customers by total spend
            </p>
          </div>
        </div>
        {data.length > 5 && (
          <button
            onClick={() => setShowAll(!showAll)}
            className="flex items-center gap-2 rounded-full border border-green-500/30 bg-green-500/10 px-4 py-2 text-sm font-medium text-green-400 transition-colors hover:bg-green-500/20"
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

      {/* Customer List */}
      <div className="space-y-4">
        {displayData.map((customer, index) => (
          <div
            key={customer.name}
            className="flex items-center justify-between rounded-xl bg-white/5 p-4 transition-colors duration-200 hover:bg-white/10"
          >
            <div className="flex items-center gap-4">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-green-600 text-sm font-bold text-white shadow-md">
                {index + 1}
              </div>
              <div>
                <h4 className="font-semibold text-white">{customer.name}</h4>
                <p className="text-sm text-gray-400">
                  {customer.transactions} transactions
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="font-bold text-green-400">
                ${customer.total_spent.toLocaleString()}
              </p>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-7 flex items-center justify-between rounded-xl bg-white/5 p-4 transition-colors duration-200 hover:bg-white/10">
        <div className="flex items-center gap-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-green-600 text-sm font-bold text-white shadow-md">
            <Asterisk />
          </div>
          <h4 className="font-semibold text-white">Average Customer Value</h4>
        </div>
        <div className="text-right">
          <p className="font-bold text-green-400">
            ${metric.avg_customer_value.toLocaleString()}
          </p>
        </div>
      </div>
      <div className="flex items-center justify-between rounded-xl bg-white/5 p-4 transition-colors duration-200 hover:bg-white/10">
        <div className="flex items-center gap-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-green-600 text-sm font-bold text-white shadow-md">
            <Asterisk />
          </div>
          <h4 className="font-semibold text-white">Top Customer Value</h4>
        </div>
        <div className="text-right">
          <p className="font-bold text-green-400">
            ${metric.top_customer_value.toLocaleString()}
          </p>
        </div>
      </div>
      <div className="flex items-center justify-between rounded-xl bg-white/5 p-4 transition-colors duration-200 hover:bg-white/10">
        <div className="flex items-center gap-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-green-600 text-sm font-bold text-white shadow-md">
            <Asterisk />
          </div>
          <h4 className="font-semibold text-white">Total Customer</h4>
        </div>
        <div className="text-right">
          <p className="font-bold text-green-400">{metric.total_customers}</p>
        </div>
      </div>
    </div>
  );
};

export default Customers;

"use client";
import React from "react";
import { MapPin } from "lucide-react";

const Region = ({ data }) => {
  return (
    <div className="mt-10 flex flex-col gap-6 rounded-2xl border border-white/20 bg-white/10 p-8 text-white shadow-2xl backdrop-blur-md transition-all duration-300 hover:scale-[1.02] hover:shadow-orange-500/20">
      {/* Header Section */}
      <div className="flex items-center gap-4">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-orange-500/20 bg-orange-500/10">
          <MapPin className="h-6 w-6 text-orange-400" />
        </div>
        <div>
          <h3 className="text-2xl font-bold tracking-tight text-white">
            Regional Performance
          </h3>
          <p className="text-sm text-gray-400">Revenue by region</p>
        </div>
      </div>

      <hr className="my-2 border-gray-700" />

      {/* Region List */}
      <div className="space-y-4">
        {data.map((region, index) => (
          <div
            key={region.region}
            className="flex items-center justify-between rounded-xl bg-white/5 p-4 transition-colors duration-200 hover:bg-white/10"
          >
            <div className="flex items-center gap-4">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-orange-600 text-sm font-bold text-white shadow-md">
                {index + 1}
              </div>
              <div>
                <h4 className="font-semibold text-white">{region.region}</h4>
                <p className="text-sm text-gray-400">
                  {region.transactions} transactions
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="font-bold text-green-400">
                ${region.total_revenue.toLocaleString()}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Region;

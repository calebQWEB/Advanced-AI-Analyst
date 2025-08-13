"use client";
import React from "react";

const Revenue = ({ data }) => {
  return (
    <div className="mt-10 flex flex-col gap-6 bg-white/10 backdrop-blur-md border rounded-3xl border-white/20 p-8 text-white shadow-2xl transition-all duration-300 hover:scale-[1.02] hover:shadow-green-500/20">
      {/* Main Revenue Display */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          {/* Enhanced Icon */}
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-green-600">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"
              />
            </svg>
          </div>
          <span className="text-2xl font-bold tracking-tight">
            Total Revenue
          </span>
        </div>
        <span className="rounded-full bg-green-600/20 px-4 py-1 text-sm font-medium text-green-400">
          Monthly
        </span>
      </div>

      <div className="flex items-end justify-between">
        <span className="text-5xl font-extrabold text-green-400">
          $
          {data?.sales_metrics?.total_revenue.toLocaleString() ||
            data?.total_revenue?.toLocaleString()}
        </span>
        <div className="flex items-center text-xl font-semibold text-gray-400">
          <span className="mr-1">USD</span>
        </div>
      </div>

      <hr className="my-4 border-gray-700" />

      {/* Revenue Breakdown Section */}
      {data?.revenue_by_category && (
        <div>
          <h3 className="text-xl font-semibold text-gray-300">
            Revenue By Category
          </h3>
          <ul className="mt-4 space-y-4">
            {data?.revenue_by_category.map((category) => (
              <li
                key={category?.category}
                className="group flex flex-col gap-2 rounded-lg bg-gray-800 p-4 transition-colors duration-200 hover:bg-gray-700"
              >
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium text-gray-400 group-hover:text-gray-200">
                    {category?.category}
                  </span>
                  <span className="font-semibold text-white">
                    ${category?.revenue.toLocaleString()}
                  </span>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-gray-700">
                  <div
                    className="h-full rounded-full bg-green-500 transition-all duration-500"
                    style={{
                      width: `${
                        (category?.revenue / data?.total_revenue) * 100
                      }%`,
                    }}
                  />
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Revenue;

"use client";
import React, { useState } from "react";
import { ShoppingBag, Eye, EyeOff } from "lucide-react";

const Products = ({ data }) => {
  const [showAll, setShowAll] = useState(false);
  const displayData = showAll ? data : data.slice(0, 5);

  return (
    <div className="mt-10 flex flex-col gap-6 rounded-2xl border border-white/20 bg-white/10 p-8 text-white shadow-2xl backdrop-blur-md transition-all duration-300 hover:scale-[1.02] hover:shadow-blue-500/20">
      {/* Header Section */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-blue-500/20 bg-blue-500/10">
            <ShoppingBag className="h-6 w-6 text-blue-400" />
          </div>
          <div>
            <h3 className="text-2xl font-bold tracking-tight text-white">
              Top Products
            </h3>
            <p className="text-sm text-gray-400">
              Best selling products by revenue
            </p>
          </div>
        </div>
        {data.length > 5 && (
          <button
            onClick={() => setShowAll(!showAll)}
            className="flex items-center gap-2 rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-2 text-sm font-medium text-blue-400 transition-colors hover:bg-blue-500/20"
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

      {/* Product List */}
      <div className="space-y-4">
        {displayData.map((product, index) => (
          <div
            key={product.name}
            className="flex items-center justify-between rounded-xl bg-white/5 p-4 transition-colors duration-200 hover:bg-white/10"
          >
            <div className="flex items-center gap-4">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-blue-600 text-sm font-bold text-white shadow-md">
                {index + 1}
              </div>
              <div>
                <h4 className="font-semibold text-white">{product.name}</h4>
                <p className="text-sm text-gray-400">
                  {product.units_sold} units sold
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="font-bold text-green-400">
                ${product.total_revenue.toLocaleString()}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Products;

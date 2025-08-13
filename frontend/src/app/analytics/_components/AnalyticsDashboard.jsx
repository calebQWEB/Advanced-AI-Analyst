"use client";
import { useState } from "react";
import {
  TrendingUp,
  TrendingDown,
  Users,
  ShoppingBag,
  MapPin,
  Calendar,
  AlertTriangle,
  Zap,
  DollarSign,
  BarChart3,
  Trophy,
  Star,
  Eye,
  EyeOff,
} from "lucide-react";
import Revenue from "./Revenue";
import Customers from "./Customers";
import Products from "./Products";
import Region from "./Region";
import SalesPerformance from "./SalesPerformance";
import AIGeneratedInsigts from "./AIGeneratedInsigts";

// Main Analytics Dashboard Component
export default function AnalyticsDashboard({ fileData, fileAnalytics }) {
  return (
    <>
      {fileAnalytics && (
        <div>
          {(fileAnalytics.total_revenue || fileAnalytics.sales_metrics) && (
            <Revenue data={fileAnalytics} />
          )}
          {fileAnalytics.top_customers && (
            <Customers
              data={fileAnalytics?.top_customers}
              metric={fileAnalytics?.customer_metrics}
            />
          )}
          {fileAnalytics.top_products && (
            <Products data={fileAnalytics?.top_products} />
          )}
          {fileAnalytics.regional_performance && (
            <Region data={fileAnalytics?.regional_performance} />
          )}
          {fileAnalytics.top_sales_reps && (
            <SalesPerformance data={fileAnalytics?.top_sales_reps} />
          )}
          <AIGeneratedInsigts data={fileAnalytics} />
        </div>
      )}
    </>
  );
}

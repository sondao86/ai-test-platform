import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const PHASE_NAMES: Record<number, string> = {
  1: "Ingest & Chunk",
  2: "Requirement Clarification",
  3: "Test Category Classification",
  4: "Test Case Generation",
};

export const PHASE_DESCRIPTIONS: Record<number, string> = {
  1: "Parse BRD into structured sections",
  2: "Generate clarification questions and extract requirements",
  3: "Map requirements to 6 data quality test categories",
  4: "Generate concrete test case specifications",
};

export const STATUS_COLORS: Record<string, string> = {
  created: "bg-gray-100 text-gray-800",
  in_progress: "bg-blue-100 text-blue-800",
  completed: "bg-green-100 text-green-800",
  archived: "bg-red-100 text-red-800",
  awaiting_user: "bg-yellow-100 text-yellow-800",
  pending: "bg-gray-100 text-gray-700",
};

export const SEVERITY_COLORS: Record<string, string> = {
  critical: "bg-red-100 text-red-800 border-red-300",
  suggestion: "bg-blue-100 text-blue-800 border-blue-300",
  info: "bg-gray-100 text-gray-700 border-gray-300",
};

export const AGENT_COLORS: Record<string, string> = {
  business_agent: "bg-purple-100 text-purple-800",
  data_translator_agent: "bg-indigo-100 text-indigo-800",
  data_engineer_agent: "bg-blue-100 text-blue-800",
  data_governance_agent: "bg-red-100 text-red-800",
  data_ops_agent: "bg-orange-100 text-orange-800",
  data_architect_agent: "bg-teal-100 text-teal-800",
  bi_analytics_agent: "bg-green-100 text-green-800",
};

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString();
}

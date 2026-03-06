import Link from "next/link";
import { FileText, MessageSquareQuote, CheckSquare, Settings, Database, PlayCircle, ShieldCheck } from "lucide-react";

export default function Home() {
  const phases = [
    { title: "Phase 1: Ingest & Chunk", desc: "Parse BRD into structured sections", icon: FileText },
    { title: "Phase 2: Clarification", desc: "Generate clarification questions", icon: MessageSquareQuote },
    { title: "Phase 3: Classification", desc: "Map to test categories", icon: CheckSquare },
    { title: "Phase 4: Test Generation", desc: "Generate test case specs", icon: Settings },
    { title: "Phase 5: Req-Test Mapping", desc: "Generate trace matrix", icon: Database },
    { title: "Phase 6: Execution", desc: "Execute configured tests", icon: PlayCircle },
    { title: "Phase 7: Root Cause", desc: "Analyze failures & evidence", icon: ShieldCheck },
  ];

  return (
    <div className="flex flex-col items-center justify-center gap-12 py-16 px-4">
      <div className="text-center space-y-4">
        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-gray-900">BRD Test Pipeline</h1>
        <p className="max-w-2xl text-lg text-gray-600">
          Multi-Agent system that processes Business Requirements Documents and
          generates data pipeline test cases using 7 specialized AI agents.
        </p>
        <div className="flex justify-center gap-4 pt-4">
          <Link
            href="/projects"
            className="rounded-lg bg-blue-600 px-6 py-3 font-medium text-white hover:bg-blue-700 transition-colors shadow-sm hover:shadow"
          >
            Go to Projects Hub
          </Link>
        </div>
      </div>

      <div className="w-full max-w-5xl space-y-8">
        <div className="border-b border-gray-200 pb-4">
          <h2 className="text-2xl font-bold text-gray-900">End-to-End Pipeline Flow</h2>
          <p className="text-gray-500 mt-1">Human-in-the-loop validation correctly positioned at every major decision point.</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {phases.map((phase, i) => (
            <div key={i} className="relative rounded-xl border border-gray-200 bg-white p-5 shadow-sm hover:border-blue-200 hover:shadow-md transition-all group">
              <div className="flex items-center gap-3 mb-3 text-blue-600 bg-blue-50 w-fit p-2 rounded-lg">
                <phase.icon className="h-5 w-5" />
              </div>
              <h3 className="font-semibold text-gray-900">{phase.title}</h3>
              <p className="mt-2 text-sm text-gray-600 leading-relaxed">{phase.desc}</p>
            </div>
          ))}
        </div>

        <div className="mt-12 bg-white border border-gray-200 rounded-xl p-6 lg:p-8 shadow-sm">
          <h3 className="text-lg font-bold text-gray-900 mb-6">How it works (The Guide)</h3>
          <ol className="relative border-l border-blue-200 ml-3 space-y-8">
            <li className="pl-8 relative">
              <span className="absolute -left-[11px] top-1 h-5 w-5 rounded-full bg-blue-100 border-2 border-blue-600 flex items-center justify-center"></span>
              <h4 className="font-semibold text-gray-900 text-base">1. Upload & Ingest</h4>
              <p className="text-sm text-gray-600 mt-1 leading-relaxed">Start by uploading your Business Requirements Document (BRD) to a new project. The AI intelligently chunks the document into key sections.</p>
            </li>
            <li className="pl-8 relative">
              <span className="absolute -left-[11px] top-1 h-5 w-5 rounded-full bg-blue-100 border-2 border-blue-600 flex items-center justify-center"></span>
              <h4 className="font-semibold text-gray-900 text-base">2. Clarify & Classify</h4>
              <p className="text-sm text-gray-600 mt-1 leading-relaxed">The multi-agent system reviews the requirements. You will be prompted to answer clarification questions in the Review Panel. Once clear, requirements are mapped to test categories like Business Logic and Data Quality.</p>
            </li>
            <li className="pl-8 relative">
              <span className="absolute -left-[11px] top-1 h-5 w-5 rounded-full bg-blue-100 border-2 border-blue-600 flex items-center justify-center"></span>
              <h4 className="font-semibold text-gray-900 text-base">3. Generate & Map Tests</h4>
              <p className="text-sm text-gray-600 mt-1 leading-relaxed">Test cases are generated automatically using best practices and explicitly mapped to the initial requirements to create a comprehensive Traceability Matrix.</p>
            </li>
            <li className="pl-8 relative">
              <span className="absolute -left-[11px] top-1 h-5 w-5 rounded-full bg-blue-100 border-2 border-blue-600 flex items-center justify-center"></span>
              <h4 className="font-semibold text-gray-900 text-base">4. Execute & Analyze</h4>
              <p className="text-sm text-gray-600 mt-1 leading-relaxed">Execute the generated tests directly against your data warehouse (e.g., Databricks, dbt). Review the automated Root Cause Analysis scorecard on any test failures.</p>
            </li>
          </ol>
        </div>
      </div>
    </div>
  );
}

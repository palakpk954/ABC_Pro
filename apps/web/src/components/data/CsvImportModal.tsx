"use client";

import React, { useState } from "react";
import { UploadCloud, CheckCircle2, FileSpreadsheet, X } from "lucide-react";

interface CsvImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  entityName: string;
  onSuccess: (importedCount: number) => void;
}

export function CsvImportModal({
  isOpen,
  onClose,
  entityName,
  onSuccess,
}: CsvImportModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [validating, setValidating] = useState(false);
  const [previewRows, setPreviewRows] = useState<any[]>([]);
  const [isDone, setIsDone] = useState(false);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (!selected) return;
    setFile(selected);
    setValidating(true);

    // Simulate CSV parsing & row-level schema validation (FR-6)
    setTimeout(() => {
      setValidating(false);
      setPreviewRows([
        { row: 1, name: "David Kim", email: "david.k@acme.com", role: "DevOps Engineer", cost: "$90/h", capacity: "40h", status: "VALID" },
        { row: 2, name: "Nadia Belov", email: "nadia.b@acme.com", role: "Frontend Engineer", cost: "$75/h", capacity: "40h", status: "VALID" },
        { row: 3, name: "Jordan Lee", email: "jordan.l@acme.com", role: "Backend Architect", cost: "$115/h", capacity: "40h", status: "VALID" },
      ]);
    }, 600);
  };

  const handleConfirmImport = () => {
    setIsDone(true);
    setTimeout(() => {
      onSuccess(previewRows.length);
      onClose();
    }, 800);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 dark:bg-black/75 backdrop-blur-sm animate-fadeIn">
      <div className="relative w-full max-w-xl rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-slate-900 p-6 shadow-2xl backdrop-blur-2xl text-slate-900 dark:text-foreground">
        <div className="flex items-center justify-between border-b border-slate-200 dark:border-white/10 pb-4 mb-4">
          <div className="flex items-center gap-2">
            <FileSpreadsheet className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
            <h3 className="text-base font-bold text-slate-900 dark:text-white">Import {entityName} from CSV</h3>
          </div>
          <button onClick={onClose} className="rounded-lg p-1 text-muted-foreground hover:text-slate-900 dark:hover:text-white">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Upload Dropzone */}
        {!file ? (
          <label className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/30 p-8 cursor-pointer hover:border-indigo-400 dark:hover:border-indigo-500/50 hover:bg-slate-100 dark:hover:bg-slate-800/60 transition-all">
            <UploadCloud className="h-10 w-10 text-indigo-600 dark:text-indigo-400 mb-2" />
            <span className="text-sm font-semibold text-slate-900 dark:text-white">Choose CSV file or drag & drop</span>
            <span className="text-xs text-muted-foreground mt-1">
              Supports UTF-8 CSV with column headers (name, role, cost, capacity, skills)
            </span>
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="hidden"
            />
          </label>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between rounded-xl bg-slate-50 dark:bg-slate-800/60 p-3 border border-slate-200 dark:border-white/5 text-xs">
              <span className="font-medium text-slate-900 dark:text-white">{file.name} ({(file.size / 1024).toFixed(1)} KB)</span>
              <button
                onClick={() => {
                  setFile(null);
                  setPreviewRows([]);
                }}
                className="text-xs text-rose-600 dark:text-rose-400 hover:underline"
              >
                Change File
              </button>
            </div>

            {validating ? (
              <div className="p-8 text-center text-xs text-muted-foreground">
                <span className="animate-spin inline-block mr-2">&#9696;</span>
                Validating row constraints and proficiency ranges...
              </div>
            ) : (
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                    Validated Preview ({previewRows.length} Valid Rows)
                  </span>
                  <span className="flex items-center gap-1 text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold">
                    <CheckCircle2 className="h-3.5 w-3.5" /> 0 Schema Errors
                  </span>
                </div>

                <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-white/5 bg-slate-50 dark:bg-slate-950/40 text-xs">
                  <table className="w-full text-left">
                    <thead className="border-b border-slate-200 dark:border-white/5 text-[10px] text-muted-foreground font-mono">
                      <tr>
                        <th className="p-2">Row</th>
                        <th className="p-2">Name</th>
                        <th className="p-2">Role</th>
                        <th className="p-2">Rate</th>
                        <th className="p-2">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200 dark:divide-white/5">
                      {previewRows.map((r) => (
                        <tr key={r.row} className="text-slate-800 dark:text-slate-300">
                          <td className="p-2 font-mono text-muted-foreground">#{r.row}</td>
                          <td className="p-2 font-medium text-slate-900 dark:text-white">{r.name}</td>
                          <td className="p-2">{r.role}</td>
                          <td className="p-2 font-mono">{r.cost}</td>
                          <td className="p-2">
                            <span className="rounded bg-emerald-50 dark:bg-emerald-500/20 px-1.5 py-0.5 text-[10px] font-bold text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-500/30">
                              {r.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        <div className="mt-6 flex items-center justify-end gap-3 pt-4 border-t border-slate-200 dark:border-white/10 text-xs">
          <button
            onClick={onClose}
            className="rounded-xl px-4 py-2 text-muted-foreground hover:text-slate-900 dark:hover:text-white"
          >
            Cancel
          </button>
          <button
            disabled={!file || validating || previewRows.length === 0}
            onClick={handleConfirmImport}
            className="rounded-xl bg-indigo-600 px-4 py-2 font-semibold text-white shadow hover:bg-indigo-500 disabled:opacity-40 transition-colors"
          >
            {isDone ? "Importing..." : "Confirm & Import Records"}
          </button>
        </div>
      </div>
    </div>
  );
}

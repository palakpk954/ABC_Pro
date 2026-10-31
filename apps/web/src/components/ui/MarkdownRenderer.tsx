"use client";

import React from "react";
import { cn } from "@/lib/utils";

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

/**
 * High-performance, zero-dependency Markdown renderer tailored for Alex (Digital RM)
 * executive reports, staffing proposals, and structured analysis.
 */
export function MarkdownRenderer({ content, className }: MarkdownRendererProps) {
  if (!content) return null;

  // Split content into blocks by double newlines or single newlines that mark block boundaries
  const rawLines = content.split("\n");
  const blocks: { type: string; lines: string[] }[] = [];
  let currentBlock: { type: string; lines: string[] } | null = null;

  for (let i = 0; i < rawLines.length; i++) {
    const line = rawLines[i];
    const trimmed = line.trim();

    if (!trimmed) {
      if (currentBlock) {
        blocks.push(currentBlock);
        currentBlock = null;
      }
      continue;
    }

    // Determine line type
    if (trimmed.startsWith("#### ")) {
      if (currentBlock) blocks.push(currentBlock);
      blocks.push({ type: "h4", lines: [trimmed.replace(/^####\s+/, "")] });
      currentBlock = null;
    } else if (trimmed.startsWith("### ")) {
      if (currentBlock) blocks.push(currentBlock);
      blocks.push({ type: "h3", lines: [trimmed.replace(/^###\s+/, "")] });
      currentBlock = null;
    } else if (trimmed.startsWith("## ")) {
      if (currentBlock) blocks.push(currentBlock);
      blocks.push({ type: "h2", lines: [trimmed.replace(/^##\s+/, "")] });
      currentBlock = null;
    } else if (trimmed.startsWith("# ")) {
      if (currentBlock) blocks.push(currentBlock);
      blocks.push({ type: "h1", lines: [trimmed.replace(/^#\s+/, "")] });
      currentBlock = null;
    } else if (trimmed.startsWith("> ")) {
      if (currentBlock && currentBlock.type === "quote") {
        currentBlock.lines.push(trimmed.replace(/^>\s*/, ""));
      } else {
        if (currentBlock) blocks.push(currentBlock);
        currentBlock = { type: "quote", lines: [trimmed.replace(/^>\s*/, "")] };
      }
    } else if (/^(\*|-)\s+/.test(trimmed)) {
      const itemText = trimmed.replace(/^(\*|-)\s+/, "");
      if (currentBlock && currentBlock.type === "ul") {
        currentBlock.lines.push(itemText);
      } else {
        if (currentBlock) blocks.push(currentBlock);
        currentBlock = { type: "ul", lines: [itemText] };
      }
    } else if (/^\d+\.\s+/.test(trimmed)) {
      const itemText = trimmed.replace(/^\d+\.\s+/, "");
      if (currentBlock && currentBlock.type === "ol") {
        currentBlock.lines.push(itemText);
      } else {
        if (currentBlock) blocks.push(currentBlock);
        currentBlock = { type: "ol", lines: [itemText] };
      }
    } else {
      if (currentBlock && currentBlock.type === "p") {
        currentBlock.lines.push(trimmed);
      } else {
        if (currentBlock) blocks.push(currentBlock);
        currentBlock = { type: "p", lines: [trimmed] };
      }
    }
  }

  if (currentBlock) {
    blocks.push(currentBlock);
  }

  return (
    <div className={cn("space-y-2.5 text-xs text-slate-800 dark:text-slate-100", className)}>
      {blocks.map((block, idx) => {
        switch (block.type) {
          case "h1":
            return (
              <h1
                key={idx}
                className="text-base font-extrabold text-slate-900 dark:text-white pt-2 pb-1 border-b border-slate-200 dark:border-white/10"
              >
                {renderInline(block.lines[0])}
              </h1>
            );
          case "h2":
            return (
              <h2
                key={idx}
                className="text-sm font-bold text-slate-900 dark:text-white pt-2 pb-0.5 border-b border-slate-200/70 dark:border-white/5"
              >
                {renderInline(block.lines[0])}
              </h2>
            );
          case "h3":
            return (
              <div
                key={idx}
                className="flex items-center gap-2 pt-2.5 pb-1 font-bold text-xs text-indigo-950 dark:text-indigo-200"
              >
                <div className="h-3.5 w-1 rounded-full bg-indigo-600 dark:bg-indigo-400" />
                <h3 className="text-xs font-bold tracking-tight">{renderInline(block.lines[0])}</h3>
              </div>
            );
          case "h4":
            return (
              <h4
                key={idx}
                className="text-xs font-semibold text-slate-800 dark:text-slate-200 pt-1.5 pb-0.5"
              >
                {renderInline(block.lines[0])}
              </h4>
            );
          case "ul":
            return (
              <ul key={idx} className="space-y-1 pl-1">
                {block.lines.map((li, lIdx) => (
                  <li key={lIdx} className="flex items-start gap-2 leading-relaxed">
                    <span className="h-1.5 w-1.5 rounded-full bg-indigo-500 shrink-0 mt-1.5" />
                    <span className="flex-1">{renderInline(li)}</span>
                  </li>
                ))}
              </ul>
            );
          case "ol":
            return (
              <ol key={idx} className="space-y-1.5 pl-1">
                {block.lines.map((li, lIdx) => (
                  <li key={lIdx} className="flex items-start gap-2 leading-relaxed">
                    <span className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-indigo-100 dark:bg-indigo-950/60 text-[9px] font-bold text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800/50 mt-0.5">
                      {lIdx + 1}
                    </span>
                    <span className="flex-1">{renderInline(li)}</span>
                  </li>
                ))}
              </ol>
            );
          case "quote":
            return (
              <blockquote
                key={idx}
                className="my-1.5 rounded-lg border-l-2 border-indigo-500 bg-indigo-50/50 dark:bg-indigo-950/20 px-3 py-2 text-[11px] text-slate-700 dark:text-slate-300 italic"
              >
                {block.lines.map((ql, qIdx) => (
                  <p key={qIdx}>{renderInline(ql)}</p>
                ))}
              </blockquote>
            );
          case "p":
          default:
            const fullParagraph = block.lines.join(" ");
            return (
              <p key={idx} className="leading-relaxed">
                {renderInline(fullParagraph)}
              </p>
            );
        }
      })}
    </div>
  );
}

/**
 * Parses inline formatting:
 * **bold**, *italic*, `code`, and clean text
 */
function renderInline(text: string): React.ReactNode {
  if (!text) return null;

  // Regex matches **bold**, *italic*, or `code`
  const tokenRegex = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g;
  const parts = text.split(tokenRegex);

  return parts.map((part, index) => {
    if (!part) return null;

    if (part.startsWith("**") && part.endsWith("**") && part.length >= 4) {
      return (
        <strong key={index} className="font-bold text-slate-900 dark:text-white">
          {part.slice(2, -2)}
        </strong>
      );
    }

    if (part.startsWith("*") && part.endsWith("*") && part.length >= 2) {
      return (
        <em key={index} className="italic text-slate-700 dark:text-slate-300">
          {part.slice(1, -1)}
        </em>
      );
    }

    if (part.startsWith("`") && part.endsWith("`") && part.length >= 2) {
      return (
        <code
          key={index}
          className="rounded bg-slate-100 dark:bg-slate-800 px-1 py-0.5 font-mono text-[11px] text-indigo-600 dark:text-indigo-400 border border-slate-200 dark:border-white/5"
        >
          {part.slice(1, -1)}
        </code>
      );
    }

    return part;
  });
}

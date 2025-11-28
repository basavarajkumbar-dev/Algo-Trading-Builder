import React, { useState } from 'react';
import { Copy, Check, Download, Terminal } from 'lucide-react';

interface CodeViewerProps {
  code: string;
  explanation: string;
}

const CodeViewer: React.FC<CodeViewerProps> = ({ code, explanation }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const element = document.createElement("a");
    const file = new Blob([code], {type: 'text/x-python'});
    element.href = URL.createObjectURL(file);
    element.download = "algo_strategy.py";
    document.body.appendChild(element);
    element.click();
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 rounded-xl overflow-hidden border border-slate-700 shadow-2xl">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-slate-800 border-b border-slate-700">
        <div className="flex items-center space-x-2 text-slate-300">
          <Terminal size={18} className="text-emerald-400" />
          <span className="text-sm font-mono font-medium">algo_strategy.py</span>
        </div>
        <div className="flex items-center space-x-2">
          <button 
            onClick={handleDownload}
            className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-700 rounded-md transition-colors"
            title="Download .py file"
          >
            <Download size={18} />
          </button>
          <button 
            onClick={handleCopy}
            className="flex items-center space-x-1 px-3 py-1.5 text-xs font-medium text-slate-300 bg-slate-700 hover:bg-slate-600 rounded-md transition-all active:scale-95"
          >
            {copied ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>
        </div>
      </div>

      {/* Code Area */}
      <div className="flex-1 overflow-auto relative group">
        <pre className="p-4 text-sm font-mono text-slate-300 leading-relaxed tab-4">
          <code>{code}</code>
        </pre>
      </div>

      {/* Explanation Panel (if exists) */}
      {explanation && (
        <div className="bg-slate-800/80 border-t border-slate-700 p-4">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Strategy Logic Analysis</h4>
          <div className="text-sm text-slate-300 prose prose-invert max-w-none">
             {/* Using a simple pre-wrap for the markdown text for safety/simplicity without extra libs */}
            <div className="whitespace-pre-wrap font-sans">{explanation}</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CodeViewer;

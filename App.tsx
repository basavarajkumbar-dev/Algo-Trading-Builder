import React, { useState, useEffect } from 'react';
import { STRATEGY_PRESETS } from './constants';
import { StrategyPreset, GeneratorStatus } from './types';
import { generateTradingScript, explainCode } from './services/geminiService';
import StrategyCard from './components/StrategyCard';
import CodeViewer from './components/CodeViewer';
import { Code2, Play, AlertTriangle, Cpu, Loader2 } from 'lucide-react';

const App: React.FC = () => {
  const [selectedPreset, setSelectedPreset] = useState<StrategyPreset | null>(null);
  const [customPrompt, setCustomPrompt] = useState<string>('');
  const [generatedCode, setGeneratedCode] = useState<string>('');
  const [explanation, setExplanation] = useState<string>('');
  const [status, setStatus] = useState<GeneratorStatus>(GeneratorStatus.IDLE);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!selectedPreset && !customPrompt.trim()) {
      setErrorMsg("Please select a strategy or enter custom requirements.");
      return;
    }

    setStatus(GeneratorStatus.GENERATING);
    setErrorMsg(null);
    setGeneratedCode('');
    setExplanation('');

    const promptToUse = customPrompt.trim() 
      ? customPrompt 
      : selectedPreset?.prompt || '';

    // Append the mandatory accuracy check requirement if the user didn't write it in custom prompt
    const fullPrompt = `${promptToUse}\n\nIMPORTANT: Ensure the code checks for >75% accuracy on historical data before placing any orders. Pick Nifty 50 ATM Strike based on spot price.`;

    try {
      const code = await generateTradingScript(fullPrompt);
      
      // Basic cleanup to remove potential markdown code fences from the raw text
      const cleanCode = code.replace(/```python/g, '').replace(/```/g, '').trim();
      
      setGeneratedCode(cleanCode);
      
      // Generate explanation in parallel-ish (after code is ready)
      const expl = await explainCode(cleanCode);
      setExplanation(expl);

      setStatus(GeneratorStatus.COMPLETED);
    } catch (err) {
      setErrorMsg("Failed to generate code. Please check your connection or API limit.");
      setStatus(GeneratorStatus.ERROR);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-zerodha-blue/30 selection:text-zerodha-blue">
      
      {/* Navbar */}
      <nav className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-gradient-to-br from-zerodha-orange to-red-600 p-2 rounded-lg shadow-lg">
              <Cpu className="text-white" size={24} />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                KiteAlgoGen
              </h1>
              <p className="text-[10px] text-slate-500 font-mono tracking-widest uppercase">Zerodha API Workflow Builder</p>
            </div>
          </div>
          <div className="text-xs font-mono text-slate-500 bg-slate-900 px-3 py-1 rounded-full border border-slate-800">
             Model: gemini-3-pro-preview
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 h-[calc(100vh-8rem)]">
          
          {/* Left Panel: Configuration */}
          <div className="lg:col-span-4 flex flex-col space-y-6 h-full overflow-y-auto pr-2 custom-scrollbar">
            
            {/* Strategy Selection */}
            <section>
              <h2 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center">
                <Code2 size={16} className="mr-2" /> Select Strategy
              </h2>
              <div className="space-y-3">
                {STRATEGY_PRESETS.map((preset) => (
                  <StrategyCard 
                    key={preset.id} 
                    preset={preset} 
                    isSelected={selectedPreset?.id === preset.id}
                    onClick={(p) => {
                      setSelectedPreset(p);
                      setCustomPrompt(''); // Clear custom if preset selected
                    }}
                  />
                ))}
              </div>
            </section>

            {/* Custom Input */}
            <section>
               <div className="flex items-center justify-between mb-2">
                 <h2 className="text-sm font-bold text-slate-400 uppercase tracking-wider">
                   Or Custom Logic
                 </h2>
                 {customPrompt && (
                   <button 
                    onClick={() => { setCustomPrompt(''); setSelectedPreset(null); }}
                    className="text-xs text-red-400 hover:text-red-300"
                   >
                     Clear
                   </button>
                 )}
               </div>
              <textarea 
                value={customPrompt}
                onChange={(e) => {
                  setCustomPrompt(e.target.value);
                  setSelectedPreset(null); // Deselect preset if typing custom
                }}
                placeholder="Describe your custom trading strategy here. E.g., 'Buy when RSI < 30 and MACD crosses over...'"
                className="w-full h-32 bg-slate-900 border border-slate-700 rounded-xl p-4 text-sm text-slate-300 focus:ring-2 focus:ring-zerodha-blue focus:border-transparent outline-none resize-none transition-shadow shadow-inner"
              />
            </section>

            {/* Global Settings / Info */}
            <div className="bg-amber-900/20 border border-amber-900/50 rounded-xl p-4">
              <div className="flex items-start space-x-3">
                <AlertTriangle className="text-amber-500 shrink-0 mt-0.5" size={18} />
                <div className="text-xs text-amber-200/80 leading-relaxed">
                  <strong className="block text-amber-400 mb-1">Risk Warning</strong>
                  Generated code includes a logic block for <span className="font-mono bg-amber-900/40 px-1 rounded">accuracy > 75%</span>. 
                  Always paper trade before deploying real capital.
                </div>
              </div>
            </div>

            {/* Action Button */}
            <button
              onClick={handleGenerate}
              disabled={status === GeneratorStatus.GENERATING}
              className={`
                mt-auto w-full py-4 rounded-xl flex items-center justify-center space-x-2 font-bold text-white shadow-lg transition-all transform active:scale-[0.98]
                ${status === GeneratorStatus.GENERATING 
                  ? 'bg-slate-700 cursor-not-allowed' 
                  : 'bg-gradient-to-r from-zerodha-blue to-indigo-600 hover:shadow-zerodha-blue/25 hover:brightness-110'
                }
              `}
            >
              {status === GeneratorStatus.GENERATING ? (
                <>
                  <Loader2 size={20} className="animate-spin" />
                  <span>Building Strategy...</span>
                </>
              ) : (
                <>
                  <Play size={20} fill="currentColor" />
                  <span>Generate Code</span>
                </>
              )}
            </button>
            
            {errorMsg && (
              <p className="text-red-400 text-sm text-center bg-red-900/20 p-2 rounded-lg border border-red-900/50">{errorMsg}</p>
            )}
          </div>

          {/* Right Panel: Output */}
          <div className="lg:col-span-8 h-full">
            {generatedCode ? (
              <CodeViewer code={generatedCode} explanation={explanation} />
            ) : (
              <div className="h-full rounded-xl border-2 border-dashed border-slate-800 flex flex-col items-center justify-center text-slate-600 bg-slate-900/30">
                <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mb-4">
                  <Code2 size={32} />
                </div>
                <h3 className="text-lg font-medium text-slate-400">Ready to Generate</h3>
                <p className="text-sm max-w-xs text-center mt-2">
                  Select a strategy from the left panel to generate your Zerodha Kite Connect Python workflow.
                </p>
              </div>
            )}
          </div>

        </div>
      </main>
    </div>
  );
};

export default App;

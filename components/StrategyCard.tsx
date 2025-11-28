import React from 'react';
import { StrategyPreset } from '../types';
import { ArrowRight, Activity, TrendingUp } from 'lucide-react';

interface StrategyCardProps {
  preset: StrategyPreset;
  onClick: (preset: StrategyPreset) => void;
  isSelected: boolean;
}

const StrategyCard: React.FC<StrategyCardProps> = ({ preset, onClick, isSelected }) => {
  return (
    <div 
      onClick={() => onClick(preset)}
      className={`
        relative p-5 rounded-xl border transition-all duration-300 cursor-pointer group
        ${isSelected 
          ? 'bg-zerodha-blue/10 border-zerodha-blue shadow-[0_0_20px_rgba(65,132,243,0.15)]' 
          : 'bg-slate-800/50 border-slate-700 hover:border-slate-500 hover:bg-slate-800'
        }
      `}
    >
      <div className="flex items-start justify-between mb-3">
        <div className={`p-2 rounded-lg ${isSelected ? 'bg-zerodha-blue text-white' : 'bg-slate-700 text-slate-300'}`}>
          {preset.id === 'orb-breakout' ? <Activity size={20} /> : <TrendingUp size={20} />}
        </div>
        {isSelected && (
          <div className="text-zerodha-blue animate-pulse">
            <span className="text-xs font-bold uppercase tracking-wider">Active</span>
          </div>
        )}
      </div>
      
      <h3 className="text-lg font-semibold text-slate-100 mb-2 group-hover:text-zerodha-blue transition-colors">
        {preset.title}
      </h3>
      <p className="text-sm text-slate-400 leading-relaxed">
        {preset.description}
      </p>
      
      <div className="mt-4 flex items-center text-xs font-medium text-slate-500 group-hover:text-slate-300 transition-colors">
        <span>Load Strategy</span>
        <ArrowRight size={14} className="ml-1 transform group-hover:translate-x-1 transition-transform" />
      </div>
    </div>
  );
};

export default StrategyCard;

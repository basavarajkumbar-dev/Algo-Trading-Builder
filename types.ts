export interface StrategyPreset {
  id: string;
  title: string;
  description: string;
  prompt: string;
}

export interface GeneratedScript {
  code: string;
  explanation: string;
}

export enum GeneratorStatus {
  IDLE = 'IDLE',
  GENERATING = 'GENERATING',
  COMPLETED = 'COMPLETED',
  ERROR = 'ERROR'
}

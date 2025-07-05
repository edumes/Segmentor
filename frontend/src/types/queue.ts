export interface QueueItem {
  id: string;
  fileName: string;
  file?: File;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  selectedMinutes: {
    default: number[];
    vertical: number[];
  };
  error?: string;
  result?: {
    downloadUrl: string;
    fileName: string;
  };
  createdAt: string;
  updatedAt: string;
}

export interface QueueState {
  items: QueueItem[];
  currentItem: QueueItem | null;
  isProcessing: boolean;
}

export type QueueAction =
  | { type: 'SET_ITEMS'; payload: QueueItem[] }
  | { type: 'ADD_ITEM'; payload: QueueItem }
  | { type: 'REMOVE_ITEM'; payload: string }
  | { type: 'UPDATE_ITEM'; payload: Partial<QueueItem> & { id: string } }
  | { type: 'SET_CURRENT_ITEM'; payload: QueueItem | null }
  | { type: 'SET_PROCESSING'; payload: boolean }
  | { type: 'CLEAR_COMPLETED' }; 
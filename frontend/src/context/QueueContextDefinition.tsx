import { createContext } from 'react';
import type { QueueContextType } from './QueueContext';

export const QueueContext = createContext<QueueContextType | undefined>(undefined); 
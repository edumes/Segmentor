import { useContext } from 'react';
import { QueueContext } from '../context/QueueContextDefinition';

export function useQueue() {
    const context = useContext(QueueContext);
    if (context === undefined) {
        throw new Error('useQueue must be used within a QueueProvider');
    }
    return context;
} 
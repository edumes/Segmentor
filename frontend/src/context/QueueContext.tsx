import { notifications } from '@mantine/notifications';
import type { ReactNode } from 'react';
import { useEffect, useReducer } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import type { QueueAction, QueueItem, QueueState } from '../types/queue';
import { QueueContext } from './QueueContextDefinition';

const API_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/ws/queue';
const POLLING_INTERVAL = 2000; // 2 seconds

const initialState: QueueState = {
    items: [],
    currentItem: null,
    isProcessing: false,
};

async function loadQueue(): Promise<QueueItem[]> {
    try {
        const response = await fetch(`${API_URL}/queue/`);
        if (!response.ok) throw new Error('Failed to load queue');
        return await response.json();
    } catch (error) {
        console.error('Error loading queue:', error);
        return [];
    }
}

function queueReducer(state: QueueState, action: QueueAction): QueueState {
    switch (action.type) {
        case 'SET_ITEMS':
            return {
                ...state,
                items: action.payload,
            };
        case 'ADD_ITEM':
            return {
                ...state,
                items: [...state.items, action.payload],
            };
        case 'REMOVE_ITEM':
            return {
                ...state,
                items: state.items.filter(item => item.id !== action.payload),
                currentItem: state.currentItem?.id === action.payload ? null : state.currentItem,
            };
        case 'UPDATE_ITEM':
            return {
                ...state,
                items: state.items.map(item =>
                    item.id === action.payload.id ? { ...item, ...action.payload } : item
                ),
                currentItem:
                    state.currentItem?.id === action.payload.id
                        ? { ...state.currentItem, ...action.payload }
                        : state.currentItem,
            };
        case 'SET_CURRENT_ITEM':
            return {
                ...state,
                currentItem: action.payload,
            };
        case 'SET_PROCESSING':
            return {
                ...state,
                isProcessing: action.payload,
            };
        case 'CLEAR_COMPLETED':
            return {
                ...state,
                items: state.items.filter(item => item.status !== 'completed'),
            };
        default:
            return state;
    }
}

export interface QueueContextType {
    state: QueueState;
    addToQueue: (item: Omit<QueueItem, 'id' | 'status' | 'progress' | 'createdAt' | 'updatedAt'>) => Promise<void>;
    removeFromQueue: (id: string) => Promise<void>;
    updateQueueItem: (id: string, updates: Partial<QueueItem>) => void;
    setCurrentItem: (item: QueueItem | null) => void;
    setProcessing: (isProcessing: boolean) => void;
    clearCompleted: () => void;
    refreshQueue: () => Promise<void>;
}

export function QueueProvider({ children }: { children: ReactNode }) {
    const [state, dispatch] = useReducer(queueReducer, initialState);

    // Handle WebSocket messages
    const handleWebSocketMessage = (data: { type: string; items: QueueItem[] }) => {
        if (data.type === 'queue_update') {
            dispatch({ type: 'SET_ITEMS', payload: data.items });
        }
    };

    // Initialize WebSocket connection
    useWebSocket(WS_URL, handleWebSocketMessage);

    // Load initial queue state
    const refreshQueue = async () => {
        const items = await loadQueue();
        dispatch({ type: 'SET_ITEMS', payload: items });
    };

    // Initial load
    useEffect(() => {
        refreshQueue();
    }, []);

    // Polling for pending items
    useEffect(() => {
        const hasPendingItems = state.items.some(item => item.status === 'pending' || item.status === 'processing');

        if (hasPendingItems) {
            const interval = setInterval(refreshQueue, POLLING_INTERVAL);
            return () => clearInterval(interval);
        }
    }, [state.items]);

    const addToQueue = async (item: Omit<QueueItem, 'id' | 'status' | 'progress' | 'createdAt' | 'updatedAt'>) => {
        try {
            const formData = new FormData();
            if (!item.file) throw new Error('File is required');
            formData.append('file', item.file);
            formData.append('defaults', item.selectedMinutes.default.join(','));
            formData.append('verticals', item.selectedMinutes.vertical.join(','));

            const response = await fetch(`${API_URL}/upload/`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) throw new Error('Failed to upload video');
        } catch (error) {
            console.error('Error adding to queue:', error);
            notifications.show({
                title: 'Error',
                message: 'Failed to add video to queue',
                color: 'red',
            });
        }
    };

    const removeFromQueue = async (id: string) => {
        try {
            const response = await fetch(`${API_URL}/queue/${id}`, {
                method: 'DELETE',
            });

            if (!response.ok) throw new Error('Failed to remove item');
        } catch (error) {
            console.error('Error removing from queue:', error);
            notifications.show({
                title: 'Error',
                message: 'Failed to remove item from queue',
                color: 'red',
            });
        }
    };

    const updateQueueItem = (id: string, updates: Partial<QueueItem>) => {
        dispatch({ type: 'UPDATE_ITEM', payload: { id, ...updates } });
    };

    const setCurrentItem = (item: QueueItem | null) => {
        dispatch({ type: 'SET_CURRENT_ITEM', payload: item });
    };

    const setProcessing = (isProcessing: boolean) => {
        dispatch({ type: 'SET_PROCESSING', payload: isProcessing });
    };

    const clearCompleted = () => {
        dispatch({ type: 'CLEAR_COMPLETED' });
    };

    return (
        <QueueContext.Provider
            value={{
                state,
                addToQueue,
                removeFromQueue,
                updateQueueItem,
                setCurrentItem,
                setProcessing,
                clearCompleted,
                refreshQueue,
            }}
        >
            {children}
        </QueueContext.Provider>
    );
} 
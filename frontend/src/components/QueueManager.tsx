import {
  ActionIcon,
  Badge,
  Button,
  Card,
  Group,
  Progress,
  Stack,
  Text,
  Title
} from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { IconDownload, IconPlayerPause, IconPlayerPlay, IconTrash } from '@tabler/icons-react';
import { useEffect } from 'react';
import { useQueue } from '../hooks/useQueue';
import type { QueueItem } from '../types/queue';

const API_URL = 'http://localhost:8000';

export default function QueueManager() {
  const {
    state: { items, isProcessing },
    removeFromQueue,
    // updateQueueItem,
    setCurrentItem,
    setProcessing,
  } = useQueue();

  const processNextItem = async () => {
    if (isProcessing || !items.length) return;

    const nextItem = items.find(item => item.status === 'pending');
    if (!nextItem) return;

    setProcessing(true);
    setCurrentItem(nextItem);

    try {
      const response = await fetch(`${API_URL}/queue/${nextItem.id}/process`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to start processing');
      }
    } catch (error) {
      console.error('Error processing video:', error);
      notifications.show({
        title: 'Error',
        message: 'Failed to process video',
        color: 'red',
      });
      setProcessing(false);
      setCurrentItem(null);
    }
  };

  useEffect(() => {
    if (!isProcessing && items.some(item => item.status === 'pending')) {
      processNextItem();
    }
  }, [isProcessing, items]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'green';
      case 'failed':
        return 'red';
      case 'processing':
        return 'blue';
      default:
        return 'gray';
    }
  };

  const handleDownload = async (item: QueueItem) => {
    if (!item.result) return;

    try {
      const response = await fetch(`${API_URL}${item.result.downloadUrl}`);
      if (!response.ok) throw new Error('Failed to download file');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = item.result.fileName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading file:', error);
      notifications.show({
        title: 'Error',
        message: 'Failed to download file',
        color: 'red',
      });
    }
  };

  return (
    <Stack gap="md" px={{ base: 'xs', sm: 'md', md: 'xl' }}>
      <Group justify="space-between" wrap="wrap" gap="md">
        <Title order={2}>Queue Manager</Title>
        <Group gap="xs" wrap="wrap">
          <Button
            leftSection={<IconPlayerPlay size={16} />}
            onClick={processNextItem}
            disabled={isProcessing || !items.some(item => item.status === 'pending')}
            w={{ base: '100%', sm: 'auto' }}
          >
            Process Next
          </Button>
          <Button
            leftSection={<IconPlayerPause size={16} />}
            onClick={() => setProcessing(false)}
            disabled={!isProcessing}
            color="red"
            w={{ base: '100%', sm: 'auto' }}
          >
            Stop Processing
          </Button>
        </Group>
      </Group>

      <Stack gap="sm">
        {items.map(item => (
          <Card key={item.id} withBorder shadow="sm" p={{ base: 'sm', sm: 'md' }}>
            <Group justify="space-between" mb="xs" wrap="wrap" gap="xs">
              <Text fw={500} style={{ wordBreak: 'break-word' }}>{item.fileName}</Text>
              <Group gap="xs" wrap="nowrap">
                <Badge color={getStatusColor(item.status)}>{item.status}</Badge>
                {item.status === 'completed' && item.result && (
                  <ActionIcon
                    color="blue"
                    onClick={() => handleDownload(item)}
                  >
                    <IconDownload size={16} />
                  </ActionIcon>
                )}
                <ActionIcon
                  color="red"
                  onClick={() => removeFromQueue(item.id)}
                  disabled={item.status === 'processing'}
                >
                  <IconTrash size={16} />
                </ActionIcon>
              </Group>
            </Group>

            {item.status === 'processing' && (
              <Progress
                value={item.progress}
                size="sm"
                radius="xl"
                striped
                animated
                mb="xs"
              />
            )}

            {item.error && (
              <Text c="red" size="sm">
                Error: {item.error}
              </Text>
            )}

            <Text size="sm" c="dimmed" style={{ wordBreak: 'break-word' }}>
              Selected minutes - Default: {item.selectedMinutes.default.join(', ')} | Vertical:{' '}
              {item.selectedMinutes.vertical.join(', ')}
            </Text>
          </Card>
        ))}

        {items.length === 0 && (
          <Text c="dimmed" ta="center" py="xl">
            No items in queue
          </Text>
        )}
      </Stack>
    </Stack>
  );
} 
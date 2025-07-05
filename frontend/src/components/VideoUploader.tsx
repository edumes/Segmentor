import { Carousel } from '@mantine/carousel';
import '@mantine/carousel/styles.css';
import {
  Button,
  Card,
  Checkbox,
  Container,
  FileInput,
  Grid,
  Group,
  Image,
  Loader,
  Modal,
  Paper,
  Progress,
  rem,
  Stack,
  Text,
  Title,
} from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { useEffect, useRef, useState } from 'react';
import { useQueue } from '../hooks/useQueue';

interface SelectedMinutes {
  default: number[];
  vertical: number[];
}

export default function VideoUploader() {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [frames, setFrames] = useState<string[]>([]);
  const [selectedMinutes, setSelectedMinutes] = useState<SelectedMinutes>({ default: [], vertical: [] });
  const [isLoading, setIsLoading] = useState(false);
  const [isExtracting,
    // setIsExtracting
  ] = useState(false);
  const [progress, setProgress] = useState(0);
  const [carouselOpened, setCarouselOpened] = useState(false);
  const [selectedFrameIndex, setSelectedFrameIndex] = useState(0);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { addToQueue } = useQueue();

  const handleVideoUpload = (file: File | null) => {
    if (file) {
      setVideoFile(file);
      setSelectedMinutes({ default: [], vertical: [] });
      setFrames([]);
      const videoUrl = URL.createObjectURL(file);
      if (videoRef.current) {
        videoRef.current.src = videoUrl;
      }
    }
  };

  const captureFrame = (time: number): Promise<string> => {
    return new Promise((resolve) => {
      if (videoRef.current && canvasRef.current) {
        videoRef.current.currentTime = time;
        videoRef.current.onseeked = () => {
          const canvas = canvasRef.current!;
          const video = videoRef.current!;
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          const ctx = canvas.getContext('2d')!;
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          resolve(canvas.toDataURL('image/jpeg'));
        };
      }
    });
  };

  const generateFrames = async () => {
    if (!videoRef.current) return;

    setIsLoading(true);
    setProgress(0);

    try {
      const video = videoRef.current;
      const duration = video.duration;
      const frames: string[] = [];
      const totalFrames = Math.ceil(duration / 60);

      // Capture one frame per minute
      for (let time = 0; time < duration; time += 60) {
        const frame = await captureFrame(time);
        frames.push(frame);
        setProgress(((frames.length / totalFrames) * 100));
      }

      setFrames(frames);
    } catch (error) {
      console.error('Error generating frames:', error);
      notifications.show({
        title: 'Error',
        message: 'Error generating video frames',
        color: 'red',
      });
    } finally {
      setIsLoading(false);
      setProgress(0);
    }
  };

  const toggleMinuteSelection = (minute: number, format: 'default' | 'vertical') => {
    setSelectedMinutes(prev => {
      const newSelection = { ...prev };
      const index = newSelection[format].indexOf(minute);

      if (index === -1) {
        newSelection[format] = [...newSelection[format], minute].sort((a, b) => a - b);
      } else {
        newSelection[format] = newSelection[format].filter(m => m !== minute);
      }

      return newSelection;
    });
  };

  const handleAddToQueue = async () => {
    if (!videoFile || (!selectedMinutes.default.length && !selectedMinutes.vertical.length)) {
      notifications.show({
        title: 'Error',
        message: 'Please select a video and at least one minute',
        color: 'red',
      });
      return;
    }

    try {
      await addToQueue({
        fileName: videoFile.name,
        file: videoFile,
        selectedMinutes,
      });

      // Reset form
      setVideoFile(null);
      setFrames([]);
      setSelectedMinutes({ default: [], vertical: [] });
      if (videoRef.current) {
        videoRef.current.src = '';
      }

      // Clear FileInput
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) {
        fileInput.value = '';
      }

      notifications.show({
        title: 'Success',
        message: 'Video added to queue',
        color: 'green',
      });
    } catch (error) {
      console.error('Error adding to queue:', error);
      notifications.show({
        title: 'Error',
        message: 'Failed to add video to queue',
        color: 'red',
      });
    }
  };

  const handleFrameClick = (index: number) => {
    setSelectedFrameIndex(index);
    setCarouselOpened(true);
  };

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.onloadedmetadata = generateFrames;
    }
  }, [videoFile]);

  return (
    <Container size="xl" py="xl" px={{ base: 'xs', sm: 'md', md: 'xl' }}>
      <Paper shadow="md" radius="lg" p={{ base: 'md', sm: 'xl' }} withBorder>
        <Stack gap="xl">
          <Group justify="center">
            <Title order={1} ta="center">Video Uploader</Title>
          </Group>

          <Group justify="center">
            <FileInput
              label="Select a video"
              placeholder="Click to select or drag a file"
              accept="video/*"
              onChange={handleVideoUpload}
              clearable
              size="md"
              style={{ width: '100%', maxWidth: rem(500) }}
              disabled={isLoading || isExtracting}
            />
          </Group>

          <video
            ref={videoRef}
            style={{ display: 'none' }}
            crossOrigin="anonymous"
          />

          <canvas
            ref={canvasRef}
            style={{ display: 'none' }}
          />

          {(isLoading || isExtracting) && (
            <Stack gap="md" align="center">
              <Loader size="xl" />
              <Text size="lg" fw={500} ta="center">
                {isLoading ? 'Processing video...' : 'Extracting segments...'}
              </Text>
              {isLoading && (
                <Progress
                  value={progress}
                  size="xl"
                  radius="xl"
                  style={{ width: '100%', maxWidth: rem(500) }}
                  striped
                  animated
                />
              )}
            </Stack>
          )}

          {!isLoading && !isExtracting && frames.length > 0 && (
            <Grid gutter={{ base: 'xs', sm: 'md', md: 'lg' }}>
              {frames.map((frame, index) => (
                <Grid.Col key={index} span={{ base: 12, xs: 6, sm: 6, md: 4, lg: 3 }}>
                  <Card shadow="sm" padding="lg" radius="md" withBorder h="100%">
                    <Card.Section>
                      <Image
                        src={frame}
                        alt={`Frame at ${index} minutes`}
                        height={200}
                        fit="cover"
                        style={{ cursor: 'pointer' }}
                        onClick={() => handleFrameClick(index)}
                      />
                    </Card.Section>

                    {/* <Group justify="space-between" mt="md" mb="xs">
                      <Text fw={500} size="lg">Minute {index}</Text>
                    </Group> */}

                    <Group gap="md" mt="md" wrap="nowrap">
                      <Checkbox
                        label="Default"
                        checked={selectedMinutes.default.includes(index)}
                        onChange={() => toggleMinuteSelection(index, 'default')}
                        size="lg"
                        disabled={isExtracting}
                      />
                      <Checkbox
                        label="Vertical"
                        checked={selectedMinutes.vertical.includes(index)}
                        onChange={() => toggleMinuteSelection(index, 'vertical')}
                        size="lg"
                        disabled={isExtracting}
                      />
                    </Group>
                  </Card>
                </Grid.Col>
              ))}
            </Grid>
          )}

          {!isLoading && !isExtracting && frames.length > 0 && (
            <Group justify="center" mt="auto" pt="xl" gap="md">
              <Button
                onClick={handleAddToQueue}
                disabled={!videoFile || (!selectedMinutes.default.length && !selectedMinutes.vertical.length)}
                size="lg"
                w={{ base: '100%', sm: 'auto' }}
                style={{ maxWidth: rem(250) }}
              >
                Add to Queue
              </Button>
            </Group>
          )}
        </Stack>
      </Paper>

      <Modal
        opened={carouselOpened}
        onClose={() => setCarouselOpened(false)}
        size="xl"
        centered
        padding={0}
        withCloseButton={false}
      >
        <Carousel
          initialSlide={selectedFrameIndex}
          withIndicators
          height={500}
          emblaOptions={{ align: 'start', dragFree: true, loop: true }}
          styles={{
            indicator: {
              width: rem(12),
              height: rem(4),
              transition: 'width 250ms ease',
              '&[data-active]': {
                width: rem(40),
              },
            },
          }}
        >
          {frames.map((frame, index) => (
            <Carousel.Slide key={index}>
              <Image
                src={frame}
                alt={`Frame at ${index} minutes`}
                height={500}
                fit="contain"
                style={{ backgroundColor: '#f8f9fa' }}
              />
              <Text
                size="lg"
                fw={500}
                style={{
                  position: 'absolute',
                  bottom: rem(20),
                  left: '50%',
                  transform: 'translateX(-50%)',
                  backgroundColor: 'rgba(0, 0, 0, 0.7)',
                  color: 'white',
                  padding: `${rem(8)} ${rem(16)}`,
                  borderRadius: rem(4),
                }}
              >
                Minute {index}
              </Text>
            </Carousel.Slide>
          ))}
        </Carousel>
      </Modal>
    </Container>
  );
} 
import { AppShell, Button, createTheme, Group, MantineProvider, Text, Burger, Drawer, Stack } from '@mantine/core';
import { Notifications } from '@mantine/notifications';
import { IconList, IconUpload } from '@tabler/icons-react';
import { Link, Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import QueueManager from './components/QueueManager';
import VideoUploader from './components/VideoUploader';
import { QueueProvider } from './context/QueueContext';
import { useDisclosure } from '@mantine/hooks';

function App() {
  const [opened, { toggle }] = useDisclosure();
  const theme = createTheme({
    colors: {
      twilightPurple: [
        '#faf5ff', // very light lavender
        '#f3e8ff',
        '#e9d5ff',
        '#d8b4fe',
        '#c084fc', // soft purple
        '#a855f7', // vibrant purple
        '#9333ea', // strong accent
        '#7e22ce',
        '#6b21a8',
        '#581c87', // deep purple
      ],
      accentPink: [
        '#fff0f6',
        '#ffe4ec',
        '#ffc9d8',
        '#ffa1be',
        '#f872a2',
        '#ec4899',
        '#db2777',
        '#be185d',
        '#9d174d',
        '#831843',
      ],
    },

    primaryColor: 'twilightPurple',

    fontFamily: 'Inter, sans-serif',

    headings: {
      fontFamily: 'Inter, sans-serif',
      sizes: {
        h1: { fontSize: '2.25rem', fontWeight: '700' },
        h2: { fontSize: '1.875rem', fontWeight: '600' },
        h3: { fontSize: '1.5rem', fontWeight: '600' },
      },
    },

    shadows: {
      md: '0 4px 12px rgba(88, 28, 135, 0.15)',
      xl: '0 8px 24px rgba(88, 28, 135, 0.2)',
    },

    defaultRadius: 'md',
  });

  return (
    <MantineProvider theme={theme} defaultColorScheme="dark">
      <Notifications />
      <QueueProvider>
        <Router>
          <AppShell
            header={{ height: 60 }}
            padding="md"
          >
            <AppShell.Header>
              <Group h="100%" px="md" justify="space-between">
                <Group>
                  <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
                  <Text size="xl" fw={700}>Video Segmenter</Text>
                </Group>
                <Group visibleFrom="sm">
                  <Button
                    component={Link}
                    to="/"
                    variant="subtle"
                    leftSection={<IconUpload size={16} />}
                  >
                    Upload
                  </Button>
                  <Button
                    component={Link}
                    to="/queue"
                    variant="subtle"
                    leftSection={<IconList size={16} />}
                  >
                    Queue
                  </Button>
                </Group>
              </Group>
            </AppShell.Header>

            <Drawer
              opened={opened}
              onClose={toggle}
              size="100%"
              padding="md"
              hiddenFrom="sm"
              zIndex={1000}
            >
              <Stack>
                <Button
                  component={Link}
                  to="/"
                  variant="subtle"
                  leftSection={<IconUpload size={16} />}
                  onClick={toggle}
                  fullWidth
                >
                  Upload
                </Button>
                <Button
                  component={Link}
                  to="/queue"
                  variant="subtle"
                  leftSection={<IconList size={16} />}
                  onClick={toggle}
                  fullWidth
                >
                  Queue
                </Button>
              </Stack>
            </Drawer>

            <AppShell.Main>
              <Routes>
                <Route path="/" element={<VideoUploader />} />
                <Route path="/queue" element={<QueueManager />} />
              </Routes>
            </AppShell.Main>
          </AppShell>
        </Router>
      </QueueProvider>
    </MantineProvider>
  );
}

export default App;

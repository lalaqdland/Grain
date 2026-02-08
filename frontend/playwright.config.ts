import { defineConfig } from '@playwright/test'

process.env.NO_PROXY = '127.0.0.1,localhost'
process.env.no_proxy = '127.0.0.1,localhost'

const frontendPort = 13102
const backendPort = 18102

export default defineConfig({
  testDir: './e2e',
  timeout: 120000,
  expect: {
    timeout: 10000,
  },
  fullyParallel: false,
  retries: 0,
  use: {
    baseURL: `http://127.0.0.1:${frontendPort}`,
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',
    video: 'retain-on-failure',
  },
  webServer: [
    {
      command: `python -m uvicorn main:app --host 127.0.0.1 --port ${backendPort}`,
      cwd: '../backend',
      url: `http://127.0.0.1:${backendPort}/health`,
      reuseExistingServer: false,
      env: {
        ...process.env,
        API_HOST: '127.0.0.1',
        API_PORT: String(backendPort),
        API_RELOAD: 'false',
        CORS_ORIGINS: `http://127.0.0.1:${frontendPort},http://localhost:${frontendPort}`,
      },
    },
    {
      command: `npx next dev -p ${frontendPort}`,
      cwd: '.',
      url: `http://127.0.0.1:${frontendPort}`,
      reuseExistingServer: false,
      env: {
        ...process.env,
        NEXT_PUBLIC_API_URL: `http://127.0.0.1:${backendPort}`,
      },
    },
  ],
})

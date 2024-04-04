import { config } from 'dotenv'
import { createEnv } from '@t3-oss/env-core'
import { z } from 'zod'

config()

export const env = createEnv({
  server: {
    SAFEWAY_USERNAME: z.string().min(1),
    SAFEWAY_PASSWORD: z.string().min(1)
  },
  runtimeEnv: process.env,
  emptyStringAsUndefined: true
})

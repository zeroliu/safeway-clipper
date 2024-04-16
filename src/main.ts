import { PlaywrightCrawler } from 'crawlee'

import { router } from './routes.js'
import { COUPONS_URL, isProduction } from './constants.js'

const startUrls = [COUPONS_URL]

const crawler = new PlaywrightCrawler({
  headless: true,
  launchContext: {
    userDataDir: !isProduction ? './user-data' : undefined
  },
  requestHandler: router,
  requestHandlerTimeoutSecs: 3600,
  maxRequestRetries: 2,
  maxRequestsPerCrawl: 10000,
  maxConcurrency: 10
})

await crawler.run(startUrls)

import { Dataset, PlaywrightCrawler } from 'crawlee'

import { router } from './routes.js'
import { COUPONS_URL, isProduction } from './constants.js'

const startUrls = [COUPONS_URL]

const crawler = new PlaywrightCrawler({
  launchContext: {
    userDataDir: !isProduction ? './user-data' : undefined
  },
  requestHandler: router,
  maxRequestsPerCrawl: 10000
  // maxRequestRetries: 0,
  // headless: true,
  // maxConcurrency: 1,
  // preNavigationHooks: [
  //   async ({ request, log }, _options) => {
  //     log.info(`Navigating to ${request.url}`)
  //   }
  // ]
})

try {
  await crawler.run(startUrls)
} finally {
  if (Dataset.length > 0) {
    await Dataset.exportToCSV('coupons')
  }
}

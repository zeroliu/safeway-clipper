import { Dataset, PlaywrightCrawler } from 'crawlee'

import { router } from './routes.js'

const startUrls = ['https://www.safeway.com/foru/coupons-deals.html']

const crawler = new PlaywrightCrawler({
  launchContext: {
    userDataDir: './user-data'
  },
  requestHandler: router,
  maxRequestsPerCrawl: 10000,
  maxRequestRetries: 0
  //   headless: true,
  //   maxConcurrency: 1,
  //   preNavigationHooks: [
  //     async ({ request, log }, _options) => {
  //       log.info(`Navigating to ${request.url}`)
  //     }
  //   ]
})

try {
  await crawler.run(startUrls)
} finally {
  await Dataset.exportToCSV('coupons')
}

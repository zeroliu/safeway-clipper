import { createPlaywrightRouter } from 'crawlee'
import { env } from './env.js'

export const router = createPlaywrightRouter()

router.addDefaultHandler(async ({ page, enqueueLinks, log }) => {
  await page.waitForTimeout(1000)

  // if redirected to sign-in page, sign in
  if (page.url() === 'https://www.safeway.com/account/sign-in.html') {
    log.info('Redirected to sign-in page, signing in...')
    await page.fill('input[name="userId"]', env.SAFEWAY_USERNAME)
    await page.fill('input[name="inputPassword"]', env.SAFEWAY_PASSWORD)
    await page.click('//input[@id="btnSignIn"]')
  } else {
    log.info('Already signed in, continuing...')
  }

  await page.waitForTimeout(3000)

  let loadMoreButton = await page.$('//button[@class="btn load-more"]')
  while (loadMoreButton) {
    await loadMoreButton.click()
    await page.waitForTimeout(1000)
    loadMoreButton = await page.$('//button[@class="btn load-more"]')
  }

  await enqueueLinks({
    globs: ['https://www.safeway.com/foru/offer-details.*.*.*.html'],
    label: 'offer-details'
  })
})

router.addHandler('offer-details', async ({ request, page, pushData, log }) => {
  await page.waitForTimeout(3000)

  let url = request.loadedUrl
  let heading = await (await page.$('//span[@id="offerDetailHeadingSavings"]'))?.innerText()
  let title = await (await page.$('//div[@id="offerDetailTitleId"]'))?.innerText()
  let description = await (await page.$('//div[@id="offerDetailDescriptionId"]'))?.innerText()
  let expiration = await (await page.$('//span[@class="offer-details-end-date"]'))?.innerText()

  log.info(`${heading} - ${title} - ${description} - ${expiration}: ${url}`)

  const clipButton = await page.$('button:has-text(" Clip Coupon ")')
  if (clipButton) {
    log.info('Clipping new coupon...')
    await clipButton.click()
    await page.waitForTimeout(1000)
  }

  await pushData({
    url,
    title,
    heading,
    description,
    expiration
  })
})

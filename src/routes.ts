import { createPlaywrightRouter } from 'crawlee'
import { env } from './env.js'
import { SIGN_IN_URL } from './constants.js'

export const router = createPlaywrightRouter()

router.addDefaultHandler(async ({ page, log }) => {
  Promise.any([
    page.waitForSelector('//div[@class="coupon-grid-offers"]', { timeout: 10000 }),
    page.waitForURL(SIGN_IN_URL, { timeout: 10000 })
  ])

  // if redirected to sign-in page, sign in
  if (page.url() === SIGN_IN_URL) {
    log.info('Redirected to sign-in page, signing in...')
    await page.fill('input[name="userId"]', env.SAFEWAY_USERNAME)
    await page.fill('input[name="inputPassword"]', env.SAFEWAY_PASSWORD)
    await page.click('//input[@id="btnSignIn"]')
  } else {
    log.info('Already signed in, continuing...')
  }

  await page.waitForSelector('//div[@class="coupon-grid-offers"]', { timeout: 10000 })

  // load all coupons
  let loadMoreButton = await page.$('//button[@class="btn load-more"]')
  while (loadMoreButton) {
    await loadMoreButton.click()
    await page.waitForTimeout(1000)
    loadMoreButton = await page.$('//button[@class="btn load-more"]')
  }

  let newCouponClipped = 0
  try {
    // clip all coupons
    const clipButtons = await page.$$('button:has-text(" Clip Coupon ")')
    for (const clipButton of clipButtons) {
      await clipButton.click()
      newCouponClipped++

      await page.waitForTimeout(1000)

      const errorModal = await page.$('//*[@id="errorModal"]//button[@class="create-modal-close-icon modal-close"]')

      if (errorModal?.isVisible()) {
        await errorModal.click()
        await page.waitForTimeout(100)
      }
    }
  } catch (e) {
    log.error('Error clipping coupons')
  } finally {
    log.info(`${newCouponClipped} new coupons clipped.`)
  }
  /**
   * Clip on offer details page
   */
  // await enqueueLinks({
  //   globs: ['https://www.safeway.com/foru/offer-details.*.*.*.html'],
  //   label: 'offer-details'
  // })
})

router.addHandler('offer-details', async ({ request, page, pushData, log }) => {
  await page.waitForSelector('//div[@id="offerDetailTitleId"]', { timeout: 10000 })

  let url = request.loadedUrl
  let title = await (await page.$('//div[@id="offerDetailTitleId"]'))?.innerText()
  let heading = await (await page.$('//span[@id="offerDetailHeadingSavings"]'))?.innerText()
  let description = await (await page.$('//div[@id="offerDetailDescriptionId"]'))?.innerText()
  let expiration = await (await page.$('//span[@class="offer-details-end-date"]'))?.innerText()

  log.info(`${url}: ${title} - ${heading} - ${description} - ${expiration}`)

  const clipButton = await page.$('button:has-text(" Clip Coupon ")')
  if (clipButton) {
    await clipButton.click()
    await page.waitForTimeout(1000)
    log.info('Coupon clipped')
  }

  await pushData({
    url,
    title,
    heading,
    description,
    expiration
  })
})

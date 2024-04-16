import { createPlaywrightRouter } from 'crawlee'

import { env } from './env.js'
import { SIGN_IN_URL } from './constants.js'

export const router = createPlaywrightRouter()

router.addDefaultHandler(async ({ page, log }) => {
  await Promise.any([
    page.waitForSelector('//div[@class="coupon-grid-offers"]', { timeout: 10000 }),
    page.waitForURL(SIGN_IN_URL, { timeout: 10000 })
  ])

  // if redirected to sign-in page, sign in
  if (page.url() === SIGN_IN_URL) {
    log.info('Redirected to sign-in page, signing in ...')
    await page.fill('input[name="userId"]', env.SAFEWAY_USERNAME)
    await page.fill('input[name="inputPassword"]', env.SAFEWAY_PASSWORD)
    await page.click('//input[@id="btnSignIn"]')
  } else {
    log.info('Already signed in, continuing ...')
  }

  await page.waitForSelector('//div[@class="coupon-grid-offers"]', { timeout: 10000 })

  // clip all new coupons
  log.info('Loading all coupons ...')
  let loadMoreButton = await page.$('//button[@class="btn load-more"]')
  while (loadMoreButton) {
    await loadMoreButton.click({ timeout: 5000 })
    await page.waitForTimeout(500)
    loadMoreButton = await page.$('//button[@class="btn load-more"]')
  }

  const clipButtons = await page.$$('button:has-text(" Clip Coupon ")')
  log.info(`Found ${clipButtons.length} new coupons, clipping ...`)

  let clipped = 0
  for (const clipButton of clipButtons) {
    try {
      await clipButton.click({ timeout: 1000 })

      clipped++

      await page.waitForTimeout(500)

      const errorModal = await page.$('//*[@id="errorModal"]//button[@class="create-modal-close-icon modal-close"]')
      const isErrorModalVisible = errorModal?.isVisible()
      if (errorModal && isErrorModalVisible) {
        await errorModal.click({ timeout: 100 })
        await page.waitForTimeout(10)
      }
    } catch (e) {
      // continue
    }
  }

  log.info(`Clipped ${clipped} new coupons.`)
})

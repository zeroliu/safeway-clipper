import { createPlaywrightRouter } from 'crawlee'

import { env } from './env.js'
import { COUPONS_URL, SIGN_IN_URL } from './constants.js'

export const router = createPlaywrightRouter()

router.addDefaultHandler(async ({ page, log }) => {
  await Promise.any([
    page.waitForSelector('//div[@class="coupon-grid-offers"]', { timeout: 10000 }),
    page.waitForURL(SIGN_IN_URL, { timeout: 10000 })
  ])

  // if redirected to sign-in page, sign in
  if (page.url() === SIGN_IN_URL) {
    log.info('Redirected to sign-in page, signing in ...')

    // Wait for the email/username input field to be visible
    await page.waitForSelector('#enterUsername', { timeout: 10000 })

    // Fill in credentials
    await page.fill('#enterUsername', env.SAFEWAY_USERNAME)
    const signInWithPasswordButton = await page.$('button:has-text(" Sign in with password ")')
    await signInWithPasswordButton?.click()

    await page.waitForSelector('#password', { timeout: 10000 })
    await page.fill('#password', env.SAFEWAY_PASSWORD)

    // Click the sign in button - using a more reliable selector
    await page.click('button[type="submit"]', { delay: 500 })

    // Wait longer for authentication and redirect
    await page.waitForTimeout(3000)
    await page.waitForURL(url => url.toString().startsWith(COUPONS_URL), { timeout: 20000 })
  } else {
    log.info('Already signed in, continuing ...')
  }

  await page.waitForTimeout(1000)
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

  if (clipButtons.length === 0) {
    log.info('Great! All coupons has been clipped.')
    return
  }

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

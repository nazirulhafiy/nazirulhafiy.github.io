#!/usr/bin/env node
/**
 * Runtime regression check for /contact/ GA4 custom events.
 *
 * Uses a local static server + Chromium. Injects a gtag/dataLayer stub only —
 * does not load googletagmanager.com or emit production GA traffic.
 *
 * Covers: single emission, one event per repeated activation (no double
 * registration), unmarked HTTPS links, absent/nonfunction/throwing gtag
 * preserving default action, and no PII in event params.
 */

import { spawn } from 'node:child_process'
import { chromium } from '@playwright/test'

const PORT = Number(process.env.CONTACT_EVENTS_CHECK_PORT || 8766)
const BASE = `http://127.0.0.1:${PORT}`
const CONTACT_URL = `${BASE}/contact/`

const PII_PATTERNS = [
  /@/,
  /mailto:/i,
  /60135623005/,
  /\+60\s*1/,
  /wa\.me/i,
  /linkedin\.com\/in\//i,
  /BEGIN:VCARD/i,
  /nazirul@/i,
  /\.vcf/i,
]

function startStaticServer(port) {
  const child = spawn('python3', ['-m', 'http.server', String(port), '--bind', '127.0.0.1'], {
    cwd: process.cwd(),
    stdio: ['ignore', 'pipe', 'pipe'],
  })
  let log = ''
  child.stdout.on('data', (chunk) => {
    log += chunk
  })
  child.stderr.on('data', (chunk) => {
    log += chunk
  })
  return { child, log: () => log }
}

async function waitForServer(url, child, log) {
  const deadline = Date.now() + 30_000
  while (Date.now() < deadline) {
    if (child.exitCode !== null) {
      throw new Error(`http.server exited ${child.exitCode}\n${log()}`)
    }
    try {
      const response = await fetch(url)
      if (response.ok) return
    } catch {
      /* not up yet */
    }
    await new Promise((resolve) => setTimeout(resolve, 200))
  }
  throw new Error(`Timed out waiting for ${url}\n${log()}`)
}

function assert(condition, message) {
  if (!condition) throw new Error(message)
}

function paramsHavePii(params) {
  const blob = JSON.stringify(params ?? {})
  return PII_PATTERNS.some((re) => re.test(blob))
}

function customEvents(recorded) {
  return recorded.filter(
    (row) => row.name === 'email_click' || row.name === 'contact_download',
  )
}

async function openContact(browser, { gtagMode }) {
  const context = await browser.newContext()
  const pageErrors = []
  const page = await context.newPage()
  page.on('pageerror', (err) => pageErrors.push(String(err)))

  await page.addInitScript((mode) => {
    window.__snRecorded = []
    if (mode === 'absent') {
      // Leave window.gtag undefined (localhost loader also skips gtag).
      return
    }
    if (mode === 'nonfunction') {
      window.gtag = { not: 'callable' }
      return
    }
    if (mode === 'throwing') {
      window.gtag = function throwingGtag() {
        throw new Error('stub gtag throw')
      }
      return
    }
    // mode === 'stub'
    window.dataLayer = window.dataLayer || []
    window.gtag = function stubGtag() {
      const args = Array.from(arguments)
      window.dataLayer.push(args)
      if (args[0] === 'event') {
        window.__snRecorded.push({
          name: args[1],
          params: args[2] && typeof args[2] === 'object' ? { ...args[2] } : {},
        })
      }
    }
  }, gtagMode)

  await page.goto(CONTACT_URL, { waitUntil: 'domcontentloaded' })
  await page.locator('main#content').waitFor({ timeout: 15_000 })
  return { context, page, pageErrors }
}

async function recordedEvents(page) {
  return page.evaluate(() => window.__snRecorded.slice())
}

/**
 * Click a selector and report whether any earlier bubble handler cancelled the
 * default action.
 *
 * The page script listens on `document` (bubble). A probe on the anchor itself
 * would run in the target phase — before that delegated handler — and would
 * observe too early. The probe therefore also listens on `document` (bubble),
 * registered after the page script, so it runs after the implementation.
 * Only then does the probe call preventDefault so mailto/download stay local.
 */
async function clickAndProbeDefault(page, selector) {
  return page.evaluate((sel) => {
    const a = document.querySelector(sel)
    if (!a) return { ok: false, reason: `missing ${sel}` }
    return new Promise((resolve) => {
      const onClick = (ev) => {
        const target = ev.target && ev.target.closest ? ev.target.closest('a') : null
        if (target !== a) return
        document.removeEventListener('click', onClick, false)
        resolve({
          ok: true,
          defaultPrevented: ev.defaultPrevented,
          href: a.getAttribute('href') || '',
          eventName: a.getAttribute('data-sn-event') || null,
        })
        // Test-only cancel AFTER observing what earlier handlers did.
        ev.preventDefault()
      }
      document.addEventListener('click', onClick, false)
      a.click()
    })
  }, selector)
}

/**
 * Isolated harness: inject a temporary document bubble canceler (not product
 * code) registered after the page script but before the probe. The probe must
 * observe defaultPrevented === true, proving the oracle catches cancellation.
 */
async function caseProbeOracleDetectsCancellation(browser) {
  const { context, page } = await openContact(browser, { gtagMode: 'stub' })
  try {
    const result = await page.evaluate(() => {
      const a = document.querySelector('a[data-sn-event="email_click"]')
      if (!a) return { ok: false, reason: 'missing email_click bar' }
      return new Promise((resolve) => {
        const canceler = (ev) => {
          const target = ev.target && ev.target.closest ? ev.target.closest('a') : null
          if (target !== a) return
          ev.preventDefault()
        }
        const probe = (ev) => {
          const target = ev.target && ev.target.closest ? ev.target.closest('a') : null
          if (target !== a) return
          document.removeEventListener('click', canceler, false)
          document.removeEventListener('click', probe, false)
          resolve({
            ok: true,
            defaultPrevented: ev.defaultPrevented,
          })
          // Already cancelled by canceler; keep local either way.
          ev.preventDefault()
        }
        // Order on document bubble: page script → canceler → probe.
        document.addEventListener('click', canceler, false)
        document.addEventListener('click', probe, false)
        a.click()
      })
    })
    assert(result.ok, result.reason || 'oracle harness failed to run')
    assert(
      result.defaultPrevented === true,
      'oracle must observe defaultPrevented after an intentional canceler; probe ordering is wrong',
    )

    // Sanity: without the canceler, the real page script must leave default intact.
    const clean = await clickAndProbeDefault(page, 'a[data-sn-event="email_click"]')
    assert(clean.ok, 'clean email_click probe failed')
    assert(
      clean.defaultPrevented === false,
      'real contact-events script unexpectedly prevented default',
    )
  } finally {
    await context.close()
  }
}

async function clickHttpsBars(page) {
  const selectors = [
    'a.contact-bar[href^="https://wa.me/"]',
    'a.contact-bar[href*="linkedin.com"]',
    'a.contact-bar[href="https://hafiy.my/"]',
    'a.contact-bar[href="https://pcds2030.com"]',
    'a.contact-bar[href="https://sde2030.com"]',
    'a.contact-bar[href="https://ai.sarawak.news"]',
  ]
  for (const sel of selectors) {
    const result = await clickAndProbeDefault(page, sel)
    assert(result.ok, `HTTPS bar missing: ${sel}`)
    assert(
      result.defaultPrevented === false,
      `unexpected defaultPrevented before probe on ${sel}`,
    )
  }
}

async function caseSuccessfulSingleEmission(browser) {
  const { context, page, pageErrors } = await openContact(browser, { gtagMode: 'stub' })
  try {
    const email = await clickAndProbeDefault(page, 'a[data-sn-event="email_click"]')
    const download = await clickAndProbeDefault(page, 'a[data-sn-event="contact_download"]')
    assert(email.ok && download.ok, 'instrumented bars missing')
    assert(email.defaultPrevented === false, 'email_click listener prevented default')
    assert(download.defaultPrevented === false, 'contact_download listener prevented default')

    const events = customEvents(await recordedEvents(page))
    assert(events.length === 2, `expected 2 custom events, got ${JSON.stringify(events)}`)
    assert(events[0].name === 'email_click', `first event ${events[0].name}`)
    assert(events[1].name === 'contact_download', `second event ${events[1].name}`)
    for (const ev of events) {
      assert(
        ev.params && ev.params.surface === 'contact',
        `bad params for ${ev.name}: ${JSON.stringify(ev.params)}`,
      )
      assert(!paramsHavePii(ev.params), `PII in ${ev.name}: ${JSON.stringify(ev.params)}`)
      assert(Object.keys(ev.params).length === 1, `unexpected extra params on ${ev.name}`)
    }
    assert(pageErrors.length === 0, `page errors: ${pageErrors.join('; ')}`)
  } finally {
    await context.close()
  }
}

async function caseRepeatedActivationsOneEach(browser) {
  const { context, page } = await openContact(browser, { gtagMode: 'stub' })
  try {
    for (let i = 0; i < 2; i += 1) {
      await clickAndProbeDefault(page, 'a[data-sn-event="email_click"]')
      await clickAndProbeDefault(page, 'a[data-sn-event="contact_download"]')
    }
    const events = customEvents(await recordedEvents(page))
    const emails = events.filter((e) => e.name === 'email_click')
    const downloads = events.filter((e) => e.name === 'contact_download')
    assert(
      emails.length === 2,
      `expected 2 email_click (one per activation), got ${emails.length}: ${JSON.stringify(events)}`,
    )
    assert(
      downloads.length === 2,
      `expected 2 contact_download (one per activation), got ${downloads.length}: ${JSON.stringify(events)}`,
    )
    assert(events.length === 4, `expected exactly 4 custom events, got ${events.length}`)
  } finally {
    await context.close()
  }
}

async function caseUninstrumentedHttpsSilent(browser) {
  const { context, page } = await openContact(browser, { gtagMode: 'stub' })
  try {
    await clickHttpsBars(page)
    const events = customEvents(await recordedEvents(page))
    assert(
      events.length === 0,
      `HTTPS bars must not emit custom events, got ${JSON.stringify(events)}`,
    )
  } finally {
    await context.close()
  }
}

async function caseGtagFailurePreservesDefault(browser, gtagMode) {
  const { context, page, pageErrors } = await openContact(browser, { gtagMode })
  try {
    const email = await clickAndProbeDefault(page, 'a[data-sn-event="email_click"]')
    const download = await clickAndProbeDefault(page, 'a[data-sn-event="contact_download"]')
    assert(email.ok && download.ok, `${gtagMode}: instrumented bars missing`)
    assert(
      email.defaultPrevented === false,
      `${gtagMode}: email default was prevented`,
    )
    assert(
      download.defaultPrevented === false,
      `${gtagMode}: download default was prevented`,
    )
    assert(email.href.startsWith('mailto:'), `${gtagMode}: email href lost`)
    assert(download.href.includes('.vcf'), `${gtagMode}: vcf href lost`)

    const events = customEvents(await recordedEvents(page))
    assert(
      events.length === 0,
      `${gtagMode}: expected no recorded custom events, got ${JSON.stringify(events)}`,
    )
    // throwing mode must be caught inside the page script
    assert(
      pageErrors.length === 0,
      `${gtagMode}: uncaught page errors: ${pageErrors.join('; ')}`,
    )
  } finally {
    await context.close()
  }
}

const CASES = [
  ['probe oracle detects cancellation', caseProbeOracleDetectsCancellation],
  ['successful single emission', caseSuccessfulSingleEmission],
  ['repeated activations one event each', caseRepeatedActivationsOneEach],
  ['uninstrumented HTTPS links silent', caseUninstrumentedHttpsSilent],
  ['absent gtag preserves default', (b) => caseGtagFailurePreservesDefault(b, 'absent')],
  ['nonfunction gtag preserves default', (b) => caseGtagFailurePreservesDefault(b, 'nonfunction')],
  ['throwing gtag preserves default', (b) => caseGtagFailurePreservesDefault(b, 'throwing')],
]

async function main() {
  const server = startStaticServer(PORT)
  try {
    await waitForServer(CONTACT_URL, server.child, server.log)
    const browser = await chromium.launch()
    const results = []
    try {
      for (const [name, run] of CASES) {
        try {
          await run(browser)
          results.push({ name, ok: true })
          console.log(`PASS  ${name}`)
        } catch (error) {
          const message = error instanceof Error ? error.message : String(error)
          results.push({ name, ok: false, message })
          console.log(`FAIL  ${name}`)
          console.log(`      ${message}`)
        }
      }
    } finally {
      await browser.close()
    }

    const failed = results.filter((r) => !r.ok)
    console.log(
      `contact-events-check: ${failed.length === 0 ? 'PASS' : 'FAIL'} ` +
        `(${results.length - failed.length}/${results.length}) url: ${CONTACT_URL}`,
    )
    process.exit(failed.length === 0 ? 0 : 1)
  } finally {
    if (server.child.exitCode === null) server.child.kill('SIGTERM')
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.stack || error.message : error)
  process.exit(1)
})

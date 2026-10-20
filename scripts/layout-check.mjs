#!/usr/bin/env node
/**
 * Layout check for the static portfolio site.
 *
 * Serves the repo root with `python3 -m http.server` unless LAYOUT_CHECK_URL is set,
 * then opens Chromium and WebKit (in parallel).
 *
 * Fails when the page scrolls horizontally, `[data-box]` elements overlap
 * (a box that contains another is not an overlap), a `[data-box]` element is
 * clipped, or a `[data-one-line]` element wraps onto more than one line.
 */

import { spawn } from 'node:child_process'
import { chromium, webkit } from '@playwright/test'

const VIEWPORTS = [
  { name: '375x667', width: 375, height: 667 },
  { name: '390x844', width: 390, height: 844 },
  { name: '390x680', width: 390, height: 680 },
  { name: '1280x800', width: 1280, height: 800 },
]

const SCHEMES = ['light', 'dark']

const PAGES = [
  { name: 'home', path: '/' },
  { name: 'experience', path: '/experience.html' },
  { name: 'posts', path: '/posts/' },
]

const TOLERANCE_PX = 1

const browserTypes = { chromium, webkit }

function selectedBrowsers() {
  const raw = process.env.LAYOUT_CHECK_BROWSERS || 'chromium,webkit'
  const names = raw.split(',').map((name) => name.trim()).filter(Boolean)
  for (const name of names) {
    if (!browserTypes[name]) {
      throw new Error(`Unknown browser "${name}". Use chromium and/or webkit.`)
    }
  }
  return names
}

function siteUrl(port, path = '/') {
  const base = `http://127.0.0.1:${port}`
  return new URL(path, base).href
}

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
      /* server not up yet */
    }
    await new Promise((resolve) => setTimeout(resolve, 200))
  }
  throw new Error(`Timed out waiting for ${url}\n${log()}`)
}

function describeFailures(failures) {
  return failures.map((failure) => {
    if (failure.kind === 'horizontal-overflow') {
      return `  horizontal overflow: scrollWidth ${failure.scrollWidth} > clientWidth ${failure.clientWidth}`
    }
    if (failure.kind === 'overlap') {
      return `  overlap: ${failure.a} × ${failure.b} (x ${failure.overlapX}px, y ${failure.overlapY}px)`
    }
    if (failure.kind === 'clipped') {
      if (failure.via === 'ancestor') {
        return `  clipped: ${failure.label} border box is cut by a clipping ancestor`
      }
      return `  clipped: ${failure.label} scroll ${failure.scrollWidth}×${failure.scrollHeight} client ${failure.clientWidth}×${failure.clientHeight}`
    }
    if (failure.kind === 'wrap') {
      return `  wrapped: ${failure.label} is ${failure.lines} lines`
    }
    if (failure.kind === 'missing-markers') {
      return `  missing markers: page has no [data-box] elements`
    }
    return `  ${JSON.stringify(failure)}`
  })
}

async function settle(page) {
  await page.evaluate(async () => {
    if (document.fonts?.ready) {
      await Promise.race([
        document.fonts.ready,
        new Promise((resolve) => setTimeout(resolve, 8000)),
      ])
    }
  })
}

async function measure(page) {
  return page.evaluate((tolerance) => {
    function px(value) {
      return Math.round(value * 10) / 10
    }

    function describe(el) {
      const tag = el.tagName.toLowerCase()
      const testid = el.getAttribute('data-testid')
      if (testid) return `${tag}[data-testid="${testid}"]`
      const text = (el.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 40)
      return text ? `${tag} "${text}"` : tag
    }

    function clips(overflow) {
      return overflow === 'hidden' || overflow === 'clip' || overflow === 'scroll' || overflow === 'auto'
    }

    function lineCount(el) {
      const text = (el.innerText || '').replace(/\s+/g, ' ').trim()
      if (!text) return 1
      const range = document.createRange()
      range.selectNodeContents(el)
      const rects = [...range.getClientRects()].filter((rect) => rect.width > 0.5 && rect.height > 0.5)
      const tops = []
      for (const rect of rects) {
        if (!tops.some((top) => Math.abs(top - rect.top) <= 2)) tops.push(rect.top)
      }
      return Math.max(1, tops.length)
    }

    const failures = []
    const doc = document.documentElement
    const scrollWidth = Math.max(doc.scrollWidth, document.body?.scrollWidth ?? 0)
    const clientWidth = doc.clientWidth
    if (scrollWidth > clientWidth + tolerance) {
      failures.push({
        kind: 'horizontal-overflow',
        scrollWidth,
        clientWidth,
      })
    }

    const boxes = [...document.querySelectorAll('[data-box]')]
    const measured = boxes.map((el) => ({
      el,
      label: describe(el),
      rect: el.getBoundingClientRect(),
    }))

    for (let i = 0; i < measured.length; i += 1) {
      for (let j = i + 1; j < measured.length; j += 1) {
        const a = measured[i]
        const b = measured[j]
        if (a.el.contains(b.el) || b.el.contains(a.el)) continue
        const overlapX = Math.min(a.rect.right, b.rect.right) - Math.max(a.rect.left, b.rect.left)
        const overlapY = Math.min(a.rect.bottom, b.rect.bottom) - Math.max(a.rect.top, b.rect.top)
        if (overlapX > tolerance && overlapY > tolerance) {
          failures.push({
            kind: 'overlap',
            a: a.label,
            b: b.label,
            overlapX: px(overlapX),
            overlapY: px(overlapY),
          })
        }
      }
    }

    for (const el of boxes) {
      const style = getComputedStyle(el)
      const overflowY = el.scrollHeight - el.clientHeight
      const overflowX = el.scrollWidth - el.clientWidth
      if (
        (clips(style.overflowY) && overflowY > tolerance) ||
        (clips(style.overflowX) && overflowX > tolerance)
      ) {
        failures.push({
          kind: 'clipped',
          via: 'scroll',
          label: describe(el),
          scrollWidth: el.scrollWidth,
          scrollHeight: el.scrollHeight,
          clientWidth: el.clientWidth,
          clientHeight: el.clientHeight,
        })
        continue
      }

      const rect = el.getBoundingClientRect()
      if (rect.width < 1 && rect.height < 1) continue
      let parent = el.parentElement
      while (parent) {
        const parentStyle = getComputedStyle(parent)
        const parentRect = parent.getBoundingClientRect()
        const cutX =
          clips(parentStyle.overflowX) &&
          (rect.left < parentRect.left - tolerance || rect.right > parentRect.right + tolerance)
        const cutY =
          clips(parentStyle.overflowY) &&
          (rect.top < parentRect.top - tolerance || rect.bottom > parentRect.bottom + tolerance)
        if (cutX || cutY) {
          failures.push({ kind: 'clipped', via: 'ancestor', label: describe(el) })
          break
        }
        parent = parent.parentElement
      }
    }

    for (const el of document.querySelectorAll('[data-one-line]')) {
      const lines = lineCount(el)
      if (lines > 1) {
        failures.push({ kind: 'wrap', label: describe(el), lines })
      }
    }

    return failures
  }, TOLERANCE_PX)
}

async function openPage(context, pageDef, port) {
  const page = await context.newPage()
  const url = siteUrl(port, pageDef.path)
  await page.goto(url, { waitUntil: 'domcontentloaded' })
  await page.locator('main#content').waitFor({ timeout: 15_000 })
  await settle(page)
  return page
}

async function runBrowser(name, port) {
  const started = Date.now()
  const browser = await browserTypes[name].launch()
  const failures = []
  try {
    for (const viewport of VIEWPORTS) {
      for (const scheme of SCHEMES) {
        const context = await browser.newContext({
          viewport: { width: viewport.width, height: viewport.height },
          colorScheme: scheme,
          deviceScaleFactor: 1,
        })
        try {
          for (const pageDef of PAGES) {
            const page = await openPage(context, pageDef, port)
            try {
              const found = await measure(page)
              const boxes = await page.locator('[data-box]').count()
              if (boxes < 1) found.push({ kind: 'missing-markers' })
              if (found.length > 0) {
                failures.push({
                  browser: name,
                  viewport: viewport.name,
                  scheme,
                  page: pageDef.name,
                  found,
                })
              }
            } finally {
              await page.close()
            }
          }
        } finally {
          await context.close()
        }
      }
    }
  } finally {
    await browser.close()
  }
  return { name, ms: Date.now() - started, failures }
}

function formatSeconds(ms) {
  return `${(ms / 1000).toFixed(1)}s`
}

function printReport(results, url) {
  const failures = results.flatMap((result) => result.failures)
  const status = failures.length === 0 ? 'PASS' : 'FAIL'
  const checks = results.length * VIEWPORTS.length * SCHEMES.length * PAGES.length
  const lines = [
    `layout-check: ${status}`,
    `url: ${url}`,
    `label: ${process.env.LAYOUT_CHECK_LABEL || 'current'}`,
    `checks: ${checks} (${results.length} browsers × ${VIEWPORTS.length} viewports × ${SCHEMES.length} schemes × ${PAGES.length} pages)`,
    `browsers: ${results.map((result) => `${result.name} ${formatSeconds(result.ms)}`).join(', ')}`,
    `total: ${formatSeconds(results.reduce((sum, result) => sum + result.ms, 0))}`,
  ]
  if (failures.length === 0) {
    console.log(lines.join('\n'))
    return
  }
  console.log(lines.join('\n'))
  console.log('')
  for (const failure of failures) {
    console.log(`${failure.browser} ${failure.scheme} ${failure.viewport} ${failure.page}`)
    console.log(describeFailures(failure.found).join('\n'))
  }
}

async function main() {
  const names = selectedBrowsers()
  const port = Number(process.env.LAYOUT_CHECK_PORT || 8765)
  const externalUrl = process.env.LAYOUT_CHECK_URL
  let server = null
  const url = externalUrl || siteUrl(port, '/')

  if (!externalUrl) {
    server = startStaticServer(port)
    try {
      await waitForServer(url, server.child, server.log)
    } catch (error) {
      server.child.kill('SIGTERM')
      throw error
    }
  }

  try {
    const results = await Promise.all(names.map((name) => runBrowser(name, port)))
    printReport(results, url)
    const failed = results.some((result) => result.failures.length > 0)
    if (server) server.child.kill('SIGTERM')
    process.exit(failed ? 1 : 0)
  } finally {
    if (server && server.child.exitCode === null) server.child.kill('SIGTERM')
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.stack || error.message : error)
  process.exit(1)
})

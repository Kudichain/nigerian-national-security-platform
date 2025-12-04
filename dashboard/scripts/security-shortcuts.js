#!/usr/bin/env node
/*
 * Security Shortcut Controller
 * Provides password-protected terminal shortcuts for rapid navigation to
 * sensitive dashboard views during development or CI/CD smoke checks.
 */

import readline from 'readline'
import { spawn } from 'child_process'

const PASSWORD = process.env.SECURITY_SHORTCUT_PASSWORD
const BASE_URL = process.env.SECURITY_SHORTCUT_BASE_URL || 'http://localhost:3002'

if (!PASSWORD) {
  console.error('[security-shortcuts] Missing SECURITY_SHORTCUT_PASSWORD environment variable.')
  console.error('Set it before starting the shortcut controller. Example:')
  console.error('  SECURITY_SHORTCUT_PASSWORD="super-secret" npm run security:shortcuts')
  process.exit(1)
}

if (!process.stdin.isTTY) {
  console.error('[security-shortcuts] Non-interactive terminal detected. A TTY session is required.')
  process.exit(1)
}

const shortcuts = [
  { key: 'h', label: 'Help / shortcuts overview', action: () => printHelp() },
  { key: 'c', label: 'CCTV Monitoring', path: '/cctv' },
  { key: 'z', label: 'Citizen Search', path: '/citizen-search' },
  { key: 's', label: 'Surveillance Command', path: '/surveillance' },
  { key: 'd', label: 'Drone Operations Center', path: '/drone-live' },
  { key: 'v', label: 'City Surveillance Grid', path: '/city-surveillance' },
  { key: 't', label: 'Number Tracing Intelligence', path: '/citizen-search?mode=number-trace' },
  { key: 'n', label: 'NIN Identity Search', path: '/identity?mode=nin' },
  { key: 'w', label: 'World-Security Control Hub', path: '/' },
  { key: 'q', label: 'Quit controller', action: () => gracefulExit(0) },
]

const shortcutMap = new Map(shortcuts.map((shortcut) => [shortcut.key, shortcut]))

function printBanner() {
  console.clear()
  console.log('═══════════════════════════════════════════════════════════════════════════════')
  console.log('  ⚔️  WORLD-SECURITY SHORTCUT CONTROLLER')
  console.log('  • Terminal integration for secure dashboard routing (CI/CD friendly)')
  console.log('  • Press the mapped keys to request access to protected destinations')
  console.log('  • All entries require password validation before unlocking')
  console.log('═══════════════════════════════════════════════════════════════════════════════')
  printHelp()
}

function printHelp() {
  console.log('\nAvailable secure shortcuts:')
  shortcuts.forEach((shortcut) => {
    if (shortcut.key === 'h') return
    console.log(`  [${shortcut.key}] ${shortcut.label}`)
  })
  console.log('\nUtility controls:')
  console.log('  [h] Show this help panel')
  console.log('  [q] Quit controller')
  console.log('\nPress the desired key to initiate password verification.')
}

function openInBrowser(url) {
  const target = `${BASE_URL}${url}`
  const platform = process.platform
  let command
  let args

  if (platform === 'win32') {
    command = 'cmd'
    args = ['/c', 'start', '""', target]
  } else if (platform === 'darwin') {
    command = 'open'
    args = [target]
  } else {
    command = 'xdg-open'
    args = [target]
  }

  const child = spawn(command, args, {
    detached: true,
    stdio: 'ignore',
  })
  child.unref()
  console.log(`[security-shortcuts] Access granted → ${target}`)
}

function gracefulExit(code) {
  console.log('\nShutting down security shortcut controller...')
  if (process.stdin.isTTY) {
    process.stdin.setRawMode(false)
    process.stdin.pause()
  }
  process.exit(code)
}

function askPassword(promptText = 'Access password: ') {
  return new Promise((resolve) => {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      terminal: true,
    })

    rl.stdoutMuted = true
    rl.setPrompt(promptText)
    rl.prompt()

    rl._writeToOutput = function _writeToOutput() {
      if (rl.stdoutMuted) {
        const masked = '*'.repeat(rl.line.length)
        rl.output.write(`\u001B[2K\u001B[200D${promptText}${masked}`)
      }
    }

    rl.on('line', (line) => {
      rl.close()
      process.stdout.write('\n')
      resolve(line.trim())
    })
  })
}

async function handleShortcut(shortcut) {
  if (shortcut.action) {
    shortcut.action()
    return
  }

  process.stdin.setRawMode(false)
  process.stdin.pause()

  try {
    const input = await askPassword('Access password: ')
    if (input !== PASSWORD) {
      console.log('[security-shortcuts] Access denied. Invalid password.')
      return
    }

    if (shortcut.path) {
      openInBrowser(shortcut.path)
    } else if (shortcut.action) {
      shortcut.action()
    }
  } finally {
    process.stdin.setRawMode(true)
    process.stdin.resume()
  }
}

function handleKeypress(buffer) {
  const key = buffer.toString()

  if (buffer.length === 1 && buffer[0] === 3) {
    gracefulExit(0)
    return
  }

  const shortcut = shortcutMap.get(key)

  if (!shortcut) {
    console.log(`[security-shortcuts] Unrecognized key: ${JSON.stringify(key)}. Press h for help.`)
    return
  }

  handleShortcut(shortcut).catch((error) => {
    console.error('[security-shortcuts] Unexpected error:', error)
  })
}

function bootstrap() {
  printBanner()
  process.stdin.setEncoding('utf8')
  process.stdin.setRawMode(true)
  process.stdin.resume()
  process.stdin.on('data', handleKeypress)
}

bootstrap()

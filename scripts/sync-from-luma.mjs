#!/usr/bin/env node
// Copies the Luma creator workflows from a luma-v2 checkout into this plugin.
//
//   node scripts/sync-from-luma.mjs <path-to-luma-v2-checkout>
//   node scripts/sync-from-luma.mjs <path-to-luma-v2-checkout> --check
//
// The source is <checkout>/mcp-skills, read-only. The target is plugins/luma/skills in this repo.
// Each workflow folder (SKILL.md plus references/) is copied as is, and _shared/ is copied beside
// them, so every relative link in the source resolves the same way once the plugin is installed:
//   ../_shared/luma-tools.md                       -> skills/_shared/luma-tools.md
//   ../short-film/references/ffmpeg.md             -> skills/short-film/references/ffmpeg.md
//   ../../memory-reel/references/reel-edit.md      -> from a reference file, same target
// The source README.md is about how the text is built in luma-v2, not a workflow, so it stays there.
// Nothing is rewritten and nothing is pushed. --check writes nothing and exits 1 when
// plugins/luma/skills differs from what a sync would produce.

import { execFileSync } from 'node:child_process'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const target = path.join(repoRoot, 'plugins', 'luma', 'skills')
const SHARED = '_shared'
const EM_DASH = String.fromCharCode(0x2014)

const args = process.argv.slice(2)
const check = args.includes('--check')
const positional = args.filter((a) => !a.startsWith('--'))
if (positional.length !== 1 || args.some((a) => a.startsWith('--') && a !== '--check')) {
  console.error('usage: node scripts/sync-from-luma.mjs <path-to-luma-v2-checkout> [--check]')
  process.exit(2)
}

const checkout = path.resolve(positional[0])
const source = path.join(checkout, 'mcp-skills')
if (!fs.existsSync(path.join(source, SHARED, 'luma-tools.md'))) {
  console.error(`not a luma-v2 checkout: ${source}/${SHARED}/luma-tools.md is missing`)
  process.exit(2)
}

const problems = []

function walk(dir) {
  const out = []
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name.startsWith('.')) continue
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) out.push(...walk(full))
    else if (entry.isFile()) out.push(full)
  }
  return out.sort()
}

function frontmatter(text) {
  const m = text.match(/^---\n([\s\S]*?)\n---\n/)
  if (!m) return null
  const fields = {}
  for (const line of m[1].split('\n')) {
    const kv = line.match(/^([A-Za-z_]+):\s*(.*)$/)
    if (kv) fields[kv[1]] = kv[2]
  }
  return fields
}

// Which top-level entries are shipped: every folder, and each must be _shared or a workflow.
function plan() {
  const workflows = []
  for (const entry of fs.readdirSync(source, { withFileTypes: true })) {
    if (!entry.isDirectory() || entry.name.startsWith('.')) continue
    if (entry.name === SHARED) continue
    if (!fs.existsSync(path.join(source, entry.name, 'SKILL.md'))) {
      problems.push(`${entry.name}/ has no SKILL.md and is not ${SHARED}/`)
      continue
    }
    workflows.push(entry.name)
  }
  return workflows.sort()
}

function copyInto(dest, workflows) {
  fs.mkdirSync(dest, { recursive: true })
  for (const name of [SHARED, ...workflows]) {
    for (const file of walk(path.join(source, name))) {
      const out = path.join(dest, path.relative(source, file))
      fs.mkdirSync(path.dirname(out), { recursive: true })
      fs.copyFileSync(file, out)
    }
  }
}

// Every relative link, markdown or backticked, must land on a file inside the skills folder.
function verify(root) {
  const files = walk(root)
  const set = new Set(files)
  for (const file of files) {
    const rel = path.relative(root, file)
    if (!file.endsWith('.md')) continue
    const text = fs.readFileSync(file, 'utf8')
    if (text.includes(EM_DASH)) problems.push(`${rel}: contains an em dash`)

    const refs = new Set()
    for (const m of text.matchAll(/\]\(([^)\s]+)\)/g)) refs.add(m[1])
    for (const m of text.matchAll(/`((?:\.\.\/|references\/)[^`\s]+\.md)`/g)) refs.add(m[1])
    for (const ref of refs) {
      if (/^(https?:|mailto:|#)/.test(ref)) continue
      const resolved = path.resolve(path.dirname(file), ref.split('#')[0])
      if (!resolved.startsWith(root + path.sep)) {
        problems.push(`${rel}: link ${ref} leaves the plugin`)
      } else if (!set.has(resolved)) {
        problems.push(`${rel}: link ${ref} does not resolve`)
      }
    }

    if (path.basename(file) === 'SKILL.md') {
      const fm = frontmatter(text)
      const slug = path.basename(path.dirname(file))
      if (!fm) problems.push(`${rel}: no frontmatter`)
      else {
        if (fm.name !== slug) problems.push(`${rel}: name "${fm.name}" is not the folder name`)
        if (!fm.description) problems.push(`${rel}: no description`)
      }
    }
  }
  return files
}

function sourceRevision() {
  const git = (...a) =>
    execFileSync('git', ['-C', checkout, ...a], {
      encoding: 'utf8',
      env: { ...process.env, GIT_OPTIONAL_LOCKS: '0' },
    }).trim()
  try {
    const sha = git('rev-parse', '--short', 'HEAD')
    const dirty = git('status', '--porcelain', '--', 'mcp-skills') !== ''
    return `${sha}${dirty ? ' (mcp-skills has uncommitted changes)' : ''}`
  } catch {
    return 'unknown (not a git checkout)'
  }
}

function sameTree(a, b) {
  const list = (root) => (fs.existsSync(root) ? walk(root).map((f) => path.relative(root, f)) : [])
  const la = list(a)
  const lb = list(b)
  if (la.join('\n') !== lb.join('\n')) return false
  return la.every((rel) => fs.readFileSync(path.join(a, rel)).equals(fs.readFileSync(path.join(b, rel))))
}

const workflows = plan()
if (workflows.length === 0) problems.push('no workflows found in mcp-skills/')

const staging = fs.mkdtempSync(path.join(os.tmpdir(), 'luma-skills-'))
try {
  copyInto(staging, workflows)
  const files = verify(staging)
  if (problems.length > 0) {
    console.error(problems.map((p) => `  ${p}`).join('\n'))
    console.error(`\n${problems.length} problem(s). ${check ? 'Nothing compared.' : 'plugins/luma/skills left untouched.'}`)
    process.exit(1)
  }
  if (check) {
    if (sameTree(staging, target)) {
      console.log(`plugins/luma/skills matches ${source} (${files.length} files)`)
    } else {
      console.error('plugins/luma/skills differs from the source. Run the sync without --check.')
      process.exit(1)
    }
  } else {
    if (path.dirname(path.dirname(target)) !== path.join(repoRoot, 'plugins')) throw new Error('unexpected target')
    fs.rmSync(target, { recursive: true, force: true })
    fs.cpSync(staging, target, { recursive: true })
    console.log(`synced ${workflows.length} workflows and ${SHARED}/ (${files.length} files) into plugins/luma/skills`)
    console.log(`workflows: ${workflows.join(', ')}`)
    console.log(`source: ${source} at ${sourceRevision()}`)
    console.log('nothing was committed or pushed')
  }
} finally {
  fs.rmSync(staging, { recursive: true, force: true })
}

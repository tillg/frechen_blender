import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Change, Git, Step, Workflow } from '../types'

// Skeleton after w12-free's tools/claude-mods/w12-mission-control; the state
// model is this project's spec workflow (specs/changes/<name>/ frontmatter).
const PANE = 'spec-status'
const DIR = 'specs/changes'
const REFRESH_MS = 60_000
const TWEAK = 'tweak: side lane for small changes (no change dir)'
const NONE = 'No active change — /spec:propose to start'
const EMPTY: Workflow = { others: [], unreadable: false, updatedAt: 0 }
// Change the tag when a field of the workflow changes.
const workflowRef = atom({ plugin: 'spec', key: 'workflow' } as const, EMPTY, { shape: 'workflow-3' })

const STEP_OF: Record<string, Step> = {
  exploring: 'propose',
  proposed: 'refine',
  applying: 'apply',
}
const ROWS: { step: Step; label: string }[] = [
  { step: 'propose', label: 'propose' },
  { step: 'refine', label: 'grill | iterate   (optional)' },
  { step: 'apply', label: 'apply' },
  { step: 'review', label: 'adversarial-code-review' },
  { step: 'archive', label: 'archive' },
]

const field = (text: string, key: string) =>
  text.match(new RegExp(`^${key}:\\s*(\\S+)`, 'm'))?.[1]

async function readChange($: EngineInterface, name: string): Promise<Change> {
  const dir = `${DIR}/${name}`
  const files = (await $.fs.list(dir)).filter(f => f.kind === 'file' && f.name.endsWith('.md'))
  const docs: { status?: string; order: number }[] = []
  let done = 0
  let total = 0
  for (const f of files) {
    const text = await $.fs.read(`${dir}/${f.name}`)
    const order = Number(field(text, 'order'))
    docs.push({ status: field(text, 'status'), order: isNaN(order) ? Infinity : order })
    if (f.name === 'plan.md') {
      const lines = text.split('\n')
      done = lines.filter(l => /^\s*- \[x\]/i.test(l)).length
      total = lines.filter(l => /^\s*- \[[ x]\]/i.test(l)).length
    }
  }
  // Majority status; on a tie the file with the lowest order (reference/frontmatter.md).
  const counts: Record<string, number> = {}
  for (const d of docs) if (d.status) counts[d.status] = (counts[d.status] ?? 0) + 1
  const top = Math.max(0, ...Object.values(counts))
  const lead = docs
    .filter(d => d.status && counts[d.status] === top)
    .sort((a, b) => a.order - b.order)[0]
  const status = lead?.status ?? 'exploring'
  const reviewed = files.some(f => f.name === 'review.md')
  const step: Step =
    status === 'applied' ? (reviewed ? 'archive' : 'review') : (STEP_OF[status] ?? 'propose')
  return { name, status, done, total, reviewed, step }
}

const git = async ($: EngineInterface, args: string[], stdin?: string) => {
  const r = await $.process.run(['git', ...args], { stdin })
  return r.exitCode === 0 ? r.stdout : undefined
}

// One `git status --porcelain=v2 --branch`, plus where HEAD stands against main.
async function readGit($: EngineInterface): Promise<Git | undefined> {
  const out = await git($, ['status', '--porcelain=v2', '--branch'])
  if (out === undefined) return undefined
  const g: Git = { branch: '', staged: 0, modified: 0, untracked: 0, conflicted: 0 }
  let hasUpstream = false
  for (const l of out.split('\n')) {
    if (l.startsWith('# branch.head ')) g.branch = l.slice(14)
    else if (l.startsWith('# branch.upstream ')) hasUpstream = true
    else if (l.startsWith('# branch.ab ')) {
      const [a, b] = l.slice(12).split(' ')
      g.ahead = Number(a)
      g.behind = -Number(b)
    } else if (l.startsWith('1 ') || l.startsWith('2 ')) {
      if (l[2] !== '.') g.staged++
      if (l[3] !== '.') g.modified++
    } else if (l.startsWith('u ')) g.conflicted++
    else if (l.startsWith('? ')) g.untracked++
  }
  if (!hasUpstream) g.ahead = g.behind = undefined
  if (g.branch !== 'main') {
    for (const ref of ['origin/main', 'main']) {
      const counts = await git($, ['rev-list', '--left-right', '--count', `${ref}...HEAD`])
      if (counts === undefined) continue
      const [behind, ahead] = counts.trim().split(/\s+/).map(Number)
      Object.assign(g, { mainRef: ref, mainAhead: ahead, mainBehind: behind })
      break
    }
  }
  return g
}

// A branch and its change dir match with `_` and `-` treated alike (feature/use_setup ↔ use-setup).
const sameName = (a: string, b: string) => a.replace(/_/g, '-') === b.replace(/_/g, '-')

// Every other branch (local or remote) whose own change dir, named like the branch, exists on it.
async function otherChanges($: EngineInterface, ours: string): Promise<string[]> {
  const refs = (await git($, ['for-each-ref', '--format=%(refname:short)', 'refs/heads', 'refs/remotes'])) ?? ''
  const asked = refs
    .split('\n')
    .filter(Boolean)
    .flatMap(ref => {
      const name = ref.split('/').pop()!
      return [...new Set([name, name.replace(/_/g, '-')])].map(n => ({ ref, name, dir: n }))
    })
    .filter(r => r.ref.includes('/') && !sameName(r.name, ours) && r.name !== 'main' && r.name !== 'HEAD')
  if (asked.length === 0) return []
  const out = await git(
    $,
    ['cat-file', '--batch-check'],
    asked.map(r => `${r.ref}:${DIR}/${r.dir}`).join('\n') + '\n',
  )
  const found = (out ?? '').split('\n').slice(0, asked.length)
  return [...new Set(asked.filter((_, i) => found[i] && !found[i].endsWith(' missing')).map(r => r.dir))].sort()
}

async function collect($: EngineInterface): Promise<Workflow> {
  const updatedAt = Date.now()
  const g = await readGit($).catch(() => undefined)
  const name = g?.branch.split('/').pop() ?? ''
  const others = await otherChanges($, name).catch(() => [])
  try {
    const dirs = (await $.fs.exists(DIR)) ? await $.fs.list(DIR) : []
    const match = dirs.find(d => d.kind === 'dir' && sameName(d.name, name))
    const ours = match ? await readChange($, match.name) : undefined
    return { ours, others, git: g, unreadable: false, updatedAt }
  } catch {
    return { others, git: g, unreadable: true, updatedAt }
  }
}

let inFlight: Promise<Workflow> | null = null

function refresh($: EngineInterface): Promise<Workflow> {
  inFlight ??= (async () => {
    try {
      const next = await collect($)
      await update($, workflowRef, () => next)
      return next
    } catch {
      return { ...EMPTY, unreadable: true, updatedAt: Date.now() }
    } finally {
      inFlight = null
    }
  })()
  return inFlight
}

// One row per step: 'done' | 'current' | 'todo'.
function rowsOf(c: Change) {
  const at = ROWS.findIndex(r => r.step === c.step)
  return ROWS.map((r, i) => {
    const kind = i < at ? 'done' : i === at ? 'current' : 'todo'
    const mark = kind === 'done' ? '✓ ' : kind === 'current' ? '▶ ' : '  '
    const n = r.step === 'apply' && c.total > 0 ? `  ${c.done}/${c.total}` : ''
    return { kind, text: `  ${mark}${r.label}${n}` }
  })
}

const plural = (n: number, what: string) => `${n} ${what}`

function gitLines(g: Git): string[] {
  const sync =
    g.ahead === undefined
      ? 'not pushed'
      : g.ahead + (g.behind ?? 0) === 0
        ? 'in sync with origin'
        : `${g.ahead} to push, ${g.behind} to pull`
  const tree = [
    g.staged && plural(g.staged, 'staged'),
    g.modified && plural(g.modified, 'modified'),
    g.untracked && plural(g.untracked, 'untracked'),
    g.conflicted && plural(g.conflicted, 'conflicted'),
  ].filter(Boolean)
  return [
    `  ${g.branch}  ·  ${sync}`,
    ...(g.mainRef ? [`  vs ${g.mainRef}:  ${g.mainAhead} ahead, ${g.mainBehind} behind`] : []),
    `  ${tree.length ? tree.join(' · ') : 'clean'}`,
  ]
}

// The picture as titled sections: our change, the other changes, git.
function sections(w: Workflow): { title: string; rows: { kind: string; text: string }[] }[] {
  const ours = w.ours
    ? { title: `${w.ours.name}  ·  ${w.ours.status}`, rows: rowsOf(w.ours) }
    : { title: w.git?.branch ? NONE.replace('change', `change on ${w.git.branch}`) : NONE, rows: [] }
  const others = { title: 'Other changes', rows: w.others.map(n => ({ kind: 'todo', text: `  ${n}` })) }
  const git = w.git ? [{ title: 'Git', rows: gitLines(w.git).map(text => ({ kind: 'todo', text })) }] : []
  return [ours, ...(w.others.length ? [others] : []), ...git]
}

/** The command's text answer: the same picture as the pane. */
function summaryText(w: Workflow): string {
  if (w.unreadable) return 'spec: specs/ not readable'
  return sections(w)
    .flatMap((s, i) => [
      s.title,
      ...s.rows.map(r => r.text),
      ...(i === 0 ? [TWEAK] : []),
      '',
    ])
    .join('\n')
    .trimEnd()
}

export const register: Register = on => {
  let isOffered = false

  on('session.start', async ($, e, next) => {
    // `status` is a name Claude Code ships; the registry refuses it.
    await $.command
      .register({
        name: 'spec-status',
        description: 'Spec workflow pane: toggle it, or "refresh"',
        argumentHint: '[refresh]',
      })
      .catch(() => undefined)
    try {
      $.clock.every(REFRESH_MS, () => {
        void refresh($)
      })
    } catch {}
    void refresh($)

    return next(e)
  })

  // session.start does not say whether the surface docks panes; a drawing does.
  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (!isOffered && e.viewport?.isFullscreen !== undefined) {
      isOffered = true
      if (e.viewport.isFullscreen) void $.ui.open({ id: PANE, title: 'Spec workflow' })
    }
    return next(e)
  })

  on('command.run', { command: 'spec-status' }, async ($, e) => {
    const w = await refresh($)
    if (e.args.trim() !== 'refresh') {
      const isOpen = await $.ui
        .panes()
        .then(panes => panes.some(p => p.id === PANE))
        .catch(() => false)
      if (isOpen) await $.ui.close({ id: PANE })
      else await $.ui.open({ id: PANE, title: 'Spec workflow' })
    }
    return { text: summaryText(w) }
  })

  on('turn.complete', async ($, e, next) => {
    if (e.agentId === undefined) await refresh($)
    return next(e)
  })

  on('tool.call', async ($, e, next) => {
    const ran = await next(e)
    if (['Write', 'Edit', 'Bash'].includes(String(e.tool))) void refresh($)
    return ran
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const w = await read($, workflowRef)
    const cols = Math.max(10, e.props.bodyColumns)
    const room = Math.max(2, (e.viewport?.rows ?? 24) - 4)
    const fit = (s: string) => s.slice(0, cols)
    if (w.unreadable) return <Text dimColor>{fit('specs/ not readable')}</Text>
    // Rows left once every section's title, gap and the tweak line are drawn; the other changes give way.
    const all = sections(w)
    let left = room - all.length * 2 - 1
    return (
      <Box flexDirection="column">
        {all.map((s, i) => {
          const rows = s.rows
          const cut = s.title === 'Other changes' && rows.length > left ? Math.max(0, left - 1) : rows.length
          left -= cut
          return (
            <Box flexDirection="column" marginBottom={1}>
              <Text bold>{fit(s.title)}</Text>
              {rows.slice(0, cut).map(r => (
                <Text
                  bold={r.kind === 'current'}
                  color={r.kind === 'current' ? 'success' : undefined}
                  dimColor={r.kind === 'done'}
                >
                  {fit(r.text)}
                </Text>
              ))}
              {cut < rows.length && <Text dimColor>{fit(`  +${rows.length - cut} more`)}</Text>}
              {i === 0 && <Text dimColor>{fit(TWEAK)}</Text>}
            </Box>
          )
        })}
      </Box>
    )
  })
}

import { expect, test } from 'claude-code/testing'

const PANE = {
  plugin: 'spec',
  component: 'Pane',
  requestId: 'spec-status',
  props: {
    title: 'Spec workflow',
    isFocused: false,
    bodyColumns: 80,
    placement: 'dock',
    scroll: { offset: 0, bodyRows: 40 },
    view: {},
  },
} as const

const file = (name: string) => ({ name, kind: 'file' as const, size: 1, mtimeMs: 0 })
const dir = (name: string) => ({ name, kind: 'dir' as const, size: 0, mtimeMs: 0 })

// Fake project: files maps `specs/changes/<change>/<file>` to its text.
// The engine hands fs hooks absolute paths, so match on the project-relative tail.
const fakeFs = (on: any, files: Record<string, string> | null) => {
  const tail = (p: string) => (p.includes('specs/') ? p.slice(p.indexOf('specs/')) : p)
  // Files outside specs/ by their path's end.
  const outside = (p: string) => Object.entries(files ?? {}).find(([k]) => !k.startsWith('specs/') && (p === k || p.endsWith(`/${k}`)))?.[1]
  on('fs.exists', (_: any, e: any) => ({ value: files !== null && tail(e.path) === 'specs/changes' }))
  on('fs.list', (_: any, e: any) => {
    const prefix = `${tail(e.path)}/`
    const names = Object.keys(files ?? {})
      .filter(f => f.startsWith(prefix))
      .map(f => f.slice(prefix.length))
    if (tail(e.path) === 'specs/changes') return { value: [...new Set(names.map(n => n.split('/')[0]))].map(dir) }
    return { value: names.map(file) }
  })
  on('fs.read', (_: any, e: any) => ({ value: (files ?? {})[tail(e.path)] ?? outside(e.path) ?? '' }))
}

// Fake git: `status` is `git status --porcelain=v2 --branch`'s output, `refs` the branches with the change
// dirs each holds, `vsMain` what `git rev-list --left-right --count origin/main...HEAD` prints.
type Git = {
  status: string
  refs?: Record<string, string[]>
  vsMain?: string
  /** `git rev-parse --show-toplevel`, `lsof … -Fpn` and `ps -o pid=,args=` output. */
  root?: string
  lsof?: string
  ps?: string
}
const fakeGit = (on: any, git: Git) => {
  const ran = (stdout: string, exitCode = 0) => ({
    value: { exitCode, stdout, stderr: '', isStdoutTruncated: false, isStderrTruncated: false },
  })
  on('process.run', (_: any, e: any) => {
    const [cmd, sub] = e.argv
    if (cmd === 'lsof') return git.lsof === undefined ? ran('', 1) : ran(git.lsof)
    if (cmd === 'ps') return ran(git.ps ?? '')
    if (sub === 'rev-parse') return git.root === undefined ? ran('', 128) : ran(`${git.root}\n`)
    if (sub === 'status') return ran(git.status)
    if (sub === 'rev-list') return git.vsMain === undefined ? ran('', 128) : ran(git.vsMain)
    if (sub === 'for-each-ref') return ran(Object.keys(git.refs ?? {}).join('\n') + '\n')
    if (sub === 'cat-file') {
      const out = String(e.init?.stdin ?? '')
        .split('\n')
        .filter(Boolean)
        .map(l => {
          const [ref, path] = l.split(':')
          const name = path.split('/').pop()!
          return (git.refs?.[ref] ?? []).includes(name) ? `abc tree 10` : `${l} missing`
        })
      return ran(out.join('\n') + '\n')
    }
    return ran('', 1)
  })
}

const status = (head: string, more = '') =>
  `# branch.oid abc\n# branch.head ${head}\n${more}`

const start = async ($: any, on: any) => {
  on('command.register', () => ({ value: { command: 'spec-status' } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_: any, e: any) => ({ cwd: e.cwd }))
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
}

const texts = async (ui: any) => ((await ui.findAll({ type: 'Text' })) as any[]).map(t => t.text)

const A = 'specs/changes/add-auth'
const PLAN = '- [x] a\n- [X] b\n- [ ] c\n- [ ] d\n- [ ] e\n'

test('applying: apply row shows 2/5 and is highlighted', async ($, on) => {
  fakeFs(on, {
    [`${A}/proposal.md`]: 'status: applying\norder: 1\n',
    [`${A}/plan.md`]: `status: applying\norder: 2\n${PLAN}`,
  })
  fakeGit(on, { status: status('feature/add-auth') })
  await start($, on)

  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ ...PANE, surface })
    const row = await ui.find({ type: 'Text', text: /apply\s+2\/5/ })
    expect(row?.text).toMatch(/apply\s+2\/5/)
    expect(row?.props).toMatchObject({ bold: true, color: 'success' })
    await ui.unmount()
  }
})

test('no specs/changes: shows the empty line', async ($, on) => {
  fakeFs(on, null)
  fakeGit(on, { status: status('feature/add-auth') })
  await start($, on)

  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  expect((await ui.find({ type: 'Text', text: /No active change/ }))?.text).toMatch(/No active change/)
  await ui.unmount()
})

test('applied + review.md: archive is highlighted', async ($, on) => {
  fakeFs(on, {
    [`${A}/plan.md`]: `status: applied\n${PLAN}`,
    [`${A}/review.md`]: 'findings\n',
  })
  fakeGit(on, { status: status('feature/add-auth') })
  await start($, on)

  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  const row = await ui.find({ type: 'Text', text: /archive/ })
  expect(row?.props).toMatchObject({ bold: true, color: 'success' })
  await ui.unmount()
})

test('only the branch\'s change is drawn; other changes are names from their own branches', async ($, on) => {
  fakeFs(on, {
    [`${A}/plan.md`]: `status: applying\n${PLAN}`,
    // a stale copy carried over from the branch this one started from
    ['specs/changes/old-one/plan.md']: `status: applying\n${PLAN}`,
  })
  fakeGit(on, {
    status: status('feature/add-auth'),
    refs: {
      'feature/add-auth': ['add-auth', 'old-one'],
      'origin/feature/org-unit-members': ['org-unit-members', 'old-one'],
      'feature/org-unit-members': ['org-unit-members'],
      'origin/feature/fix-just': [],
      main: [],
      origin: [],
    },
  })
  await start($, on)

  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  const all = await texts(ui)
  expect(all.filter(t => /^add-auth\s+·/.test(t))).toHaveLength(1)
  expect(all.some(t => /old-one/.test(t))).toBe(false)
  expect(all.filter(t => /^\s*org-unit-members$/.test(t))).toHaveLength(1)
  expect(all.some(t => /fix-just/.test(t))).toBe(false)
  expect(all.filter(t => /apply\s+2\/5/.test(t))).toHaveLength(1)
  await ui.unmount()
})

test('branch and change dir match with _ and - treated alike', async ($, on) => {
  fakeFs(on, { ['specs/changes/use-setup/plan.md']: `status: applying\n${PLAN}` })
  fakeGit(on, {
    status: status('feature/use_setup'),
    refs: { 'feature/use_setup': ['use-setup'], 'origin/feature/add_auth': ['add-auth'] },
  })
  await start($, on)

  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  const all = await texts(ui)
  expect(all.filter(t => /^use-setup\s+·/.test(t))).toHaveLength(1)
  expect(all.filter(t => /apply\s+2\/5/.test(t))).toHaveLength(1)
  expect(all.filter(t => /^\s*add-auth$/.test(t))).toHaveLength(1)
  await ui.unmount()
})

test('a branch without a change dir says so and still lists the others', async ($, on) => {
  fakeFs(on, { [`${A}/plan.md`]: `status: applying\n${PLAN}` })
  fakeGit(on, {
    status: status('feature/fix-just'),
    refs: { 'feature/fix-just': ['add-auth'], 'origin/feature/add-auth': ['add-auth'] },
  })
  await start($, on)

  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  const all = await texts(ui)
  expect(all.some(t => /No active change on feature\/fix-just/.test(t))).toBe(true)
  expect(all.some(t => /apply/.test(t))).toBe(false)
  expect(all.filter(t => /^\s*add-auth$/.test(t))).toHaveLength(1)
  await ui.unmount()
})

test('git summary: upstream, main, working tree', async ($, on) => {
  fakeFs(on, { [`${A}/plan.md`]: `status: applying\n${PLAN}` })
  fakeGit(on, {
    status: status(
      'feature/add-auth',
      '# branch.upstream origin/feature/add-auth\n# branch.ab +1 -2\n' +
        '1 M. N... 100644 100644 100644 a b x.ts\n1 .M N... 100644 100644 100644 a b y.ts\n' +
        '1 MM N... 100644 100644 100644 a b z.ts\nu UU N... 1 2 3 4 a b c w.ts\n? new.ts\n',
    ),
    vsMain: '3\t5\n',
  })
  await start($, on)

  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  const all = (await texts(ui)).join('\n')
  expect(all).toMatch(/feature\/add-auth\s+·\s+1 to push, 2 to pull/)
  expect(all).toMatch(/vs origin\/main:\s+5 ahead, 3 behind/)
  expect(all).toMatch(/archive\ntweak: side lane[^\n]*\nGit\n/)
  expect(all).toMatch(/2 staged · 2 modified · 1 untracked · 1 conflicted/)
  await ui.unmount()
})

test('git summary: unpushed branch, clean tree, no branch-name warning', async ($, on) => {
  fakeFs(on, null)
  fakeGit(on, { status: status('fix-just'), vsMain: '0\t0\n' })
  await start($, on)

  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  const all = (await texts(ui)).join('\n')
  expect(all).toMatch(/fix-just\s+·\s+not pushed/)
  expect(all).toMatch(/clean/)
  expect(all).not.toMatch(/rejects this branch name/)
  await ui.unmount()
})

test('Serving: the repo\'s running Vite servers, each with a link to the house and the Ofen', async ($, on) => {
  fakeFs(on, null)
  fakeGit(on, {
    status: status('main'),
    root: '/repo',
    lsof: 'p1\nf16\nn127.0.0.1:5181\np2\nf15\nn*:4173\np3\nf9\nn[::1]:9999\n',
    ps:
      '    1 node /repo/web/node_modules/.bin/vite --port 5181 --strictPort\n' +
      '    2 node /repo/.worktrees/tour/web/node_modules/.bin/vite preview --port 4173\n' +
      '    3 node /elsewhere/web/node_modules/.bin/vite\n',
  })
  await start($, on)

  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  const all = await texts(ui)
  expect(all).toContain('Serving')
  expect(all.some(t => /dev\s+:5181/.test(t))).toBe(true)
  expect(all.some(t => /preview\s+:4173\s+\(tour\)/.test(t))).toBe(true)
  const links = ((await ui.findAll({ type: 'Link' })) as any[]).map(l => [l.props.label, l.props.href])
  expect(links).toEqual([
    ['Haus', 'http://localhost:4173/frechen_blender/'],                         // by port
    ['Ofen', 'http://localhost:4173/frechen_blender/ofen.html'],
    ['Haus', 'http://localhost:5181/'],
    ['Ofen', 'http://localhost:5181/ofen.html'],
  ])
  await ui.unmount()
})

test('Serving: none running says how to start one', async ($, on) => {
  fakeFs(on, null)
  fakeGit(on, { status: status('main'), root: '/repo', lsof: '' })
  await start($, on)

  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  const all = await texts(ui)
  expect(all.some(t => /no server running/.test(t))).toBe(true)
  expect(await ui.findAll({ type: 'Link' })).toEqual([])
  await ui.unmount()
})

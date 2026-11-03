export type Step = 'none' | 'propose' | 'refine' | 'apply' | 'review' | 'archive'

export type Change = {
  name: string
  status: string
  done: number
  total: number
  reviewed: boolean
  step: Step
}

export type Git = {
  branch: string
  /** Commits to push and to pull; undefined when the branch has no upstream. */
  ahead?: number
  behind?: number
  /** Against origin/main (else main); undefined when neither resolves. */
  mainRef?: string
  mainAhead?: number
  mainBehind?: number
  staged: number
  modified: number
  untracked: number
  conflicted: number
}

/** A dev stack with a listening port (`84<n><role>`), or this checkout's own stack. */
export type Stack = {
  n: number
  /** Role digits listening: 1 client, 2 server, 3 compose Postgres, 4/5 embedded Postgres, 9 Keycloak. */
  roles: number[]
  /** The branch the stack was started on (`tmp/stack/branch`), else its checkout's current branch. */
  branch?: string
  /** This checkout's stack (`.env`). */
  ours: boolean
}

export type Workflow = {
  /** The change named like the branch (its last path segment). */
  ours?: Change
  /** Names of the changes on the other branches. */
  others: string[]
  git?: Git
  stacks: Stack[]
  unreadable: boolean
  updatedAt: number
}

declare module 'claude-code' {
  interface PluginState {
    spec: { workflow: Shaped<Workflow> }
  }
}

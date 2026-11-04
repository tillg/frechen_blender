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

/** A Vite server of this repo (or one of its worktrees) listening on localhost. */
export type Server = {
  kind: 'dev' | 'preview'
  port: number
  /** The worktree's name under .worktrees/, undefined for the main checkout. */
  worktree?: string
  /** The house's URL; the Ofen is `${url}ofen.html`. */
  url: string
}

export type Workflow = {
  /** The change named like the branch (its last path segment). */
  ours?: Change
  /** Names of the changes on the other branches. */
  others: string[]
  git?: Git
  servers: Server[]
  unreadable: boolean
  updatedAt: number
}

declare module 'claude-code' {
  interface PluginState {
    spec: { workflow: Shaped<Workflow> }
  }
}

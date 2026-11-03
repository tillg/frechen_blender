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

export type Workflow = {
  /** The change named like the branch (its last path segment). */
  ours?: Change
  /** Names of the changes on the other branches. */
  others: string[]
  git?: Git
  unreadable: boolean
  updatedAt: number
}

declare module 'claude-code' {
  interface PluginState {
    spec: { workflow: Shaped<Workflow> }
  }
}

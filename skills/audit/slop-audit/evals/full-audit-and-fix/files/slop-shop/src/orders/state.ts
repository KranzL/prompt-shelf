export type SyncState =
  | { kind: 'idle' }
  | { kind: 'syncing'; startedAt: number }
  | { kind: 'synced'; at: number }
  | { kind: 'failed'; error: Error }

export type SyncEvent =
  | { type: 'start'; at: number }
  | { type: 'succeed'; at: number }
  | { type: 'fail'; error: Error }
  | { type: 'reset' }

export function transition(state: SyncState, event: SyncEvent): SyncState {
  switch (state.kind) {
    case 'idle':
      return event.type === 'start' ? { kind: 'syncing', startedAt: event.at } : state
    case 'syncing':
      if (event.type === 'succeed') return { kind: 'synced', at: event.at }
      if (event.type === 'fail') return { kind: 'failed', error: event.error }
      return state
    case 'synced':
    case 'failed':
      if (event.type === 'reset') return { kind: 'idle' }
      if (event.type === 'start') return { kind: 'syncing', startedAt: event.at }
      return state
  }
}

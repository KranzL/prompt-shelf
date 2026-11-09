import { readFile } from 'node:fs/promises'

export async function readConfig(path: string): Promise<Record<string, string>> {
  try {
    const raw = await readFile(path, 'utf8')
    return parseConfig(raw)
  } catch (err) {
    throw new Error(`Could not read config at ${path}: ${(err as Error).message}`)
  }
}

export function parseConfig(raw: string): Record<string, string> {
  const out: Record<string, string> = {}
  for (const line of raw.split('\n')) {
    const [key, ...rest] = line.split('=')
    if (key.trim()) out[key.trim()] = rest.join('=').trim()
  }
  return out
}

export function optionalTags(input: { tags?: string[] }): string[] {
  return input.tags ?? []
}

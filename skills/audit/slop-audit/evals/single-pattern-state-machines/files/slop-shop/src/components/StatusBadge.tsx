export function StatusBadge({ status }: { status: string }) {
  const color =
    status === 'pending' ? 'gray' :
    status === 'paid' ? 'blue' :
    status === 'processing' ? 'yellow' :
    status === 'shipped' ? 'green' :
    status === 'cancelled' ? 'red' : 'gray'
  return <span style={{ color }}>{status}</span>
}

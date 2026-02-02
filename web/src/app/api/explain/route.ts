import { API_BASE } from '@/lib/config'

export async function POST(req: Request) {
  const body = await req.json()
  const res = await fetch(`${API_BASE}/explain`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': process.env.API_KEY!
    },
    body: JSON.stringify(body)
  })
  return Response.json(await res.json())
}   
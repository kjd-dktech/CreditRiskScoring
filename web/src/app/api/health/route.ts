import { API_BASE } from '@/lib/config'

export async function GET() {
  try {
    const res = await fetch(`${API_BASE}/health`, {
      headers: { 'x-api-key': process.env.API_KEY! },
    });
    const data = await res.json();
    return Response.json(data);
  } catch (error) {
    return Response.json({ status: 'offline' }, { status: 500 });
  }
}
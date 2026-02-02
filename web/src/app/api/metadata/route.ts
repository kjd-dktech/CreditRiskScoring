import { API_BASE } from '@/lib/config'

export async function GET() {
  try {
    const res = await fetch(`${API_BASE}/metadata`, {
      headers: { 'x-api-key': process.env.API_KEY! }
    });
    return Response.json(await res.json());
  } catch (error) {
    return Response.json({ loan_types: [], new_repeat_loan: [] });
  }
}
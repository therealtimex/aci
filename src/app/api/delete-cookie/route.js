import { NextResponse } from 'next/server';

export async function GET() {
  const response = NextResponse.json({ message: 'Cookie deleted' });
  response.cookies.delete('accessToken');
  return response;
}

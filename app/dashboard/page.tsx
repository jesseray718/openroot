import { cookies } from 'next/headers';
import { verifyJWT } from '@/lib/auth';
import { redirect } from 'next/navigation';

export default async function DashboardPage() {
  const cookieStore = await cookies();
  const token = cookieStore.get('token')?.value;

  const user = token ? await verifyJWT(token) : null;

  if (!user) {
    redirect('/login');
  }

  return (
    <main className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Protected Dashboard</h1>
      <div className="bg-slate-800 text-slate-100 p-6 rounded-lg shadow-md">
        <p className="text-lg">Welcome back, <span className="font-semibold">{user.email as string}</span>!</p>
        <p className="text-sm text-slate-400 mt-2">User ID: {user.userId as string}</p>
      </div>
    </main>
  );
}

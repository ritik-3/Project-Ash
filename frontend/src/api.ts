export type AssistResponse = {
  summary: string;
  success: boolean;
  step_results: Array<{ step_id: number; success: boolean; message: string }>;
};

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000';

export async function fetchStatus(): Promise<Record<string, unknown>> {
  const response = await fetch(`${API_BASE}/status`);
  if (!response.ok) {
    throw new Error('Failed to fetch status');
  }
  return (await response.json()) as Record<string, unknown>;
}

export async function executeAssist(text: string, confirmed = false): Promise<AssistResponse> {
  const response = await fetch(`${API_BASE}/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, confirmed }),
  });

  if (!response.ok) {
    throw new Error('Failed to execute request');
  }

  return (await response.json()) as AssistResponse;
}

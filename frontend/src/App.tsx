import { FormEvent, useEffect, useState } from 'react';
import { executeAssist, fetchStatus } from './api';

type Step = { step_id: number; success: boolean; message: string };

export function App() {
  const [status, setStatus] = useState<string>('loading');
  const [runtime, setRuntime] = useState<string>('unknown');
  const [text, setText] = useState<string>('open github.com');
  const [summary, setSummary] = useState<string>('');
  const [steps, setSteps] = useState<Step[]>([]);
  const [requireConfirm, setRequireConfirm] = useState<boolean>(false);

  useEffect(() => {
    void (async () => {
      try {
        const payload = await fetchStatus();
        setStatus(String(payload.status ?? 'ready'));
        const rt = payload.runtime as { phase?: string } | undefined;
        setRuntime(rt?.phase ?? 'unknown');
      } catch {
        setStatus('offline');
      }
    })();
  }, []);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const result = await executeAssist(text, requireConfirm);
    setSummary(result.summary);
    setSteps(result.step_results ?? []);
    setRequireConfirm(result.summary.includes('Confirmation required'));
  }

  return (
    <main className="layout">
      <section className="card">
        <h1>Project Ash Control</h1>
        <p>API status: <strong>{status}</strong> | runtime: <strong>{runtime}</strong></p>
        <form onSubmit={onSubmit} className="form">
          <textarea value={text} onChange={(e) => setText(e.target.value)} rows={4} />
          <div className="actions">
            <button type="submit">Run Task</button>
            <button type="button" onClick={() => setRequireConfirm(true)}>Force Confirm</button>
          </div>
        </form>
      </section>
      <section className="card">
        <h2>Result</h2>
        <p>{summary || 'No task run yet.'}</p>
        <ul>
          {steps.map((step) => (
            <li key={step.step_id}>{step.step_id}. {step.message}</li>
          ))}
        </ul>
      </section>
    </main>
  );
}

import { useEffect, useState } from "react";

const API = "/api/tickets";
const PRIORITIES = ["low", "medium", "high", "urgent"];
const STATUSES = ["open", "in_progress", "resolved", "closed"];

export default function App() {
  const [tickets, setTickets] = useState([]);
  const [stats, setStats] = useState(null);
  const [title, setTitle] = useState("");
  const [priority, setPriority] = useState("medium");
  const [assignee, setAssignee] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  async function refresh() {
    try {
      const [tRes, sRes] = await Promise.all([
        fetch(API),
        fetch(`${API}/stats/summary`),
      ]);
      if (!tRes.ok || !sRes.ok) throw new Error("Failed to load data");
      setTickets(await tRes.json());
      setStats(await sRes.json());
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function createTicket(e) {
    e.preventDefault();
    if (!title.trim()) return;
    try {
      const res = await fetch(API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, priority, assignee: assignee || null }),
      });
      if (!res.ok) throw new Error("Could not create ticket");
      setTitle("");
      setAssignee("");
      setPriority("medium");
      refresh();
    } catch (e) {
      setError(e.message);
    }
  }

  async function changeStatus(id, status) {
    await fetch(`${API}/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
    });
    refresh();
  }

  async function remove(id) {
    await fetch(`${API}/${id}`, { method: "DELETE" });
    refresh();
  }

  return (
    <div className="app">
      <header>
        <h1>🎫 DeskFlow</h1>
        <p className="tagline">A tiny helpdesk ticketing board</p>
      </header>

      {error && <div className="banner error">{error}</div>}

      {stats && (
        <section className="stats">
          <div className="stat">
            <span className="num">{stats.total}</span>
            <span className="label">Total</span>
          </div>
          {STATUSES.map((s) => (
            <div className="stat" key={s}>
              <span className="num">{stats.by_status[s] || 0}</span>
              <span className="label">{s.replace("_", " ")}</span>
            </div>
          ))}
        </section>
      )}

      <section className="card">
        <h2>New ticket</h2>
        <form onSubmit={createTicket} className="new-form">
          <input
            type="text"
            placeholder="What's the problem?"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
          <select value={priority} onChange={(e) => setPriority(e.target.value)}>
            {PRIORITIES.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
          <input
            type="text"
            placeholder="Assignee (optional)"
            value={assignee}
            onChange={(e) => setAssignee(e.target.value)}
          />
          <button type="submit">Add</button>
        </form>
      </section>

      <section className="card">
        <h2>Tickets</h2>
        {loading ? (
          <p className="muted">Loading…</p>
        ) : tickets.length === 0 ? (
          <p className="muted">No tickets yet. Create one above.</p>
        ) : (
          <ul className="tickets">
            {tickets.map((t) => (
              <li key={t.id} className={`ticket pr-${t.priority}`}>
                <div className="ticket-main">
                  <span className="ticket-title">{t.title}</span>
                  <span className="meta">
                    #{t.id} · {t.priority}
                    {t.assignee ? ` · ${t.assignee}` : ""}
                  </span>
                </div>
                <div className="ticket-actions">
                  <select
                    value={t.status}
                    onChange={(e) => changeStatus(t.id, e.target.value)}
                  >
                    {STATUSES.map((s) => (
                      <option key={s} value={s}>
                        {s.replace("_", " ")}
                      </option>
                    ))}
                  </select>
                  <button className="del" onClick={() => remove(t.id)}>
                    ✕
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <footer>
        <a href="/api/../docs" target="_blank" rel="noreferrer">
          API docs
        </a>
      </footer>
    </div>
  );
}

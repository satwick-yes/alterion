"use client";

import { useEffect, useState } from "react";

export default function Dashboard() {
  const [data, setData] = useState<any>({ tasks: {} });

  useEffect(() => {
    const interval = setInterval(() => {
      fetch("/api/status")
        .then((res) => res.json())
        .then((json) => setData(json))
        .catch((err) => console.error("Error fetching status:", err));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const tasks = Object.values(data.tasks || {});

  return (
    <div style={{ padding: "40px", color: "#fff", fontFamily: "Inter, sans-serif" }}>
      <h1 style={{ fontSize: "2rem", marginBottom: "20px", color: "#ff7700" }}>JARVIS Supervisor Dashboard</h1>
      <p style={{ color: "#aaa", marginBottom: "40px" }}>Live overview of autonomous background workers and tasks.</p>

      <div style={{ display: "grid", gap: "20px" }}>
        {tasks.length === 0 ? (
          <div style={{ padding: "20px", background: "#140600", borderRadius: "10px", border: "1px solid #471d00" }}>
            <p>No active tasks in the queue.</p>
          </div>
        ) : (
          tasks.map((task: any) => (
            <div key={task.task_id} style={{ padding: "20px", background: "#140600", borderRadius: "10px", border: "1px solid #471d00" }}>
              <h2 style={{ fontSize: "1.2rem", color: "#ffbb00", marginBottom: "10px" }}>{task.goal}</h2>
              <p style={{ marginBottom: "5px" }}><strong>Status:</strong> {task.status.toUpperCase()}</p>
              <p style={{ marginBottom: "15px", color: "#8c8c8c" }}>ID: {task.task_id}</p>
              
              {task.steps && task.steps.length > 0 && (
                <div style={{ marginTop: "10px", padding: "10px", background: "#0a0300", borderRadius: "5px" }}>
                  <h3 style={{ fontSize: "1rem", marginBottom: "10px", color: "#aaa" }}>Execution Steps:</h3>
                  {task.steps.map((step: any, idx: number) => (
                    <div key={idx} style={{ marginBottom: "5px", paddingLeft: "10px", borderLeft: "2px solid #55aa00" }}>
                      <p><strong>{step.tool}:</strong> {step.description} ({step.status})</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

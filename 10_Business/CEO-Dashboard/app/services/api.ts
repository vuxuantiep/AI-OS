// API Service für die Kommunikation mit dem FastAPI Backend

export interface ExecuteAgentTask {
  prompt: string;
  project_path?: string;
}

export interface AgentResponse {
  status: 'success' | 'error';
  terminal_logs: string;
  message: string;
}

export async function executeAgent(task: ExecuteAgentTask): Promise<AgentResponse> {
  // Placeholder für den echten API-Call
  console.log('Sending task to backend:', task);
  
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        status: 'success',
        terminal_logs: 'Done',
        message: 'Agent hat die Aufgabe im Terminal erfolgreich beendet.'
      });
    }, 1000);
  });
}

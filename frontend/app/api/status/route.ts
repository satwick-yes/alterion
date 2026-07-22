import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    const alterionDir = path.resolve(process.cwd(), '..'); 
    const stateLogPath = path.join(alterionDir, 'agent', 'state_log.json');
    
    if (fs.existsSync(stateLogPath)) {
      const data = fs.readFileSync(stateLogPath, 'utf8');
      return NextResponse.json(JSON.parse(data));
    } else {
      return NextResponse.json({ tasks: {}, error: "state_log.json not found" });
    }
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

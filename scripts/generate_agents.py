import os
import re
import json

def generate_agent_prompt(activity, description):
    # Basic templating for prompt generation. 
    # For a production system, this could call an LLM to generate highly nuanced prompts.
    role = f"{activity} Specialist"
    prompt = f"You are an expert {role}. Your primary goal is to {description.lower()} "
    prompt += "Use your tools efficiently to accomplish this task. Follow best practices for the domain."
    
    # Heuristic for tools
    tools = ["cmd_control", "file_controller"]
    if "analysis" in description.lower() or "search" in description.lower() or "research" in description.lower():
        tools.append("web_search")
    if "code" in description.lower() or "script" in description.lower() or "program" in description.lower():
        tools.append("code_helper")
        
    return role, prompt, tools

def parse_encyclopedia(input_file, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    registry = {}
    current_category = "general"

    if input_file.endswith('.docx'):
        import docx
        doc = docx.Document(input_file)
        
        # Parse the 3-row tables
        for table in doc.tables:
            cells = [cell.text.strip() for row in table.rows for cell in row.cells if cell.text.strip()]
            if len(cells) >= 3:
                try:
                    item_id = int(cells[0])
                    activity = cells[1]
                    description = cells[2]
                except ValueError:
                    continue
                    
                role, prompt, tools = generate_agent_prompt(activity, description)
                
                agent_config = {
                    "id": item_id,
                    "name": f"{activity} Agent",
                    "role": role,
                    "description": description,
                    "system_prompt": prompt,
                    "tools_required": tools,
                    "autonomy_level": "HUMAN_ASSISTED"
                }
                
                # Determine category by chunking every 500 agents
                cat_slug = f"agents_{((item_id - 1) // 500) * 500 + 1}_to_{((item_id - 1) // 500 + 1) * 500}"
                if cat_slug not in registry:
                    registry[cat_slug] = []
                    
                registry[cat_slug].append(agent_config)
    else:
        # Fallback to old txt logic if needed (removed for brevity)
        pass

    # Save to JSON files
    total_agents = 0
    for category, agents in registry.items():
        if not agents:
            continue
        out_path = os.path.join(output_dir, f"{category}.json")
        with open(out_path, 'w', encoding='utf-8') as out_f:
            json.dump({
                "department": category,
                "agents": agents
            }, out_f, indent=2)
        print(f"Generated {out_path} with {len(agents)} agents.")
        total_agents += len(agents)
        
    print(f"Successfully generated {total_agents} agent configurations across {len(registry)} departments.")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Use the DOCX file directly
    input_file = r"c:\Users\satwi\Downloads\alterion\PC_Activities_2450_Individual_Format.docx"
    output_dir = os.path.join(base_dir, "agent", "registry")
    
    print(f"Reading from: {input_file}")
    parse_encyclopedia(input_file, output_dir)

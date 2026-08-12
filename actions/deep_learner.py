import json
import time
import os
from pathlib import Path
from core.inference_wrapper import inference_client
from actions.web_search import _ddg_search, _format_ddg
from memory.vector_memory import vector_memory_db

def learn_topic_deeply(parameters: dict, player=None, speak=None) -> str:
    """
    Performs iterative deep research on a complex topic, stores facts in Vector DB,
    and generates a summary report document.
    """
    topic = parameters.get("topic", "").strip()
    if not topic:
        return "No topic provided for deep learning."

    if speak:
        speak(f"Right away, sir. I am beginning a deep dive into {topic}. This will take a few moments as I compile the research.")
    if player:
        player.write_log(f"DEEP_LEARNER: Starting deep research on '{topic}'...")

    # 1. Generate sub-topics
    prompt = (
        f"I need to learn everything about '{topic}'. "
        "Break this major topic down into exactly 4 or 5 critical sub-topics or core questions that I must research to have a comprehensive understanding. "
        "Return ONLY a JSON list of strings representing these sub-topics. "
        "Example: [\"History and Origins\", \"Core Principles\", \"Modern Applications\", \"Future Prospects\"]"
    )

    try:
        if player:
            player.write_log(f"DEEP_LEARNER: Generating research sub-topics...")
        response = inference_client.generate_json(
            prompt=prompt,
            system_instruction="You are an expert curriculum designer. Return only a JSON array of strings.",
            provider="gemini"
        )
        subtopics = response if isinstance(response, list) else response.get("subtopics", [])
        if not subtopics:
            subtopics = [f"{topic} core concepts", f"{topic} history", f"{topic} applications"]
    except Exception as e:
        if player:
            player.write_log(f"DEEP_LEARNER: Error generating subtopics, using defaults. {e}")
        subtopics = [f"{topic} core principles", f"{topic} overview", f"{topic} advanced concepts"]

    if player:
        player.write_log(f"DEEP_LEARNER: Sub-topics identified: {', '.join(subtopics)}")

    full_report = [f"# Comprehensive Report: {topic.title()}", ""]
    
    # 2. Iterate through sub-topics
    for sub in subtopics:
        if player:
            player.write_log(f"DEEP_LEARNER: Researching '{sub}'...")
        
        search_query = f"{topic} {sub}"
        results = _ddg_search(search_query, max_results=5)
        search_context = _format_ddg(search_query, results)

        synthesis_prompt = (
            f"You are writing a highly comprehensive, expert-level textbook chapter on '{topic}'.\n"
            f"Write the section covering: '{sub}'.\n\n"
            f"Here is some live search context to anchor your response:\n{search_context}\n\n"
            f"CRITICAL INSTRUCTIONS:\n"
            f"1. Do NOT restrict yourself to the search context. Utilize your vast internal knowledge base to write an incredibly detailed, exhaustive, and factual chapter section.\n"
            f"2. Ensure the section is extremely deep, covering history, mechanics, formulas, and edge cases where applicable. The section should be at least 800-1000 words long.\n"
            f"3. Do NOT include markdown code blocks, just standard markdown text with rich headers, sub-headers, and bullets."
        )

        try:
            section_content = inference_client.generate_text(
                prompt=synthesis_prompt,
                system_instruction="You are a brilliant researcher and textbook author. Synthesize the provided information into an exhaustively detailed chapter section.",
                provider="openrouter"
            )
        except Exception as e:
            if player:
                player.write_log(f"DEEP_LEARNER: Error synthesizing '{sub}': {e}")
            section_content = f"Information regarding {sub} could not be successfully synthesized. Raw data:\n{search_context}"

        # 3. Add to Full Report
        full_report.append(f"## {sub.title()}")
        full_report.append(section_content)
        full_report.append("")

        # 4. Extract atomic facts for Vector DB
        extract_prompt = (
            f"Extract the most important, standalone facts from the following text about '{topic}'.\n"
            f"Each fact should be a complete sentence that makes sense on its own.\n"
            f"Return ONLY a JSON list of strings.\n\n"
            f"Text:\n{section_content[:3000]}" # Limiting size to avoid huge prompts
        )
        
        try:
            facts_list = inference_client.generate_json(
                prompt=extract_prompt,
                system_instruction="You are a knowledge extraction engine. Return only a JSON array of strings containing standalone facts.",
                provider="gemini"
            )
            if isinstance(facts_list, dict) and "facts" in facts_list:
                facts_list = facts_list["facts"]
                
            if isinstance(facts_list, list):
                for fact in facts_list:
                    # Index into vector database
                    vector_memory_db.add_memory(f"Fact about {topic}: {fact}", category="deep_learning")
        except Exception as e:
            if player:
                player.write_log(f"DEEP_LEARNER: Failed to extract vector facts for '{sub}': {e}")
                
        # Sleep slightly to prevent rate limits
        time.sleep(2)

    # 5. Save Summary Report
    try:
        desktop_path = Path.home() / "Desktop"
        safe_topic_name = "".join([c if c.isalnum() else "_" for c in topic])
        report_file = desktop_path / f"VANI_Research_{safe_topic_name}.md"
        
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("\n".join(full_report))
            
        report_msg = f"A detailed summary report has been saved to your Desktop as '{report_file.name}'."
    except Exception as e:
        report_msg = f"Could not save the summary report to Desktop due to an error: {e}"

    success_msg = f"I have finished deeply researching '{topic}'. I have memorized all the core concepts, and {report_msg}"
    
    if player:
        player.write_log("DEEP_LEARNER: Research complete!")
        
    return success_msg

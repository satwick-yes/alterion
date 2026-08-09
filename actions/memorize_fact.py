def memorize_fact(parameters: dict, response=None, player=None) -> str:
    """
    Called by Vani to explicitly save a user preference or fact to LTM.
    """
    fact = parameters.get("fact", "").strip()
    if not fact:
        return "Please provide a 'fact' to memorize."
        
    from core.memory_manager import memory_manager
    result = memory_manager.store_memory(fact)
    
    if player:
        player.write_log(f"[Memory] 🧠 Learned: {fact}")
        
    return result

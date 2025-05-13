from typing import TypedDict, List, Dict, Any, Literal
from data.input.mock_asset_data import mock_asset_data
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field
import enum
import json
import os
from datetime import datetime
from langchain_openai import ChatOpenAI
from app.infrastructure.settings import settings
from langchain_core.language_models.chat_models import BaseChatModel
from app.infrastructure.database import get_db_context
from app.tools.get_solana_native_token_yield_options import (
    get_solana_native_token_yield_options,
)
from langchain.tools import Tool
from langchain.agents import AgentType, initialize_agent
from app.clients.llm_model_client import get_llm_model
from app.services.asset_opportunity_graph_script import (
    AssetState,
    generate_solana_optimization_suggestions,
    get_optimization_suggestion_from_profile
)

if __name__ == "__main__":
    # Build the graph
    workflow = StateGraph(AssetState)

    workflow.add_node("A", get_optimization_suggestion_from_profile)
    workflow.set_entry_point("A")
    workflow.add_edge("A", END)

    app = workflow.compile()
    # result = app.invoke(mock_asset_data)
    result = generate_solana_optimization_suggestions(assets=mock_asset_data)

    # Extract the optimization suggestions
    solana_opportunities = result.get("solana_opportunities", {})

    # Save the optimization suggestions to a JSON file
    output_dir = "data/output"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "optimizationOutput.json")

    with open(output_file, "w") as f:
        json.dump(solana_opportunities, f, indent=2)

    print(f"Optimization suggestions saved to {output_file}")
    print(json.dumps(solana_opportunities, indent=2))

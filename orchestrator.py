import json
from pydantic import BaseModel, Field
from groq import Groq
import os

from agents.github_agent import GithubAgent
from agents.linear_agent import LinearAgent
from utils.config import GROQ_API_KEY, get_available_users_str, get_user_id_by_name, get_user_name, get_user_mapping_str, USERS_CONFIG

class RoutingDecision(BaseModel):
    intent: str
    target_user: str
    reasoning: str

class Orchestrator:
    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment variables.")
        self.client = Groq(api_key=GROQ_API_KEY)
        self.pending_query: str = None
        self.pending_user: str = None

    def process_query(self, query: str) -> str:
        """
        Processes a user query by determining intent via LLM and user mapping,
        routing to the appropriate agent with multi-turn clarification memory.
        """
        available_users = get_available_users_str()
        extracted_user_id = get_user_id_by_name(query)

        # Handle multi-turn follow up: User provided missing user name for a pending query
        if self.pending_query and extracted_user_id:
            prev_query = self.pending_query
            self.pending_query = None
            combined_query = f"{prev_query} for {get_user_name(extracted_user_id)}"
            return self.process_query(combined_query)

        # Handle multi-turn follow up: User provided missing action for a pending user
        if self.pending_user and not extracted_user_id:
            prev_user_id = self.pending_user
            self.pending_user = None
            combined_query = f"{query} for {get_user_name(prev_user_id)}"
            return self.process_query(combined_query)

        # Clear any old context if new user is explicitly specified or fresh query starts
        if extracted_user_id:
            self.pending_query = None
        
        # 1. Routing phase (LLM)
        user_ids_str = ", ".join(USERS_CONFIG.keys())
        prompt = f"""
You are an intelligent routing agent. Your job is to classify user queries.
The system has two agents: GitHub and Linear.
The available users in the system are: {available_users} ({get_user_mapping_str()}).

Rules:
1. Intent Classification:
   - "github": If the query asks for GitHub data (repos, pull requests, PRs, stars, starred repositories, commits).
   - "linear": If the query asks for Linear data (issues, tickets, tasks, priority, projects, teams). Note: queries mentioning "issues" or "priority" without specifying GitHub or Linear should be classified as "linear".
   - "clarify_user": If the query relates to GitHub or Linear but NO user is mentioned in the query.
   - "clarify_action": If a user is mentioned, but NO specific action or service (GitHub or Linear) is asked for.
   - "out_of_scope": If the query is completely unrelated to GitHub or Linear (e.g. weather, sports, cooking).

2. target_user:
   - If a specific user from the mapping is mentioned -> target_user="<their target_user ID>".
   - If no user is mentioned -> target_user="".

User Query: {query}

You MUST return your response as a valid JSON object matching exactly this schema:
{{
  "intent": "<one of: github, linear, clarify_user, clarify_action, out_of_scope>",
  "target_user": "<one of: {user_ids_str}, or empty string>",
  "reasoning": "<string>"
}}
"""
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON string back into our Pydantic model
            decision_dict = json.loads(response.choices[0].message.content)
            decision = RoutingDecision(**decision_dict)
            
        except Exception as e:
            decision = RoutingDecision(
                intent="clarify_user" if not extracted_user_id else "github",
                target_user=extracted_user_id or "",
                reasoning=f"LLM Error fallback: {str(e)}"
            )

        # Programmatic user resolution to guarantee case-insensitive match accuracy
        target_user_id = extracted_user_id or decision.target_user.strip()
        if target_user_id not in USERS_CONFIG:
            target_user_id = ""

        print(f"\033[90m[Router Logic] Intent: {decision.intent} | Target: {target_user_id} | Reasoning: {decision.reasoning}\033[0m")

        # 2. Execution Phase (Agents)
        if decision.intent == "out_of_scope":
            self.pending_query = None
            self.pending_user = None
            return "I cannot answer this question"
            
        if not target_user_id or decision.intent == "clarify_user":
            self.pending_query = query
            self.pending_user = None
            return f"Which user's data would you like to access? Available users: {available_users}."

        if decision.intent == "clarify_action":
            self.pending_user = target_user_id
            self.pending_query = None
            user_disp_name = get_user_name(target_user_id)
            return f"What data would you like to see for {user_disp_name}? (e.g., GitHub pull requests or Linear issues)"
            
        if decision.intent == "github":
            self.pending_query = None
            self.pending_user = None
            try:
                agent = GithubAgent(user_id=target_user_id)
                return agent.process_query(query)
            except Exception as e:
                return str(e)
                
        if decision.intent == "linear":
            self.pending_query = None
            self.pending_user = None
            try:
                agent = LinearAgent(user_id=target_user_id)
                return agent.process_query(query)
            except Exception as e:
                return str(e)
                
        return "Unknown state reached in Orchestrator."

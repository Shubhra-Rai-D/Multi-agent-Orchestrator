import requests
from utils.config import get_user_config

class LinearAgent:
    def __init__(self, user_id: str):
        self.user_id = user_id
        config = get_user_config(user_id)
        if not config or not config.get("linear_api_key"):
            raise ValueError(f"Linear API key not found for user {user_id}")
        
        self.name = config.get("name")
        self.api_key = config.get("linear_api_key")
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        self.url = "https://api.linear.app/graphql"

    def get_issues(self, status_filter: str = None) -> str:
        """Fetch issues assigned to the user, optionally filtered by status."""
        
        # GraphQL query to get issues assigned to the authenticated user
        query = """
        query {
          viewer {
            assignedIssues(first: 50) {
              nodes {
                title
                identifier
                state {
                  name
                }
              }
            }
          }
        }
        """
        
        try:
            response = requests.post(self.url, headers=self.headers, json={'query': query})
            response.raise_for_status()
            data = response.json()
            
            issues = data.get("data", {}).get("viewer", {}).get("assignedIssues", {}).get("nodes", [])
            
            if status_filter:
                status_lower = status_filter.lower()
                # filter by state name, e.g., "in progress" or "todo"
                issues = [issue for issue in issues if issue.get("state", {}).get("name", "").lower() == status_lower]
                if not issues:
                     return f"{self.name} has no issues with status '{status_filter}'."
            else:
                if not issues:
                    return f"{self.name} has no assigned issues."

            count = len(issues)
            status_text = f" that are {status_filter}" if status_filter else " assigned"
            
            result = f"{self.name} has {count} issues{status_text}:\n"
            for issue in issues[:10]: # limit to 10
                state_name = issue.get("state", {}).get("name", "Unknown")
                result += f"- [{issue.get('identifier')}] {issue.get('title')} ({state_name})\n"
                
            return result.strip()
            
        except Exception as e:
            return f"Error fetching Linear issues for {self.name}: {str(e)}"
            
    def process_query(self, query: str) -> str:
        """Process the query using basic keyword matching for Linear requests."""
        query_lower = query.lower()
        
        if "in progress" in query_lower:
            return self.get_issues(status_filter="In Progress")
        elif "todo" in query_lower or "to do" in query_lower:
            return self.get_issues(status_filter="Todo")
        elif "high priority" in query_lower:
             
             return self.get_issues()
        else:
            return self.get_issues() # default to returning all assigned issues

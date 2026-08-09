from github import Github
from github import Auth
from utils.config import get_user_config

class GithubAgent:
    def __init__(self, user_id: str):
        self.user_id = user_id
        config = get_user_config(user_id)
        if not config or not config.get("github_token"):
            raise ValueError(f"GitHub token not found for user {user_id}")
        
        self.name = config.get("name")
        self.username = config.get("github_username")
        
        auth = Auth.Token(config.get("github_token"))
        self.gh = Github(auth=auth)

    def get_repositories(self) -> str:
        """Fetch repositories for the user."""
        try:
            # We get the authenticated user
            user = self.gh.get_user()
            repos = list(user.get_repos())
            
            if not repos:
                return f"{self.name} has no repositories."
            
            response = f"{self.name} has {len(repos)} repositories:\n"
            for i, repo in enumerate(repos, 1):
                response += f"{i}. {repo.name}\n"
            
            return response.strip()
        except Exception as e:
            return f"Error fetching repositories for {self.name}: {str(e)}"

    def get_pull_requests(self) -> str:
        """Fetch open pull requests created by the user across their repos."""
        try:
            query = f"author:{self.username} type:pr state:open"
            issues = self.gh.search_issues(query)
            
            if issues.totalCount == 0:
                return f"{self.name} has no open pull requests."
            
            response = f"{self.name} has {issues.totalCount} open pull requests:\n"
            for i, pr in enumerate(issues[:10], 1): # Limit to 10 for display
                response += f"{i}. {pr.title} (#{pr.number})\n"
                
            return response.strip()
        except Exception as e:
            return f"Error fetching pull requests for {self.name}: {str(e)}"

    def get_starred_repos(self) -> str:
        """Fetch repositories starred by the user."""
        try:
            user = self.gh.get_user()
            starred = list(user.get_starred())

            if not starred:
                return f"{self.name} has not starred any repositories."

            response = f"{self.name} has starred {len(starred)} repositories:\n"
            for i, repo in enumerate(starred[:10], 1):  # Limit to 10 for display
                stars = repo.stargazers_count
                response += f"{i}. {repo.full_name} ★{stars}\n"

            return response.strip()
        except Exception as e:
            return f"Error fetching starred repositories for {self.name}: {str(e)}"
    
    def process_query(self, query: str) -> str:
        """Routes the query to the correct GitHub capability based on keywords."""
        query_lower = query.lower()
        if "star" in query_lower:
            return self.get_starred_repos()
        elif "repositor" in query_lower or "repo" in query_lower:
            return self.get_repositories()
        elif "pull request" in query_lower or "pr" in query_lower or "prs" in query_lower:
            return self.get_pull_requests()
        else:
            return f"I am the GitHub agent. I can help with repositories, pull requests, and starred repos for {self.name}. Please clarify your request."

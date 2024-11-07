import requests
import os
def get_headers():
    TOKEN = os.getenv("GITHUB_TOKEN")
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
def get_url():
    return "https://api.github.com/graphql"

def get_user():
    return os.getenv("GITHUB_USER")

def get_projects(limit:int=20)->dict:
    username = get_user()
    query = """
    query {
      user(login: "%s") {
        projectsV2(first: %d) {
          nodes {
            id
            title
            number
          }
        }
      }
    }
    """ % (username, limit)
    response = requests.post(
        get_url(), headers=get_headers(), json={"query": query})
    return response.json()

def get_todos_in(project_name:str)->dict:
    projects = get_projects()
    project = next((p for p in projects["data"]["user"]["projectsV2"]["nodes"] if p["title"] == project_name), None)
    # print(project)
    # exit()

    query = """
    {
        node(id: "%s") {
            ... on ProjectV2 {
                items(first: 100) {
                    nodes {
                        type
                        fieldValues(first: 100) {
                            nodes {
                                ... on ProjectV2ItemFieldTextValue {
                                    text
                                }
                                ... on ProjectV2ItemFieldSingleSelectValue {
                                    name
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """ % (project["id"], )
    response = requests.post(
        get_url(), headers=get_headers(), json={"query": query})
    todos = response.json()['data']['node']['items']['nodes']
    def reshape_todo(todos:dict)->list:
        return [{"title": todo["fieldValues"]["nodes"][0]["text"], "status": todo["fieldValues"]["nodes"][1]["name"]} for todo in todos]
    todos = reshape_todo(todos)
    return todos

def todo_split_by_status(todos:dict)->dict:
    status = {}
    for todo in todos:
        if todo["status"] not in status:
            status[todo["status"]] = []
        status[todo["status"]].append(todo)
    return status

if __name__ == "__main__":
    todo = get_todos_in("LIFE")
    print(todo)
    print(todo_split_by_status(todo))

# '{"query":"query{user(login: \"jyukipann\") {projectV2(number: 2){id}}}"}'

# '{"query":"{user(login: "jyukipann") {projectsV2(first: 20) {nodes {id title}}}}"}'
# '{"query":"{user(login: "jyukipann") {projectsV2(first: 20) {nodes {id title}}}}"}'
# {'query': '{user(login: "jyukipann") {projectsV2(first: 20) {nodes {id title}}}}'}

# {'errors': [{'path': ['query', 'user', 'projectV2'], 'extensions': {'code': 'missingRequiredArguments', 'className': 'Field', 'name': 'projectV2', 'arguments': 'number'}, 'locations': [{'line': 4, 'column': 13}], 'message': "Field 'projectV2' is missing required arguments: number"}, {'path': ['query', 'user', 'projectV2', 'title'], 'extensions': {'code': 'argumentNotAccepted', 'name': 'projectV2', 'typeName': 'Field', 'argumentName': 'title'}, 'locations': [{'line': 4, 'column': 23}], 'message': "Field 'projectV2' doesn't accept argument 'title'"}]}
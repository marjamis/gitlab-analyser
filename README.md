# gitlab-analyser

Using the GitLab GraphQL API to generate data about the groups, project, repos, etc for a GitLab endpoint. For stats, repo health, and other fun data analysis.

Currently the analyser will collect basic information about:

- GitLab Groups, and sub-groups
- GitLab Projects
  - List of Branches, and their last commits details
  - Pipeline Schedules

## Example

The application requires the following environment variables set to know which GitLab GraphQL API endpoint to connect to:

| Environment Variables | Value |
| --- | --- |
| GITLAB_TOKEN | A token from GitLab with read permissions on the Groups and Project you want information for. Additional information available at [GitLab](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html). |
| GITLAB_GRAPHQL_ENDPOINT | The API endpoint of your GitLab. Example being ```http://localhost:8080/api/graphql``` |

## Options

```bash
$ python main.py --help

Usage: main.py [OPTIONS]

Options:
  --generate-data BOOLEAN     Generate new data instead of using saved data
                              [default: True]
  --output-format [html|csv]  Type of output  [default: html]
  --output-directory TEXT     Output location  [default: .]
  --help                      Show this message and exit.
```

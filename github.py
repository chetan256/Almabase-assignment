import sys
import re
import requests
import json

class GitHub:

    def __init__(self):
        self.github_url = r'https://api.github.com/'
        self.org_url = r'orgs/'
        self.search_repo_url = r'search/repositories'

    def get_request(self,url):
        return requests.get(url)

    def is_valid_organization(self,organization):
        url = self.github_url + self.org_url + organization
        print "Organization URL: " + url
        response = self.get_request(url)
        return (response.status_code == 200)

    def get_popular_repositories(self,organization,sort_on,n):
        url = self.github_url + self.search_repo_url + r'?q=user:' + organization + r'&sort=' + sort_on
        print "Search URL: " + url
        response = self.get_request(url)
        repo_json_response = json.loads(response.text)
        results = []
        for repo in repo_json_response['items'][0:n]:
            results.append((repo['id'],repo['name'],repo['forks']))
        if len(results) == n:
            return results
        else:
            #Handle Paginated results
            next_page, last_page = map(int,re.findall(r'page=(\d+)',response.headers['Link']))
            while next_page <= last_page and len(results) < n:
                remaining_result_count = n - len(results)
                next_url = url + r'&page=' + str(next_page)
                print "Fetching Results from: " + next_url
                response = self.get_request(next_url)
                repo_json_response = json.loads(response.text)
                for repo in repo_json_response['items'][0:remaining_result_count]:
                    results.append((repo['id'],repo['name'], repo['forks']))
                next_page+=1
        return results

    def get_top_committees(self,org,id,m):
        url = self.github_url + 'repositories/' + str(id) +'/contributors'
        print "Contributors URL: " + url
        response = self.get_request(url)
        contributors_json_response = json.loads(response.text)
        results = []
        for contribution in contributors_json_response[0:m]:
            results.append((contribution['login'], contribution['contributions']))
        if len(results) == m:
            return results
        else:
            # Handle Paginated results
            if 'Link' in response.headers:
                print response.headers['Link']
                next_page, last_page = map(int, re.findall(r'page=(\d+)', response.headers['Link']))
                while next_page <= last_page and len(results) < n:
                    remaining_result_count = m - len(results)
                    next_url = url + r'?page=' + str(next_page)
                    print "Fetching Results from: " + next_url
                    response = self.get_request(next_url)
                    contributors_json_response = json.loads(response.text)
                    for contribution in contributors_json_response[0:remaining_result_count]:
                        results.append((contribution['login'], contribution['contributions']))
                    next_page += 1
        return results


if __name__ == '__main__':
    if len(sys.argv)!=4:
        print "Invaild arguments"
        print "Usage: github.py organization n m"
        print "Ex: github.py google 5 6"
    org , n , m = sys.argv[1:]
    github = GitHub()
    if github.is_valid_organization(org):
        print org + " is a valid Organization"
        sort_on = 'forks'
        print "Sorting Results on " + sort_on + " count"
        popular_repos_org = github.get_popular_repositories(org,sort_on,int(n))
        print n + " most popular Repositories of " + org + " and their fork counts:"
        for repo in popular_repos_org:
            print "##############################"
            print repo[0], repo[1] , repo[2]
            top_committees = github.get_top_committees(org,repo[0],int(m))
            print m + " most popular Committees and their commit counts:"
            for committee in top_committees:
                print committee[0],committee[1]
            print "##############################"
    else:
        print "Invalid Organization"
        sys.exit()
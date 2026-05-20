from github_api import get_github

g = get_github()

def get_rate():
    return g.get_rate_limit()

if __name__ == "__main__":
    rate = get_rate()
    print(rate)

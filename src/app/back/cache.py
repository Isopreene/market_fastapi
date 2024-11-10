class Cache:
    def __init__(self):
        """Кэш для проекта. В следующем поменять на Redis"""
        self.categories: list = []
        self.articles: list = []
        self.pages_number: int = 0

    def get_articles(self, limit: int = 100, page: int = 1) -> list:
        self.pages_number: int = (len(self.articles) / limit).__ceil__()
        return self.articles[(page-1)*limit:page*limit+1]

from .template import CrawlerTemplate

class ExampleCrawler(CrawlerTemplate):
    def __init__(self, *args, **kwargs) -> None:
        """This is an example Crawler class."""
        super().__init__(*args, **kwargs)

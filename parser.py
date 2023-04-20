from base_parser import BaseScraper
from playwright.sync_api import Playwright, sync_playwright


class Jooble(BaseScraper):

    def scrape_data(self, tag):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            def intercept_request(route, request):
                headers = request.headers
                headers['User-Agent'] = 'Mediapartners-Google'
                route.continue_(headers=headers)

            page.route('**', intercept_request)

            url = f'https://jooble.org/SearchResult?{tag}'
            page.goto(url)

            # Wait for the job search results to load
            page.wait_for_selector('div.infinite-scroll-component__outerdiv > div > div > article')

            jobs = page.query_selector_all('//div[@class="infinite-scroll-component__outerdiv"]/div/div/article')

            for j in jobs:
                j.wait_for_selector('a')
                url = j.query_selector('a').get_attribute('href')
                date = j.query_selector('section > div._15xYk4 > div > div.fAH3JV > div.e0VAhp').text_content()
                company = j.query_selector(
                    'section > div._15xYk4 > div > div._1JrOtp._30OfJk > div > p.Ya0gV9').text_content()
                location = j.query_selector('section > div._15xYk4 > div > a.fAH3JV > div._2_Ab4T').text_content()
                job = {
                    'source': self.source(),
                    'title': j.query_selector('header > h2 > a').text_content(),
                    'company': company,
                    'url': url,
                    'location': location,
                    'date': self._previous_date(date),
                    'raw_date': date,
                    'description': j.query_selector('div._9jGwm1 > span').inner_text(),
                    'salary_range': j.query_selector('div._3-PWkq > p.jNebTl').inner_text(),
                    'full_description': self.full_description(),
                }
                print(job)

            browser.close()

    def source(self):
        return 'jooble'

    def full_description(self):
        # TODO
        pass

jooble = Jooble()
jooble.scrape_data('rgns=Remote&salaryMin=30000&salaryRate=5&ukw=python%20developer')

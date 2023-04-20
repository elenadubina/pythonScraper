from base_parser import BaseParser
from playwright.sync_api import Playwright, sync_playwright


class Jooble(BaseParser):

    def scrape_data(self, tag):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()

            def intercept_request(route, request):
                headers = request.headers
                headers['User-Agent'] = 'Mediapartners-Google'
                route.continue_(headers=headers)

            context.route('**', intercept_request)

            page = context.new_page()
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
                    'full_description': self.full_description(context, url),
                }
                print(job)

            browser.close()

    def source(self):
        return 'jooble'

    def full_description(self, context, url):
        new_page = context.new_page()
        response = new_page.goto(url)

        # Print the status code
        print(f'Status code: {response.status}')

        # Extract the full job description here
        full_description_selector = '#app > div > div._1n0Vx9 > div._34s2-- > main > div > div > div > div._2W_4lT > div.Cf01MF > div > div > div > div > div._1yTVFy'
        raw_full_description = new_page.inner_text(full_description_selector)
        # Clean up the text by replacing newline characters with spaces
        cleaned_description = raw_full_description.replace('\n', ' ')

        # Remove special characters (e.g., '\xa0') with a space
        cleaned_description = cleaned_description.replace('\xa0', ' ')
        new_page.close()
        return cleaned_description


jooble = Jooble()
jooble.scrape_data('rgns=Remote&salaryMin=30000&salaryRate=5&ukw=python%20developer')


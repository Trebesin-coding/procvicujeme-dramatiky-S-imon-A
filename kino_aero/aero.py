from playwright.sync_api import sync_playwright, Browser, Page, ElementHandle
import json

def get_program_names(program: ElementHandle) -> list[str]:
    name_labels: list[ElementHandle] = program.query_selector_all(".program__movie-name")
    names: list[str] = []

    for name_label in name_labels:
        names.append(name_label.text_content())
    
    return names

def get_program_prices(program: ElementHandle) -> list[int]:
    price_divs: list[ElementHandle] = program.query_selector_all(".program__price")
    prices: list[int] = []

    for price_div in price_divs:
        price_string: str = price_div.query_selector("span").text_content()
        price_string = price_string.strip()

        if price_string == "Zdarma":
            prices.append(0)
        else:
            price: int = int(price_string[:len(price_string) - 3])

            prices.append(price)
    
    return prices

def rate_film(name: str, price: int, page: Page) -> dict:
    page.goto("https://www.csfd.cz/")

    page.query_selector('input[name="q"]').fill(name)

    page.wait_for_timeout(2000)

    page.query_selector(".tt-suggestion").click()

    page.wait_for_timeout(1000)

    rating: str = page.query_selector(".film-rating-average").text_content()
    rating = rating.strip()

    film_name: str = page.query_selector("h1").text_content()
    film_name = film_name.strip()

    film_rating: dict = {
        "name": "",
        "rating": "",
        "rating_number": 0,
        "price": 0,
        "value": "",
        "value_number": 0
    }

    film_rating["name"] = name
    film_rating["price"] = price

    if name != film_name:
        film_rating["rating"] = "not on ČSFD"
    else:
        film_rating["rating"] = rating

        rating_number: int = int(rating[:len(rating) - 1])

        film_rating["rating_number"] = rating_number

        value: float = rating_number / price
        value *= 1000
        value = round(value)
        value /= 10

        film_rating["value"] = str(value) + "%"
        film_rating["value_number"] = value

    return film_rating

def main() -> None:
    with sync_playwright() as p:
        browser: Browser = p.chromium.launch(headless=False)

        page: Page = browser.new_page()
        page.goto("https://www.kinoaero.cz/")

        programs: list[ElementHandle] = page.query_selector_all(".program")
        ratings: list[dict] = []

        day_limit: int = 2
        current_day_index: int = 0

        program_datas: list = []

        for program in programs:
            current_day_index += 1

            if current_day_index > day_limit:
                break

            names: list[str] = get_program_names(program)
            prices: list[str] = get_program_prices(program)

            program_data: list = [names, prices]
            program_datas.append(program_data)

        for program_data in program_datas:
            names: list[str] = program_data[0]
            prices: list[int] = program_data[1]

            for name in names:
                index: int = names.index(name)
                price: int = prices[index]

                rating: dict = rate_film(name, price, page)

                ratings.append(rating)
            
            page.goto("https://www.kinoaero.cz/")

        with open("rating.json", "w") as file:
            json.dump(ratings, file, indent=4)
        

        input("Zadej input pro zavření prohlížeče")

        browser.close()

if __name__ == "__main__":
    main()